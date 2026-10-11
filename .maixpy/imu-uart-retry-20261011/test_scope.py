import unittest
try:
    import coordinator as c
except ModuleNotFoundError:
    c = None

UART = 'mavlink start -d /dev/ttyS2 -b p:SER_GPS1_BAUD -m p:MAV_1_MODE -r p:MAV_1_RATE -s -x'
LOGGER = 'logger start -b 64 -t -m all'

class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(c, 'New scoped coordinator is not implemented yet')

    def test_only_exact_backup_restore(self):
        for line in (UART, LOGGER, c.START, 'logger stop', c.LOGGER):
            c.check_command(line, UART, LOGGER, {'HEARTBEAT':1.0})
        for line in ('param set EKF2_EV_CTRL 1','mavlink stop-all','commander arm',
                     'mavlink stop -d /dev/ttyS3',UART+' -f',LOGGER+' -r 2500'):
            with self.assertRaises(ValueError):
                c.check_command(line, UART, LOGGER, {'HEARTBEAT':1.0})

    def test_only_backed_stream_rate(self):
        c.check_command('mavlink stream -d /dev/ttyS2 -s HEARTBEAT -r 1', UART, LOGGER, {'HEARTBEAT':1.0})
        for line in ('mavlink stream -d /dev/ttyS2 -s HEARTBEAT -r 2',
                     'mavlink stream -d /dev/ttyS3 -s HEARTBEAT -r 1',
                     'mavlink stream -d /dev/ttyS2 -s ODOMETRY -r 10'):
            with self.assertRaises(ValueError):
                c.check_command(line, UART, LOGGER, {'HEARTBEAT':1.0})

    def test_port_block_is_unique_and_target_only(self):
        status='instance #0:\n /dev/ttyS0 @57600\ninstance #1:\n /dev/ttyS2 @115200\ninstance #2:\n /dev/ttyS3 @115200'
        self.assertNotIn('ttyS3', c.port_block(status, '/dev/ttyS2', 115200))
        for text in (status.replace('115200','921600'), status+status):
            with self.assertRaises(ValueError): c.port_block(text, '/dev/ttyS2',115200)

    def test_sdlog_parsed_not_parameter_metadata(self):
        text='x SDLOG_BACKEND [1,2] : 3\nx SDLOG_UUID [2,3] : 1\n961/1780 parameters used.'
        self.assertEqual(c.sdlog_values(text), {'SDLOG_BACKEND':3,'SDLOG_UUID':1})

    def test_receiver_failure_is_not_outer_success(self):
        self.assertFalse(c.receiver_ok(1, {'error':None, 'termios_restored':True}))
        self.assertFalse(c.receiver_ok(0, {'error':'crc','termios_restored':True}))
        self.assertFalse(c.receiver_ok(0, {'error':None,'termios_restored':False}))
        self.assertTrue(c.receiver_ok(0, {'error':None,'termios_restored':True}))

if __name__ == '__main__': unittest.main()
