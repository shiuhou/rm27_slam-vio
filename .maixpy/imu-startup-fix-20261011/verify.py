"""Offline provenance checks and legacy/current wire replay; no hardware API."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONTROLLER = ROOT/'.maixpy/imu-design-20261010/single-uart/controller'
sys.path.insert(0, str(CONTROLLER))
from session import Controller
from capture_report import audit_capture


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    trial = ROOT/'.maixpy/imu-uart-trial-20261011'
    manifest = json.loads((trial/'hashes.json').read_text(encoding='utf-8'))
    for name, expected in manifest.items():
        assert sha(trial/name) == expected, name
    frozen = ROOT/'.maixpy/imu-design-20261010/single-uart/reassembly'
    items = json.loads((frozen/'manifest.json').read_text(encoding='utf-8'))['files']
    for item in items:
        assert sha(frozen/item['path']) == item['sha256'], item['path']
    stage = ROOT/'.maixpy/mavlink2-20261010/VALIDATION.md'
    assert sha(stage) == 'd9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
    legacy_audit = audit_capture(trial/'physical-trial-01',epoch='ORIGINAL_FAILED_TRIAL_UNCHANGED')
    assert legacy_audit['raw_decode_parity'] and legacy_audit['tx_write_calls'] == 0
    assert legacy_audit['session']['error'] == 'invalid MAVLink data: Bad prefix'
    backup = HERE/'baseline/session.py'
    assert sha(backup) == '9f30f12bf596a2f452a19d00b1a7e6cbaf50aad7c6a28ba7cb974934c8f2a9fb'
    # Same original __file__ preserves existing dependency layout for this
    # immutable source snapshot, without replacing the current import module.
    namespace = {'__file__':str(CONTROLLER/'session.py'),'__name__':'pre_sync_baseline'}
    exec(compile(backup.read_text(encoding='utf-8'),str(backup),'exec'),namespace)
    rows = [json.loads(line) for line in
            (trial/'physical-trial-01/wire.jsonl').read_text(encoding='utf-8').splitlines()]
    raw = bytes.fromhex(next(r['wire_hex'] for r in rows if r['event'] == 'rx_chunk'))
    before = namespace['Controller'](0)
    assert before.feed_wire(raw,0) == [] and before.error == 'invalid MAVLink data: Bad prefix'
    after = Controller(0)
    assert after.feed_wire(raw,0) == [] and after.error is None and after.state == 'WAIT_HEARTBEAT'
    assert after.tick(5_000_000_000) == [] and after.error == 'initial heartbeat timeout'
    assert after.start_sent_ns is None and after.reassembler.packet_count == 0
    files = ['session.py','startup_sync.py','capture_report.py','uart_session.py',
             'test_startup_sync.py','test_startup_pty.py']
    print(json.dumps(dict(
        original_trial_entries_verified=len(manifest), frozen_reassembly_entries_verified=len(items),
        stage_ab_unchanged_sha256=sha(stage), legacy_capture_parity=True,
        saved_rx_only='NO_START_NO_TX_TIMEOUT_NOT_HARDWARE_PASS',
        before_fix='Bad prefix', after_fix_without_new_bytes='initial heartbeat timeout',
        physical_throughput='NOT_QUALIFIED', clock_synchronization='UNKNOWN',
        openvins_admissible=False,
        source_sha256={name:sha(CONTROLLER/name) for name in files}),indent=2))


if __name__ == '__main__':
    main()
