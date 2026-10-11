"""Offline failed-prefix diagnostics only. No device IO, repair or admission."""
from collections import Counter
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'imu-design-20261010/single-uart/controller'))
from capture_report import audit_capture,_imu_summary
from ulog_mavlink import validate_ulog

def wire_gaps(rows):
    frames=[r for r in rows if r.get('event')=='frame' and (r.get('sysid'),r.get('compid'))==(1,1)]
    wire=[]
    for before,after in zip(frames,frames[1:]):
        expected=(before['seq']+1)&255
        if after['seq']!=expected:
            wire.append(dict(before_seq=before['seq'],after_seq=after['seq'],expected=expected,
                missing_modulo256=(after['seq']-expected)&255,
                before_type=before['type'],after_type=after['type'],
                receipt_interval_ns=after['receipt_mono_ns']-before['receipt_mono_ns']))
    logging=[r for r in frames if r['type'] in ('LOGGING_DATA','LOGGING_DATA_ACKED')]
    gaps=[]; duplicates=[]
    for before,after in zip(logging,logging[1:]):
        previous=before['fields']['sequence']; actual=after['fields']['sequence']
        if actual==previous and after['type']=='LOGGING_DATA_ACKED':
            duplicates.append(actual);continue
        expected=(previous+1)&65535
        if actual!=expected:
            gaps.append(dict(before_sequence=previous,after_sequence=actual,expected=expected,
                missing_modulo65536=(actual-expected)&65535,
                before_mavlink_seq=before['seq'],after_mavlink_seq=after['seq'],
                before_receipt_ns=before['receipt_mono_ns'],after_receipt_ns=after['receipt_mono_ns']))
    return dict(px4_frames=len(frames),logging_frames=len(logging),
        frame_counts=dict(Counter(r['type'] for r in frames)),
        mavlink_sequence_discontinuities=wire,logging_discontinuities=gaps,
        duplicate_acked_logging_sequences=duplicates,
        caveat='Modulo sequence evidence on retained frames, not exact sensor loss or an authenticated delivery counter',
        transport_qualified=False,openvins_admissible=False)

def complete_record_view(raw):
    if len(raw)<16 or raw[:8]!=b'ULog\x01\x12\x35\x01':raise ValueError('ULog header absent')
    cursor=16
    while cursor+3<=len(raw):
        end=cursor+3+int.from_bytes(raw[cursor:cursor+2],'little')
        if end>len(raw):break
        cursor=end
    return raw[:cursor],len(raw)-cursor

def main():
    directory=HERE/'download/physical-trial-01'
    report=audit_capture(directory,epoch='CURRENT_D6F12AD1_FAILED_UART_PREFIX')
    summary=report['session']
    assert summary['error']=='logging sequence discontinuity: expected 435, received 436'
    assert not report['transport_qualified'] and not report['openvins_admissible']
    rows=[json.loads(x) for x in (directory/'wire.jsonl').read_text().splitlines()]
    raw=(directory/'received-prefix.bin').read_bytes()
    original_sha=hashlib.sha256(raw).hexdigest()
    assert original_sha==summary['received_prefix_sha256']
    view,excluded=complete_record_view(raw)
    _,log=validate_ulog(view)
    imu=_imu_summary(view,instance=0,gyro_device=6684690,accel_device=6946834,
                     epoch='CURRENT_BMI088_FAILED_PREFIX_DIAGNOSTICS_NOT_DATASET')
    topics=[dict(name=d.name,instance=d.multi_id,records=len(d.data['timestamp'])) for d in log.data_list]
    cpuload=[float(v) for d in log.data_list if d.name=='cpuload' for v in d.data['load']]
    states={}
    for d in log.data_list:
        if d.name=='actuator_armed':states['armed_values']=sorted(set(bool(v) for v in d.data['armed']))
        if d.name=='vehicle_status':states['arming_states']=sorted(set(int(v) for v in d.data['arming_state']))
    tx_counts=Counter()
    from ulog_mavlink import decoder_module
    for row in rows:
        if row.get('event')=='tx_write':
            message=decoder_module.Decoder().feed(bytes.fromhex(row['wire_hex']),row['receipt_mono_ns'])[0]
            label=message['type']
            if label=='COMMAND_LONG':label+=':'+str(message['fields']['command'])
            tx_counts[label]+=1
    result=dict(session_result='FAILED_SEQUENCE_GAP_NO_60S_ACCEPTANCE',
        raw_prefix_sha256=original_sha,original_bytes=len(raw),diagnostic_in_memory_bytes=len(view),
        diagnostic_excluded_partial_bytes=excluded,
        diagnostic_view='COMPLETE_RETAINED_RECORDS_IN_MEMORY_ONLY; no shortened ULog written, failure unchanged',
        normal_data_first_to_last_accepted_receipt_s=(summary['last_logging_mono_ns']-summary['normal_data_start_mono_ns'])/1e9,
        wire=wire_gaps(rows),tx_write_counts=dict(tx_counts),topics=topics,imu=imu,
        cpu_load_retained_samples=cpuload,disarmed_retained_records=states,
        changed_parameter_count_retained=len(log.changed_parameters),
        temporal_alignment='NO_CAMERA_CLOCK_MAP',tail_complete='UNKNOWN',source_complete='UNKNOWN',
        transport_qualified=False,openvins_admissible=False)
    assert hashlib.sha256((directory/'received-prefix.bin').read_bytes()).hexdigest()==original_sha
    with (HERE/'failure-analysis.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
