"""Linux-only real termios/PTY integration. Never opens a physical UART."""
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest


@unittest.skipUnless(os.name == 'posix','real POSIX PTY unavailable on this Windows host')
class PTYTests(unittest.TestCase):
    def case(self, armed, *, negotiate=False, upgrade=True):
        import pty
        import select
        import termios
        from pymavlink.dialects.v20 import common as m
        from test_session import heartbeat, command_ack, packets, fixture
        from uart_session import OwnedUART, run_session
        from test_negotiation import v1_heartbeat
        from capture_report import audit_capture
        master, slave = pty.openpty()
        path = os.ttyname(slave)
        original = termios.tcgetattr(slave)
        os.close(slave)  # Production owners() must see no pre-existing slave owner.
        errors = []
        received = []
        stop = threading.Event()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'pty'
            def peer():
                try:
                    deadline = time.monotonic()+5
                    while time.monotonic()<deadline:
                        evidence = output/'wire.jsonl'
                        if evidence.exists() and 'uart_opened' in evidence.read_text(): break
                        time.sleep(.005)
                    else: raise AssertionError('PTY never opened')
                    parser = m.MAVLink(None)
                    next_hb = 0
                    upgraded = not negotiate
                    while not stop.is_set():
                        now = time.monotonic()
                        if now >= next_hb:
                            os.write(master,heartbeat(armed) if upgraded else v1_heartbeat(armed))
                            next_hb = now+1
                        if select.select([master],[],[],.02)[0]:
                            try: data = os.read(master,4096)
                            except OSError:
                                if stop.is_set(): break
                                continue
                            for msg in parser.parse_buffer(data) or []:
                                received.append(msg)
                                if msg.get_type() == 'HEARTBEAT' and not upgraded and upgrade:
                                    self.assertEqual(msg.get_msgbuf()[0],253)
                                    self.assertEqual((msg.get_srcSystem(),msg.get_srcComponent()),(1,191))
                                    upgraded = True
                                    os.write(master,heartbeat(armed))
                                if msg.get_type() != 'COMMAND_LONG': continue
                                if msg.command == m.MAV_CMD_LOGGING_START:
                                    self.assertTrue(upgraded,'START before peer upgraded')
                                    os.write(master,command_ack(m.MAV_CMD_LOGGING_START)+b''.join(packets(fixture())))
                                elif msg.command == m.MAV_CMD_LOGGING_STOP:
                                    os.write(master,command_ack(m.MAV_CMD_LOGGING_STOP))
                except BaseException as exc: errors.append(exc)
            worker = threading.Thread(target=peer,daemon=True)
            worker.start()
            try:
                result = run_session(OwnedUART(path,921600,approved=True),output,seconds=1,
                                     negotiate_mavlink2=negotiate)
                stop.set(); worker.join(2)
                self.assertFalse(worker.is_alive())
                self.assertEqual(errors,[])
                self.assertEqual(termios.tcgetattr(master),original)
                self.assertTrue(result['termios_restored'])
                if armed:
                    self.assertIn('armed',result['error'])
                    rows = [json.loads(x) for x in (output/'wire.jsonl').read_text().splitlines()]
                    self.assertFalse(any(r['event']=='tx_write' for r in rows))
                elif negotiate and not upgrade:
                    self.assertIn('negotiation timeout',result['error'])
                    self.assertGreater(len(received),0)
                    self.assertTrue(all(msg.get_type() == 'HEARTBEAT' for msg in received))
                    self.assertIsNone(result['negotiation_confirmed_mono_ns'])
                    self.assertFalse(result['start_accepted'])
                else:
                    self.assertIsNone(result['error'])
                    self.assertEqual((output/'framing-valid.ulg').read_bytes(),fixture())
                audit = audit_capture(output,epoch='SYNTHETIC_POSIX_PTY_NOT_HARDWARE')
                self.assertTrue(audit['raw_decode_parity'])
                self.assertFalse(audit['transport_qualified'])
                self.assertFalse(audit['openvins_admissible'])
            finally:
                stop.set(); worker.join(2); os.close(master)

    def test_real_pty_roundtrip_and_termios_restore(self): self.case(False)
    def test_real_pty_armed_refusal_and_restore(self): self.case(True)
    def test_real_pty_v1_to_v2_reactive_peer_same_owner(self): self.case(False,negotiate=True)
    def test_real_pty_v1_armed_no_tx_and_restore(self): self.case(True,negotiate=True)
    def test_real_pty_v1_never_upgrades_timeout_no_logging(self): self.case(False,negotiate=True,upgrade=False)


if __name__ == '__main__': unittest.main()
