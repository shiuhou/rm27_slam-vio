"""Read-only posttrial UART attrs/owners/source audit; no UART data or settings."""
import glob
import hashlib
import json
import os
from pathlib import Path
import termios
root=Path(__file__).resolve().parent
before=json.loads((root/'board-preflight.json').read_text())
owners=[p for p in glob.glob('/proc/[0-9]*/fd/*') if os.path.exists(p) and os.path.realpath(p)=='/dev/ttyS2']
assert not owners,'Unexpected UART owner; no process killed'
fd=os.open('/dev/ttyS2',os.O_RDONLY|os.O_NOCTTY|os.O_NONBLOCK)
try:attrs=termios.tcgetattr(fd)
finally:os.close(fd)
actual={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in before['source_sha256']}
assert actual==before['source_sha256'],'Tested source changed'
pid_file=root/'receiver.pid'
alive=pid_file.exists() and (Path('/proc')/pid_file.read_text()).exists()
row=dict(owners=owners,termios_after=repr(attrs),termios_unchanged=repr(attrs)==before['termios_before'],
    receiver_process_alive=alive,receiver_output_exists=(root/'physical-trial-01').exists(),
    no_uart_data_read=True,no_tx=True,no_setting_change=True,source_sha256=actual)
assert row['termios_unchanged'] and not alive
with (root/'board-after.json').open('x') as f:json.dump(row,f,indent=2)
print(json.dumps(row))
