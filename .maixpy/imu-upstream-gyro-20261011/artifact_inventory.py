"""Exclusive hash/size inventory of this deployment's existing evidence only."""
import hashlib
import json
from pathlib import Path
import re

root=Path(__file__).resolve().parent
assert re.fullmatch(r'/root/rm27-controller-gyro-20261011\.[A-Za-z0-9]{6}',str(root))
paths=sorted((root/'physical-trial-01').glob('*'))
paths += [root/n for n in ('attestation.json','preflight.json','metrics.jsonl',
    'uart-counters.jsonl','board-after.json')]
assert paths and all(p.is_file() and not p.is_symlink() for p in paths)
rows=[dict(path=p.relative_to(root).as_posix(),bytes=p.stat().st_size,
    sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]
with (root/'artifact-sha256.json').open('x') as f:json.dump(rows,f,indent=2)
print(json.dumps(rows))
