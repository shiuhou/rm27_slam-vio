"""Read-only offline startup diagnosis; reproduces failures, does not fix them.

No UART/SSH/configuration API. Synthetic cases are not hardware qualification.
"""
import hashlib
import json
from pathlib import Path
import sys

from pymavlink import __version__
from pymavlink.dialects.v20 import common as m

ROOT = Path(__file__).resolve().parents[2]
CONTROLLER = ROOT/'.maixpy/imu-design-20261010/single-uart/controller'
TRIAL = ROOT/'.maixpy/imu-uart-trial-20261011'
sys.path.insert(0, str(CONTROLLER))
from session import Controller


def heartbeat(armed=False):
    return m.MAVLink_heartbeat_message(m.MAV_TYPE_QUADROTOR,
        m.MAV_AUTOPILOT_PX4, 29 | (m.MAV_MODE_FLAG_SAFETY_ARMED if armed else 0),
        0, m.MAV_STATE_STANDBY, 3).pack(m.MAVLink(None, srcSystem=1, srcComponent=1))


def replay(data):
    events = []
    controller = Controller(0, emit=events.append)
    wires = controller.feed_wire(data, 1_000_000)
    return controller, wires, events


def main():
    manifest = json.loads((TRIAL/'hashes.json').read_text(encoding='utf-8'))
    for name, expected in manifest.items():
        assert hashlib.sha256((TRIAL/name).read_bytes()).hexdigest() == expected, name
    rows = [json.loads(line) for line in
            (TRIAL/'physical-trial-01/wire.jsonl').read_text(encoding='utf-8').splitlines()]
    chunks = [r for r in rows if r['event'] == 'rx_chunk']
    assert len(chunks) == 1
    raw = bytes.fromhex(chunks[0]['wire_hex'])
    assert raw.hex() == 'f93bfeffa6ffffff80e0fd885c91fc3452fdffe7d5'
    c, wires, events = replay(raw)
    decoded = [r for r in events if r['event'] in ('frame', 'bad_data')]
    stored = [r for r in rows if r['event'] in ('frame', 'bad_data')]
    assert [{k: v for k, v in r.items() if k != 'receipt_mono_ns'} for r in decoded] == [
            {k: v for k, v in r.items() if k != 'receipt_mono_ns'} for r in stored]
    assert c.error == 'invalid MAVLink data: Bad prefix' and c.state == 'DONE'
    assert wires == [] and not c.start_accepted and c.reassembler.packet_count == 0
    parser = c.reassembler.decoder.parser
    assert parser.buf_len() == 19 and parser.expected_length == 263
    assert c.feed_wire(heartbeat(), 2_000_000) == [] and c.state == 'DONE'

    hb = heartbeat()
    clean, clean_wires, _ = replay(hb)
    assert clean.state == 'STARTING' and clean.error is None and clean_wires
    # Correct split reads from a known frame boundary are already supported.
    for split in range(1, len(hb)):
        c = Controller(0)
        assert c.feed_wire(hb[:split], 0) == [] and c.error is None
        assert c.feed_wire(hb[split:], 1_000_000) and c.state == 'STARTING'
    # Attaching midway through an existing valid frame is different from split IO.
    for offset in range(1, len(hb)):
        c, wires, events = replay(hb[offset:]+hb)
        assert c.state == 'DONE' and c.error == 'invalid MAVLink data: Bad prefix'
        assert not wires
        assert any(r.get('type') == 'HEARTBEAT' for r in events)
    candidate, _, _ = replay(raw+hb)
    assert candidate.reassembler.decoder.parser.buf_len() == 19+len(hb)
    assert candidate.reassembler.decoder.parser.expected_length == 263
    # Existing safety behavior remains unchanged during this diagnosis.
    armed, wires, _ = replay(heartbeat(True))
    assert not wires and armed.state == 'DONE' and 'armed' in armed.error
    same_read, wires, _ = replay(hb+heartbeat(True))
    assert not wires and 'armed' in same_read.error
    c = Controller(0)
    assert c.feed_wire(hb, 0)
    stop = c.feed_wire(b'\xf9\x3b', 1_000_000)
    decoded_stop = m.MAVLink(None).parse_buffer(b''.join(stop))
    assert len(decoded_stop) == 1 and decoded_stop[0].command == m.MAV_CMD_LOGGING_STOP
    assert c.state == 'STOPPING' and c.error is not None

    sources = [CONTROLLER/'session.py', CONTROLLER/'uart_session.py',
               ROOT/'.maixpy/imu-input-20261010/imu_input.py']
    print(json.dumps(dict(
        diagnosis='REPRODUCED_NOT_FIXED', evidence_kind='SAVED_WIRE_AND_SYNTHETIC_CASES',
        pymavlink=__version__, original_trial_manifest_entries_verified=len(manifest),
        saved_rx_bytes=len(raw), saved_error='Bad prefix', offending_prefix_hex='f93b',
        parser_buffer_remaining=19, parser_expected_candidate_bytes=263,
        clean_frame_split_cases=len(hb)-1, late_attachment_failure_cases=len(hb)-1,
        armed_and_post_start_corruption_guards='UNCHANGED_CHECKED',
        physical_byte_origin='UNKNOWN', physical_throughput='NOT_QUALIFIED',
        source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sources}), indent=2))


if __name__ == '__main__':
    main()
