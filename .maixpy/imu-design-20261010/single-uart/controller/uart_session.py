"""Explicitly approved finite ULog acquisition runner, never launched by tests.

No PX4 configuration API. Independent USB control must prepare/back up/restore
the actual PX4 configuration. An input preflight file is an operator attestation,
not authenticated device readback. Receipt clocks are not camera/FC clock mapping.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import time

from session import Controller, fresh_disarmed
from probe import owners

EXPECTED_HASH = 'd6f12ad1c4f70ad3230afd7d86e971421e02fef4'


def validate_preflight(row, now_ns, *, negotiate_mavlink2=False,
                       logger_reader='poll_vehicle_imu'):
    if type(negotiate_mavlink2) is not bool:
        raise ValueError('negotiate_mavlink2 requires an actual boolean')
    if negotiate_mavlink2 and row.get('heartbeat_negotiation_approved') is not True:
        raise ValueError('explicit heartbeat negotiation approval missing')
    expected = dict(firmware_hash=EXPECTED_HASH,ekf2_ev_ctrl=0,disarmed=True,
        propellers_removed=True,uart='/dev/ttyS2',baud=921600,mavlink_datarate=46080,
        gyro_device_id=6684690,accel_device_id=6946834,vehicle_imu_instance=0,
        logger_backend='mavlink',configuration_backup_verified=True)
    if logger_reader == 'poll_vehicle_imu':
        if 'logger_rate_hz' in row:
            raise ValueError('mixed poll/rate reader attestation')
        expected.update(logger_poll='vehicle_imu')
    elif logger_reader == 'fixed_2500hz':
        expected.update(logger_poll=None, logger_rate_hz=2500,
                        logger_reader='fixed_2500hz')
    else:
        raise ValueError('unapproved logger reader profile')
    for key, value in expected.items():
        if type(row.get(key)) is not type(value) or row[key] != value:
            raise ValueError('preflight differs from approved proposal: '+key)
    prepared = row.get('prepared_m3c_monotonic_ns')
    if type(prepared) is not int or prepared <= 0 or not 0 <= now_ns-prepared <= 60_000_000_000:
        raise ValueError('preflight stale/future or missing same-M3C monotonic timestamp')


class OwnedUART:
    """One exclusive POSIX descriptor, byte writes bounded and exact attrs restored."""
    def __init__(self, path, baud, *, approved=False, emit=lambda row: None):
        self.path, self.baud, self.approved, self.emit = path, baud, approved, emit
        self.fd = self.old = None
        self.locked = False
        self.restored = None

    def __enter__(self):
        import fcntl
        import termios
        self.fcntl, self.termios = fcntl, termios
        if owners(self.path):
            raise RuntimeError('UART occupied; no process killed')
        with open('/proc/consoles') as consoles:
            if any(line.split()[0] == os.path.basename(self.path) for line in consoles if line.strip()):
                raise RuntimeError('system console refused')
        speed = getattr(termios, 'B'+str(self.baud), None)
        if speed is None:
            raise RuntimeError('baud unsupported by termios')
        self.fd = os.open(self.path, os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
        try:
            fcntl.ioctl(self.fd, termios.TIOCEXCL)
            self.locked = True
            own_fd = '/proc/%d/fd/%d' % (os.getpid(),self.fd)
            if any(entry != own_fd for entry in owners(self.path)):
                raise RuntimeError('another UART owner raced exclusive acquisition')
            self.old = termios.tcgetattr(self.fd)
            attrs = copy.deepcopy(self.old)
            attrs[0] = attrs[1] = attrs[3] = 0
            mask = termios.CSIZE|termios.PARENB|termios.CSTOPB|termios.CRTSCTS|termios.CREAD|termios.CLOCAL
            attrs[2] = (attrs[2] & ~mask)|termios.CS8|termios.CREAD|termios.CLOCAL
            attrs[4] = attrs[5] = speed
            attrs[6][termios.VMIN] = attrs[6][termios.VTIME] = 0
            if attrs != self.old and not self.approved:
                raise RuntimeError('temporary UART settings not approved')
            termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
            applied = termios.tcgetattr(self.fd)
            if (any(applied[i] != 0 for i in (0,1,3)) or applied[4:6] != [speed,speed]
                or applied[2]&mask != termios.CS8|termios.CREAD|termios.CLOCAL
                or any(applied[6][i] not in (0,b'\x00') for i in (termios.VMIN,termios.VTIME))):
                raise RuntimeError('UART readback mismatch')
            self.emit(dict(event='uart_opened',path=self.path,baud=self.baud,
                           old_termios=repr(self.old),applied_termios=repr(applied),
                           input_flushed=False,exclusive=True))
            return self
        except BaseException:
            self._close()
            raise

    def read(self, timeout):
        import select
        if not 0 <= timeout <= .1:
            raise ValueError('bounded read timeout required')
        if select.select([self.fd], [], [], timeout)[0]:
            return os.read(self.fd, 8192)
        return b''

    def write(self, wire):
        import select
        if not select.select([], [self.fd], [], .1)[1]:
            raise TimeoutError('UART write readiness timeout')
        # One syscall, no retry/drain; partial transmission is terminal evidence.
        return os.write(self.fd, wire)

    def _close(self):
        if self.fd is None:
            return
        try:
            if self.old is not None:
                try:
                    self.termios.tcsetattr(self.fd, self.termios.TCSANOW, self.old)
                    self.restored = self.termios.tcgetattr(self.fd) == self.old
                    if not self.restored:
                        raise RuntimeError('termios restoration readback mismatch')
                finally:
                    self.emit(dict(event='uart_restored',termios_restored=self.restored is True))
        finally:
            try:
                if self.locked:
                    self.fcntl.ioctl(self.fd, self.termios.TIOCNXCL)
            finally:
                os.close(self.fd)
                self.fd = None

    def __exit__(self, *exc):
        self._close()


def run_session(port, output, *, seconds=60, clock=time.monotonic_ns, preflight=None,
                negotiate_mavlink2=False):
    """Bounded event loop; scripted offline peers use the same parser and sender.

    A port must provide a context manager plus read(timeout_s)/write(bytes). The
    real port changes only M3C termios; it never changes PX4 settings.
    """
    output = Path(output)
    output.mkdir(exist_ok=False)
    if preflight is not None:
        with (output/'preflight-attestation.json').open('x',encoding='utf-8') as snapshot:
            json.dump(preflight,snapshot,indent=2,allow_nan=False)
    with (output/'wire.jsonl').open('x', encoding='utf-8') as evidence:
        def emit(row):
            evidence.write(json.dumps(row,allow_nan=False)+'\n')
            evidence.flush()
        c = Controller(clock(),seconds=seconds,emit=emit,negotiate_mavlink2=negotiate_mavlink2)
        # Real UART context uses the same durable sink for restoration evidence.
        if isinstance(port, OwnedUART):
            port.emit = emit
        def transmit(wires):
            for wire in wires:
                if wire != c.stop_wire and (c.error is not None or not fresh_disarmed(c.heartbeat,clock()/1e9)):
                    emit(dict(event='tx_cancelled',receipt_mono_ns=clock(),wire_hex=wire.hex(),
                              reason='heartbeat/safety recheck at actual write'))
                    transmit(c.abort('stale heartbeat before UART write',clock()))
                    continue
                count = port.write(wire)
                emit(dict(event='tx_write',receipt_mono_ns=clock(),wire_hex=wire.hex(),
                          requested=len(wire),written=count))
                if count != len(wire):
                    raise RuntimeError('partial UART write; no frame retry')
        runner_error = None
        try:
            with port:
                try:
                    while c.state != 'DONE':
                        transmit(c.tick(clock()))
                        if c.state == 'DONE': break
                        data = port.read(.02)
                        receipt = clock()
                        if data:
                            emit(dict(event='rx_chunk',receipt_mono_ns=receipt,wire_hex=data.hex()))
                            transmit(c.feed_wire(data,receipt))
                except BaseException as exc:
                    runner_error = type(exc).__name__+': '+str(exc)
                    emit(dict(event='runner_failure',message=runner_error))
                    try:
                        transmit(c.abort(runner_error,clock()))
                        # Only STOP/ACK observation now. A second IO failure exits,
                        # so disconnected/throwing ports cannot spin indefinitely.
                        while c.state != 'DONE':
                            transmit(c.tick(clock()))
                            if c.state == 'DONE': break
                            data = port.read(.02)
                            receipt = clock()
                            if data:
                                emit(dict(event='rx_chunk',receipt_mono_ns=receipt,wire_hex=data.hex()))
                                transmit(c.feed_wire(data,receipt))
                    except BaseException as cleanup_exc:
                        emit(dict(event='cleanup_failure',message=type(cleanup_exc).__name__+': '+str(cleanup_exc)))
        except BaseException as exc:
            runner_error = type(exc).__name__+': '+str(exc)
            emit(dict(event='port_failure',message=runner_error))
            c.abort(runner_error,clock())  # Intent only; closed port is never reused.
        summary = c.summary()
        if runner_error and summary['error'] is None:
            summary['error'] = runner_error
        summary.update(termios_restored=getattr(port,'restored','NOT_MEASURED_OFFLINE_PEER'),
                       preflight_evidence='OPERATOR_ATTESTATION_NOT_AUTHENTICATED_READBACK' if preflight is not None else 'ABSENT_OFFLINE_TEST',
                       px4_configuration_restored='NOT_PERFORMED_BY_UART_RUNNER',
                       evidence_kind='UART_IF_EXPLICITLY_LAUNCHED_OTHERWISE_SCRIPTED_PEER')
        # Retain received prefix even on failure, never pad or overwrite it.
        raw = bytes(c.reassembler.buffer)
        with (output/'received-prefix.bin').open('xb') as prefix:
            prefix.write(raw)
        summary['received_prefix_sha256'] = hashlib.sha256(raw).hexdigest()
        if c.result_bytes is not None and summary['error'] is None:
            with (output/'framing-valid.ulg').open('xb') as log:
                log.write(c.result_bytes)
        with (output/'summary.json').open('x',encoding='utf-8') as report:
            json.dump(summary,report,indent=2,allow_nan=False)
        return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trial-approved',action='store_true',help='required; this flag alone is not authorization')
    p.add_argument('--negotiate-mavlink2',action='store_true',help='approved finite heartbeat-only v1 bootstrap; default requires v2 first')
    p.add_argument('--preflight',required=True,help='fresh same-M3C operator attestation from USB audit')
    p.add_argument('--output',required=True)
    p.add_argument('--seconds',type=int,choices=range(1,61),default=60)
    args = p.parse_args()
    if not args.trial_approved:
        p.error('explicit approved high-rate/logger trial required; no device opened')
    preflight = json.loads(Path(args.preflight).read_text(encoding='utf-8'))
    validate_preflight(preflight,time.monotonic_ns(),negotiate_mavlink2=args.negotiate_mavlink2)
    if os.name != 'posix':
        p.error('Linux UART only; use offline unit tests on Windows')
    signal.signal(signal.SIGTERM,lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    port = OwnedUART('/dev/ttyS2',921600,approved=True)
    summary = run_session(port,args.output,seconds=args.seconds,preflight=preflight,
                          negotiate_mavlink2=args.negotiate_mavlink2)
    print(json.dumps(summary,allow_nan=False))
    return 1 if summary['error'] is not None or summary['termios_restored'] is not True else 0


if __name__ == '__main__':
    raise SystemExit(main())
