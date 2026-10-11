"""Bounded single-owner MAVLink ULog session. Wire intents only; no device IO.

Not a VIO frontend. Accepted STOP and a quiet UART do not certify the source tail.
"""
from pathlib import Path
import sys
from pymavlink.dialects.v20 import common as m

sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'reassembly'))
from ulog_mavlink import Reassembler, ReassemblyError
from startup_sync import StartupSync

# Reuse the original guard, without its serial/discovery entry point.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]/'m3c-ping-20261009'))
from probe import fresh_disarmed


class Controller:
    STRICT_POLICY = 'STRICT_V2_FIRST'
    NEGOTIATION_POLICY = 'GUARDED_V1_HEARTBEAT_BOOTSTRAP_V1'

    def __init__(self, start_ns, *, seconds=60, emit=lambda row: None,
                 max_bytes=64*1024*1024, negotiate_mavlink2=False):
        if type(start_ns) is not int or start_ns < 0:
            raise ValueError('integer monotonic start required')
        if type(seconds) not in (int, float) or not 0 < seconds <= 60:
            raise ValueError('bounded capture duration (0,60] required')
        if type(negotiate_mavlink2) is not bool:
            raise ValueError('negotiate_mavlink2 requires an actual boolean')
        self.negotiate_mavlink2 = negotiate_mavlink2
        self.negotiation_started_ns = self.negotiation_confirmed_ns = None
        self.started_ns = self.now_ns = start_ns
        self.duration_ns = int(seconds*1e9)
        self.emit = emit
        self.reassembler = Reassembler(max_bytes=max_bytes)
        self.startup = StartupSync(self.reassembler.decoder)
        self.encoder = m.MAVLink(None, srcSystem=1, srcComponent=191)
        self.state = 'WAIT_HEARTBEAT'
        self.error = None
        self.heartbeat = None
        self.start_sent_ns = self.data_start_ns = self.stop_sent_ns = None
        self.last_logging_ns = self.stop_ack_ns = self.next_heartbeat_ns = None
        self.start_accepted = self.stop_accepted = self.saw_normal_data = False
        self.result_bytes = None
        self.stop_wire = None
        self.last_boot_ms = None
        if self.negotiate_mavlink2:
            self.emit(dict(event='mavlink2_negotiation_policy',receipt_mono_ns=start_ns,
                           policy=self.NEGOTIATION_POLICY))

    def _wire(self, message):
        wire = message.pack(self.encoder)
        self.encoder.seq = (self.encoder.seq+1) & 255
        self.emit(dict(event='tx_intent',receipt_mono_ns=self.now_ns,
                       type=message.get_type(),wire_hex=wire.hex()))
        return wire

    def _command(self, command):
        return self._wire(m.MAVLink_command_long_message(1, 1, command, 0, *([0]*7)))

    def _stop(self):
        if self.stop_sent_ns is not None:
            return []
        self.state = 'STOPPING'
        self.stop_sent_ns = self.now_ns
        self.emit(dict(event='stopping',receipt_mono_ns=self.now_ns,error=self.error))
        self.stop_wire = self._command(m.MAV_CMD_LOGGING_STOP)
        return [self.stop_wire]

    def abort(self, reason, now_ns):
        if self.state == 'DONE':
            return []
        if type(now_ns) is int:
            self.now_ns = max(self.now_ns, now_ns)
        if self.error is None:
            self.error = reason
            self.emit(dict(event='failure',receipt_mono_ns=self.now_ns,message=reason))
        if self.start_sent_ns is not None:
            return self._stop()
        self.state = 'DONE'
        return []

    def _advance_time(self, now_ns):
        if type(now_ns) is not int or now_ns < self.now_ns:
            return self.abort('invalid/backwards monotonic receipt', self.now_ns)
        self.now_ns = now_ns
        return []

    def _receiving_if_ready(self):
        if self.state == 'STARTING' and self.start_accepted and self.saw_normal_data:
            self.state = 'RECEIVING'
            self.data_start_ns = self.now_ns
            self.emit(dict(event='normal_data_transition',receipt_mono_ns=self.now_ns))

    def feed_wire(self, wire, receipt_ns):
        if self.state == 'DONE':
            return []
        output = self._advance_time(receipt_ns)
        if self.state == 'DONE':
            return output
        if self.state in ('WAIT_HEARTBEAT','NEGOTIATING_MAVLINK2') and self.now_ns-self.started_ns >= 5_000_000_000:
            reason = 'negotiation timeout' if self.state == 'NEGOTIATING_MAVLINK2' else 'initial heartbeat timeout'
            return output+self.abort(reason, self.now_ns)
        if self.error is not None:
            # Still decode ACKs to close a failed session; never resume acquisition.
            pass
        try:
            rows = self.startup.feed(wire, self.now_ns)
        except Exception as exc:
            return output+self.abort('MAVLink decoding: '+str(exc), self.now_ns)
        # Preserve all decoded rows before any failure in the same read chunk.
        for row in rows:
            self.emit(row)
        # A later fault in one read must not let an earlier queued START/ACK escape.
        # Validate the entire read before forming any outbound intent. Version1
        # is allowed ONLY for bootstrap heartbeat/uptime, never for logging/ACK.
        # Track version progression in wire order, including within one read.
        v2_seen = self.negotiation_confirmed_ns is not None or self.start_sent_ns is not None
        boot_seen = self.last_boot_ms
        for row in rows:
            if row.get('event') == 'bad_data':
                return output+self.abort('invalid MAVLink data: '+row.get('reason',''),self.now_ns)
            typ = row.get('type')
            source = (row.get('sysid'),row.get('compid'))
            if not (typ in ('LOGGING_DATA','LOGGING_DATA_ACKED') or
                    (source == (1,1) and typ in ('HEARTBEAT','COMMAND_ACK','SYSTEM_TIME'))):
                continue
            frame = bytes.fromhex(row['wire_hex'])
            version = row.get('mavlink_version')
            bootstrap_v1 = (self.negotiate_mavlink2 and not v2_seen and version == 1
                            and source == (1,1) and typ in ('HEARTBEAT','SYSTEM_TIME'))
            if (row.get('crc_status') != 'VERIFIED' or not (version == 2 or bootstrap_v1)
                    or (version == 2 and frame[2] != 0)):
                if typ == 'HEARTBEAT':
                    return output+self.abort('unverified/signed/non-MAVLink2 heartbeat',self.now_ns)
                return output+self.abort('unverified/signed/non-MAVLink2 control or logging frame',self.now_ns)
            f = row['fields']
            if typ == 'HEARTBEAT':
                if f.get('autopilot') != m.MAV_AUTOPILOT_PX4 or f.get('mavlink_version') != 3:
                    return output+self.abort('unexpected PX4 heartbeat identity',self.now_ns)
                if f['base_mode'] & m.MAV_MODE_FLAG_SAFETY_ARMED:
                    return output+self.abort('armed PX4 heartbeat',self.now_ns)
                self.heartbeat = (self.now_ns/1e9,f['base_mode'])
                if version == 2:
                    v2_seen = True
            elif typ == 'SYSTEM_TIME':
                if boot_seen is not None and f['time_boot_ms'] < boot_seen:
                    return output+self.abort('PX4 reboot/uptime regression; new epoch required',self.now_ns)
                boot_seen = f['time_boot_ms']
        if self.state in ('NEGOTIATING_MAVLINK2','STARTING','RECEIVING') and not fresh_disarmed(self.heartbeat,self.now_ns/1e9):
            return output+self.abort('stale heartbeat',self.now_ns)
        for row in rows:
            if row.get('event') == 'bad_data':
                output += self.abort('invalid MAVLink data: '+row.get('reason', ''), self.now_ns)
                continue
            typ = row.get('type')
            source = (row.get('sysid'), row.get('compid'))
            relevant = typ in ('LOGGING_DATA', 'LOGGING_DATA_ACKED') or (
                source == (1, 1) and typ in ('HEARTBEAT', 'COMMAND_ACK', 'SYSTEM_TIME'))
            if not relevant:
                continue
            f = row['fields']
            if typ == 'HEARTBEAT':
                if f.get('autopilot') != m.MAV_AUTOPILOT_PX4 or f.get('mavlink_version') != 3:
                    output += self.abort('unexpected PX4 heartbeat identity', self.now_ns)
                    continue
                self.heartbeat = (self.now_ns/1e9, f['base_mode'])
                if f['base_mode'] & m.MAV_MODE_FLAG_SAFETY_ARMED:
                    output += self.abort('armed PX4 heartbeat', self.now_ns)
                elif self.state in ('WAIT_HEARTBEAT','NEGOTIATING_MAVLINK2') and self.error is None:
                    if row['mavlink_version'] == 1:
                        if self.state == 'WAIT_HEARTBEAT':
                            self.state = 'NEGOTIATING_MAVLINK2'
                            self.negotiation_started_ns = self.now_ns
                            self.next_heartbeat_ns = self.now_ns
                            self.emit(dict(event='mavlink2_negotiation_started',receipt_mono_ns=self.now_ns))
                        continue
                    if self.negotiate_mavlink2:
                        self.negotiation_confirmed_ns = self.now_ns
                        self.emit(dict(event='mavlink2_negotiation_confirmed',receipt_mono_ns=self.now_ns))
                    self.state = 'STARTING'
                    self.start_sent_ns = self.now_ns
                    if self.next_heartbeat_ns is None:
                        self.next_heartbeat_ns = self.now_ns
                    output.append(self._command(m.MAV_CMD_LOGGING_START))
            elif typ == 'SYSTEM_TIME':
                boot = f['time_boot_ms']
                if self.last_boot_ms is not None and boot < self.last_boot_ms:
                    output += self.abort('PX4 reboot/uptime regression; new epoch required',self.now_ns)
                self.last_boot_ms = boot
            elif typ == 'COMMAND_ACK':
                command = f.get('command')
                if command not in (m.MAV_CMD_LOGGING_START, m.MAV_CMD_LOGGING_STOP):
                    continue
                if (f.get('target_system'), f.get('target_component')) != (1, 191):
                    output += self.abort('unexpected command ack route', self.now_ns)
                    continue
                if command == m.MAV_CMD_LOGGING_START and self.state == 'STARTING':
                    if f['result'] == m.MAV_RESULT_ACCEPTED:
                        self.start_accepted = True
                        self._receiving_if_ready()
                    elif f['result'] != m.MAV_RESULT_IN_PROGRESS:
                        output += self.abort('start rejected: '+str(f['result']), self.now_ns)
                elif command == m.MAV_CMD_LOGGING_STOP and self.state == 'STOPPING':
                    if f['result'] == m.MAV_RESULT_ACCEPTED:
                        self.stop_accepted = True
                        if self.stop_ack_ns is None:
                            self.stop_ack_ns = self.now_ns
                    elif f['result'] != m.MAV_RESULT_IN_PROGRESS:
                        output += self.abort('stop rejected: '+str(f['result']), self.now_ns)
            else:
                if self.start_sent_ns is None:
                    output += self.abort('unsolicited logging before own start', self.now_ns)
                    continue
                if self.error is not None:
                    continue
                try:
                    before = self.reassembler.packet_count
                    acks = self.reassembler.feed(row)
                except ReassemblyError as exc:
                    output += self.abort(str(exc), self.now_ns)
                    continue
                self.last_logging_ns = self.now_ns
                self.emit(dict(event='logging_packet',receipt_mono_ns=self.now_ns,
                               sequence=f['sequence'],length=f['length'],
                               retransmission=before == self.reassembler.packet_count,
                               bytes_reassembled=len(self.reassembler.buffer)))
                # ACK reliable header/retries immediately, before periodic heartbeat.
                for sequence in acks:
                    output.append(self._wire(m.MAVLink_logging_ack_message(1, 1, sequence)))
                if typ == 'LOGGING_DATA':
                    self.saw_normal_data = True
                    self._receiving_if_ready()
        output += self.tick(self.now_ns)
        if self.error is not None:
            for wire in output:
                if wire != self.stop_wire:
                    self.emit(dict(event='intent_cancelled',receipt_mono_ns=self.now_ns,wire_hex=wire.hex()))
            output = [wire for wire in output if wire == self.stop_wire]
        return output

    def tick(self, now_ns):
        if self.state == 'DONE':
            return []
        output = self._advance_time(now_ns)
        if self.state == 'WAIT_HEARTBEAT':
            if self.now_ns-self.started_ns >= 5_000_000_000:
                output += self.abort('initial heartbeat timeout', self.now_ns)
            return output
        if self.state == 'NEGOTIATING_MAVLINK2' and self.now_ns-self.started_ns >= 5_000_000_000:
            return output+self.abort('negotiation timeout',self.now_ns)
        if self.state == 'STOPPING':
            elapsed = self.now_ns-self.stop_sent_ns
            quiet_since = max(self.stop_ack_ns or self.stop_sent_ns,
                              self.last_logging_ns or self.stop_sent_ns)
            if self.stop_accepted and self.now_ns-quiet_since >= 250_000_000:
                self._finish()
            elif elapsed >= 3_000_000_000:
                if self.error is None:
                    self.error = 'stop acknowledgement timeout' if not self.stop_accepted else 'stop tail timeout'
                self.state = 'DONE'
            return output
        if not fresh_disarmed(self.heartbeat, self.now_ns/1e9):
            return output+self.abort('stale heartbeat', self.now_ns)
        if self.state == 'STARTING' and self.now_ns-self.start_sent_ns >= 15_000_000_000:
            return output+self.abort('startup timeout', self.now_ns)
        if self.state == 'RECEIVING':
            if self.now_ns-self.last_logging_ns >= 2_500_000_000:
                return output+self.abort('stream idle timeout', self.now_ns)
            if self.now_ns-self.data_start_ns >= self.duration_ns:
                return output+self._stop()
        if self.now_ns >= self.next_heartbeat_ns:
            output.append(self._wire(m.MAVLink_heartbeat_message(m.MAV_TYPE_ONBOARD_CONTROLLER,
                          m.MAV_AUTOPILOT_INVALID, 0, 0, m.MAV_STATE_STANDBY, 3)))
            # No burst/catch-up if the event loop is late.
            self.next_heartbeat_ns = self.now_ns+1_000_000_000
        return output

    def _finish(self):
        if self.error is None:
            try:
                self.result_bytes = self.reassembler.finish()
            except ReassemblyError as exc:
                self.error = str(exc)
        self.state = 'DONE'

    def summary(self):
        return dict(**self.reassembler.summary(),state=self.state,error=self.error,
                    controller_started_mono_ns=self.started_ns,
                    negotiate_mavlink2=self.negotiate_mavlink2,
                    mavlink2_negotiation_policy=self.NEGOTIATION_POLICY if self.negotiate_mavlink2 else self.STRICT_POLICY,
                    negotiation_started_mono_ns=self.negotiation_started_ns,
                    negotiation_confirmed_mono_ns=self.negotiation_confirmed_ns,
                    start_accepted=self.start_accepted,stop_accepted=self.stop_accepted,
                    normal_data_start_mono_ns=self.data_start_ns,
                    last_logging_mono_ns=self.last_logging_ns,
                    startup_policy=StartupSync.POLICY,
                    startup_boundary_found=self.startup.complete,
                    startup_received_bytes=self.startup.received_bytes,
                    startup_excluded_bytes=self.startup.excluded_bytes,
                    startup_buffered_bytes=len(self.startup.buffer),
                    startup_completeness='NOT_MEASURED_PRE_START',
                    tail_complete='UNKNOWN',clock_synchronization='UNKNOWN',
                    configured_duration_s=self.duration_ns/1e9)
