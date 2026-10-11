"""Synthetic negotiation safety/state/runner evidence only, not hardware PASS."""
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from pymavlink.dialects.v10 import common as m1
from pymavlink.dialects.v20 import common as m2
from session import Controller
from test_session import heartbeat, pack, decode, command_ack, packets, fixture
from test_uart_session import Clock, Peer
import uart_session as u
from capture_report import audit_capture

def v1_heartbeat(armed=False, source=(1,1), autopilot=m1.MAV_AUTOPILOT_PX4):
    return m1.MAVLink_heartbeat_message(m1.MAV_TYPE_QUADROTOR,autopilot,
        29 | (m1.MAV_MODE_FLAG_SAFETY_ARMED if armed else 0),0,m1.MAV_STATE_STANDBY,3).pack(
            m1.MAVLink(None,srcSystem=source[0],srcComponent=source[1]))

def v1_time(boot):
    return m1.MAVLink_system_time_message(0,boot).pack(m1.MAVLink(None,srcSystem=1,srcComponent=1))

class NegotiationTests(unittest.TestCase):
    def setUp(self):
        self.assertIn('negotiate_mavlink2',inspect.signature(Controller).parameters,
                      'Heartbeat-only negotiation phase not implemented')
        self.rows=[]
        self.c=Controller(0,seconds=1,emit=self.rows.append,negotiate_mavlink2=True)

    def test_initial_v1_only_replies_v2_heartbeat(self):
        messages=decode(self.c.feed_wire(v1_heartbeat(),100_000_000))
        self.assertEqual([m.get_type() for m in messages],['HEARTBEAT'])
        self.assertEqual(messages[0].get_msgbuf()[0],253)
        self.assertEqual((messages[0].get_srcSystem(),messages[0].get_srcComponent()),(1,191))
        self.assertEqual((messages[0].type,messages[0].autopilot),(m2.MAV_TYPE_ONBOARD_CONTROLLER,m2.MAV_AUTOPILOT_INVALID))
        self.assertEqual(self.c.state,'NEGOTIATING_MAVLINK2')
        self.assertIsNone(self.c.start_sent_ns)

    def test_v2_confirmation_starts_once(self):
        self.c.feed_wire(v1_heartbeat(),100_000_000)
        messages=decode(self.c.feed_wire(heartbeat(),200_000_000))
        self.assertEqual([m.command for m in messages if m.get_type()=='COMMAND_LONG'],[m2.MAV_CMD_LOGGING_START])
        self.assertEqual(self.c.state,'STARTING')
        self.assertEqual(self.c.summary()['negotiation_confirmed_mono_ns'],200_000_000)
        self.assertFalse(any(m.get_type()=='COMMAND_LONG' for m in decode(self.c.feed_wire(heartbeat(),300_000_000))))

    def test_default_still_refuses_v1_without_tx(self):
        strict=Controller(0)
        self.assertEqual(strict.feed_wire(v1_heartbeat(),0),[])
        self.assertIn('non-MAVLink2',strict.error)

    def test_already_v2_starts_without_bootstrap(self):
        self.c.feed_wire(heartbeat(),100_000_000)
        self.assertEqual(self.c.state,'STARTING')
        self.assertIsNone(self.c.summary()['negotiation_started_mono_ns'])
        self.assertEqual(self.c.summary()['negotiation_confirmed_mono_ns'],100_000_000)

    def test_no_heartbeat_no_tx(self):
        self.assertEqual(self.c.tick(0),[])
        self.assertEqual(self.c.tick(5_000_000_000),[])
        self.assertIn('initial heartbeat timeout',self.c.error)

    def test_fresh_v1_cannot_extend_five_second_deadline(self):
        for ns in range(5):
            messages=decode(self.c.feed_wire(v1_heartbeat(),ns*1_000_000_000))
            self.assertTrue(all(m.get_type()=='HEARTBEAT' for m in messages))
        self.assertEqual(self.c.feed_wire(heartbeat(),5_000_000_000),[])
        self.assertIn('negotiation timeout',self.c.error)
        self.assertIsNone(self.c.start_sent_ns)

    def test_stale_negotiation_aborts_without_stop(self):
        self.c.feed_wire(v1_heartbeat(),100_000_000)
        self.assertEqual(self.c.tick(2_700_000_000),[])
        self.assertIn('stale heartbeat',self.c.error)
        self.assertIsNone(self.c.stop_sent_ns)

    def test_one_hz_no_catch_up(self):
        self.c.feed_wire(v1_heartbeat(),100_000_000)
        self.assertEqual(self.c.tick(900_000_000),[])
        self.assertEqual(len(self.c.tick(1_100_000_000)),1)
        self.assertEqual(len(self.c.tick(2_300_000_000)),1)
        self.assertEqual(self.c.tick(2_300_000_000),[])

    def test_same_read_armed_vetoes_heartbeat_and_start(self):
        for later in (v1_heartbeat(True),heartbeat(True)):
            c=Controller(0,negotiate_mavlink2=True)
            self.assertEqual(c.feed_wire(v1_heartbeat()+later,0),[])
            self.assertIn('armed',c.error)
            self.assertIsNone(c.start_sent_ns)

    def test_same_read_crc_failure_vetoes_reply(self):
        bad=bytearray(heartbeat()); bad[-1]^=1
        self.assertEqual(self.c.feed_wire(v1_heartbeat()+bad,0),[])
        self.assertIn('invalid MAVLink',self.c.error)

    def test_signed_heartbeat_does_not_negotiate(self):
        encoder=m2.MAVLink(None,srcSystem=1,srcComponent=1)
        encoder.signing.secret_key=b'x'*32; encoder.signing.sign_outgoing=True
        signed=m2.MAVLink_heartbeat_message(m2.MAV_TYPE_QUADROTOR,m2.MAV_AUTOPILOT_PX4,29,0,3,3).pack(encoder)
        self.assertEqual(self.c.feed_wire(v1_heartbeat()+signed,0),[])
        self.assertIn('signed',self.c.error)

    def test_foreign_and_wrong_autopilot_refused(self):
        self.assertEqual(self.c.feed_wire(v1_heartbeat(source=(2,1)),0),[])
        self.assertEqual(self.c.state,'WAIT_HEARTBEAT')
        self.assertEqual(self.c.feed_wire(v1_heartbeat(autopilot=m1.MAV_AUTOPILOT_INVALID),1),[])
        self.assertIn('identity',self.c.error)

    def test_v1_boot_time_allowed_only_before_v2(self):
        self.assertEqual([m.get_type() for m in decode(self.c.feed_wire(v1_heartbeat()+v1_time(1000),0))],['HEARTBEAT'])
        self.assertEqual(self.c.last_boot_ms,1000)
        self.assertEqual(self.c.feed_wire(v1_time(500),100_000_000),[])
        self.assertIn('reboot',self.c.error)

    def test_unsolicited_logging_vetoes_reply(self):
        self.assertEqual(self.c.feed_wire(v1_heartbeat()+packets(fixture())[0],0),[])
        self.assertIn('unsolicited logging',self.c.error)

    def test_after_upgrade_v1_is_terminal(self):
        self.c.feed_wire(v1_heartbeat(),0); self.c.feed_wire(heartbeat(),100_000_000)
        messages=decode(self.c.feed_wire(v1_heartbeat(),200_000_000))
        self.assertEqual([m.command for m in messages],[m2.MAV_CMD_LOGGING_STOP])
        self.assertIn('non-MAVLink2',self.c.error)

    def test_same_read_v2_then_v1_is_not_a_safe_start(self):
        self.assertEqual(self.c.feed_wire(heartbeat()+v1_heartbeat(),0),[])
        self.assertIsNone(self.c.start_sent_ns)
        self.assertIn('non-MAVLink2',self.c.error)

    def test_opt_in_requires_actual_boolean(self):
        for value in (0,1,None,'true'):
            with self.assertRaises(ValueError): Controller(0,negotiate_mavlink2=value)

    def test_v1_sequence_byte_is_not_signed_flags(self):
        encoder=m1.MAVLink(None,srcSystem=1,srcComponent=1); encoder.seq=3
        wire=m1.MAVLink_heartbeat_message(m1.MAV_TYPE_QUADROTOR,m1.MAV_AUTOPILOT_PX4,29,0,3,3).pack(encoder)
        self.assertEqual(wire[2],3)
        self.assertEqual([x.get_type() for x in decode(self.c.feed_wire(wire,0))],['HEARTBEAT'])

    def test_v1_ack_never_allowed_during_negotiation(self):
        ack=m1.MAVLink_command_ack_message(m1.MAV_CMD_LOGGING_START,m1.MAV_RESULT_ACCEPTED).pack(
            m1.MAVLink(None,srcSystem=1,srcComponent=1))
        self.assertEqual(self.c.feed_wire(v1_heartbeat()+ack,0),[])
        self.assertIn('non-MAVLink2 control',self.c.error)
        self.assertIsNone(self.c.start_sent_ns)

    def test_same_read_v2_then_v1_uptime_vetoes_start(self):
        self.assertEqual(self.c.feed_wire(heartbeat()+v1_time(1000),0),[])
        self.assertIsNone(self.c.start_sent_ns)
        self.assertIn('non-MAVLink2 control',self.c.error)

    def test_negotiation_cancel_never_sends_stop(self):
        self.c.feed_wire(v1_heartbeat(),0)
        self.assertEqual(self.c.abort('cancelled offline',100_000_000),[])
        self.assertEqual(self.c.state,'DONE')
        self.assertIsNone(self.c.stop_sent_ns)

    def test_v1_reboot_same_read_vetoes_all_tx(self):
        self.assertEqual(self.c.feed_wire(v1_heartbeat()+v1_time(1000)+v1_time(900),0),[])
        self.assertIn('reboot',self.c.error)
        self.assertFalse(any(r['event']=='tx_intent' for r in self.rows))


