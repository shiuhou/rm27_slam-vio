"""ONE finite instrumented physical trial; supervisor stops only its receiver."""
import os
from pathlib import Path
import sys
from monitor import supervise

root=Path(__file__).resolve().parent
os.chdir(root)
sys.path.insert(0,'/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages')
os.environ['PYTHONPATH']=str(root)+':/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages'
result=supervise([sys.executable,'-B',str(root/'receive.py')],root,timeout=85)
print(result,flush=True)
raise SystemExit(result['receiver_exit'] or int(result['timed_out']))
