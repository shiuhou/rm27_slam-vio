"""Seal generated evidence/local report state after read-only verification."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
verification=json.loads((HERE/'verification-02.json').read_text())
reports={'HANDOFF.md':'HANDOFF.md','VAULT_UPDATE.md':'VAULT_UPDATE.md','new_plan.md':'new_plan.md',
    '.maixpy/README.md':'README.md','.maixpy/imu-design-20261010/LATEST.md':'LATEST.md',
    'rm27/perception/vision/docs/CODEX_RESUME.md':'CODEX_RESUME.md'}
for name,backup in reports.items():
    old=(HERE/'repo-before'/backup).read_bytes()
    current=(ROOT/name).read_bytes()
    if name=='.maixpy/README.md':
        marker=b'Latest OFFLINE attribution:'
        prefix,body=old.split(marker,1)
        assert current.startswith(prefix) and current.endswith(marker+body),name
    else:
        # Keep the ORIGINAL CRLF/LF bytes, not a text-normalized comparison.
        separator=b'\r\n\r\n' if b'\r\n' in old else b'\n\n'
        assert current.endswith(old.split(separator,1)[1]),name
external=set(json.loads((HERE/'expected.json').read_text())['source_sha256'])|set(reports)
external.update({'.maixpy/mavlink2-20261010/VALIDATION.md',
    '.maixpy/imu-uart-trial-20261011/topics.txt','.maixpy/imu-offline-20261008/bench_io.py',
    '.maixpy/imu-offline-20261008/capture_guard.py','.maixpy/imu-transport-20261010/rate_control.py',
    '.maixpy/imu-uart-negotiated-trial-20261011/coordinator.py',
    '.maixpy/imu-uart-negotiated-trial-20261011/analyze_failure.py',
    '.maixpy/imu-gap-diagnosis-20261011/diagnose.py',
    '.maixpy/imu-gap-diagnosis-20261011/manifest.json',
    '.maixpy/imu-gap-diagnosis-20261011/source/common.xml',
    '.maixpy/px4-v117-source-audit-20261009/source/new/src__modules__logger__logger.cpp',
    '.maixpy/px4-v117-source-audit-20261009/source/new/src__modules__logger__logged_topics.cpp'})
def entries(root,paths):
    return [dict(path=str(p.relative_to(root)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p))
        for p in sorted(paths)]
paths=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json']
result=dict(scope='ONE_APPROVED_REDUCED_TELEMETRY_PHYSICAL_COMPARISON_RESTORED_INPUT_PARTIAL',
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    firmware='d6f12ad1c4f70ad3230afd7d86e971421e02fef4',
    transport_comparison=verification['transport_comparison'],transport_qualified=False,
    openvins_admissible=False,stage_c='CLOSED',
    board_new_tests_pass=13,board_skips=0,windows_tests_pass=14,windows_posix_skips=3,
    original_report_bodies_preserved=True,files=entries(HERE,paths),
    external_files=entries(ROOT,[ROOT/n for n in external]))
with (HERE/'manifest.json').open('x',encoding='utf-8') as output:json.dump(result,output,indent=2,allow_nan=False)
assert all(sha(HERE/e['path'])==e['sha256'] for e in result['files'])
assert all(sha(ROOT/e['path'])==e['sha256'] for e in result['external_files'])
print(json.dumps(dict(own_files=len(result['files']),external_files=len(result['external_files']),
    manifest_sha256=sha(HERE/'manifest.json'),original_report_bodies_preserved=True)))