class NegotiatingPeer(Peer):
    def __init__(self,clock,fault=None):
        super().__init__(clock,fault)
        self.queue=[v1_heartbeat()]; self.upgraded=False

    def write(self,wire):
        message=m2.MAVLink(None).parse_buffer(wire)[0]
        if message.get_type()=='HEARTBEAT' and not self.upgraded:
            if self.fault=='partial_bootstrap':
                self.written.append(wire)
                return len(wire)-1
            self.upgraded=True; self.queue.append(heartbeat())
        if message.get_type()=='COMMAND_LONG' and message.command==m2.MAV_CMD_LOGGING_START:
            assert self.upgraded, 'Peer saw logging START before negotiatedv2'
        return super().write(wire)

class NegotiationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.assertIn('negotiate_mavlink2',inspect.signature(u.run_session).parameters,
                      'Negotiation not wired into same-owner runner')

    def test_same_port_negotiation_then_byte_exact_log_and_audit(self):
        clock=Clock(); peer=NegotiatingPeer(clock)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'scripted'
            result=u.run_session(peer,output,seconds=1,clock=clock,negotiate_mavlink2=True)
            self.assertIsNone(result['error']); self.assertTrue(peer.closed)
            self.assertEqual((output/'framing-valid.ulg').read_bytes(),fixture())
            report=audit_capture(output,epoch='SYNTHETIC_NEGOTIATION_NOT_REAL_IMU')
            self.assertTrue(report['raw_decode_parity'])
            self.assertFalse(report['transport_qualified']); self.assertFalse(report['openvins_admissible'])
            self.assertTrue(report['session']['negotiate_mavlink2'])

    def test_partial_bootstrap_write_never_starts_or_retries(self):
        clock=Clock(); peer=NegotiatingPeer(clock,'partial_bootstrap')
        with tempfile.TemporaryDirectory() as tmp:
            result=u.run_session(peer,Path(tmp)/'partial',seconds=1,clock=clock,negotiate_mavlink2=True)
        self.assertIn('partial UART write',result['error'])
        self.assertEqual(len(peer.written),1)
        self.assertEqual(decode(peer.written)[0].get_type(),'HEARTBEAT')

    def test_bootstrap_freshness_rechecked_before_actual_write(self):
        class WriteClock(Clock):
            delayed=False
            def __call__(self):
                receipt=self.ns
                if self.delayed:
                    self.ns+=2_600_000_000; self.delayed=False
                return receipt
        clock=WriteClock(); peer=NegotiatingPeer(clock)
        first=peer.read
        def delayed_read(timeout):
            data=first(timeout)
            if data and not peer.upgraded:
                clock.delayed=True
            return data
        peer.read=delayed_read
        with tempfile.TemporaryDirectory() as tmp:
            result=u.run_session(peer,Path(tmp)/'stale-write',seconds=1,clock=clock,negotiate_mavlink2=True)
        self.assertIn('before UART write',result['error'])
        self.assertEqual(peer.written,[])

    def test_negotiation_requires_preflight_approval(self):
        row=dict(firmware_hash=u.EXPECTED_HASH,ekf2_ev_ctrl=0,disarmed=True,
            propellers_removed=True,uart='/dev/ttyS2',baud=921600,mavlink_datarate=46080,
            gyro_device_id=6684690,accel_device_id=6946834,vehicle_imu_instance=0,
            logger_backend='mavlink',logger_poll='vehicle_imu',configuration_backup_verified=True,
            prepared_m3c_monotonic_ns=1_000_000_000)
        for value in (None,False,1,'true'):
            with self.assertRaises(ValueError):
                u.validate_preflight(dict(row,heartbeat_negotiation_approved=value),2_000_000_000,negotiate_mavlink2=True)
        u.validate_preflight(dict(row,heartbeat_negotiation_approved=True),2_000_000_000,negotiate_mavlink2=True)

    def test_audit_cannot_downgrade_negotiation_to_legacy_mode(self):
        clock=Clock(); peer=NegotiatingPeer(clock)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'mutated'
            u.run_session(peer,output,seconds=1,clock=clock,negotiate_mavlink2=True)
            summary=json.loads((output/'summary.json').read_text())
            for key in list(summary):
                if key.startswith('negotiation_') or key in ('negotiate_mavlink2','mavlink2_negotiation_policy'):
                    del summary[key]
            (output/'summary.json').write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError,'negotiation policy'):
                audit_capture(output,epoch='SYNTHETIC_METADATA_MUTATION')

    def test_audit_rejects_premature_logging_tx(self):
        clock=Clock(); peer=NegotiatingPeer(clock)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'tx-mutated'
            result=u.run_session(peer,output,seconds=1,clock=clock,negotiate_mavlink2=True)
            rows=[json.loads(line) for line in (output/'wire.jsonl').read_text().splitlines()]
            start=next(row for row in rows if row['event']=='tx_write' and decode([bytes.fromhex(row['wire_hex'])])[0].get_type()=='COMMAND_LONG')
            start['receipt_mono_ns']=result['negotiation_confirmed_mono_ns']-1
            (output/'wire.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in rows))
            with self.assertRaisesRegex(ValueError,'before.*negotiat'):
                audit_capture(output,epoch='SYNTHETIC_TX_MUTATION')

    def test_audit_negotiation_summary_tampering(self):
        clock=Clock(); peer=NegotiatingPeer(clock)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'summary-mutated'
            original=u.run_session(peer,output,seconds=1,clock=clock,negotiate_mavlink2=True)
            for field,value in (('negotiate_mavlink2',1),('negotiation_started_mono_ns',None),
                                ('negotiation_confirmed_mono_ns',0),('mavlink2_negotiation_policy',None)):
                with self.subTest(field=field):
                    summary=dict(original); summary[field]=value
                    (output/'summary.json').write_text(json.dumps(summary))
                    with self.assertRaisesRegex(ValueError,'negotiation'):
                        audit_capture(output,epoch='SYNTHETIC_SUMMARY_MUTATION')

    def test_audit_missing_none_timestamp_is_explicit_failure(self):
        clock=Clock(); peer=Peer(clock)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'missing-field'
            summary=u.run_session(peer,output,seconds=1,clock=clock,negotiate_mavlink2=True)
            self.assertIsNone(summary['negotiation_started_mono_ns'])
            del summary['negotiation_started_mono_ns']
            (output/'summary.json').write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError,'negotiation'):
                audit_capture(output,epoch='SYNTHETIC_MISSING_SUMMARY')

if __name__=='__main__': unittest.main()
