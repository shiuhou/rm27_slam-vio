"""One read-only /proc CPU/memory observation of OUR receiver; no UART access."""
import json
import os
from pathlib import Path
import sys
import time
root=Path(__file__).resolve().parent
label=sys.argv[1]
assert label in ('during-01','during-02')
pid_path=root/'receiver.pid'
row=dict(receipt_mono_ns=time.monotonic_ns(),clk_tck=os.sysconf('SC_CLK_TCK'),
         memory=Path('/proc/meminfo').read_text(),system_cpu=Path('/proc/stat').read_text().splitlines()[0],
         uart_access=False)
if pid_path.exists():
    pid=int(pid_path.read_text()); proc=Path('/proc')/str(pid)
    if proc.exists():
        argv=(proc/'cmdline').read_bytes().split(b'\0')
        assert b'.maixpy/imu-design-20261010/single-uart/controller/uart_session.py' in argv
        assert os.path.realpath(proc/'cwd')==str(root)
        stat=(proc/'stat').read_text(); fields=stat[stat.rfind(')')+2:].split()
        row.update(pid=pid,utime_ticks=int(fields[11]),stime_ticks=int(fields[12]),
                   starttime_ticks=int(fields[19]),status=(proc/'status').read_text(),receiver_alive=True)
    else:row['receiver_alive']=False
else:row['receiver_alive']=False
with (root/(label+'.json')).open('x') as f:json.dump(row,f,indent=2)
print(json.dumps(row))
