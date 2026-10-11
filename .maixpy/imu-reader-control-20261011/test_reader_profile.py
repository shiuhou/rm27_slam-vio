"""Reader-profile tests; no physical UART, bench access is a denied boundary."""
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                     'imu-design-20261010/single-uart/controller'))
import uart_session as u

try:
    import coordinator as c
except ImportError:
    c = None


def legacy():
    return dict(firmware_hash=u.EXPECTED_HASH, ekf2_ev_ctrl=0, disarmed=True,
        propellers_removed=True, uart='/dev/ttyS2', baud=921600,
        mavlink_datarate=46080, gyro_device_id=6684690, accel_device_id=6946834,
        vehicle_imu_instance=0, logger_backend='mavlink', logger_poll='vehicle_imu',
        configuration_backup_verified=True, heartbeat_negotiation_approved=True,
        prepared_m3c_monotonic_ns=1_000_000_000)


def fixed():
    return dict(legacy(), logger_poll=None, logger_rate_hz=2500,
                logger_reader='fixed_2500hz')


class ReaderProfileTests(unittest.TestCase):
    def test_legacy_default_still_valid(self):
        u.validate_preflight(legacy(), 2_000_000_000)

    def test_fixed_requires_explicit_profile(self):
        with self.assertRaises(ValueError):
            u.validate_preflight(fixed(), 2_000_000_000)
        u.validate_preflight(fixed(), 2_000_000_000, logger_reader='fixed_2500hz')

    def test_ambiguous_and_changed_settings_rejected(self):
        for changes in ({'logger_poll':'vehicle_imu'}, {'logger_rate_hz':True},
            {'logger_rate_hz':2499}, {'logger_reader':'poll_vehicle_imu'},
            {'disarmed':False}, {'ekf2_ev_ctrl':1}, {'baud':115200},
            {'gyro_device_id':3604506}, {'configuration_backup_verified':False}):
            with self.assertRaises(ValueError):
                u.validate_preflight(dict(fixed(), **changes), 2_000_000_000,
                                     logger_reader='fixed_2500hz')
        with self.assertRaises(ValueError):
            u.validate_preflight(dict(legacy(), logger_rate_hz=2500), 2_000_000_000)

    def test_unknown_profile_and_stale_attestation_rejected(self):
        with self.assertRaises(ValueError):
            u.validate_preflight(fixed(), 2_000_000_000, logger_reader='arbitrary')
        with self.assertRaises(ValueError):
            u.validate_preflight(fixed(), 70_000_000_000, logger_reader='fixed_2500hz')


class CommandScopeTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(c, 'fixed-reader coordinator missing')

    def check(self, line):
        c.check_command(line,
            'mavlink start -d /dev/ttyS2 -b p:SER_GPS1_BAUD -m p:MAV_1_MODE -r p:MAV_1_RATE -s -x',
            'logger start -b 64 -t -m all',
            {'HEARTBEAT':1., 'TIMESYNC':10., 'HIGHRES_IMU':50.},
            {'HIGHRES_IMU':0.})

    def test_exact_candidate_restore_and_treatment_allowed(self):
        for line in (c.LOGGER, 'logger start -b 64 -t -m all',
                     'mavlink stream -d /dev/ttyS2 -s HIGHRES_IMU -r 0'):
            self.check(line)

    def test_other_factors_and_unsafe_commands_rejected(self):
        for line in (c.c.LOGGER, 'logger start -b 64 -t -m mavlink -r 5000',
            c.LOGGER+' -p vehicle_imu', 'param set EKF2_EV_CTRL 1', 'param save',
            'commander arm', 'motor_test test', 'offboard start',
            'mavlink stop -d /dev/ttyS3',
            'mavlink stream -d /dev/ttyS2 -s HEARTBEAT -r 0',
            'mavlink stream -d /dev/ttyS2 -s TIMESYNC -r 0'):
            with self.assertRaises(ValueError, msg=line):
                self.check(line)


class LaunchGateTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(c, 'fixed-reader coordinator missing')

    def test_missing_flag_never_constructs_link(self):
        denied = types.ModuleType('bench_io')
        denied.Link = Mock(side_effect=AssertionError('device opened'))
        with patch.dict(sys.modules, {'bench_io': denied}):
            with patch.object(sys,'argv',['coordinator.py']):
                with self.assertRaises(SystemExit) as error:
                    c.main()
            self.assertEqual(error.exception.code,2)
            denied.Link.assert_not_called()

    def test_missing_deployment_never_constructs_link(self):
        import tempfile
        denied = types.ModuleType('bench_io')
        denied.Link = Mock(side_effect=AssertionError('device opened'))
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(c,'HERE',Path(folder)), \
                 patch.object(sys,'argv',['coordinator.py','--trial-approved']), \
                 patch.dict(sys.modules, {'bench_io': denied}):
                with self.assertRaises(FileNotFoundError):
                    c.main()
                denied.Link.assert_not_called()
