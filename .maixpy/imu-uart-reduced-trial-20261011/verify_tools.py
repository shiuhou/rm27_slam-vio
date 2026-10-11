"""Read-only deployed tool parity, no device access or settings change."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
expected = json.loads((root/'tools-expected.json').read_text(encoding='utf-8-sig'))
actual = {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in expected}
assert actual == expected, 'New deployed scope/monitor tools differ from local tested files'
row = dict(tool_sha256=actual, tools_verified=len(actual), physical_device_access=False)
with (root/'tools-parity.json').open('x', encoding='utf-8') as output:
    json.dump(row, output, indent=2)
print(json.dumps(row))
