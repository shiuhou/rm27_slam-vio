"""New scope/sampler tests only; synthetic/PTY, never the physical UART."""
import importlib.util
from pathlib import Path
import struct
import unittest

path = Path(__file__).resolve().parent/'trial_tools.py'
if path.exists():
    spec = importlib.util.spec_from_file_location('trial_tools', path)
    t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
else:
    t = None

def table():
    return dict(HEARTBEAT=1.,SYSTEM_TIME=1.,TIMESYNC=10.,LINK_NODE_STATUS=1.,
        SYS_STATUS=5.,STATUSTEXT=20.,COMMAND_LONG=None,HIGHRES_IMU=50.,
        ATTITUDE=100.,ODOMETRY=30.,CAMERA_TRIGGER=None)

class ScopeTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(t, 'Reduced telemetry scope/sampler tools missing')
    def test_only_nonessential_finite_streams_disabled(self):
        self.assertEqual(t.treatment(table()), {'HIGHRES_IMU':0.,'ATTITUDE':0.,'ODOMETRY':0.})
    def test_missing_or_nonfinite_backup_refused(self):
        for bad in (dict(table(),ATTITUDE=float('nan')), dict(table(),ATTITUDE=-1),
                    {k:v for k,v in table().items() if k!='LINK_NODE_STATUS'}):
            with self.assertRaises(ValueError): t.treatment(bad)
    def test_after_table_accepts_intentionally_removed_highres_not_fake_row(self):
        raw='instance #1:\n Name Rate Config (current) [Hz] Message Size (if active) [B]\n HEARTBEAT 1.00 (1.000) 21\n SYSTEM_TIME 1.00 (1.000) 24\n COMMAND_LONG unlimited\ninstance #2:\n HIGHRES_IMU 50.00 (1.000) 75\n'
        self.assertEqual(t.stream_table(raw),dict(HEARTBEAT=1.,SYSTEM_TIME=1.,COMMAND_LONG=None))
        with self.assertRaises(ValueError): t.stream_table(raw.replace('1.00 (1.000)','nan (1.000)',1))
    def test_duplicate_or_incomplete_target_table_refused(self):
        raw='instance #1:\n HEARTBEAT 1.00 (1.000) 21\n SYSTEM_TIME 1.00 (1.000) 24\n'
        with self.assertRaises(ValueError): t.stream_table(raw+' HEARTBEAT 1.00 (1.000) 21\n')
        with self.assertRaises(ValueError): t.stream_table(raw.replace('SYSTEM_TIME','INVALID'))
    def test_command_scope_rejects_wrong_link_health_and_other_mutations(self):
        treatment=t.treatment(table())
        for cmd in ('mavlink stream -d /dev/ttyS2 -s ATTITUDE -r 0',
                    'mavlink stream -d /dev/ttyS2 -s ATTITUDE -r 100'):
            t.check_command(cmd,'saved uart','saved logger',table(),treatment)
        for cmd in ('mavlink stream -d /dev/ttyS3 -s ATTITUDE -r 0',
                    'mavlink stream -d /dev/ttyS2 -s HEARTBEAT -r 0',
                    'mavlink stream -d /dev/ttyS2 -s ATTITUDE -r 200',
                    'param set EKF2_EV_CTRL 1','commander arm','mavlink stop-all'):
            with self.assertRaises(ValueError): t.check_command(cmd,'saved uart','saved logger',table(),treatment)

class MetricsTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(t, 'Reduced telemetry scope/sampler tools missing')
    def test_proc_stat_fields_are_not_shifted_by_spaces_parentheses(self):
        fields=['S']+['0']*21
        fields[11]='25'; fields[12]='7'; fields[19]='1000'; fields[21]='12'
        status='VmRSS:\t128 kB\nvoluntary_ctxt_switches:\t10\nnonvoluntary_ctxt_switches:\t3\n'
        row=t.proc_sample('42 (receiver (test)) '+' '.join(fields), status, now_ns=100,clk_tck=100,page_size=4096)
        self.assertEqual((row['utime_ticks'],row['stime_ticks'],row['starttime_ticks']),(25,7,1000))
        self.assertEqual(row['rss_bytes'],128*1024)
        self.assertEqual(row['voluntary_context_switches'],10)
    def test_short_stat_is_not_reported_as_zero_cpu(self):
        with self.assertRaises(ValueError): t.proc_sample('42 (x) S 0','',now_ns=1,clk_tck=100,page_size=4096)
    def test_uart_counters_decode_only_exact_linux_structure(self):
        result=t.decode_icount(struct.pack('20i',*range(20)))
        self.assertEqual((result['rx'],result['frame'],result['overrun'],result['buf_overrun']),(4,6,7,10))
        with self.assertRaises(ValueError): t.decode_icount(b'\0'*79)
    def test_unsupported_counter_ioctl_stays_unknown(self):
        import errno
        def unsupported(*args): raise OSError(errno.ENOTTY,'unsupported')
        row=t.uart_counters(123,ioctl=unsupported)
        self.assertEqual(row['status'],'UNKNOWN_UNSUPPORTED_IOCTL')
        self.assertNotIn('rx',row)

if __name__=='__main__': unittest.main()
