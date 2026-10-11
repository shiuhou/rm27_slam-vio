"""Existing saved ULog bytes through the controller, SYNTHETIC wire/time/ACKs.

No receive rate, ACK latency, current BMI088, Linux UART or VIO result is inferred.
"""
import hashlib
from io import BytesIO
import json
from pyulog import ULog
from session import Controller
from replay_saved import SOURCES
from test_session import heartbeat, command_ack, packets
from pymavlink.dialects.v20 import common as m


def replay(label, path, expected_hash, expected_dropouts):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError('saved input SHA mismatch')
    c = Controller(0,seconds=1)
    c.feed_wire(heartbeat(),0)
    c.feed_wire(command_ack(m.MAV_CMD_LOGGING_START),1)
    wires = packets(raw)
    for index, wire in enumerate(wires):
        c.feed_wire(wire,10+index)
        if c.error is not None: raise AssertionError(c.error)
    c.feed_wire(heartbeat(),1_100_000_000)
    if c.state != 'STOPPING': raise AssertionError('bounded stop not entered')
    c.feed_wire(command_ack(m.MAV_CMD_LOGGING_STOP),1_200_000_000)
    c.tick(1_500_000_000)
    if c.error is not None or c.result_bytes != raw:
        raise AssertionError('controller output differs / failed: '+str(c.error))
    log = ULog(BytesIO(c.result_bytes))
    if len(log.dropouts) != expected_dropouts or log.file_corruption:
        raise AssertionError('loss evidence changed')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise AssertionError('original source changed')
    return dict(label=label,framing='SYNTHETIC_NOT_UART',receipt_times='ARTIFICIAL_ORDER_TOKENS',
                unchanged_source_sha256=expected_hash,bytes=len(raw),packet_count=len(wires),
                exact_byte_reconstruction=True,logger_dropout_events=len(log.dropouts),
                dropout_duration_ms=sum(d.duration for d in log.dropouts),
                controller=c.summary(),actual_transport_rate='UNKNOWN')


if __name__ == '__main__':
    print(json.dumps([replay(*source) for source in SOURCES],indent=2))
