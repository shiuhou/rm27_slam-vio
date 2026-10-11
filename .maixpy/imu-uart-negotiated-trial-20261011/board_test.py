"""Current-revision M3C PTY qualification only; never opens physical UART."""
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

root=Path(__file__).resolve().parent
site='/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages'
sys.path.insert(0,site); sys.path.insert(0,str(root))
expected=json.loads((root/'expected.json').read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root/'controller-source-02.tar.gz')==expected['source_archive_sha256']
assert sha(root/'pyulog-1.2.4.tar.gz')==expected['pyulog_archive_sha256']
actual={name:sha(root/name) for name in expected['source_sha256']}
assert actual==expected['source_sha256'],'Source differs from local tested revision'
import numpy,pymavlink,pyulog
row=dict(hostname=platform.node(),architecture=platform.machine(),python=sys.version,
    versions=dict(numpy=numpy.__version__,pymavlink=pymavlink.__version__,pyulog=version('pyulog')),
    imported_files=dict(numpy=numpy.__file__,pymavlink=pymavlink.__file__,pyulog=pyulog.__file__),
    source_sha256=actual,source_archive_sha256=expected['source_archive_sha256'],
    pyulog_archive_sha256=expected['pyulog_archive_sha256'],physical_uart_opened=False)
assert row['hostname']=='maixcam2-9d05' and row['architecture']=='aarch64'
assert row['versions']==dict(numpy='2.2.6',pymavlink='2.4.49',pyulog='1.2.4')
with (root/'environment.json').open('x') as f:json.dump(row,f,indent=2)
env=dict(os.environ,PYTHONPATH=str(root)+':'+site)
with (root/'tests.txt').open('x') as log:
    result=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',
        '.maixpy/imu-design-20261010/single-uart/controller','-p','test_*.py','-v'],
        cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=50)
    log.write('\nPythonExit='+str(result.returncode)+'\n')
text=(root/'tests.txt').read_text()
print(json.dumps(row))
print(text)
assert result.returncode==0 and 'Ran 120 tests' in text and '\nOK\n' in text and 'skipped=' not in text
print('M3C_SOFTWARE_PTY_ONLY_PASS',sha(root/'tests.txt'))
