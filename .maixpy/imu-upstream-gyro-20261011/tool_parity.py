"""Read-only deployed-tool parity, exclusive local report; no UART access."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
expected=json.loads((root/'tools-expected.json').read_text())
actual={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in expected}
assert actual==expected,'Root deployed tool bytes differ'
with (root/'tools-parity.json').open('x') as f:json.dump(dict(tool_sha256=actual),f,indent=2)
print(json.dumps(actual))
