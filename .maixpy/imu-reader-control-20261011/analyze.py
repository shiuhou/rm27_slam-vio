"""Offline reader-control evidence, reusing frozen audits; never VIO admission."""
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'imu-uart-reduced-trial-20261011'))
from trial_analysis import diagnostic_json,cpu_summary
sys.path.insert(0,str(HERE.parent/'imu-uart-negotiated-trial-20261011'))
from analyze_failure import complete_record_view,wire_gaps
sys.path.insert(0,str(HERE.parent/'imu-gap-diagnosis-20261011'))
import diagnose as link_diagnostics
sys.path.insert(0,str(HERE.parent/'imu-design-20261010/single-uart/controller'))
from capture_report import audit_capture,_imu_summary,distribution
from ulog_mavlink import validate_ulog,inspect_imu
from compare import comparison

EPOCH='D6F12AD1_FIXED_2500HZ_READER_REAL_UART_CONTROL'
def save(name,row):
    with (HERE/name).open('x',encoding='utf-8') as f:
        json.dump(diagnostic_json(row),f,indent=2,allow_nan=False)
def jsonl(path):return [json.loads(x) for x in path.read_text().splitlines()]

def main():
    capture=HERE/'download/physical-trial-01'
    audit=audit_capture(capture,epoch=EPOCH)
    save('capture-audit.json',audit)
    wire=jsonl(capture/'wire.jsonl')
    frames=[r for r in wire if r.get('event')=='frame' and (r.get('sysid'),r.get('compid'))==(1,1)]
    checked=[link_diagnostics.verify_unknown_frame(r) for r in frames if r.get('crc_status')!='VERIFIED']
    raw=(capture/'received-prefix.bin').read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    view,excluded=complete_record_view(raw)
    _,log=validate_ulog(view)
    imu=_imu_summary(view,instance=0,gyro_device=6684690,accel_device=6946834,epoch=EPOCH)
    original_rows=inspect_imu(view,instance=0,gyro_device=6684690,accel_device=6946834,epoch=EPOCH)['diagnostic_means']
    originals=[r['original'] for r in original_rows]
    old_path=HERE.parent/'imu-uart-reduced-trial-20261011/download/physical-trial-01/framing-valid.ulg'
    assert hashlib.sha256(old_path.read_bytes()).hexdigest()=='658287cb149e1afbd56c9df799807729cd0930e4943190a580fb08b42eebca06'
    old=inspect_imu(old_path.read_bytes(),instance=0,gyro_device=6684690,accel_device=6946834,epoch='FROZEN_BASELINE')
    statuses={name:[{key:values[i].item() for key,values in d.data.items()}
        for d in log.data_list if d.name==name for i in range(len(d.data['timestamp']))]
        for name in ('logger_status','vehicle_imu_status','sensor_selection','cpuload','actuator_armed','vehicle_status')}
    compared=comparison([r['original'] for r in old['diagnostic_means']],originals,statuses['logger_status'])
    save('comparison.json',compared)
    normal=[r for r in frames if r['type']=='LOGGING_DATA']
    normal_span=(normal[-1]['receipt_mono_ns']-normal[0]['receipt_mono_ns'])/1e9 if len(normal)>1 else None
    logging=[r for r in frames if r['type'] in ('LOGGING_DATA','LOGGING_DATA_ACKED')]
    intervals=[(b['receipt_mono_ns']-a['receipt_mono_ns'])/1e6 for a,b in zip(logging,logging[1:])]
    steady=[r for r in frames if normal[0]['receipt_mono_ns']<=r['receipt_mono_ns']<=normal[-1]['receipt_mono_ns']] if normal else []
    cpu=cpu_summary(jsonl(HERE/'download/metrics.jsonl'))
    result=dict(scope='ONE_REAL_FIXED_READER_CONTROL_NOT_VIO_QUALIFICATION',
        raw_prefix_sha256=digest,original_bytes=len(raw),in_memory_complete_records_bytes=len(view),
        excluded_partial_bytes=excluded,raw_decode_parity_verified=audit['raw_decode_parity'],
        all_retained_px4_frames_crc_verified=True,px4_frames=len(frames),unknown_frames_verified=checked,
        bad_data_events=sum(r.get('event')=='bad_data' for r in wire),
        session_error=audit['session']['error'],finite_framing_verified=audit['session']['finite_framing_verified'],
        normal_LOGGING_DATA_first_to_last_receipt_s=normal_span,normal_logging_frames=len(normal),
        normal_logging_wire_bytes=sum(len(bytes.fromhex(r['wire_hex'])) for r in normal),
        steady_all_frame_wire_bytes=sum(len(bytes.fromhex(r['wire_hex'])) for r in steady),
        packet_read_receipt_intervals_ms=distribution(intervals),wire=wire_gaps(wire),imu=imu,
        topic_records=[dict(name=d.name,instance=d.multi_id,records=len(d.data['timestamp'])) for d in log.data_list],
        retained_status_records=statuses,retained_changed_parameters=len(log.changed_parameters),
        retained_dropouts=[dict(timestamp=d.timestamp,duration=d.duration) for d in log.dropouts],
        cpu=cpu,uart_counters=jsonl(HERE/'download/uart-counters.jsonl'),
        link_counters=link_diagnostics.correlate(frames),
        packet_local_stop_metadata=link_diagnostics.packet_metadata([r for r in frames if r['type']=='LOGGING_DATA_ACKED']),
        comparison=compared,data_caveat='Integrals not instantaneous samples; bytes untouched; READ receipts not measurement latency',
        source_complete='UNKNOWN',tail_complete='UNKNOWN',clock_synchronization='UNKNOWN',
        transport_qualified=False,openvins_admissible=False,stage_c='CLOSED')
    assert hashlib.sha256((capture/'received-prefix.bin').read_bytes()).hexdigest()==digest
    save('analysis.json',result)
    print(json.dumps(dict(error=result['session_error'],normal_receipt_s=normal_span,imu=imu,
        cpu=cpu,gyro_continuity=compared['observed_gyro_continuity'],
        logger=compared['candidate_logger'],wire_gaps=len(result['wire']['mavlink_sequence_discontinuities']),
        logging_gaps=len(result['wire']['logging_discontinuities']),openvins_admissible=False),indent=2,allow_nan=False))

if __name__=='__main__':main()
