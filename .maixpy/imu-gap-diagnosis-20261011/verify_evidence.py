"""Read-only offline replay/preservation audit; output is exclusive-create only."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import diagnose as d

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRIAL = HERE.parent/'imu-uart-negotiated-trial-20261011'
REPORT_BACKUPS = {
    'HANDOFF.md': 'HANDOFF.md', 'VAULT_UPDATE.md': 'VAULT_UPDATE.md',
    'new_plan.md': 'new_plan.md', '.maixpy/README.md': 'README.md',
    '.maixpy/imu-design-20261010/LATEST.md': 'LATEST.md',
    'rm27/perception/vision/docs/CODEX_RESUME.md': 'CODEX_RESUME.md'}
REPORT_ANCHORS = {
    'HANDOFF.md': 'User authorized ONE physical run',
    'VAULT_UPDATE.md': '## Negotiated physical IMU trial / confirmed gap',
    'new_plan.md': '> 2026-10-11 最新真机试验',
    '.maixpy/README.md': 'Latest physical result:',
    '.maixpy/imu-design-20261010/LATEST.md': '**2026-10-11 negotiated physical trial:',
    'rm27/perception/vision/docs/CODEX_RESUME.md': '最新真机：'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    prior = json.loads((TRIAL/'manifest.json').read_text(encoding='utf-8-sig'))
    for entry in prior['files']:
        assert sha(TRIAL/entry['path']) == entry['sha256'], entry['path']
    for entry in prior['external_files']:
        path = HERE/'repo-before'/REPORT_BACKUPS[entry['path']] if entry['path'] in REPORT_BACKUPS else ROOT/entry['path']
        assert sha(path) == entry['sha256'], entry['path']
    for name, backup in REPORT_BACKUPS.items():
        old = (HERE/'repo-before'/backup).read_bytes()
        current = (ROOT/name).read_bytes()
        marker = REPORT_ANCHORS[name].encode('utf-8')
        assert old[old.index(marker):] == current[current.index(marker):], name
    expected = json.loads((TRIAL/'expected.json').read_text())
    for name, digest in expected['source_sha256'].items():
        assert sha(ROOT/name) == digest, name
    old_counts = {}
    old = HERE.parent/'imu-uart-trial-20261011'
    entries = json.loads((old/'hashes.json').read_text())
    for name, digest in entries.items():
        assert sha(old/name) == digest, name
    old_counts['original_trial'] = len(entries)
    for name in ('imu-uart-retry-20261011', 'imu-negotiation-fix-20261011',
                 'imu-design-20261010/single-uart/reassembly'):
        old = HERE.parent/name
        entries = json.loads((old/'manifest.json').read_text(encoding='utf-8-sig'))['files']
        for entry in entries:
            assert sha(old/entry['path']) == entry['sha256'], entry['path']
        old_counts[name] = len(entries)
    stage_sha = sha(HERE.parent/'mavlink2-20261010/VALIDATION.md')
    assert stage_sha == 'd9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
    capture = TRIAL/'download/physical-trial-01'
    assert sha(capture/'wire.jsonl') == 'f424acde1d4a64a51a441ab6e4bbd4c0f8be171eaf419c4b184d8ffed3a97153'
    assert sha(capture/'received-prefix.bin') == 'b66b017ab4acbf04a85e76b196f8d98a4752ab885350881c15ab83d9e7505327'
    assert sha(capture/'summary.json') == 'b5cd54d1d195290c1bf3b707fbf221a87391854f691a552ddce67bc1b92d4922'
    assert not (capture/'framing-valid.ulg').exists()
    sys.path.insert(0, str(HERE.parent/'imu-design-20261010/single-uart/controller'))
    from capture_report import audit_capture
    assert audit_capture(capture, epoch='CURRENT_D6F12AD1_FAILED_UART_PREFIX') == json.loads((TRIAL/'capture-audit.json').read_text())
    rows = [json.loads(x) for x in (capture/'wire.jsonl').read_text().splitlines()]
    frames = [r for r in rows if r.get('event') == 'frame' and (r.get('sysid'), r.get('compid')) == (1, 1)]
    unknown = [r for r in frames if r.get('crc_status') != 'VERIFIED']
    checked = [d.verify_unknown_frame(r) for r in unknown]
    assert len(checked) == 33 and len(frames) == 3697
    saved = json.loads((HERE/'diagnosis.json').read_text())
    assert saved['counters'] == d.correlate(frames)
    assert saved['packet_local_post_failure_metadata'] == d.packet_metadata([
        r for r in frames if r['type'] == 'LOGGING_DATA_ACKED' and r['fields']['sequence'] >= 437])
    assert saved['transport_qualified'] is saved['openvins_admissible'] is False
    assert saved['stage_c'] == 'CLOSED' and saved['physical_fix'] == 'NOT_VALIDATED'
    assert all(i['unaccounted_successful_sends'] == 0 for i in saved['counters']['intervals'])
    assert sum(i['tx_rejected_delta'] for i in saved['counters']['intervals']) == 6
    assert saved['logging435_counter_interval']['tx_success_delta'] == 398
    assert saved['logging435_counter_interval']['tx_rejected_delta'] == 1
    assert json.loads((HERE/'source/px4-mavlink-submodule.json').read_text())['sha'] == saved['mavlink_submodule_hash']
    assert json.loads((HERE/'source/px4-nuttx-submodule.json').read_text())['sha'] == 'fb2fadf6f599c1406f052db013efd00a2518e72c'
    assert json.loads((HERE/'source/mavlink-pymavlink-submodule.json').read_text())['sha'] == 'fcaa2c7d25e3169dc66155929c338487941555e9'
    # A source-defined rejection consumes a global sequence before send_start.
    helper = (HERE/'source/mavlink_helpers.h').read_text()
    start = helper.index('MAVLINK_HELPER void _mav_finalize_message_chan_send(')
    assert helper.index('status->current_tx_seq++;', start) < helper.index('MAVLINK_START_UART_SEND(', start)
    result = dict(scope='OFFLINE_ONLY_NO_DEVICE_OR_RUNTIME_CHANGE',
        prior_trial_files_verified=len(prior['files']), prior_external_snapshot_files_verified=len(prior['external_files']),
        root_before_report_backups=len(REPORT_BACKUPS), deployed_source_files_unchanged=len(expected['source_sha256']),
        six_original_report_tails_byte_unchanged=True,
        other_frozen_artifacts=old_counts, stage_ab_sha256=stage_sha,
        raw_wire_replay_unchanged=True, all_retained_px4_frames=3697,
        previous_unknown_crc_verified=len(checked), previous_unknown_types=dict(Counter(x['name'] for x in checked)),
        counter_and_packet_metadata_replay_matches=True, rejected_send_total_in_nine_intervals=6,
        terminal_interval_successful_writes=398, terminal_interval_received_frames=398,
        terminal_interval_send_rejection_events=1,
        source_sequence_assigned_before_buffer_check=True,
        transport_qualified=False, openvins_admissible=False, physical_fix='NOT_VALIDATED', stage_c='CLOSED')
    # Preserve the original dated output. Later replays print a fresh result;
    # redirect to a NEW generated console log, never overwrite old evidence.
    if not (HERE/'verification.json').exists():
        with (HERE/'verification.json').open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2, allow_nan=False))

if __name__ == '__main__': main()
