"""Read-only post-run owner/attrs check; no read of UART data or TX/settings."""
import glob
import json
import os
from pathlib import Path
import termios

root=Path('/root/rm27-controller-startup-pty-20261011.Jg12Lv')
owners=[p for p in glob.glob('/proc/[0-9]*/fd/*')
        if os.path.exists(p) and os.path.realpath(p)=='/dev/ttyS2']
assert not owners, 'Unexpected UART owner; no process killed'
fd=os.open('/dev/ttyS2',os.O_RDONLY|os.O_NOCTTY|os.O_NONBLOCK)
try: attrs=termios.tcgetattr(fd)
finally: os.close(fd)
before=json.loads((root/'retry-board-preflight.json').read_text())
row=dict(owners=owners,termios_after=repr(attrs),
         termios_unchanged=repr(attrs)==before['termios_before'],
         receiver_output_exists=(root/'physical-trial-02').exists(),
         receiver_pid_file_exists=(root/'retry-receiver.pid').exists(),
         actual_preflight_exists=(root/'retry-preflight.json').exists(),
         no_uart_data_read=True,no_tx=True,no_setting_change=True)
assert row['termios_unchanged'] and not row['receiver_output_exists']
assert not row['receiver_pid_file_exists'] and not row['actual_preflight_exists']
with (root/'retry-board-after.json').open('x') as f: json.dump(row,f,indent=2)
print(json.dumps(row))
