"""Read-only identity/source/owner/attributes audit; no UART data read/TX/change."""
import glob
import hashlib
import json
import os
from pathlib import Path
import platform
import termios

root=Path(__file__).resolve().parent
tested=json.loads((root/'environment.json').read_text())
actual={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in tested['source_sha256']}
assert actual==tested['source_sha256'],'Previously tested runtime source changed'
tests=(root/'tool-tests-02.txt').read_text()
assert 'Ran 13 tests' in tests and '\nOK\n' in tests and 'PythonExit=0' in tests and 'skipped=' not in tests
owners=[p for p in glob.glob('/proc/[0-9]*/fd/*') if os.path.exists(p) and os.path.realpath(p)=='/dev/ttyS2']
consoles=Path('/proc/consoles').read_text()
assert not owners,'UART occupied; no process killed'
assert not any(line.split()[0]=='ttyS2' for line in consoles.splitlines()),'Console refused'
assert platform.node()==tested['hostname'] and hasattr(termios,'B921600')
assert not (root/'physical-trial-01').exists(),'Preserve previous output'
fd=os.open('/dev/ttyS2',os.O_RDONLY|os.O_NOCTTY|os.O_NONBLOCK)
try:attrs=termios.tcgetattr(fd)
finally:os.close(fd)
row=dict(hostname=platform.node(),source_sha256=actual,owners=owners,consoles=consoles,
    termios_before=repr(attrs),b921600=termios.B921600,no_data_read=True,no_tx=True,no_setting_change=True,
    board_test_sha256=hashlib.sha256((root/'tool-tests-02.txt').read_bytes()).hexdigest())
with (root/'board-preflight.json').open('x') as f:json.dump(row,f,indent=2)
print(json.dumps(row))
