"""Read-only board identity, source and UART owner/attributes check. No reads/TX."""
import glob
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import sys
import termios

root = Path('/root/rm27-controller-startup-pty-20261011.Jg12Lv')
expected = json.loads((root/'retry-expected-environment.json').read_text())
actual = {name:hashlib.sha256((root/name).read_bytes()).hexdigest()
          for name in expected['source_sha256']}
owners = [p for p in glob.glob('/proc/[0-9]*/fd/*')
          if os.path.exists(p) and os.path.realpath(p)=='/dev/ttyS2']
consoles = Path('/proc/consoles').read_text()
assert not owners, 'UART occupied; no process killed'
assert not any(line.split()[0]=='ttyS2' for line in consoles.splitlines()), 'system console'
assert actual == expected['source_sha256'], 'deployed source changed'
assert hasattr(termios,'B921600'), 'termios baud unavailable'
assert not (root/'physical-trial-02').exists(), 'preserve existing trial'
fd = os.open('/dev/ttyS2',os.O_RDONLY|os.O_NOCTTY|os.O_NONBLOCK)
try:
    attrs = termios.tcgetattr(fd)
finally:
    os.close(fd)
import numpy, pymavlink, pyulog
row = dict(hostname=platform.node(),architecture=platform.machine(),python=sys.version,
           versions=dict(numpy=numpy.__version__,pymavlink=pymavlink.__version__,pyulog=version('pyulog')),
           source_sha256=actual,owners=owners,consoles=consoles,termios_before=repr(attrs),
           b921600=termios.B921600,no_data_read=True,no_tx=True,no_setting_change=True)
assert row['hostname']==expected['hostname'] and row['architecture']==expected['architecture']
assert row['versions']==expected['versions'], 'environment differs from tested deployment'
with (root/'retry-board-preflight.json').open('x') as f:
    json.dump(row,f,indent=2)
print(json.dumps(row))
