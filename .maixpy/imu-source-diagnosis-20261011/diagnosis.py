"""Read-only saved ULog timing diagnosis. No hardware, repair or VIO exporter."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('source_timing_prior',HERE.parent/'imu-design-20261010/offline.py')
prior=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prior)
RAW_SHA='658287cb149e1afbd56c9df799807729cd0930e4943190a580fb08b42eebca06'
FIRMWARE='d6f12ad1c4f70ad3230afd7d86e971421e02fef4'


def cadence(rows):
    audit=prior.audit(rows,units=prior.UNITS,epoch='OFFLINE_SOURCE_TIMING_ONLY')
    prior.need(len(rows)>1,'at least two records required')
    prior.need(not set(audit['issues']) & {'ordering','publication_ordering','identity','calibration'},
        'invalid chronology or epoch change; segment before computing cadence')
    intervals=[b['timestamp_sample']-a['timestamp_sample'] for a,b in zip(rows,rows[1:])]
    span=rows[-1]['timestamp_sample']-rows[0]['timestamp_sample']
    median=statistics.median(intervals)
    residual=audit['gyro_coverage_residual_us']
    holes=[dict(after_index=i+1,residual_us=r,before=rows[i],after=rows[i+1])
        for i,r in enumerate(residual) if r>2]
    bins=Counter((r['timestamp_sample']-rows[0]['timestamp_sample'])//1000000 for r in rows)
    hz=(len(rows)-1)*1e6/span
    return dict(count=len(rows),span_us=span,retained_hz=hz,
        original_minimum_hz=200,original_rate_gate_pass=hz>=200,
        gyro_holes=holes,uncovered_gyro_us=sum(x['residual_us'] for x in holes),
        covered_gyro_us=sum(r['delta_angle_dt'] for r in rows[1:]),
        gyro_overlap_events=sum(r < -2 for r in residual),
        max_endpoint_interval_us=max(intervals),median_endpoint_interval_us=median,
        large_endpoint_intervals=sum(x>1.5*median for x in intervals),
        accel_coverage=audit['accel_coverage'],
        complete_one_second_bins=[dict(second=i,count=bins[i]) for i in range(span//1000000)],
        publication_minus_sample_us=dict(min=min(r['timestamp']-r['timestamp_sample'] for r in rows),
            median=statistics.median(r['timestamp']-r['timestamp_sample'] for r in rows),
            max=max(r['timestamp']-r['timestamp_sample'] for r in rows)),
        openvins_admissible=False,source_complete='UNKNOWN',clock_status='UNKNOWN',tail_complete='UNKNOWN')


def configuration(rate, gyro_period, accel_period):
    prior.need(all(type(x) in (int,float) and math.isfinite(x) and x>0
        for x in (rate,gyro_period,accel_period)),'finite positive rate/period required')
    prior.need(50<=rate<=1000,'source integration rate outside audited range')
    # Positive roundf, not Python bankers rounding. This is a timing model,
    # not a bit-exact C++/float32 or workqueue execution simulator.
    rnd=lambda x:math.floor(x+.5)
    integration_us=int(1e6/rate)
    gyro_samples=max(1,rnd(integration_us/gyro_period))
    if gyro_samples>8:gyro_samples=max(1,rnd(integration_us/gyro_period/2)*2)
    accel_samples=max(1,rnd(rnd(gyro_samples*gyro_period)/accel_period))
    callback_samples=gyro_samples
    for n in range(8,0,-1):
        if callback_samples>8:callback_samples//=2
        if callback_samples%n==0:break
    return dict(semantic='TIMING_CONFIGURATION_MODEL_NOT_PUBLICATION_TRACE',
        configured_hz=rate,requested_interval_us=integration_us,
        gyro_samples=gyro_samples,accel_samples=accel_samples,gyro_callback_updates=n,
        gyro_reset_interval_us=rnd((gyro_samples-.5)*gyro_period),
        accel_reset_interval_us=rnd((accel_samples-.5)*accel_period),
        backup_schedule_us=max(1000,min(20000,int(min(8*gyro_period,8*accel_period))//2)),
        gyro_nominal_window_us=gyro_samples*gyro_period,
        accel_nominal_window_us=accel_samples*accel_period,
        accel_baseline_hz=1e6/(accel_samples*accel_period))


def multiples(durations, period, baseline):
    prior.need(math.isfinite(period) and period>0 and type(baseline) is int and baseline>0,
        'positive period and integer baseline required')
    prior.need(bool(durations) and all(type(x) is int and x>0 for x in durations),'positive integer dt required')
    inferred=[math.floor(x/period+.5) for x in durations]
    counts=Counter(inferred)
    residual=[dt-n*period for dt,n in zip(durations,inferred)]
    return dict(semantic='INFERRED_SI_PUBLICATION_PERIOD_MULTIPLES_NOT_HARDWARE_COUNTS',
        period_us=period,baseline_periods=baseline,
        counts={str(n):counts[n] for n in sorted(counts)},
        duration_sum_us=sum(durations),mean_duration_us=statistics.mean(durations),
        extended_integrals=sum(n>baseline for n in inferred),
        extra_periods_over_baseline=sum(n-baseline for n in inferred),
        residual_min_us=min(residual),residual_max_us=max(residual),
        caveat='Nearest status-derived mean period multiples; original per-sensor endpoints/samples are absent.')


def correlate(holes, statuses, full_rate_topics):
    prior.need(bool(statuses),'logger counter evidence absent')
    changes=[]
    for a,b in zip(statuses,statuses[1:]):
        prior.need(b['timestamp']>a['timestamp'],'counter timestamp order invalid')
        prior.need(b['message_gaps']>=a['message_gaps'],'counter reset/wrap; segment first')
        if b['message_gaps']>a['message_gaps']:
            changes.append(dict(before=a,after=b,event_increment=b['message_gaps']-a['message_gaps']))
    out=[]
    for hole in holes:
        matching=[x for x in changes if x['before']['timestamp']<hole['before']['timestamp']
            <hole['after']['timestamp']<x['after']['timestamp']]
        label='UNKNOWN'
        if len(matching)==1:
            label='LOGGER_VEHICLE_IMU_SUBSCRIPTION_SKIP' if full_rate_topics==['vehicle_imu'] else 'AMBIGUOUS'
        out.append(dict(after_index=hole['after_index'],residual_us=hole['residual_us'],
            brackets=matching,attribution=label,exact_missing_generations='UNKNOWN',
            precise_scheduling_trigger='UNKNOWN'))
    return dict(counter_first=statuses[0]['message_gaps'],counter_last=statuses[-1]['message_gaps'],
        counter_increment_events=sum(x['event_increment'] for x in changes),
        changes=changes,holes=out,
        caveat='Counter increments discontinuity EVENTS, not missing-generation count. Brackets are not event timestamps.')


def analyze(path):
    # Existing audited schema/framing/identity and integral-semantics code.
    sys.path.insert(0,str(HERE.parent/'imu-design-20261010/single-uart/controller'))
    from capture_report import inspect_imu
    from ulog_mavlink import validate_ulog
    raw=Path(path).read_bytes()
    prior.need(hashlib.sha256(raw).hexdigest()==RAW_SHA,'not the pinned complete reduced-telemetry evidence')
    inspected=inspect_imu(raw,instance=0,gyro_device=6684690,accel_device=6946834,epoch='D6F12AD1_OFFLINE_REANALYSIS')
    _,log=validate_ulog(raw)
    rows=[r['original'] for r in inspected['diagnostic_means']]
    status=log.get_dataset('vehicle_imu_status',0).data
    prior.need(set(map(int,status['gyro_device_id']))=={6684690} and
        set(map(int,status['accel_device_id']))=={6946834},'status sensor identity changed')
    rates={k:dict(min=float(min(status[k])),median=float(statistics.median(status[k])),max=float(max(status[k])))
        for k in ('gyro_rate_hz','gyro_raw_rate_hz','accel_rate_hz','accel_raw_rate_hz')}
    cfg=configuration(int(log.initial_parameters['IMU_INTEG_RATE']),
        1e6/rates['gyro_rate_hz']['median'],1e6/rates['accel_rate_hz']['median'])
    logger=log.get_dataset('logger_status',0).data
    statuses=[{k:int(logger[k][i]) for k in ('timestamp','message_gaps','type','backend','num_messages')}
        for i in range(len(logger['timestamp']))]
    prior.need(all((r['type'],r['backend'],r['num_messages'])==(0,2,8) for r in statuses),'logger config evidence differs')
    topics=(HERE.parent/'imu-uart-reduced-trial-20261011/topics-readback.txt').read_text(encoding='utf-8').splitlines()
    full=[line.split()[0] for line in topics if line.split()[1]=='0']
    timing=cadence(rows)
    gm=multiples([r['delta_angle_dt'] for r in rows],1e6/rates['gyro_rate_hz']['median'],cfg['gyro_samples'])
    am=multiples([r['delta_velocity_dt'] for r in rows],1e6/rates['accel_rate_hz']['median'],cfg['accel_samples'])
    # Accounting decomposition uses all but first record, like the source span.
    accel_sum=sum(r['delta_velocity_dt'] for r in rows[1:])
    n=len(rows)-1
    base=cfg['accel_nominal_window_us']
    return dict(provenance='REAL_SAVED_REDUCED_TELEMETRY_LOG_OFFLINE_REANALYSIS',
        raw_sha256=RAW_SHA,raw_bytes=len(raw),firmware=FIRMWARE,
        parameters={k:log.initial_parameters.get(k) for k in ('IMU_INTEG_RATE','SENS_IMU_AUTOCAL','SENS_IMU_MODE')},
        changed_parameters=len(log.changed_parameters),cadence=timing,status_rates=rates,
        configuration_model=cfg,gyro_period_model=gm,accel_period_model=am,
        rate_decomposition=dict(retained_intervals=n,span_us=timing['span_us'],
            accel_integral_sum_us=accel_sum,nominal_accel_windows_us=n*base,
            extended_accel_duration_over_model_us=accel_sum-n*base,
            gyro_span_minus_accel_duration_us=timing['span_us']-accel_sum,
            sensitivity_one_extra_record_hz=(n+1)*1e6/timing['span_us'],
            caveat='Arithmetic sensitivity/model, NOT inserted samples, exact publisher count, or accel endpoint coverage.'),
        logger=correlate(timing['gyro_holes'],statuses,full),
        retained_gap_neighborhood=[dict(index=i,**rows[i]) for h in timing['gyro_holes']
            for i in range(max(0,h['after_index']-5),min(len(rows),h['after_index']+6))],
        dropout_events=len(log.dropouts),openvins_admissible=False,stage_c='CLOSED',
        unobserved=['missing integral payload/generation magnitude','per-sensor SI publications',
            'VehicleIMU Run/callback/backup execution trace','logger read/poll/lock scheduling trace',
            'independent accel endpoint','source tail completeness','clock mapping'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('output exists; refuse overwrite')
    result=analyze(HERE.parent/'imu-uart-reduced-trial-20261011/download/physical-trial-01/framing-valid.ulg')
    with args.output.open('x',encoding='utf-8') as output:json.dump(result,output,indent=2,allow_nan=False)
    print(json.dumps(dict(count=result['cadence']['count'],hz=result['cadence']['retained_hz'],
        gyro_holes_us=result['cadence']['uncovered_gyro_us'],
        logger_counter_events=result['logger']['counter_increment_events'],
        extended_accel_integrals=result['accel_period_model']['extended_integrals'],
        original_rate_gate_pass=result['cadence']['original_rate_gate_pass'],openvins_admissible=False)))
