"""POSIX supervised dummy processes and PTY ioctl only; no physical UART."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

path=Path(__file__).resolve().parent/'monitor.py'
if path.exists():
    spec=importlib.util.spec_from_file_location('monitor',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
else:m=None

class PresenceTests(unittest.TestCase):
    def test_monitor_exists(self):self.assertIsNotNone(m,'Start-gated receiver CPU monitor missing')

@unittest.skipUnless(os.name=='posix','POSIX child gate/PTY only')
class SupervisorTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(m,'Start-gated receiver CPU monitor missing')
    def test_sampler_records_child_before_gate_and_early_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            script="import os,sys,time; assert os.read(int(sys.argv[-1]),1)==b'G'; time.sleep(.08); sys.exit(7)"
            result=m.supervise([sys.executable,'-B','-c',script],root,timeout=2)
            rows=[json.loads(x) for x in (root/'metrics.jsonl').read_text().splitlines()]
            first=next(x for x in rows if x.get('event')=='receiver_cpu')
            gate=next(x for x in rows if x.get('event')=='receiver_gate_released')
            self.assertLessEqual(first['receipt_mono_ns'],gate['receipt_mono_ns'])
            self.assertEqual(result['receiver_exit'],7)
            self.assertFalse(result['receiver_alive_after'])
    def test_bounded_supervisor_terminates_only_its_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=m.supervise([sys.executable,'-B','-c',"import os,sys,time; os.read(int(sys.argv[-1]),1); time.sleep(10)"],Path(tmp),timeout=.15)
            self.assertTrue(result['timed_out'])
            self.assertFalse(result['receiver_alive_after'])
    def test_uart_ioctl_on_pty_remains_unknown_not_zero(self):
        import pty
        from trial_tools import uart_counters
        master,slave=pty.openpty()
        try:self.assertTrue(uart_counters(slave)['status'].startswith('UNKNOWN'))
        finally:os.close(master);os.close(slave)

if __name__=='__main__':unittest.main()
