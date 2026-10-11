"""Offline actual-trial diagnostics; no device access, byte repair or admission."""
import json
import math
from pathlib import Path

def diagnostic_json(value):
    if isinstance(value,float) and not math.isfinite(value):
        return dict(status='NONFINITE_DIAGNOSTIC',value=str(value))
    if isinstance(value,dict):return {k:diagnostic_json(v) for k,v in value.items()}
    if isinstance(value,list):return [diagnostic_json(v) for v in value]
    return value

def cpu_summary(rows):
    samples=[r for r in rows if r.get('event')=='receiver_cpu' and 'utime_ticks' in r]
    if len(samples)<2:return dict(status='UNKNOWN_INSUFFICIENT_SAMPLES')
    first,last=samples[0],samples[-1]
    intervals=[]
    for before,after in zip(samples,samples[1:]):
        if (any(after[k]!=first[k] for k in ('pid','starttime_ticks','clk_tck'))
                or first['clk_tck']<=0 or after['receipt_mono_ns']<=before['receipt_mono_ns']
                or after['utime_ticks']<before['utime_ticks'] or after['stime_ticks']<before['stime_ticks']):
            raise ValueError('CPU process/counter/clock epoch or order changed')
        intervals.append((after['receipt_mono_ns']-before['receipt_mono_ns'])/1e9)
    span=(last['receipt_mono_ns']-first['receipt_mono_ns'])/1e9
    cpu=(last['utime_ticks']+last['stime_ticks']-first['utime_ticks']-first['stime_ticks'])/first['clk_tck']
    gates=[r['receipt_mono_ns'] for r in rows if r.get('event')=='receiver_gate_released']
    return dict(status='MEASURED_OBSERVED_SAMPLING_WINDOW',samples=len(samples),sample_span_s=span,
        first_sample_mono_ns=first['receipt_mono_ns'],last_sample_mono_ns=last['receipt_mono_ns'],
        first_sample_before_gate=first['receipt_mono_ns']<gates[0] if len(gates)==1 else None,
        cpu_seconds=cpu,mean_percent_of_one_core=100*cpu/span,
        max_sampling_interval_s=max(intervals),peak_observed_rss_bytes=max(r['rss_bytes'] for r in samples),
        caveat='Sample-window CPU ticks, not exact process lifetime, per-core peak or proof against scheduling stalls')

def main():
    import hashlib
    import sys
    root=Path(__file__).resolve().parent
    sys.path.insert(0,str(root.parent/'imu-uart-negotiated-trial-20261011'))
    from analyze_failure import complete_record_view,wire_gaps
    sys.path.insert(0,str(root.parent/'imu-gap-diagnosis-20261011'))
    import diagnose as diagnosis
    sys.path.insert(0,str(root.parent/'imu-design-20261010/single-uart/controller'))
    from capture_report import audit_capture,_imu_summary,distribution
    from ulog_mavlink import validate_ulog
    capture=root/'download/physical-trial-01'
    audit=audit_capture(capture,epoch='D6F12AD1_REDUCED_TELEMETRY_REAL_UART_TRIAL')
    rows=[json.loads(x) for x in (capture/'wire.jsonl').read_text().splitlines()]
    frames=[r for r in rows if r.get('event')=='frame' and (r.get('sysid'),r.get('compid'))==(1,1)]
    unknown=[r for r in frames if r.get('crc_status')!='VERIFIED']
    checked=[diagnosis.verify_unknown_frame(r) for r in unknown]
    raw=(capture/'received-prefix.bin').read_bytes();digest=hashlib.sha256(raw).hexdigest()
    view,excluded=complete_record_view(raw)
    _,log=validate_ulog(view)
    imu=_imu_summary(view,instance=0,gyro_device=6684690,accel_device=6946834,
        epoch='D6F12AD1_REDUCED_REAL_INTEGRAL_DIAGNOSTICS_NOT_OPENVINS_INPUT')
    metrics=[json.loads(x) for x in (root/'download/metrics.jsonl').read_text().splitlines()]
    counters=diagnosis.correlate(frames)
    summary=audit['session']
    normal=(summary['last_logging_mono_ns']-summary['normal_data_start_mono_ns'])/1e9
    statuses={name:[{key:values[i].item() for key,values in d.data.items()}
        for d in log.data_list if d.name==name for i in range(len(d.data['timestamp']))]
        for name in ('logger_status','vehicle_imu_status','sensor_selection','cpuload','actuator_armed','vehicle_status')}
    result=dict(scope='ONE_ACTUAL_REDUCED_TELEMETRY_PHYSICAL_TRIAL_OFFLINE_ANALYSIS',
        raw_prefix_sha256=digest,original_bytes=len(raw),in_memory_complete_records_bytes=len(view),
        excluded_partial_bytes=excluded,raw_decode_parity_verified=audit['raw_decode_parity'],
        all_retained_px4_frames_crc_verified=True,px4_frames=len(frames),unknown_frames_verified=checked,
        session_error=summary['error'],finite_framing_verified=summary['finite_framing_verified'],
        normal_data_first_to_last_accepted_receipt_s=normal,wire=wire_gaps(rows),imu=imu,
        topic_records=[dict(name=d.name,instance=d.multi_id,records=len(d.data['timestamp'])) for d in log.data_list],
        retained_status_records=statuses,retained_changed_parameters=len(log.changed_parameters),
        retained_dropouts=[dict(timestamp=d.timestamp,duration=d.duration) for d in log.dropouts],
        cpu=cpu_summary(metrics),uart_counters=[json.loads(x) for x in (root/'download/uart-counters.jsonl').read_text().splitlines()],
        link_counters=counters,packet_local_stop_metadata=diagnosis.packet_metadata([
            r for r in frames if r.get('type')=='LOGGING_DATA_ACKED']),
        data_caveat='Original bytes untouched; partial views in memory only; integrals not instantaneous samples',
        source_complete='UNKNOWN',tail_complete='UNKNOWN',clock_synchronization='UNKNOWN',
        transport_qualified=False,openvins_admissible=False,stage_c='CLOSED')
    assert hashlib.sha256((capture/'received-prefix.bin').read_bytes()).hexdigest()==digest
    # First attempt's partial analysis.json is retained as failed helper output.
    # NaN health temperature is explicitly encoded, not hidden/replaced with 0.
    assert audit==json.loads((root/'capture-audit.json').read_text())
    encoded=json.dumps(diagnostic_json(result),indent=2,allow_nan=False)
    with (root/'analysis-02.json').open('x',encoding='utf-8') as output:output.write(encoded)
    print(json.dumps(dict(error=summary['error'],normal_data_s=normal,imu=imu,cpu=result['cpu'],
        wire_gaps=len(result['wire']['mavlink_sequence_discontinuities']),
        logging_gaps=len(result['wire']['logging_discontinuities']),
        counter_intervals=len(counters['intervals']),transport_qualified=False),indent=2,allow_nan=False))

if __name__=='__main__':main()
