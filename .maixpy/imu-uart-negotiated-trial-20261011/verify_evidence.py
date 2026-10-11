"""Independent OFFLINE restoration/provenance audit of ONE failed physical trial.

No device access, no shortened/repaired ULog, no transport/source admission.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

import coordinator as c
from analyze_failure import complete_record_view

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent/'imu-transport-20261010'))
import rate_control as r
from capture_report import audit_capture
from ulog_mavlink import inspect_imu

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    rows = [json.loads(x) for x in (HERE/'coordinator.jsonl').read_text().splitlines()]
    backup = next(x for x in rows if x.get('backup_verified'))
    def outputs(command):
        return [rows[i+1]['output'] for i, row in enumerate(rows[:-1])
                if row.get('command') == command]
    assert rows[-1]['finished'] is True and rows[-1]['errors'] == []
    assert rows[-1]['acquisition_errors'] == ['receiver exit 1']
    assert [x['receiver_exit'] for x in rows if 'receiver_exit' in x] == [1]
    assert any(x.get('stream_mapping_restored') is True for x in rows)
    assert any(x.get('px4_configuration_restored') is True for x in rows)
    for row in rows:
        if 'command' in row:
            c.check_command(row['command'], backup['uart'], backup['logger'], backup['streams'])
    commands = [x['command'] for x in rows if 'command' in x]
    assert commands.count(c.START) == commands.count(c.LOGGER) == 1
    assert c.HASH in outputs('ver all')[0]
    assert {k: v['rate'] for k, v in r.streams(outputs('mavlink status streams')[-1]).items()} == backup['streams']
    assert c.sdlog_values(outputs('param show SDLOG*')[-1]) == backup['sdlog']
    ps = outputs('ps')[-1]
    assert backup['uart'] in ps and backup['logger'] in ps
    assert all(x in ps for x in backup['unrelated_uart_commands'].values())
    logger = outputs('logger status')[-1]
    assert 'Not logging' in logger and 'mode: all' in logger
    restored = c.port_block(outputs('mavlink status')[-1], '/dev/ttyS2', 115200)
    assert all(x in restored for x in ('5760 B/s', 'flow control: OFF', 'mode: Onboard'))
    flow = c.port_block(outputs('mavlink status')[-1], '/dev/ttyS3', 115200)
    assert 'compid: 88' in flow and 'msgid:  132' in flow and 'msgid:  106' in flow
    assert 'Disarmed' in outputs('commander status')[-1]
    assert re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s', outputs('param show EKF2_EV_CTRL')[-1])
    assert not re.search(r'^\s*etc/?\s*$', outputs('ls /fs/microsd')[-1], re.M)
    assert (HERE/'topics-readback.txt').read_bytes() == (HERE.parent/'imu-uart-trial-20261011/topics.txt').read_bytes()
    heartbeat_modes = [int(x) for x in re.findall(r'FC_HEARTBEAT\s+[0-9.]+\s+(\d+)',
        (HERE/'coordinator-console.txt').read_text(encoding='utf-16'))]
    assert heartbeat_modes and all(x == 29 for x in heartbeat_modes)
    before = json.loads((HERE/'board-preflight.json').read_text())
    after = json.loads((HERE/'board-after.json').read_text())
    environment = json.loads((HERE/'environment.json').read_text())
    expected = json.loads((HERE/'expected.json').read_text())
    assert before['owners'] == after['owners'] == []
    assert after['termios_unchanged'] is True and after['termios_after'] == before['termios_before']
    assert after['receiver_process_alive'] is False
    assert before['source_sha256'] == after['source_sha256'] == environment['source_sha256'] == expected['source_sha256']
    for name, digest in expected['source_sha256'].items():
        assert sha(ROOT/name) == digest, name
    for field in ('source_archive_sha256', 'pyulog_archive_sha256'):
        assert environment[field] == expected[field]
    assert sha(HERE.parent/'imu-negotiation-fix-20261011/controller-source-02.tar.gz') == expected['source_archive_sha256']
    assert sha(HERE.parent/'controller-m3c-pty-20261011/pyulog-1.2.4.tar.gz') == expected['pyulog_archive_sha256']
    tests = (HERE/'tests.txt').read_text()
    assert 'Ran 120 tests in 16.584s' in tests and '\nOK\n' in tests and 'PythonExit=0' in tests
    # Test names include "skipped_logging_sequence"; inspect result markers,
    # not a substring of the names of loss-rejection regressions.
    assert not re.search(r'\.\.\. skipped\b|\bOK \(skipped=', tests)
    remote_hashes = []
    for line in (HERE/'remote-artifact-sha256.txt').read_text(encoding='utf-16').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})\s+(.+)', line)
        if not match:
            assert not line.strip()
            continue
        remote = match[2]
        if '/physical-trial-01/' in remote:
            local = HERE/'download/physical-trial-01'/Path(remote).name
        else:
            local = HERE/Path(remote).name
        assert sha(local) == match[1], local
        remote_hashes.append(dict(local=str(local.relative_to(HERE)), sha256=match[1]))
    assert len(remote_hashes) == 6
    capture = HERE/'download/physical-trial-01'
    summary = json.loads((capture/'summary.json').read_text())
    assert summary['error'] == 'logging sequence discontinuity: expected 435, received 436'
    assert summary['termios_restored'] and summary['start_accepted'] and summary['stop_accepted']
    assert summary['negotiate_mavlink2'] is True and type(summary['negotiation_confirmed_mono_ns']) is int
    assert summary['negotiation_started_mono_ns'] < summary['negotiation_confirmed_mono_ns'] < summary['normal_data_start_mono_ns']
    assert not c.negotiated_receiver_ok(1, summary)
    assert not summary['finite_framing_verified'] and not (capture/'framing-valid.ulg').exists()
    audit = audit_capture(capture, epoch='CURRENT_D6F12AD1_FAILED_UART_PREFIX')
    assert audit == json.loads((HERE/'capture-audit.json').read_text())
    raw_hash = sha(capture/'received-prefix.bin')
    assert raw_hash == summary['received_prefix_sha256']
    raw = (capture/'received-prefix.bin').read_bytes()
    view, excluded = complete_record_view(raw)
    assert len(raw) == 107784 and excluded == 127
    imu = inspect_imu(view, instance=0, gyro_device=6684690, accel_device=6946834,
                      epoch='CURRENT_BMI088_FAILED_PREFIX_DIAGNOSTICS_NOT_DATASET')
    originals = [x['original'] for x in imu['diagnostic_means']]
    assert len(originals) == 513 and imu['issues'] == ['gap']
    assert all(x['openvins_admissible'] is False for x in imu['diagnostic_means'])
    fields = ('gyro_device_id', 'accel_device_id', 'gyro_calibration_count',
              'accel_calibration_count', 'delta_angle_clipping', 'delta_velocity_clipping')
    values = {name: sorted(set(x[name] for x in originals)) for name in fields}
    assert values['delta_angle_clipping'] == values['delta_velocity_clipping'] == [0]
    residual = imu['gyro_coverage_residual_us']
    gap_events = [x for x in residual if x > 2]
    analysis = json.loads((HERE/'failure-analysis.json').read_text())
    log_gap = analysis['wire']['logging_discontinuities']
    assert len(log_gap) == 1 and log_gap[0]['expected'] == 435
    wire = [json.loads(x) for x in (capture/'wire.jsonl').read_text().splitlines()]
    frames = [x for x in wire if x.get('event') == 'frame' and (x['sysid'], x['compid']) == (1, 1)]
    start = next(i for i, x in enumerate(frames) if x['type'] == 'LOGGING_DATA' and x['fields']['sequence'] == 434)
    end = next(i for i, x in enumerate(frames) if x['type'] == 'LOGGING_DATA' and x['fields']['sequence'] == 436)
    context = [dict(seq=x['seq'], type=x['type'], receipt_mono_ns=x['receipt_mono_ns']) for x in frames[start:end+1]]
    assert [(a['seq'], b['seq']) for a, b in zip(context, context[1:]) if (a['seq']+1)&255 != b['seq']] == [(34, 36)]
    frozen_counts = {}
    old = HERE.parent/'imu-uart-trial-20261011'
    manifest = json.loads((old/'hashes.json').read_text())
    for name, digest in manifest.items():
        assert sha(old/name) == digest, name
    frozen_counts['original_trial'] = len(manifest)
    for dirname in ('imu-uart-retry-20261011', 'imu-negotiation-fix-20261011'):
        old = HERE.parent/dirname
        entries = json.loads((old/'manifest.json').read_text(encoding='utf-8-sig'))['files']
        for entry in entries:
            assert sha(old/entry['path']) == entry['sha256'], entry['path']
        frozen_counts[dirname] = len(entries)
    old = HERE.parent/'imu-design-20261010/single-uart/reassembly'
    entries = json.loads((old/'manifest.json').read_text(encoding='utf-8-sig'))['files']
    for entry in entries:
        assert sha(old/entry['path']) == entry['sha256'], entry['path']
    frozen_counts['reassembly'] = len(entries)
    stage_sha = sha(HERE.parent/'mavlink2-20261010/VALIDATION.md')
    assert stage_sha == 'd9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
    assert raw_hash == sha(capture/'received-prefix.bin')
    result = dict(restoration_verified=True, firmware_hash=c.HASH, single_trial_no_retry=True,
        command_scope_verified=True, px4_stream_mapping_restored=True,
        px4_logger_restored='logger start -b 64 -t -m all; Not logging; 187 subscriptions',
        px4_uart_restored='115200/5760B_s/Onboard/flow_OFF', sdlog_restored=backup['sdlog'],
        m3c_exact_termios_restored=True, m3c_owners_after=[], unrelated_ports_preserved=True,
        observed_usb_heartbeat_count=len(heartbeat_modes), observed_base_modes=sorted(set(heartbeat_modes)),
        propellers='USER_CONFIRMED_SAME_BENCH_SESSION', disarmed=True, ekf2_ev_ctrl=0,
        board_tests=120, board_posix_pty_tests=7, board_skips=0,
        deployed_source_files_verified=len(expected['source_sha256']), remote_hashes=remote_hashes,
        frozen_artifacts_verified=frozen_counts, stage_ab_sha256=stage_sha,
        actual_receiver_exit=1, negotiation='VERIFIED_THIS_ATTEMPT', start_ack=True, stop_ack=True,
        retained_prefix_bytes=len(raw), diagnostic_excluded_incomplete_bytes=excluded,
        raw_decode_parity_verified=True, source_identity_calibration_clip_values=values,
        gyro_coverage_residual_gt2us_events=len(gap_events), gyro_coverage_residual_gt2us_sum=sum(gap_events),
        gyro_coverage_caveat='Retained integration coverage diagnostic, not exact hardware sample loss',
        logging_gap_transport_context=context,
        gap_attribution='CONFIRMED_LOGGING_GAP_WITH_MAVLINK_SEQ35_ABSENT; layer/root_cause_UNKNOWN',
        source_rate_qualification='PARTIAL_196.432901HZ_FAILED_PREFIX_NOT_200HZ_OR_60S',
        source_complete='UNKNOWN', tail_complete='UNKNOWN', clock_synchronization='UNKNOWN',
        m3c_cpu_qualification='NOT_MEASURED_PROCESS_ALREADY_GONE', transport_qualified=False,
        openvins_admissible=False, stage_c='CLOSED')
    with (HERE/'verification.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2, allow_nan=False))

if __name__ == '__main__':
    main()
