"""Supervise only our child; sample /proc before releasing its capture gate."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from trial_tools import proc_sample

def supervise(argv,root,*,timeout=85):
    root=Path(root)
    if os.name!='posix' or not 0<timeout<=85:raise ValueError('Bounded POSIX supervisor only')
    begin=time.monotonic(); child=None; read_fd=write_fd=None; timed_out=False
    with (root/'metrics.jsonl').open('x') as metrics, (root/'receiver-console.txt').open('x') as console:
        def emit(row):metrics.write(json.dumps(row,allow_nan=False)+'\n');metrics.flush()
        def sample():
            proc=Path('/proc')/str(child.pid)
            try:
                row=proc_sample((proc/'stat').read_text(),(proc/'status').read_text(),
                    now_ns=time.monotonic_ns(),clk_tck=os.sysconf('SC_CLK_TCK'),page_size=os.sysconf('SC_PAGE_SIZE'))
                emit(dict(event='receiver_cpu',pid=child.pid,**row))
                return True
            except (FileNotFoundError,ProcessLookupError):
                emit(dict(event='receiver_cpu',receipt_mono_ns=time.monotonic_ns(),pid=child.pid,status='PROCESS_EXITED'))
                return False
        def terminate():
            if child.poll() is None:child.send_signal(signal.SIGTERM)
            try:child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                child.kill();child.wait(timeout=2)
                emit(dict(event='own_child_killed_after_term_timeout',receipt_mono_ns=time.monotonic_ns()))
        try:
            emit(dict(event='monitor_started',receipt_mono_ns=time.monotonic_ns(),uart_opened_by_monitor=False))
            read_fd,write_fd=os.pipe()
            child=subprocess.Popen(argv+['--gate-fd',str(read_fd)],cwd=root,stdout=console,stderr=subprocess.STDOUT,
                pass_fds=(read_fd,))
            os.close(read_fd);read_fd=None
            with (root/'receiver.pid').open('x') as pid:pid.write(str(child.pid))
            if not sample():raise RuntimeError('Child exited before initial metric/gate')
            os.write(write_fd,b'G');os.close(write_fd);write_fd=None
            emit(dict(event='receiver_gate_released',receipt_mono_ns=time.monotonic_ns(),pid=child.pid))
            while child.poll() is None and time.monotonic()-begin<timeout:
                sample();time.sleep(.25)
            if child.poll() is None:timed_out=True;terminate()
            emit(dict(event='receiver_finished',receipt_mono_ns=time.monotonic_ns(),receiver_exit=child.returncode,timed_out=timed_out))
            return dict(receiver_exit=child.returncode,timed_out=timed_out,receiver_alive_after=child.poll() is None)
        finally:
            if child is not None and child.poll() is None:terminate()
            for fd in (read_fd,write_fd):
                if fd is not None:os.close(fd)
