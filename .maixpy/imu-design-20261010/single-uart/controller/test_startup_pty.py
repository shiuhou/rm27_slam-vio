"""POSIX PTY with pre-existing input and an already transmitting synthetic peer.

No physical UART; baud support/throughput cannot be inferred from a PTY.
"""
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest


@unittest.skipUnless(os.name == 'posix','POSIX PTY unavailable on Windows')
class StartupPTYTests(unittest.TestCase):
    def case(self, armed):
        import pty
        import select
        import termios
        import tty
        from pymavlink.dialects.v20 import common as m
        from test_session import heartbeat, command_ack, packets, fixture
        from test_startup_sync import SAVED_RX
        from uart_session import OwnedUART, run_session
        from capture_report import audit_capture

        master, slave = pty.openpty()
        path = os.ttyname(slave)
        # Fixture-only initial settings prevent the PTY's echo/canonical layer
        # from altering preloaded binary bytes. Production code does not flush.
        tty.setraw(slave)
        original = termios.tcgetattr(slave)
        prefix = SAVED_RX+heartbeat(armed)[-2:]
        os.write(master, prefix)
        self.assertTrue(select.select([slave],[],[],.5)[0])
        os.close(slave)
        errors = []
        first_write = threading.Event()
        stop = threading.Event()

        def peer():
            try:
                parser = m.MAVLink(None); parser.robust_parsing = True
                next_hb = 0
                while not stop.is_set():
                    now = time.monotonic()
                    if now >= next_hb:
                        os.write(master, heartbeat(armed))
                        first_write.set()
                        next_hb = now+.2
                    if select.select([master],[],[],.02)[0]:
                        try:
                            data = os.read(master,4096)
                        except OSError:
                            stop.wait(.005)  # Slave not open yet, or just closed.
                            continue
                        for msg in parser.parse_buffer(data) or []:
                            if msg.get_type() != 'COMMAND_LONG':
                                continue
                            if msg.command == m.MAV_CMD_LOGGING_START:
                                os.write(master,command_ack(m.MAV_CMD_LOGGING_START)+b''.join(packets(fixture())))
                            elif msg.command == m.MAV_CMD_LOGGING_STOP:
                                os.write(master,command_ack(m.MAV_CMD_LOGGING_STOP))
            except BaseException as exc:
                errors.append(exc)

        worker = threading.Thread(target=peer,daemon=True)
        worker.start()
        try:
            self.assertTrue(first_write.wait(2), 'peer must transmit before receiver opens')
            with tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp)/'preexisting-input'
                result = run_session(OwnedUART(path,921600,approved=True),output,seconds=1)
                stop.set(); worker.join(2)
                self.assertFalse(worker.is_alive())
                self.assertEqual(errors,[])
                self.assertTrue(result['termios_restored'])
                self.assertEqual(termios.tcgetattr(master),original)
                rows = [json.loads(x) for x in (output/'wire.jsonl').read_text().splitlines()]
                raw = b''.join(bytes.fromhex(r['wire_hex']) for r in rows if r['event']=='rx_chunk')
                self.assertTrue(raw.startswith(prefix))
                report = audit_capture(output,epoch='SYNTHETIC_PTY_STARTUP_ONLY')
                self.assertTrue(report['raw_decode_parity'])
                # Opaque startup candidate can consume early peer frames. Raw
                # queued bytes remain exact; no pre-START completeness claim.
                self.assertGreaterEqual(report['startup_excluded_bytes'],len(prefix))
                self.assertFalse(report['transport_qualified'])
                if armed:
                    self.assertIn('armed',result['error'])
                    self.assertFalse(any(r['event']=='tx_write' for r in rows))
                    self.assertFalse((output/'framing-valid.ulg').exists())
                else:
                    self.assertIsNone(result['error'])
                    self.assertEqual((output/'framing-valid.ulg').read_bytes(),fixture())
        finally:
            stop.set(); worker.join(2); os.close(master)

    def test_preexisting_input_roundtrip_and_restore(self):
        self.case(False)

    def test_preexisting_input_armed_refusal_and_restore(self):
        self.case(True)


if __name__ == '__main__':
    unittest.main()
