"""One approved same-board monotonic attestation, same-owner v2 bootstrap then log."""
import json
import os
from pathlib import Path
import sys
import time
root=Path(__file__).resolve().parent
os.chdir(root)
row=json.loads((root/'attestation.json').read_text())
assert row.get('heartbeat_negotiation_approved') is True
row['prepared_m3c_monotonic_ns']=time.monotonic_ns()
with (root/'preflight.json').open('x') as f:json.dump(row,f)
with (root/'receiver.pid').open('x') as f:f.write(str(os.getpid()))
env=dict(os.environ,PYTHONPATH=str(root)+':/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages')
os.execve(sys.executable,[sys.executable,'-B',
    '.maixpy/imu-design-20261010/single-uart/controller/uart_session.py',
    '--trial-approved','--negotiate-mavlink2','--preflight','preflight.json',
    '--seconds','60','--output','physical-trial-01'],env)
