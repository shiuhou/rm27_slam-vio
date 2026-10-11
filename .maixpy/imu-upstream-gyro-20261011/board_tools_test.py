"""Parity and NEW-tool tests only; no physical UART or repeated120-test suite."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys

root=Path(__file__).resolve().parent
sys.path.insert(0,'/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages')
sys.path.insert(0,str(root))
expected=json.loads((root/'expected.json').read_text())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
actual={name:sha(root/name) for name in expected['source_sha256']}
assert actual==expected['source_sha256']
assert sha(root/'controller-source-02.tar.gz')==expected['source_archive_sha256']
assert sha(root/'pyulog-1.2.4.tar.gz')==expected['pyulog_archive_sha256']
import numpy,pymavlink,pyulog
row=dict(hostname=platform.node(),architecture=platform.machine(),python=sys.version,
    versions=dict(numpy=numpy.__version__,pymavlink=pymavlink.__version__,pyulog=version('pyulog')),
    imported_files=dict(numpy=numpy.__file__,pymavlink=pymavlink.__file__,pyulog=pyulog.__file__),source_sha256=actual,
    source_archive_sha256=expected['source_archive_sha256'],pyulog_archive_sha256=expected['pyulog_archive_sha256'],
    physical_uart_opened=False,unchanged120_test_suite_not_repeated=True)
assert row['hostname']=='maixcam2-9d05' and row['architecture']=='aarch64'
assert row['versions']==dict(numpy='2.2.6',pymavlink='2.4.49',pyulog='1.2.4')
with (root/'environment.json').open('x') as f:json.dump(row,f,indent=2)
with (root/'tool-tests-02.txt').open('x') as f:
    result=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(root),'-p','test_*.py','-v'],
        cwd=root,stdout=f,stderr=subprocess.STDOUT,timeout=20)
    f.write('\nPythonExit='+str(result.returncode)+'\n')
text=(root/'tool-tests-02.txt').read_text()
print(json.dumps(row));print(text)
assert result.returncode==0 and 'Ran 13 tests' in text and '\nOK\n' in text and 'skipped=' not in text
