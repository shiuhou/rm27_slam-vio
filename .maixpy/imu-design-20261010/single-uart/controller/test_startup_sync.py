"""Startup-only regressions: saved bytes plus explicitly synthetic peers."""
import json
from pathlib import Path
import tempfile
import unittest

from pymavlink.dialects.v20 import common as m
from session import Controller
from test_session import heartbeat, pack, decode, command_ack
from test_uart_session import Peer, Clock
from uart_session import run_session
from capture_report import audit_capture

SAVED_RX = bytes.fromhex('f93bfeffa6ffffff80e0fd885c91fc3452fdffe7d5')
# The saved FE header has UNKNOWN msgid255/length255. SYNTHETIC bytes finish
# its opaque263-byte candidate; they are not measurements from the failed run.
SYNTHETIC_TAIL = b'x'*(263-(len(SAVED_RX)-2))
COMPLETED_PREFIX = SAVED_RX+SYNTHETIC_TAIL


class StartupTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.c = Controller(0, emit=self.events.append)

    def assert_started(self, wires):
        self.assertIsNone(self.c.error)
        self.assertEqual(self.c.state, 'STARTING')
        self.assertEqual([r.command for r in decode(wires) if r.get_type() == 'COMMAND_LONG'],
                         [m.MAV_CMD_LOGGING_START])

    def test_saved_rx_then_opaque_completion_and_fresh_heartbeat_can_start(self):
        self.assertEqual(self.c.feed_wire(SAVED_RX, 0), [])
        self.assertIsNone(self.c.error)
        self.assert_started(self.c.feed_wire(SYNTHETIC_TAIL+heartbeat(), 100_000_000))
        excluded = b''.join(bytes.fromhex(r['wire_hex']) for r in self.events
                            if r['event'] == 'startup_unframed')
        self.assertEqual(excluded, COMPLETED_PREFIX)
        summary = self.c.summary()
        self.assertEqual(summary.get('startup_excluded_bytes'), len(COMPLETED_PREFIX))
        self.assertEqual(summary.get('startup_policy'), 'BOUNDED_CRC_SYNC_V1')
        self.assertFalse(summary['openvins_admissible'])

    def test_completed_saved_candidate_and_valid_heartbeat_same_read(self):
        self.assert_started(self.c.feed_wire(COMPLETED_PREFIX+heartbeat(), 0))

    def test_saved_rx_plus_one_heartbeat_is_not_enough_to_disprove_unknown_outer(self):
        self.assertEqual(self.c.feed_wire(SAVED_RX+heartbeat(), 0), [])
        self.assertIsNone(self.c.error)
        self.assertEqual(self.c.state, 'WAIT_HEARTBEAT')
        self.assertEqual(self.c.tick(5_000_000_000), [])
        self.assertIn('heartbeat timeout', self.c.error)
        self.assertFalse(any(r['event']=='tx_intent' for r in self.events))

    def test_saved_rx_with_heartbeat_split_at_every_position(self):
        hb = heartbeat()
        for split in range(1, len(hb)):
            with self.subTest(split=split):
                self.c = Controller(0)
                self.assertEqual(self.c.feed_wire(COMPLETED_PREFIX+hb[:split], 0), [])
                self.assertIsNone(self.c.error)
                self.assert_started(self.c.feed_wire(hb[split:], 100_000_000))

    def test_all_late_heartbeat_attachment_positions(self):
        hb = heartbeat()
        for offset in range(1, len(hb)):
            with self.subTest(offset=offset):
                self.c = Controller(0)
                self.assert_started(self.c.feed_wire(hb[offset:]+hb, 0))

    def test_all_clean_frame_split_positions(self):
        hb = heartbeat()
        for split in range(1, len(hb)):
            with self.subTest(split=split):
                self.c = Controller(0)
                self.assertEqual(self.c.feed_wire(hb[:split], 0), [])
                self.assertIsNone(self.c.error)
                self.assert_started(self.c.feed_wire(hb[split:], 100_000_000))

    def test_unknown_plausible_header_waits_instead_of_scanning_payload(self):
        self.assertEqual(self.c.feed_wire(b'\xfd\xff\x01'+b'x'*12+heartbeat(), 0), [])
        self.assertEqual(self.c.state, 'WAIT_HEARTBEAT')
        self.assertIsNone(self.c.error)
        self.assertEqual(self.c.tick(5_000_000_000), [])
        self.assertIn('heartbeat timeout', self.c.error)
        self.assertFalse(any(r['event']=='tx_intent' for r in self.events))

    def test_known_impossible_length_header_can_be_skipped(self):
        # HEARTBEAT is at most9 payload bytes, not255. Flags do not suffice.
        impossible = b'\xfd\xff\x01\x00\x00\x01\x01\x00\x00\x00'
        self.assert_started(self.c.feed_wire(impossible+b'x'*12+heartbeat(), 0))

    def test_complete_unknown_candidate_is_excluded_whole(self):
        hb = heartbeat()
        unknown = b'\xfd\x40\x00\x00\x00\x01\x01\xff\xff\x00'
        unknown += hb+b'x'*(64-len(hb))+b'\x00\x00'
        self.assertEqual(self.c.feed_wire(unknown[:10+len(hb)], 0), [])
        self.assertEqual(self.c.feed_wire(unknown[10+len(hb):], 100_000_000), [])
        self.assertEqual(self.c.state, 'WAIT_HEARTBEAT')
        self.assert_started(self.c.feed_wire(hb, 200_000_000))
        self.assertEqual(self.c.summary()['startup_excluded_bytes'], len(unknown))

    def test_bad_crc_pre_boundary_retained_not_admitted(self):
        broken = bytearray(heartbeat()); broken[-1] ^= 1
        self.assertEqual(self.c.feed_wire(broken, 0), [])
        self.assertIsNone(self.c.error)
        self.assert_started(self.c.feed_wire(heartbeat(), 100_000_000))
        self.assertGreaterEqual(self.c.summary().get('startup_excluded_bytes', 0), len(broken))

    def test_garbage_or_crc_failure_never_transmits_without_verified_heartbeat(self):
        self.assertEqual(self.c.feed_wire(SAVED_RX+b'garbage', 0), [])
        self.assertEqual(self.c.tick(5_000_000_000), [])
        self.assertEqual(self.c.state, 'DONE')
        self.assertIn('heartbeat timeout', self.c.error)

    def test_foreign_valid_heartbeat_does_not_lock_boundary(self):
        self.assertEqual(self.c.feed_wire(b'xx'+heartbeat(source=(2, 1)), 0), [])
        self.assertEqual(self.c.state, 'WAIT_HEARTBEAT')
        self.assert_started(self.c.feed_wire(b'zz'+heartbeat(), 100_000_000))

    def test_known_valid_outer_frame_payload_is_not_scanned_for_inner_heartbeat(self):
        # Arbitrary binary payload contains an actual valid heartbeat frame.
        outer = pack(m.MAVLink_logging_data_message(1, 191, 0, 249, 0,
                                                   list(heartbeat())+[120]*(249-len(heartbeat()))))
        self.assertEqual(self.c.feed_wire(outer, 0), [])
        self.assertIn('unsolicited logging', self.c.error)

    def test_split_valid_outer_frame_never_uses_embedded_heartbeat(self):
        hb = heartbeat()
        outer = pack(m.MAVLink_logging_data_message(1,191,0,249,0,
                                                   list(hb)+[120]*(249-len(hb))))
        self.assertEqual(len(outer),267)  # Nonzero tail prevents MAVLink2 truncation.
        for split in range(1,len(outer)):
            with self.subTest(split=split):
                self.events = []
                self.c = Controller(0,emit=self.events.append)
                self.assertEqual(self.c.feed_wire(outer[:split], 0), [])
                self.assertIsNone(self.c.error)
                self.assertEqual(self.c.state, 'WAIT_HEARTBEAT')
                self.assertEqual(self.c.feed_wire(outer[split:], 100_000_000), [])
                self.assertIn('unsolicited logging', self.c.error)
                self.assertFalse(any(r['event']=='tx_intent' for r in self.events))

    def test_rejected_outer_crc_does_not_admit_embedded_heartbeat(self):
        hb = heartbeat()
        outer = bytearray(pack(m.MAVLink_logging_data_message(1,191,0,249,0,
                                                   list(hb)+[120]*(249-len(hb)))))
        outer[-1] ^= 1
        self.assertEqual(self.c.feed_wire(outer, 0), [])
        self.assertEqual(self.c.state, 'WAIT_HEARTBEAT')
        self.assertIsNone(self.c.error)
        self.assert_started(self.c.feed_wire(hb, 100_000_000))
        self.assertEqual(self.c.summary()['startup_excluded_bytes'], len(outer))

    def test_armed_heartbeat_after_startup_noise_never_transmits(self):
        self.assertEqual(self.c.feed_wire(COMPLETED_PREFIX+heartbeat(True), 0), [])
        self.assertIn('armed', self.c.error)
        self.assertFalse(any(r['event'] == 'tx_intent' for r in self.events))

    def test_same_read_noise_disarmed_then_armed_vetoes_start(self):
        self.assertEqual(self.c.feed_wire(COMPLETED_PREFIX+heartbeat()+heartbeat(True), 0), [])
        self.assertIn('armed', self.c.error)
        self.assertFalse(any(r['event'] == 'tx_intent' for r in self.events))

    def test_px4_wrong_autopilot_is_not_ignored_as_garbage(self):
        wrong = pack(m.MAVLink_heartbeat_message(m.MAV_TYPE_QUADROTOR,
                                                m.MAV_AUTOPILOT_INVALID, 29, 0, 3, 3))
        self.assertEqual(self.c.feed_wire(COMPLETED_PREFIX+wrong, 0), [])
        self.assertIn('identity', self.c.error)

    def test_px4_v1_heartbeat_is_not_accepted_as_sync(self):
        msg = m.MAVLink_heartbeat_message(m.MAV_TYPE_QUADROTOR,m.MAV_AUTOPILOT_PX4,29,0,3,3)
        wire = msg.pack(m.MAVLink(None,srcSystem=1,srcComponent=1),force_mavlink1=True)
        self.assertEqual(self.c.feed_wire(COMPLETED_PREFIX+wire, 0), [])
        self.assertIn('non-MAVLink2', self.c.error)

    def test_px4_signed_heartbeat_is_not_accepted_as_sync(self):
        enc = m.MAVLink(None,srcSystem=1,srcComponent=1)
        enc.signing.secret_key=b'x'*32; enc.signing.sign_outgoing=True
        wire=m.MAVLink_heartbeat_message(m.MAV_TYPE_QUADROTOR,m.MAV_AUTOPILOT_PX4,29,0,3,3).pack(enc)
        self.assertEqual(self.c.feed_wire(COMPLETED_PREFIX+wire, 0), [])
        self.assertIn('signed', self.c.error)

    def test_late_initial_heartbeat_cannot_escape_five_second_deadline(self):
        self.assertEqual(self.c.feed_wire(heartbeat(), 5_000_000_000), [])
        self.assertIn('heartbeat timeout', self.c.error)

    def test_startup_byte_cap_refuses_even_with_valid_heartbeat_at_end(self):
        self.assertEqual(self.c.feed_wire(b'x'*65536+heartbeat(), 0), [])
        self.assertIn('startup byte limit', self.c.error)
        self.assertFalse(any(r['event'] == 'tx_intent' for r in self.events))

    def test_repeated_noise_has_bounded_buffer_and_total_byte_cap(self):
        for index in range(64):
            self.assertEqual(self.c.feed_wire(b'x'*1024, index*1_000_000), [])
            self.assertIsNone(self.c.error)
        self.assertLessEqual(self.c.summary().get('startup_buffered_bytes', 65536), 279)
        self.assertEqual(self.c.feed_wire(b'x', 65_000_000), [])
        self.assertIn('startup byte limit', self.c.error)

    def test_junk_after_boundary_same_read_remains_fatal(self):
        self.assertEqual(self.c.feed_wire(COMPLETED_PREFIX+heartbeat()+b'xx', 0), [])
        self.assertIn('Bad prefix', self.c.error)
        self.assertFalse(any(r['event'] == 'tx_intent' for r in self.events))

    def test_post_start_crc_error_stops_without_resynchronizing(self):
        self.assert_started(self.c.feed_wire(COMPLETED_PREFIX+heartbeat(), 0))
        broken = bytearray(heartbeat()); broken[-1] ^= 1
        wires = self.c.feed_wire(broken, 100_000_000)
        self.assertEqual([r.command for r in decode(wires)], [m.MAV_CMD_LOGGING_STOP])
        self.assertEqual(self.c.state, 'STOPPING')
        self.assertIsNotNone(self.c.error)

    def test_synced_heartbeat_still_expires_before_logging_header_ack(self):
        self.assert_started(self.c.feed_wire(COMPLETED_PREFIX+heartbeat(), 0))
        wires = self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_START), 2_800_000_000)
        self.assertEqual([r.command for r in decode(wires)], [m.MAV_CMD_LOGGING_STOP])
        self.assertIn('stale', self.c.error)


