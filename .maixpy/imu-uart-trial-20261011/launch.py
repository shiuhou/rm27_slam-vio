"""One launch, attestation timestamp generated in the actual M3C clock domain."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path('/root/rm27-controller-pty-20261011.zUIWou')
os.chdir(root)
row = json.loads((root/'trial-attestation.json').read_text())
row['prepared_m3c_monotonic_ns'] = time.monotonic_ns()
with (root/'trial-preflight.json').open('x') as f:
    json.dump(row, f)
env = dict(os.environ)
env['PYTHONPATH'] = str(root/'research-lib')+':/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages'
raise SystemExit(subprocess.call([sys.executable,
    '.maixpy/imu-design-20261010/single-uart/controller/uart_session.py',
    '--trial-approved', '--preflight', 'trial-preflight.json',
    '--seconds', '60', '--output', 'physical-trial-01'], env=env))
