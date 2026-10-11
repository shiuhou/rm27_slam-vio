"""Pure retained-integral/counter comparison; never grants VIO admission."""
import importlib.util
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'imu-source-diagnosis-20261011/diagnosis.py'
spec=importlib.util.spec_from_file_location('reader_control_saved_diagnosis',path)
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def comparison(before_rows, after_rows, after_statuses):
    if len(after_statuses)<2 or any((s['type'],s['backend'],s['num_messages'])
                                  != (0,2,8) for s in after_statuses):
        raise ValueError('at least two full/MAVLink/eight-topic status records required')
    before = d.cadence(before_rows)
    after = d.cadence(after_rows)
    logger = d.correlate(after['gyro_holes'], after_statuses, ['vehicle_imu'])
    return dict(baseline=before, candidate=after, candidate_logger=logger,
        logger_observation_span_us=after_statuses[-1]['timestamp']-after_statuses[0]['timestamp'],
        logger_counter_window=[after_statuses[0]['timestamp'],after_statuses[-1]['timestamp']],
        observed_gyro_continuity=(not after['gyro_holes'] and
                                  after['gyro_overlap_events'] == 0),
        observed_subscription_continuity=(logger['counter_increment_events'] == 0),
        original_rate_gate_pass=after['original_rate_gate_pass'],
        accel_coverage=after['accel_coverage'], source_complete='UNKNOWN',
        clock_status='UNKNOWN', tail_complete='UNKNOWN',
        openvins_admissible=False, stage_c='CLOSED')