class StartupAuditTests(unittest.TestCase):
    def case(self, tmp, *, clean=False):
        clock = Clock(); peer = Peer(clock)
        peer.queue = [heartbeat()] if clean else [SAVED_RX, SYNTHETIC_TAIL+heartbeat()]
        output = Path(tmp)/'synthetic'
        summary = run_session(peer, output, seconds=1, clock=clock)
        self.assertIsNone(summary['error'])
        return output

    def test_complete_synthetic_capture_retains_startup_bytes_and_replay_parity(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = self.case(tmp)
            result = audit_capture(output, epoch='SYNTHETIC_STARTUP_ONLY')
            self.assertTrue(result['raw_decode_parity'])
            self.assertEqual(result.get('startup_excluded_bytes'), len(COMPLETED_PREFIX))
            self.assertEqual(result['imu']['count'], 2)
            self.assertFalse(result['transport_qualified'])
            self.assertFalse(result['openvins_admissible'])
            chunks = [json.loads(x) for x in (output/'wire.jsonl').read_text().splitlines()]
            self.assertEqual(bytes.fromhex(next(r['wire_hex'] for r in chunks if r['event']=='rx_chunk')),SAVED_RX)

    def test_startup_evidence_tampering_fails_parity(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = self.case(tmp)
            rows = [json.loads(x) for x in (output/'wire.jsonl').read_text().splitlines()]
            row = next((r for r in rows if r['event']=='startup_unframed'), None)
            self.assertIsNotNone(row)
            row['wire_hex']='00'
            (output/'wire.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
            with self.assertRaisesRegex(ValueError,'parity'):
                audit_capture(output,epoch='SYNTHETIC_STARTUP_ONLY')

    def test_startup_summary_counters_tampering_fails_parity(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = self.case(tmp)
            summary = json.loads((output/'summary.json').read_text())
            for field,value in [('startup_boundary_found',False),
                    ('startup_received_bytes',0),('startup_excluded_bytes',0),
                    ('startup_buffered_bytes',1),('startup_buffered_bytes',False),
                    ('startup_completeness','COMPLETE')]:
                with self.subTest(field=field,value=value):
                    tampered = dict(summary); tampered[field] = value
                    (output/'summary.json').write_text(json.dumps(tampered))
                    with self.assertRaisesRegex(ValueError,'parity'):
                        audit_capture(output,epoch='SYNTHETIC_STARTUP_ONLY')

    def test_new_capture_cannot_downgrade_to_legacy_by_deleting_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = self.case(tmp,clean=True)
            summary = json.loads((output/'summary.json').read_text())
            del summary['startup_policy']
            (output/'summary.json').write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError,'policy'):
                audit_capture(output,epoch='SYNTHETIC_STARTUP_ONLY')


if __name__ == '__main__':
    unittest.main()
