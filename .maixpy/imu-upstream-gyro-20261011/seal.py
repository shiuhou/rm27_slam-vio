"""Offline preservation check and exclusive inventory; no device access."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def log_text(name):
    raw = (HERE / name).read_bytes()
    return raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig').replace('\r\n', '\n')


reports = {
    'HANDOFF.md': 'HANDOFF.md', 'VAULT_UPDATE.md': 'VAULT_UPDATE.md',
    'new_plan.md': 'new_plan.md', '.maixpy/README.md': 'README.md',
    '.maixpy/imu-design-20261010/LATEST.md': 'LATEST.md',
    'rm27/perception/vision/docs/CODEX_RESUME.md': 'CODEX_RESUME.md',
}
for name, copy in reports.items():
    old = (HERE / 'repo-before' / copy).read_bytes()
    current = (ROOT / name).read_bytes()
    sep = b'\r\n\r\n' if b'\r\n' in old else b'\n\n'
    assert current.endswith(old.split(sep, 1)[1]), name

for path in HERE.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT).strip()
check = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
assert check.returncode == 0, check.stdout + check.stderr
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert head == '3ea1e16086965176db68b88e1c42990f92c5913e'
before = log_text('git-before.txt').splitlines()
status = subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True)
unrelated = [x for x in before if x.endswith(('tests/camera_capture.py', 'tmp/', 'PLAN_HISTORY.md'))]
assert all(x in status for x in unrelated)

for name, count, skips in (
    ('tests-final-03.txt', 22, 3), ('runner-regression.txt', 15, 0),
    ('board-tools-console.txt', 13, 0), ('board-observation-tests.txt', 6, 0),
    ('board-scope-tests.txt', 3, 0), ('board-pty-tests.txt', 5, 0),
):
    text = log_text(name)
    assert f'Ran {count} tests' in text and 'FAILED' not in text, name
    assert ('OK (skipped=3)' in text) if skips else ('\nOK\n' in text and 'skipped=' not in text), name
assert 'PythonExit=0' in log_text('tests-final-03.txt')
verification = read_json(HERE / 'verification.json')
assert json.loads(log_text('verification-console-03.txt')) == verification
assert verification['restoration_verified'] and verification['single_physical_trial_no_retry']
assert verification['matched_tx_rejection_events'] == 1
assert not verification['transport_qualified'] and not verification['openvins_admissible']
assert verification['retained_hz'] is None and verification['stage_c'] == 'CLOSED'
assert not (HERE / 'download/physical-trial-01/framing-valid.ulg').exists()

expected = read_json(HERE / 'expected.json')
for name, digest in expected['source_sha256'].items():
    assert sha(ROOT / name) == digest, name
assert sha(HERE / 'controller-source-02.tar.gz') == expected['source_archive_sha256']
for name, digest in read_json(HERE / 'tools-expected.json').items():
    assert sha(HERE / name) == digest, name
transfers = read_json(HERE / 'download/artifact-sha256.json')
for entry in transfers:
    path = HERE / 'attestation.json' if entry['path'] == 'attestation.json' else HERE / 'download' / entry['path']
    assert path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'], entry['path']

source = read_json(HERE.parent / 'imu-source-diagnosis-20261011/verification.json')['exact_source_hashes_verified']
for name, digest in source.items():
    assert sha(ROOT / name) == digest, name
stage = HERE.parent / 'mavlink2-20261010/VALIDATION.md'
assert sha(stage) == 'd9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'

# Historical own files are strict. External reports may resolve to a retained
# before-snapshot, never be mislabeled as matching the current edited report.
snapshots = [p for folder in HERE.parent.glob('*/repo-before') for p in folder.rglob('*') if p.is_file()]
frozen, resolutions = {}, []


def resolve_external(entry):
    path = ROOT / entry['path']
    if path.is_file() and sha(path) == entry['sha256']:
        return path
    aliases = {path.name, entry['path'].replace('\\', '/').replace('/', '__')}
    for candidate in snapshots:
        if candidate.name in aliases and sha(candidate) == entry['sha256']:
            resolutions.append(dict(original_path=entry['path'], sha256=entry['sha256'],
                archived_snapshot=candidate.relative_to(ROOT).as_posix(), not_current_state=True))
            return candidate
    raise AssertionError('Historical external snapshot absent: ' + entry['path'])


for name in (
    'imu-reader-control-20261011', 'imu-source-diagnosis-20261011',
    'imu-uart-reduced-trial-20261011', 'imu-gap-diagnosis-20261011',
    'imu-uart-negotiated-trial-20261011', 'imu-uart-retry-20261011',
    'imu-negotiation-fix-20261011', 'imu-design-20261010/single-uart/reassembly',
):
    directory = HERE.parent / name
    manifest = read_json(directory / 'manifest.json')
    for entry in manifest['files']:
        path = ROOT / entry['path'] if entry['path'].startswith(('.maixpy/', '.codex/')) else directory / entry['path']
        assert path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'], name + ':' + entry['path']
    for entry in manifest.get('external_files', []):
        assert sha(resolve_external(entry)) == entry['sha256']
    frozen[name] = dict(own=len(manifest['files']), external=len(manifest.get('external_files', [])),
        manifest_sha256=sha(directory / 'manifest.json'))
original = read_json(HERE.parent / 'imu-uart-trial-20261011/hashes.json')
for name, digest in original.items():
    assert sha(HERE.parent / 'imu-uart-trial-20261011' / name) == digest, name

preserved = dict(root_before_bodies_byte_preserved=list(reports), python_syntax_verified=True,
    exact_source_hashes_verified=source, historical_manifests_verified=frozen,
    historical_external_resolutions=resolutions, original_trial_hashes_verified=len(original),
    stage_ab_unchanged=True, source_files_verified=len(expected['source_sha256']),
    remote_local_hashes_verified=len(transfers), windows_pass=34, windows_skips=3,
    board_pass=27, board_skips=0, git_diff_check_exit=0, staged_diff_empty=True,
    head=head, unrelated_changes_preserved=unrelated, vault_access=False, push=False)
with (HERE / 'preservation-check.json').open('x', encoding='utf-8') as out:
    json.dump(preserved, out, indent=2, allow_nan=False)


def entries(paths):
    return [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(paths)]


own = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'manifest.json']
own += list((ROOT / '.codex/tasks/2026-10-11-imu-upstream-gyro').glob('*.md'))
external = {ROOT / p for p in source} | {ROOT / p for p in reports} | {ROOT / p for p in expected['source_sha256']}
external |= {stage, ROOT / 'docs/superpowers/plans/2026-10-11-vio-s0-upstream-gyro-observation.md'}
external |= {HERE.parent / name / 'manifest.json' for name in frozen}
external = {p for p in external if HERE not in p.parents}
manifest = dict(scope='ONE_ABORTED_UPSTREAM_GYRO_OBSERVER_TX_REJECTION_NO_SOURCE_PASS', head=head,
    acquisition='FAILED', restoration='VERIFIED', original_source_skip='UNKNOWN',
    normal_window_completed=False, actual_imu_hz=None, source_minimum_hz=200,
    source_complete='UNKNOWN', tail_complete='UNKNOWN', clock_status='UNKNOWN',
    transport_qualified=False, openvins_admissible=False, stage_c='CLOSED',
    files=entries(own), external_files=entries(external))
with (HERE / 'manifest.json').open('x', encoding='utf-8') as out:
    json.dump(manifest, out, indent=2, allow_nan=False)
print(json.dumps(dict(own_files=len(manifest['files']), external_files=len(manifest['external_files']),
    old_manifests=frozen, historical_external_snapshots=len(resolutions),
    manifest_sha256=sha(HERE / 'manifest.json'), head=head)))
