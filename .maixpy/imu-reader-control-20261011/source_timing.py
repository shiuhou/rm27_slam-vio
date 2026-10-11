"""Apply already-tested source timing model to current saved evidence only."""
import json
from pathlib import Path
import statistics
from ulog_mavlink import inspect_imu,validate_ulog
from compare import d

here=Path(__file__).resolve().parent
raw=(here/'download/physical-trial-01/framing-valid.ulg').read_bytes()
_,log=validate_ulog(raw)
records=[x['original'] for x in inspect_imu(raw,instance=0,gyro_device=6684690,
    accel_device=6946834,epoch='SOURCE_MODEL_DIAGNOSTICS_ONLY')['diagnostic_means']]
status=log.get_dataset('vehicle_imu_status',0).data
periods={kind:statistics.median(1e6/float(x) for x in status[kind+'_rate_hz']) for kind in ('gyro','accel')}
rate=log.initial_parameters['IMU_INTEG_RATE']
model=d.configuration(rate,periods['gyro'],periods['accel'])
timing=d.cadence(records)
classified={kind:d.multiples([r[field] for r in records],periods[kind],model[kind+'_samples'])
    for kind,field in (('gyro','delta_angle_dt'),('accel','delta_velocity_dt'))}
values={key:sorted(set(r[key] for r in records)) for key in ('gyro_device_id','accel_device_id',
    'gyro_calibration_count','accel_calibration_count','delta_angle_clipping','delta_velocity_clipping')}
result=dict(scope='CURRENT_REAL_ROWS_TESTED_CONFIGURATION_MODEL_NOT_RUN_TRACE',
    configured_integration_rate=rate,periods_us=periods,configuration=model,classified_integrals=classified,
    source_identity_calibration_clips=values,status_error_counts={k:sorted(set(int(x) for x in status[k]))
        for k in ('accel_error_count','gyro_error_count')},
    retained_interval_span_us=timing['span_us'],covered_gyro_us=timing['covered_gyro_us'],
    uncovered_gyro_us=timing['uncovered_gyro_us'],gyro_overlap_events=timing['gyro_overlap_events'],
    mean_endpoint_us=timing['span_us']/(len(records)-1),
    accel_window_baseline_us=4*periods['accel'],
    gyro_span_minus_accel_dt_sum_us=timing['span_us']-sum(r['delta_velocity_dt'] for r in records[1:]),
    exact_missing_generations='UNKNOWN',actual_logger_execution_trace='UNAVAILABLE',
    accel_coverage='UNKNOWN_NO_SEPARATE_ENDPOINT',openvins_admissible=False,stage_c='CLOSED')
assert timing['covered_gyro_us']+timing['uncovered_gyro_us']==timing['span_us'] and timing['gyro_overlap_events']==0
with (here/'source-timing.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps(result,indent=2,allow_nan=False))
