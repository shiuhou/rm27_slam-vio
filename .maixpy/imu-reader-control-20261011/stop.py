"""Signal ONLY our exact wrapper PID/cwd; never another UART owner."""
import os
from pathlib import Path
import signal
root=Path(__file__).resolve().parent
pid=int((root/'receiver.pid').read_text())
proc=Path('/proc')/str(pid)
if proc.exists():
    argv=(proc/'cmdline').read_bytes().split(b'\0')
    assert str(root/'receive.py').encode() in argv and b'--gate-fd' in argv
    assert os.path.realpath(proc/'cwd')==str(root)
    os.kill(pid,signal.SIGTERM)
    print('TERM_SENT_TO_OWN_RECEIVER',pid)
else:print('OWN_RECEIVER_ALREADY_EXITED',pid)
