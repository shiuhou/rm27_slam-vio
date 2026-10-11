"""One fresh same-board attestation and exec; timeout is provided by coordinator."""
import json
import os
from pathlib import Path
import sys
import time

root = Path('/root/rm27-controller-startup-pty-20261011.Jg12Lv')
os.chdir(root)
row = json.loads((root/'retry-attestation.json').read_text())
row['prepared_m3c_monotonic_ns'] = time.monotonic_ns()
with (root/'retry-preflight.json').open('x') as f:
    json.dump(row,f)
with (root/'retry-receiver.pid').open('x') as f:
    f.write(str(os.getpid()))
env = dict(os.environ)
env['PYTHONPATH'] = str(root/'research-lib')+':/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages'
os.execve(sys.executable,[sys.executable,
    '.maixpy/imu-design-20261010/single-uart/controller/uart_session.py',
    '--trial-approved','--preflight','retry-preflight.json',
    '--seconds','60','--output','physical-trial-02'],env)
