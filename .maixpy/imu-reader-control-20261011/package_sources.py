"""Generate exclusive second software snapshot; no device access."""
import hashlib
import json
from pathlib import Path
import subprocess

here=Path(__file__).resolve().parent
root=here.parents[1]
archive=here/'controller-source-03.tar.gz'
assert not archive.exists()
subprocess.run(['tar','-czf',str(archive),'-T',str(here/'source-list.txt')],cwd=root,check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
row=dict(source_sha256={name:sha(root/name) for name in (here/'source-list.txt').read_text().splitlines()},
    source_archive_sha256=sha(archive),
    pyulog_archive_sha256=sha(root/'.maixpy/controller-m3c-pty-20261011/pyulog-1.2.4.tar.gz'))
with (here/'expected-02.json').open('x',encoding='utf-8') as f:json.dump(row,f,indent=2)
print(json.dumps(row))
