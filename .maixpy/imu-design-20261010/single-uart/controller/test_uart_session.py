"""No real UART: scripted wire peer and POSIX syscall doubles on Windows."""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from pymavlink.dialects.v20 import common as m
from test_session import pack, heartbeat, command_ack, fixture, packets

try:
    import uart_session as u
except ImportError:
    u = None


class Clock:
    def __init__(self): self.ns = 0
    def __call__(self): return self.ns


class Peer:
    """Only remote boundary is synthetic; real controller/parser/wire/runner execute."""
    def __init__(self, clock, fault=None):
        self.clock = clock
        self.queue = [heartbeat()]
        self.next_hb = 1_000_000_000
        self.parser = m.MAVLink(None)
        self.written = []
        self.closed = False
        self.fault = fault
        self.broken = False
    def __enter__(self): return self
    def __exit__(self, *exc): self.closed = True
    def read(self, timeout):
        self.clock.ns += 20_000_000
        if self.fault == 'cancel' and self.clock.ns >= 400_000_000 and not self.broken:
            self.broken = True
            raise KeyboardInterrupt()
        if self.clock.ns >= self.next_hb:
            self.queue.append(heartbeat())
            self.next_hb += 1_000_000_000
        return self.queue.pop(0) if self.queue else b''
    def write(self, wire):
        self.written.append(wire)
        for msg in self.parser.parse_buffer(wire) or []:
            if msg.get_type() == 'COMMAND_LONG' and msg.command == m.MAV_CMD_LOGGING_START:
                self.queue.extend([command_ack(m.MAV_CMD_LOGGING_START), *packets(fixture())])
                if self.fault == 'write_delay': self.clock.ns += 3_000_000_000
            elif msg.get_type() == 'COMMAND_LONG' and msg.command == m.MAV_CMD_LOGGING_STOP:
                self.queue.append(command_ack(m.MAV_CMD_LOGGING_STOP))
            elif self.fault == 'partial' and msg.get_type() == 'LOGGING_ACK' and not self.broken:
                self.broken = True
                return len(wire)-1
        return len(wire)


class RunnerTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(u, 'bounded UART runner missing')

    def run_case(self, fault=None):
        clock = Clock(); peer = Peer(clock, fault)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'capture'
            summary = u.run_session(peer, output, seconds=1, clock=clock)
            rows = [json.loads(line) for line in (output/'wire.jsonl').read_text().splitlines()]
            self.assertTrue(peer.closed)
            self.assertTrue(any(r['event'] == 'rx_chunk' for r in rows))
            self.assertTrue(any(r['event'] == 'tx_write' for r in rows))
            self.assertEqual(json.loads((output/'summary.json').read_text()), summary)
            if fault:
                self.assertIsNotNone(summary['error'])
                self.assertFalse((output/'framing-valid.ulg').exists())
            else:
                self.assertEqual((output/'framing-valid.ulg').read_bytes(), fixture())
                self.assertIsNone(summary['error'])
            return summary, rows, peer

    def test_scripted_roundtrip_preserves_bytes_and_evidence(self):
        summary, _, _ = self.run_case()
        self.assertTrue(summary['finite_framing_verified'])
        self.assertEqual(summary['tail_complete'], 'UNKNOWN')

    def test_cancel_sends_stop_and_closes(self):
        summary, rows, peer = self.run_case('cancel')
        self.assertIn('KeyboardInterrupt', summary['error'])
        self.assertTrue(any(r.get('type') == 'COMMAND_LONG' for r in rows))

    def test_partial_write_aborts_without_retransmitting_frame(self):
        summary, rows, peer = self.run_case('partial')
        self.assertIn('partial UART write', summary['error'])
        self.assertTrue(any(r.get('written') != r.get('requested') for r in rows if r['event'] == 'tx_write'))
        parser = m.MAVLink(None)
        messages = [msg for wire in peer.written for msg in parser.parse_buffer(wire) or []]
        self.assertEqual(sum(msg.get_type() == 'LOGGING_ACK' for msg in messages), 1)
        self.assertEqual(sum(getattr(msg, 'command', None) == m.MAV_CMD_LOGGING_STOP for msg in messages), 1)

    def test_output_exists_refuses_before_opening_uart(self):
        clock = Clock(); peer = Peer(clock)
        with tempfile.TemporaryDirectory() as output:
            with self.assertRaises(FileExistsError): u.run_session(peer, output, seconds=1, clock=clock)
        self.assertEqual(peer.written, [])
        self.assertFalse(peer.closed)

    def test_heartbeat_freshness_rechecked_at_each_actual_write(self):
        clock = Clock(); peer = Peer(clock,'write_delay')
        with tempfile.TemporaryDirectory() as tmp:
            summary = u.run_session(peer,Path(tmp)/'slow',seconds=1,clock=clock)
        parser = m.MAVLink(None)
        messages = [msg for wire in peer.written for msg in parser.parse_buffer(wire) or []]
        self.assertFalse(any(msg.get_type() == 'HEARTBEAT' for msg in messages))
        self.assertIn('before UART write',summary['error'])
        self.assertTrue(peer.closed)

    def test_preflight_attestation_saved_but_not_claimed_verified(self):
        clock = Clock(); peer = Peer(clock)
        attestation = {'explicit_fixture':'not_device_readback'}
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'peer'
            summary = u.run_session(peer,output,seconds=1,clock=clock,preflight=attestation)
            self.assertEqual(json.loads((output/'preflight-attestation.json').read_text()),attestation)
        self.assertEqual(summary['preflight_evidence'],'OPERATOR_ATTESTATION_NOT_AUTHENTICATED_READBACK')

    def test_preflight_stale_or_changed_configuration_refused(self):
        baseline = dict(firmware_hash='d6f12ad1c4f70ad3230afd7d86e971421e02fef4',
            ekf2_ev_ctrl=0,disarmed=True,propellers_removed=True,uart='/dev/ttyS2',
            baud=921600,mavlink_datarate=46080,gyro_device_id=6684690,
            accel_device_id=6946834,vehicle_imu_instance=0,logger_backend='mavlink',
            logger_poll='vehicle_imu',configuration_backup_verified=True,
            prepared_m3c_monotonic_ns=1_000_000_000)
        u.validate_preflight(baseline, 2_000_000_000)
        with self.assertRaises(ValueError): u.validate_preflight(baseline, 70_000_000_000)
        for key, value in [('baud', 115200),('ekf2_ev_ctrl', 1),('disarmed',False),
                ('gyro_device_id',3604506),('firmware_hash','unknown'),
                ('configuration_backup_verified',False),('prepared_m3c_monotonic_ns',0)]:
            changed = dict(baseline, **{key:value})
            with self.assertRaises(ValueError, msg=key): u.validate_preflight(changed, 2_000_000_000)


class UARTTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(u, 'exclusive UART context missing')
        self.old = [7, 8, 9, 10, 1, 1, [b'\x01']*8]
        self.current = copy.deepcopy(self.old)
        self.events = []
        self.term = types.SimpleNamespace(CSIZE=3,PARENB=4,CSTOPB=8,CRTSCTS=16,
            CREAD=32,CLOCAL=64,CS8=3,VMIN=0,VTIME=1,B921600=921600,
            TCSANOW=0,TIOCEXCL=100,TIOCNXCL=101)
        self.term.tcgetattr = lambda fd: copy.deepcopy(self.current)
        self.term.tcsetattr = lambda fd, mode, value: setattr(self, 'current', copy.deepcopy(value))
        self.ioctls = []
        self.fcntl = types.SimpleNamespace(ioctl=lambda fd, cmd: self.ioctls.append(cmd))

    def context(self, *, approved=True):
        return u.OwnedUART('/dev/ttyS2',921600,approved=approved,emit=self.events.append)

    def patches(self):
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(patch.dict(sys.modules, {'termios':self.term,'fcntl':self.fcntl}))
        stack.enter_context(patch.object(u, 'owners', return_value=[]))
        stack.enter_context(patch('builtins.open', return_value=io.StringIO('ttyS0 1 E')))
        stack.enter_context(patch.object(u.os, 'open', return_value=99))
        stack.enter_context(patch.object(u.os, 'O_NOCTTY', 256, create=True))
        stack.enter_context(patch.object(u.os, 'O_NONBLOCK', 2048, create=True))
        self.close = stack.enter_context(patch.object(u.os, 'close'))
        return stack

    def test_termios_restored_on_success(self):
        with self.patches():
            with self.context(): self.assertNotEqual(self.current,self.old)
            self.assertEqual(self.current,self.old)
            self.assertIn(self.term.TIOCEXCL,self.ioctls)
            self.assertIn(self.term.TIOCNXCL,self.ioctls)
            self.close.assert_called_once_with(99)
        self.assertTrue(self.events[-1]['termios_restored'])

    def test_termios_restored_on_keyboard_interrupt(self):
        with self.patches():
            with self.assertRaises(KeyboardInterrupt):
                with self.context(): raise KeyboardInterrupt()
            self.assertEqual(self.current,self.old)
            self.close.assert_called_once_with(99)

    def test_unapproved_setting_refused_and_closed(self):
        with self.patches():
            with self.assertRaisesRegex(RuntimeError,'approved'):
                with self.context(approved=False): pass
            self.assertEqual(self.current,self.old)
            self.close.assert_called_once_with(99)

    def test_busy_refused_before_open(self):
        with self.patches(), patch.object(u,'owners',return_value=['other']):
            with self.assertRaisesRegex(RuntimeError,'occupied'):
                with self.context(): pass
            self.close.assert_not_called()

    def test_console_refused_before_open(self):
        with self.patches(), patch('builtins.open',return_value=io.StringIO('ttyS2 1 E')):
            with self.assertRaisesRegex(RuntimeError,'console'):
                with self.context(): pass
            self.close.assert_not_called()

    def test_racing_second_owner_refused_after_exclusive_lock(self):
        with self.patches(), patch.object(u,'owners',side_effect=[[],['/proc/123/fd/5']]):
            with self.assertRaisesRegex(RuntimeError,'owner'):
                with self.context(): pass
            self.close.assert_called_once_with(99)

    def test_failed_setting_readback_restores_old(self):
        original = self.term.tcsetattr
        def ignore_new(fd,mode,attrs):
            if attrs == self.old: original(fd,mode,attrs)
        self.term.tcsetattr = ignore_new
        with self.patches():
            with self.assertRaisesRegex(RuntimeError,'readback'):
                with self.context(): pass
            self.assertEqual(self.current,self.old)
            self.close.assert_called_once_with(99)

    def test_restore_failure_still_closes_descriptor(self):
        original = self.term.tcsetattr
        def fail_restore(fd,mode,attrs):
            if attrs == self.old: raise OSError('restore failed')
            original(fd,mode,attrs)
        self.term.tcsetattr = fail_restore
        with self.patches():
            with self.assertRaisesRegex(OSError,'restore failed'):
                with self.context(): pass
            self.close.assert_called_once_with(99)
        self.assertFalse(self.events[-1]['termios_restored'])


if __name__ == '__main__': unittest.main()
