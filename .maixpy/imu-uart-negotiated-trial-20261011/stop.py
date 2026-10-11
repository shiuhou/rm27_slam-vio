"""Emergency TERM ONLY own exact receiver PID; never kill another UART owner."""
import os
from pathlib import Path
import signal
root=Path(__file__).resolve().parent
pid=int((root/'receiver.pid').read_text())
proc=Path('/proc')/str(pid)
if proc.exists():
    argv=(proc/'cmdline').read_bytes().split(b'\0')
    assert b'.maixpy/imu-design-20261010/single-uart/controller/uart_session.py' in argv
    assert b'physical-trial-01' in argv and b'--negotiate-mavlink2' in argv
    assert os.path.realpath(proc/'cwd')==str(root)
    os.kill(pid,signal.SIGTERM)
    print('TERM_SENT_TO_OWN_RECEIVER',pid)
else:print('OWN_RECEIVER_ALREADY_EXITED',pid)
