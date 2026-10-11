"""Exclusive software snapshot; no device access or runtime modifications."""
import hashlib,json,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
archive=here/'controller-source-02.tar.gz'
assert not archive.exists()
subprocess.run(['tar','-czf',str(archive),'-T',str(here/'source-list.txt')],cwd=root,check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
row=dict(source_sha256={name:sha(root/name) for name in (here/'source-list.txt').read_text().splitlines()},
    source_archive_sha256=sha(archive),pyulog_archive_sha256=sha(root/'.maixpy/controller-m3c-pty-20261011/pyulog-1.2.4.tar.gz'))
with (here/'expected.json').open('x') as f:json.dump(row,f,indent=2)
names=('receive.py','observation.py','monitor.py','launch.py','stop.py','board_preflight.py',
       'board_after.py','board_tools_test.py','trial_tools.py','previous_coordinator.py','test_tools.py','test_supervisor.py')
with (here/'tools-expected.json').open('x') as f:json.dump({n:sha(here/n) for n in names},f,indent=2)
print(json.dumps(row))
