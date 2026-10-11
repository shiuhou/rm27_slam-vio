"""Synthetic wire/state-machine tests. No device, firmware or VIO evidence."""
from pathlib import Path
import sys
import unittest
from pymavlink.dialects.v20 import common as m

sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'reassembly'))
from test_ulog_mavlink import fixture, packets

try:
    from session import Controller
except ImportError:
    Controller = None


def pack(message, source=(1, 1)):
    return message.pack(m.MAVLink(None, srcSystem=source[0], srcComponent=source[1]))


def heartbeat(armed=False, source=(1, 1)):
    return pack(m.MAVLink_heartbeat_message(m.MAV_TYPE_QUADROTOR,
                m.MAV_AUTOPILOT_PX4, m.MAV_MODE_FLAG_SAFETY_ARMED if armed else 29,
                0, m.MAV_STATE_STANDBY, 3), source)


def command_ack(command, result=m.MAV_RESULT_ACCEPTED, target=(1, 191)):
    return pack(m.MAVLink_command_ack_message(command, result, 0, 0, *target))


def decode(wires):
    parser = m.MAVLink(None)
    return [message for wire in wires for message in parser.parse_buffer(wire) or []]


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Controller, 'single-owner controller implementation missing')
        self.events = []
        self.c = Controller(0, seconds=1, emit=self.events.append)

    def start(self):
        wires = self.c.feed_wire(heartbeat(), 100_000_000)
        self.assertEqual([r.command for r in decode(wires) if r.get_type() == 'COMMAND_LONG'],
                         [m.MAV_CMD_LOGGING_START])
        self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_START), 200_000_000)
        return wires

    def receive(self, raw=None):
        self.start()
        raw = fixture() if raw is None else raw
        for index, wire in enumerate(packets(raw)):
            self.c.feed_wire(wire, 300_000_000+index*10_000_000)
        self.assertEqual(self.c.state, 'RECEIVING')
        return raw

    def stop_and_finish(self):
        wires = self.c.tick(1_500_000_000)
        self.assertEqual([r.command for r in decode(wires) if r.get_type() == 'COMMAND_LONG'],
                         [m.MAV_CMD_LOGGING_STOP])
        self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_STOP), 1_600_000_000)
        self.c.tick(2_000_000_000)
        self.assertEqual(self.c.state, 'DONE')

    def test_no_tx_before_fresh_heartbeat(self):
        self.assertEqual(self.c.tick(0), [])
        self.assertEqual(self.c.tick(1_000_000_000), [])

    def test_foreign_heartbeat_does_not_start(self):
        self.assertEqual(self.c.feed_wire(heartbeat(source=(2, 1)), 0), [])
        self.assertEqual(self.c.state, 'WAIT_HEARTBEAT')

    def test_armed_before_start_never_transmits(self):
        self.assertEqual(self.c.feed_wire(heartbeat(True), 0), [])
        self.assertEqual(self.c.state, 'DONE')
        self.assertIn('armed', self.c.error)

    def test_start_targets_and_zero_parameters(self):
        messages = decode(self.start())
        cmd = next(r for r in messages if r.get_type() == 'COMMAND_LONG')
        self.assertEqual((cmd.get_srcSystem(), cmd.get_srcComponent()), (1, 191))
        self.assertEqual((cmd.target_system, cmd.target_component), (1, 1))
        self.assertEqual([getattr(cmd, 'param'+str(i)) for i in range(1, 8)], [0]*7)

    def test_header_ack_is_immediate_and_retry_idempotent(self):
        self.start()
        header = packets(fixture())[0]
        for ns in (300_000_000, 400_000_000):
            messages = decode(self.c.feed_wire(header, ns))
            acks = [r for r in messages if r.get_type() == 'LOGGING_ACK']
            self.assertEqual([(r.target_system, r.target_component, r.sequence) for r in acks], [(1, 1, 0)])
        self.assertEqual(self.c.reassembler.retransmissions, 1)
        self.assertEqual(self.c.state, 'STARTING')

    def test_header_can_precede_start_command_ack(self):
        self.c.feed_wire(heartbeat(), 0)
        for wire in packets(fixture()):
            self.c.feed_wire(wire, 100_000_000)
        self.assertEqual(self.c.state, 'STARTING')
        self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_START), 200_000_000)
        self.assertEqual(self.c.state, 'RECEIVING')

    def test_finite_success_does_not_claim_tail_or_openvins_pass(self):
        raw = self.receive()
        self.stop_and_finish()
        self.assertEqual(self.c.result_bytes, raw)
        summary = self.c.summary()
        self.assertTrue(summary['finite_framing_verified'])
        self.assertTrue(summary['stop_accepted'])
        self.assertEqual(summary['tail_complete'], 'UNKNOWN')
        self.assertEqual(summary['upstream_source_complete'], 'UNKNOWN')
        self.assertFalse(summary['openvins_admissible'])

    def test_duration_starts_at_data_transition_not_launch(self):
        self.receive()
        self.assertEqual(self.c.tick(1_200_000_000)[-1][0], 253)
        self.assertEqual(self.c.state, 'RECEIVING')
        self.c.tick(1_500_000_000)
        self.assertEqual(self.c.state, 'STOPPING')

    def test_stop_in_progress_does_not_finish(self):
        self.receive()
        self.c.tick(1_500_000_000)
        self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_STOP, m.MAV_RESULT_IN_PROGRESS), 1_600_000_000)
        self.c.tick(2_000_000_000)
        self.assertEqual(self.c.state, 'STOPPING')
        self.c.tick(4_600_000_000)
        self.assertEqual(self.c.state, 'DONE')
        self.assertIn('stop acknowledgement timeout', self.c.error)

    def test_denied_start_stops_once_never_retries_start(self):
        self.c.feed_wire(heartbeat(), 0)
        wires = self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_START, m.MAV_RESULT_DENIED), 100_000_000)
        self.assertEqual([r.command for r in decode(wires)], [m.MAV_CMD_LOGGING_STOP])
        self.assertEqual(self.c.tick(500_000_000), [])
        self.assertIn('start rejected', self.c.error)

    def test_wrong_ack_target_rejected(self):
        self.start()
        self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_START, target=(1, 42)), 300_000_000)
        self.assertIn('ack route', self.c.error)

    def test_initial_heartbeat_timeout_without_tx(self):
        self.assertEqual(self.c.tick(5_100_000_000), [])
        self.assertEqual(self.c.state, 'DONE')
        self.assertIn('heartbeat timeout', self.c.error)

    def test_stale_heartbeat_sends_only_stop(self):
        self.start()
        messages = decode(self.c.tick(2_700_000_000))
        self.assertEqual([r.command for r in messages], [m.MAV_CMD_LOGGING_STOP])
        self.assertIn('stale heartbeat', self.c.error)

    def test_armed_during_receive_sends_only_stop(self):
        self.receive()
        messages = decode(self.c.feed_wire(heartbeat(True), 500_000_000))
        self.assertEqual([r.command for r in messages], [m.MAV_CMD_LOGGING_STOP])
        self.assertIn('armed', self.c.error)

    def test_startup_timeout_despite_heartbeats(self):
        self.c.feed_wire(heartbeat(), 0)
        for ns in range(1, 16):
            self.c.feed_wire(heartbeat(), ns*1_000_000_000)
        self.assertEqual(self.c.state, 'STOPPING')
        self.assertIn('startup timeout', self.c.error)

    def test_capture_idle_timeout_despite_heartbeats(self):
        c = Controller(0, seconds=10)
        c.feed_wire(heartbeat(), 0)
        c.feed_wire(command_ack(m.MAV_CMD_LOGGING_START), 10_000_000)
        for wire in packets(fixture()):
            c.feed_wire(wire, 20_000_000)
        c.feed_wire(heartbeat(), 1_000_000_000)
        c.feed_wire(heartbeat(), 2_000_000_000)
        c.tick(2_600_000_000)
        self.assertIn('stream idle timeout', c.error)

    def test_logging_gap_stops_without_acking_missing_data(self):
        self.start()
        wires = packets(fixture(), 100)
        self.c.feed_wire(wires[0], 300_000_000)
        messages = decode(self.c.feed_wire(wires[2], 400_000_000))
        self.assertEqual([r.get_type() for r in messages], ['COMMAND_LONG'])
        self.assertIn('sequence', self.c.error)

    def test_crc_error_preserved_and_aborts(self):
        self.start()
        wire = bytearray(packets(fixture())[0]); wire[20] ^= 1
        self.c.feed_wire(wire, 300_000_000)
        self.assertIn('MAVLink', self.c.error)
        self.assertTrue(any(r.get('event') == 'bad_data' for r in self.events))

    def test_cancel_preserves_error_and_bounds_cleanup(self):
        self.receive()
        messages = decode(self.c.abort('cancelled', 500_000_000))
        self.assertEqual([r.command for r in messages], [m.MAV_CMD_LOGGING_STOP])
        self.c.tick(3_600_000_000)
        self.assertEqual(self.c.state, 'DONE')
        self.assertEqual(self.c.error, 'cancelled')
        self.assertIsNone(self.c.result_bytes)

    def test_post_stop_truncated_record_fails_without_repair(self):
        self.receive(fixture()[:-1])
        self.stop_and_finish()
        self.assertIn('truncated', self.c.error)
        self.assertIsNone(self.c.result_bytes)

    def test_late_packets_during_stop_are_retained(self):
        self.start()
        wire = packets(fixture(), 100)
        for frame in wire[:-1]:
            self.c.feed_wire(frame, 300_000_000)
        self.c.tick(1_500_000_000)
        self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_STOP), 1_600_000_000)
        self.c.feed_wire(wire[-1], 1_800_000_000)
        self.c.tick(2_000_000_000)
        self.assertEqual(self.c.state, 'STOPPING')
        self.c.tick(2_100_000_000)
        self.assertEqual(self.c.result_bytes, fixture())

    def test_receipt_order_cannot_go_backwards(self):
        self.start()
        self.c.tick(100_000_000)
        self.assertIn('monotonic', self.c.error)

    def test_every_emitted_wire_has_allowed_type_and_identity(self):
        self.receive()
        self.c.tick(1_200_000_000)
        self.stop_and_finish()
        messages = decode([bytes.fromhex(r['wire_hex']) for r in self.events if r.get('event') == 'tx_intent'])
        self.assertTrue(messages)
        self.assertTrue(all(r.get_type() in ('HEARTBEAT', 'COMMAND_LONG', 'LOGGING_ACK') for r in messages))
        self.assertTrue(all((r.get_srcSystem(), r.get_srcComponent()) == (1, 191) for r in messages))
        self.assertTrue(all(r.get_msgbuf()[0] == 253 for r in messages))

    def test_invalid_duration_refused(self):
        for seconds in (0, 61, float('nan'), True):
            with self.assertRaises(ValueError):
                Controller(0, seconds=seconds)

    def test_same_read_disarmed_then_armed_never_sends_start(self):
        wires = self.c.feed_wire(heartbeat()+heartbeat(True), 100_000_000)
        messages = decode(wires)
        self.assertFalse(any(getattr(r,'command',None) == m.MAV_CMD_LOGGING_START for r in messages))
        self.assertFalse(any(r.get_type() == 'HEARTBEAT' for r in messages))
        self.assertIn('armed', self.c.error)

    def test_stale_heartbeat_before_header_never_sends_logging_ack(self):
        self.start()
        wires = self.c.feed_wire(packets(fixture())[0], 2_800_000_000)
        self.assertEqual([r.get_type() for r in decode(wires)], ['COMMAND_LONG'])
        self.assertIn('stale heartbeat', self.c.error)

    def test_wrong_logging_identity_fails(self):
        self.start()
        parser = m.MAVLink(None)
        msg = parser.parse_buffer(packets(fixture())[0])[0]
        self.c.feed_wire(pack(msg,source=(2,1)), 300_000_000)
        self.assertIn('source', self.c.error)

    def test_signed_heartbeat_is_not_authenticated_by_crc(self):
        encoder = m.MAVLink(None,srcSystem=1,srcComponent=1)
        encoder.signing.secret_key = b'x'*32
        encoder.signing.sign_outgoing = True
        wire = m.MAVLink_heartbeat_message(m.MAV_TYPE_QUADROTOR,m.MAV_AUTOPILOT_PX4,29,0,3,3).pack(encoder)
        self.assertEqual(self.c.feed_wire(wire,0), [])
        self.assertIn('signed', self.c.error)

    def test_source_reboot_uptime_regression_fails(self):
        self.start()
        for stamp,ns in ((1000,300_000_000),(500,400_000_000)):
            self.c.feed_wire(pack(m.MAVLink_system_time_message(0,stamp)),ns)
        self.assertIn('reboot', self.c.error)

    def test_full_chunk_budget_limits_not_silently_exceeded(self):
        c = Controller(0,seconds=1,max_bytes=20)
        c.feed_wire(heartbeat(),0)
        c.feed_wire(packets(fixture())[0],100_000_000)
        self.assertIn('limit',c.error)

    def test_bad_frame_and_good_header_same_read_sends_no_ack(self):
        self.start()
        wire = bytearray(packets(fixture())[0]); wire[20] ^= 1
        wires = self.c.feed_wire(bytes(wire)+packets(fixture())[0],300_000_000)
        self.assertEqual([r.get_type() for r in decode(wires)], ['COMMAND_LONG'])

    def test_post_stop_partial_mavlink_frame_is_not_ignored(self):
        self.receive()
        self.c.tick(1_500_000_000)
        self.c.feed_wire(command_ack(m.MAV_CMD_LOGGING_STOP),1_600_000_000)
        self.c.feed_wire(heartbeat()[:-1],1_700_000_000)
        self.c.tick(2_000_000_000)
        self.assertIn('truncated MAVLink',self.c.error)


if __name__ == '__main__':
    unittest.main()
