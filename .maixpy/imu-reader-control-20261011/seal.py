"""Offline preservation and exclusive manifest; never changes prior evidence."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports={n:n.replace('/','__') for n in ('HANDOFF.md','VAULT_UPDATE.md','new_plan.md',
    '.maixpy/README.md','.maixpy/imu-design-20261010/LATEST.md','rm27/perception/vision/docs/CODEX_RESUME.md')}
for name,copy in reports.items():
    old=(HERE/'repo-before'/copy).read_bytes();current=(ROOT/name).read_bytes()
    if name=='.maixpy/README.md':
        prefix,body=old.split(b'Latest OFFLINE residual diagnosis:',1)
        assert current.startswith(prefix) and current.endswith(b'Latest OFFLINE residual diagnosis:'+body),name
    else:
        sep=b'\r\n\r\n' if b'\r\n' in old else b'\n\n'
        assert current.endswith(old.split(sep,1)[1]),name
for p in HERE.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT).strip()
check=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
assert check.returncode==0,check.stdout+check.stderr
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head=='3ea1e16086965176db68b88e1c42990f92c5913e'
old_status=(HERE/'git-before.txt').read_text(encoding='utf-16').splitlines()
status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
unrelated=[x for x in old_status if x.endswith(('tests/camera_capture.py','tmp/','PLAN_HISTORY.md'))]
assert all(x in status for x in unrelated)
logs=[('tests-profile-final.txt',8),('tests-compare-final.txt',7),('runner-regression.txt',15),
    ('diagnosis-regression.txt',19),('semantic-regression.txt',9),('reassembly-regression.txt',28)]
for name,count in logs:
    text=(HERE/name).read_text(encoding='utf-16')
    assert f'Ran {count} tests' in text and '\nOK\n' in text and 'PythonExit=0' in text and 'FAILED' not in text and 'skipped=' not in text,name
source=json.loads((HERE.parent/'imu-source-diagnosis-20261011/verification.json').read_text())['exact_source_hashes_verified']
for path,digest in source.items():assert sha(ROOT/path)==digest,path

# Current own files must match. Only historical EXTERNAL states may resolve to
# archived before-snapshots; record those resolutions rather than claiming current.
snapshots=[p for folder in HERE.parent.glob('*/repo-before') for p in folder.rglob('*') if p.is_file()]
snapshots += [HERE/'repo-before/uart_session.py']
frozen={};resolutions=[]
def resolve_external(entry):
    path=ROOT/entry['path']
    if path.is_file() and sha(path)==entry['sha256']:return path
    aliases={path.name,entry['path'].replace('\\','/').replace('/','__')}
    for candidate in snapshots:
        if candidate.name in aliases and sha(candidate)==entry['sha256']:
            resolutions.append(dict(original_path=entry['path'],sha256=entry['sha256'],
                archived_snapshot=candidate.relative_to(ROOT).as_posix(),not_current_state=True))
            return candidate
    raise AssertionError('Historical external snapshot not found: '+entry['path'])

for name in ('imu-source-diagnosis-20261011','imu-uart-reduced-trial-20261011',
    'imu-gap-diagnosis-20261011','imu-uart-negotiated-trial-20261011','imu-uart-retry-20261011',
    'imu-negotiation-fix-20261011','imu-design-20261010/single-uart/reassembly'):
    directory=HERE.parent/name
    manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8-sig'))
    for e in manifest['files']:
        path=ROOT/e['path'] if e['path'].startswith(('.maixpy/','.codex/')) else directory/e['path']
        assert sha(path)==e['sha256'],name+':'+e['path']
    for e in manifest.get('external_files',[]):assert sha(resolve_external(e))==e['sha256']
    frozen[name]=dict(own=len(manifest['files']),external=len(manifest.get('external_files',[])),manifest_sha256=sha(directory/'manifest.json'))
original_hashes=json.loads((HERE.parent/'imu-uart-trial-20261011/hashes.json').read_text())
for name,digest in original_hashes.items():
    assert sha(HERE.parent/'imu-uart-trial-20261011'/name)==digest,name
assert sha(HERE.parent/'mavlink2-20261010/VALIDATION.md')=='d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
preserved=dict(root_before_bodies_preserved=list(reports),exact_source_hashes_verified=source,
    historical_manifests_verified=frozen,historical_external_resolutions=resolutions,
    original_trial_hashes_verified=len(original_hashes),stage_ab_unchanged=True,python_syntax_verified=True,
    windows_targeted_tests_pass=86,windows_targeted_skips=0,board_tests_pass=48,board_skips=0,
    git_diff_check_exit=0,staged_diff_empty=True,head=head,unrelated_changes_preserved=unrelated,
    vault_access=False,push=False)
with (HERE/'preservation-check.json').open('x') as f:json.dump(preserved,f,indent=2)
def entries(paths):return [dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)]
packet=list((ROOT/'.codex/tasks/2026-10-11-imu-reader-control').glob('*.md'))
own=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json']
external={ROOT/p for p in source}|{ROOT/p for p in reports}|{
    ROOT/'.maixpy/imu-design-20261010/single-uart/controller/uart_session.py',
    HERE.parent/'mavlink2-20261010/VALIDATION.md',
    ROOT/'docs/superpowers/plans/2026-10-11-vio-s0-logger-reader-control.md'}
for name in frozen:external.add(HERE.parent/name/'manifest.json')
verified=json.loads((HERE/'verification.json').read_text())
manifest=dict(scope='ONE_FIXED_READER_REAL_CONTROL_NO_SOURCE_PASS',head=head,
    fixed_reader_hypothesis='FAILED',source_minimum_hz=200,actual_hz=verified['retained_hz'],
    original_rate_gate_pass=False,source_complete='UNKNOWN',tail_complete='UNKNOWN',clock_status='UNKNOWN',
    openvins_admissible=False,stage_c='CLOSED',files=entries(own+packet),external_files=entries(external))
with (HERE/'manifest.json').open('x') as f:json.dump(manifest,f,indent=2,allow_nan=False)
print(json.dumps(dict(own_files=len(manifest['files']),external_files=len(manifest['external_files']),
    old_manifests=frozen,historical_external_snapshots=len(resolutions),
    manifest_sha256=sha(HERE/'manifest.json'),head=head)))
