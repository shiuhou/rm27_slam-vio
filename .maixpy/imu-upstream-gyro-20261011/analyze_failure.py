"""FAILED transition diagnostics only; no device IO, prefix repair or admission."""
from collections import Counter
import hashlib,json,importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('legacy_failed_prefix',
    HERE.parent/'imu-uart-negotiated-trial-20261011/analyze_failure.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
complete_record_view,wire_gaps=prior.complete_record_view,prior.wire_gaps
sys.path.insert(0,str(HERE.parent/'imu-gap-diagnosis-20261011'))
import diagnose as link
sys.path.insert(0,str(HERE.parent/'imu-uart-reduced-trial-20261011'))
from trial_analysis import diagnostic_json,cpu_summary
sys.path.insert(0,str(HERE.parent/'imu-design-20261010/single-uart/controller'))
from capture_report import audit_capture
from ulog_mavlink import validate_ulog,decoder_module

def main():
    folder=HERE/'download/physical-trial-01'
    audit=audit_capture(folder,epoch='D6F12AD1_FAILED_UPSTREAM_GYRO_TRANSITION')
    summary=audit['session']
    assert summary['error']=='logging sequence discontinuity: expected 287, received 288'
    assert summary['state']=='DONE' and not summary['finite_framing_verified']
    assert not (folder/'framing-valid.ulg').exists()
    wire=[json.loads(x) for x in (folder/'wire.jsonl').read_text().splitlines()]
    frames=[r for r in wire if r.get('event')=='frame' and (r.get('sysid'),r.get('compid'))==(1,1)]
    unknown=[link.verify_unknown_frame(r) for r in frames if r.get('crc_status')!='VERIFIED']
    raw=(folder/'received-prefix.bin').read_bytes();digest=hashlib.sha256(raw).hexdigest()
    view,excluded=complete_record_view(raw);_,log=validate_ulog(view)
    rows={d.name:[{k:v[i].item() for k,v in d.data.items()} for i in range(len(d.data['timestamp']))]
        for d in log.data_list}
    normal=[r for r in frames if r['type']=='LOGGING_DATA']
    tx=[decoder_module.Decoder().feed(bytes.fromhex(r['wire_hex']),r['receipt_mono_ns'])[0]
        for r in wire if r.get('event')=='tx_write']
    counters=link.correlate(frames)
    metadata=link.packet_metadata([r for r in frames if r['type']=='LOGGING_DATA_ACKED'])
    result=dict(scope='ONE_FAILED_UPSTREAM_GYRO_OBSERVATION_NO_60S_ACCEPTANCE',
        error=summary['error'],audit=audit,raw_prefix_sha256=digest,original_bytes=len(raw),
        in_memory_complete_record_bytes=len(view),excluded_partial_bytes=excluded,
        no_repaired_log_written=True,source_records_retained=rows,
        normal_frames_retained=len(normal),normal_logging_sequences=[r['fields']['sequence'] for r in normal],
        normal_first_to_last_RECEIVED_s=(normal[-1]['receipt_mono_ns']-normal[0]['receipt_mono_ns'])/1e9 if len(normal)>1 else None,
        accepted_normal_window_s=(summary['last_logging_mono_ns']-summary['normal_data_start_mono_ns'])/1e9,
        all_retained_frames_crc_verified=True,unknown_frames_verified=unknown,
        wire=wire_gaps(wire),link_counters=counters,packet_local_stop_metadata=metadata,
        tx_write_types=dict(Counter(r['type'] for r in tx)),
        tx_control_commands=[r['fields']['command'] for r in tx if r['type']=='COMMAND_LONG'],
        cpu=cpu_summary([json.loads(x) for x in (HERE/'download/metrics.jsonl').read_text().splitlines()]),
        uart_counters=[json.loads(x) for x in (HERE/'download/uart-counters.jsonl').read_text().splitlines()],
        measured_imu_hz=None,gyro_hole_correlation='NOT_OBSERVED_INSUFFICIENT_RETAINED_IMU',
        logger_gap_attribution='AGGREGATE_TWO_FULL_RATE_TOPICS',
        source_complete='UNKNOWN',tail_complete='UNKNOWN',clock_synchronization='UNKNOWN',
        transport_qualified=False,openvins_admissible=False,stage_c='CLOSED')
    assert digest==summary['received_prefix_sha256']==hashlib.sha256((folder/'received-prefix.bin').read_bytes()).hexdigest()
    with (HERE/'failure-analysis.json').open('x') as f:json.dump(diagnostic_json(result),f,indent=2,allow_nan=False)
    print(json.dumps(diagnostic_json(dict(error=result['error'],original_bytes=len(raw),excluded=excluded,
        topic_counts={n:len(r) for n,r in rows.items()},wire=result['wire'],link_counters=counters,
        cpu=result['cpu'],uart_counters=result['uart_counters'])),indent=2,allow_nan=False))

if __name__=='__main__':main()
