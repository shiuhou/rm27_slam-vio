"""Guard tests deny physical boundaries; no device access."""
import sys
import types
import unittest
from unittest.mock import Mock,patch
try:
    import coordinator as c
except ImportError:
    c=None

class ScopeTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(c,'new scoped coordinator absent')
    def check(self,line):
        c.check_command(line,'mavlink start -d /dev/ttyS2 -b p:SER_GPS1_BAUD -m p:MAV_1_MODE -r p:MAV_1_RATE -s -x',
            'logger start -b 64 -t -m all',{'HEARTBEAT':1.,'HIGHRES_IMU':50.},{'HIGHRES_IMU':0.})
    def test_exact_start_and_source_read_only_allowed(self):
        for line in (c.START,c.LOGGER,'listener sensor_gyro -i 0 -n 1','param show IMU_INTEG_RATE',
                     'uorb top -1 sensor_gyro vehicle_imu','mavlink stream -d /dev/ttyS2 -s HIGHRES_IMU -r 0'):
            self.check(line)
    def test_other_budget_topics_factors_and_unsafe_commands_refused(self):
        for line in (c.c.START,c.c.LOGGER,c.LOGGER+' -p vehicle_imu',
            c.START.replace('80000','92160'),'param set IMU_INTEG_RATE 250',
            'commander arm','reboot','logger on','mavlink stop -d /dev/ttyS3',
            'mavlink stream -d /dev/ttyS2 -s HEARTBEAT -r 0'):
            with self.assertRaises(ValueError,msg=line):self.check(line)
    def test_missing_flag_never_opens_device(self):
        denied=types.ModuleType('bench_io');denied.Link=Mock(side_effect=AssertionError('device access'))
        with patch.dict(sys.modules,{'bench_io':denied}),patch.object(sys,'argv',['coordinator.py']):
            with self.assertRaises(SystemExit) as error:c.main()
        self.assertEqual(error.exception.code,2);denied.Link.assert_not_called()

if __name__=='__main__':unittest.main()
