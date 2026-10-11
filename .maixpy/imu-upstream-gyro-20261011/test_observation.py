"""SYNTHETIC fixtures; no physical/synchronization or VIO qualification."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'imu-design-20261010/single-uart/controller'))
import uart_session as u
try:
    from observation import source_windows,bandwidth,validate_observation
except ImportError:
    source_windows=bandwidth=validate_observation=None

def preflight():
    return dict(firmware_hash=u.EXPECTED_HASH,ekf2_ev_ctrl=0,disarmed=True,
        propellers_removed=True,uart='/dev/ttyS2',baud=921600,mavlink_datarate=80000,
        gyro_device_id=6684690,accel_device_id=6946834,vehicle_imu_instance=0,
        logger_backend='mavlink',configuration_backup_verified=True,
        logger_poll=None,logger_rate_hz=2500,logger_reader='fixed_2500hz',
        observation='UPSTREAM_GYRO0',heartbeat_negotiation_approved=True,
        prepared_m3c_monotonic_ns=1_000_000_000)

def gyro(times=range(100000,118001,1500)):
    return [dict(timestamp=t+50,timestamp_sample=t,device_id=6684690,
        x=0.,y=0.,z=0.,samples=3,error_count=1) for t in times]

def imu(times=(100000,104500,115000),dts=(4500,4500,6000)):
    return [dict(timestamp=t+200,timestamp_sample=t,delta_angle_dt=dt,
        gyro_device_id=6684690,accel_device_id=6946834,
        gyro_calibration_count=1,accel_calibration_count=1)
        for t,dt in zip(times,dts)]

class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(source_windows,'new source-window analysis absent')

    def test_intact_upstream_does_not_claim_logger_only_or_vio_pass(self):
        out=source_windows(imu(),gyro())
        hole=out['holes'][0]
        self.assertEqual(hole['uncovered_us'],4500)
        self.assertEqual(hole['source_samples_inside'],3)
        self.assertEqual(hole['upstream_observation'],'LOCALLY_INTACT_CADENCE')
        self.assertEqual(out['exact_trigger'],'UNKNOWN')
        self.assertEqual(out['logger_gap_attribution'],'AGGREGATE_TWO_FULL_RATE_TOPICS')
        self.assertFalse(out['openvins_admissible'])

    def test_upstream_gap_and_unbracketed_window_remain_unknown(self):
        g=gyro();g=[r for r in g if r['timestamp_sample']!=107500]
        self.assertEqual(source_windows(imu(),g)['holes'][0]['upstream_observation'],'UPSTREAM_CADENCE_GAP_OBSERVED')
        self.assertEqual(source_windows(imu(),gyro(range(106000,118001,1500)))['holes'][0]['upstream_observation'],'UNKNOWN_UNBRACKETED')

    def test_fully_covered_long_integral_not_hole(self):
        out=source_windows(imu(dts=(4500,4500,10500)),gyro())
        self.assertEqual(out['holes'],[])
        self.assertEqual(out['source_complete'],'UNKNOWN')
        self.assertEqual(out['accel_coverage'],'UNKNOWN_NO_SEPARATE_ENDPOINT')

    def test_identity_order_nonfinite_and_calibration_change_refused(self):
        for changed in ({'device_id':3604506},{'timestamp_sample':100000},{'x':math.nan},{'samples':0}):
            g=gyro();g[-1].update(changed)
            with self.assertRaises(ValueError):source_windows(imu(),g)
        im=imu();im[-1]['gyro_calibration_count']=2
        with self.assertRaises(ValueError):source_windows(im,gyro())

    def test_valid_explicit_profile_and_base_guard_composition(self):
        validate_observation(preflight(),2_000_000_000)
        for changed in ({'mavlink_datarate':46080},{'observation':'RAW_ADC'},
            {'disarmed':False},{'ekf2_ev_ctrl':1},{'gyro_device_id':3604506},
            {'logger_poll':'vehicle_imu'},{'baud':115200},{'configuration_backup_verified':False}):
            with self.assertRaises(ValueError):validate_observation(dict(preflight(),**changed),2_000_000_000)
        with self.assertRaises(ValueError):validate_observation(preflight(),70_000_000_000)

    def test_realistic_bandwidth_not_received_rate(self):
        out=bandwidth()
        self.assertEqual(out['sensor_gyro_ulog_bytes'],49)
        self.assertEqual(out['vehicle_imu_ulog_bytes'],65)
        self.assertGreater(out['estimated_wire_Bps'],50000)
        self.assertLess(out['estimated_wire_Bps'],56000)
        self.assertEqual(out['evidence'],'ENGINEERING_ESTIMATE_NOT_MEASUREMENT')

if __name__=='__main__':unittest.main()
