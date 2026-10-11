"""Read-only hashes of our completed trial outputs; no UART/settings access."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
files=[root/name for name in ('board-after.json','preflight.json','metrics.jsonl',
    'uart-counters.jsonl','receiver-console.txt','receiver.pid','attestation.json')]
files+=sorted((root/'physical-trial-01').glob('*'))
assert all(path.is_file() for path in files)
result=[dict(path=str(path.relative_to(root)),bytes=path.stat().st_size,
    sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in files]
with (root/'artifact-sha256.json').open('x') as output:json.dump(result,output,indent=2)
print(json.dumps(dict(files=len(result),physical_device_access=False)))
