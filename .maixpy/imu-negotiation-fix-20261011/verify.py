"""Read-only offline provenance verification. No device/network API or writes."""
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CONTROLLER=ROOT/'.maixpy/imu-design-20261010/single-uart/controller'
sys.path.insert(0,str(CONTROLLER))
from capture_report import audit_capture
from session import Controller

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def check_manifest(directory):
    data=json.loads((directory/'manifest.json').read_text(encoding='utf-8-sig'))
    for item in data['files']:
        assert sha(directory/item['path'])==item['sha256'],item['path']
    return len(data['files'])

def main():
    retry=ROOT/'.maixpy/imu-uart-retry-20261011'
    assert sha(retry/'manifest.json')=='4f212f7f6ded771946c4423fd8a252e54aff1ee2384033023bc15785e7a2f57f'
    retry_count=check_manifest(retry)
    trial=ROOT/'.maixpy/imu-uart-trial-20261011'
    old=json.loads((trial/'hashes.json').read_text(encoding='utf-8'))
    for name,expected in old.items(): assert sha(trial/name)==expected,name
    frozen_count=check_manifest(ROOT/'.maixpy/imu-design-20261010/single-uart/reassembly')
    stage=ROOT/'.maixpy/mavlink2-20261010/VALIDATION.md'
    assert sha(stage)=='d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
    audit=audit_capture(trial/'physical-trial-01',epoch='ORIGINAL_FAILED_TRIAL_UNCHANGED')
    assert audit['raw_decode_parity'] and audit['tx_write_calls']==0
    assert audit['session']['error']=='invalid MAVLink data: Bad prefix'
    expected_baseline={
        'session.py':'4792208a6cc397fd70dee89b1f116b5050c5bbe5be94bcb4b38c2675f9d18424',
        'uart_session.py':'285340c7bbfbe6bf8a2d39bef9c8958f0ba1d0868066bb47d6f1c3597f5a1f84',
        'capture_report.py':'2192488626e77be2a0f519a0d7c3ff7ad574056b848c82e9d0fe50bc136da944'}
    for name,expected in expected_baseline.items(): assert sha(HERE/'baseline'/name)==expected,name
    # Reproduce original strict negotiation deadlock from preserved source.
    namespace={'__file__':str(CONTROLLER/'session.py'),'__name__':'pre_negotiation'}
    exec(compile((HERE/'baseline/session.py').read_text(encoding='utf-8'),'pre_negotiation','exec'),namespace)
    from test_negotiation import v1_heartbeat
    before=namespace['Controller'](0)
    assert before.feed_wire(v1_heartbeat(),0)==[] and 'non-MAVLink2' in before.error
    # Saved21 bytes still do not authorize anything, even with opt-in.
    rows=[json.loads(x) for x in (trial/'physical-trial-01/wire.jsonl').read_text().splitlines()]
    saved=bytes.fromhex(next(r['wire_hex'] for r in rows if r['event']=='rx_chunk'))
    after=Controller(0,negotiate_mavlink2=True)
    assert after.feed_wire(saved,0)==[] and after.start_sent_ns is None
    assert after.tick(5_000_000_000)==[] and after.error=='initial heartbeat timeout'
    files=['session.py','uart_session.py','capture_report.py','startup_sync.py',
           'test_negotiation.py','test_posix_pty.py']
    print(json.dumps(dict(previous_preparation_entries_verified=retry_count,
        old_trial_entries_verified=len(old),frozen_reassembly_entries_verified=frozen_count,
        stage_ab_report_sha256=sha(stage),original_failed_capture_audit=True,
        baseline_source_sha256=expected_baseline,before_negotiation='non-MAVLink2 heartbeat; no TX',
        saved21_only='NO_TX_NO_START_TIMEOUT',physical_retry_executed=False,
        transport_qualified=False,openvins_admissible=False,clock_synchronization='UNKNOWN',
        source_sha256={name:sha(CONTROLLER/name) for name in files}),indent=2))

if __name__=='__main__': main()
