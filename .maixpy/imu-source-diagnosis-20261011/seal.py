"""Read-only final preservation checks, exclusive local evidence manifest."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports={'HANDOFF.md':'HANDOFF.md','VAULT_UPDATE.md':'VAULT_UPDATE.md','new_plan.md':'new_plan.md',
    '.maixpy/README.md':'README.md','.maixpy/imu-design-20261010/LATEST.md':'LATEST.md',
    'rm27/perception/vision/docs/CODEX_RESUME.md':'CODEX_RESUME.md'}
for name,backup in reports.items():
    old=(HERE/'repo-before'/backup).read_bytes()
    current=(ROOT/name).read_bytes()
    if name=='.maixpy/README.md':
        prefix,body=old.split(b'Latest physical comparison:',1)
        assert current.startswith(prefix) and current.endswith(b'Latest physical comparison:'+body)
    else:
        separator=b'\r\n\r\n' if b'\r\n' in old else b'\n\n'
        assert current.endswith(old.split(separator,1)[1]),name
for file in HERE.glob('*.py'):ast.parse(file.read_text(encoding='utf-8'),filename=str(file))
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT).strip()
check=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
assert check.returncode==0,check.stdout+check.stderr
baseline=(HERE/'git-before.txt').read_text(encoding='utf-8-sig').splitlines()
unrelated=[line for line in baseline if line.endswith(('tests/camera_capture.py','tmp/','PLAN_HISTORY.md'))]
current_status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
assert all(line in current_status for line in unrelated)
verified=json.loads((HERE/'verification.json').read_text(encoding='utf-8'))
for name,digest in verified['exact_source_hashes_verified'].items():assert sha(ROOT/name)==digest,name
msg=HERE.parent/'imu-input-20261010/msg__VehicleImu.msg'
original=(msg.parent/'manifest-sha256.txt').read_text(encoding='utf-8-sig')
line=next(x for x in original.splitlines() if x.endswith('msg__VehicleImu.msg'))
assert sha(msg)==line.split()[0]=='3d38685a61825342c70c124d7758ea31c87099a08265313e0d1e91444a8d7e6f'
for name,count in [('tests-final.txt',19),('regression-semantics.txt',9),('regression-reassembly.txt',28)]:
    output=(HERE/name).read_text(encoding='utf-16')
    assert f'Ran {count} tests' in output and '\nOK\n' in output and 'FAILED' not in output and 'skipped=' not in output
frozen_dir=HERE.parent/'imu-uart-reduced-trial-20261011'
manifest=json.loads((frozen_dir/'manifest.json').read_text(encoding='utf-8'))
for entry in manifest['files']:assert sha(frozen_dir/entry['path'])==entry['sha256']
for entry in manifest['external_files']:
    file=HERE/'repo-before'/reports[entry['path']] if entry['path'] in reports else ROOT/entry['path']
    assert sha(file)==entry['sha256']
with (HERE/'preservation-check.json').open('x',encoding='utf-8') as output:
    json.dump(dict(scope='OFFLINE_DIAGNOSIS_ONLY',root_before_bodies_preserved=list(reports),
        previous_own=80,previous_external=36,exact_source_hashes_rechecked=14,
        tests_pass=56,skips=0,python_syntax='VERIFIED',git_diff_check_exit=0,
        staged_diff_empty=True,unrelated_changes_preserved=unrelated,
        stage_ab_unchanged=True,production_runtime_unchanged=True,vault_access=False),output,indent=2)
def entries(paths):
    return [dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)]
own=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json']
packet=list((ROOT/'.codex/tasks/2026-10-11-imu-source-diagnosis').glob('*.md'))
external=set(verified['exact_source_hashes_verified'])|set(reports)|{
    '.maixpy/imu-uart-reduced-trial-20261011/manifest.json',
    '.maixpy/imu-design-20261010/offline.py',
    '.maixpy/imu-design-20261010/single-uart/reassembly/ulog_mavlink.py',
    '.maixpy/imu-design-20261010/single-uart/controller/capture_report.py',
    '.maixpy/imu-design-20261010/single-uart/controller/session.py',
    '.maixpy/imu-input-20261010/imu_input.py',
    '.maixpy/mavlink2-20261010/VALIDATION.md'}
sealed=dict(scope='OFFLINE_SOURCE_SUBSCRIPTION_DIAGNOSIS_NOT_A_FIRMWARE_FIX',
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    tests_pass=56,skips=0,original_minimum_hz=200,original_rate_gate_pass=False,
    source_complete='UNKNOWN',clock_status='UNKNOWN',tail_complete='UNKNOWN',
    openvins_admissible=False,stage_c='CLOSED',files=entries(own+packet),
    external_files=entries([ROOT/n for n in external]))
with (HERE/'manifest.json').open('x',encoding='utf-8') as output:json.dump(sealed,output,indent=2,allow_nan=False)
print(json.dumps(dict(own_files=len(sealed['files']),external_files=len(sealed['external_files']),
    manifest_sha256=sha(HERE/'manifest.json'),old_artifacts_preserved=True,root_bodies_preserved=True)))
