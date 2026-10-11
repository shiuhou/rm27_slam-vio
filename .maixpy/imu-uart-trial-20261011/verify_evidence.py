import hashlib
import json
from pathlib import Path
import re
import sys

here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'imu-transport-20261010'))
import rate_control as r
rows=[json.loads(x) for x in (here/'coordinator.jsonl').read_text().splitlines()]
def outputs(command):
    return [rows[i+1]['output'] for i,x in enumerate(rows[:-1]) if x.get('command')==command]
backup=next(x for x in rows if x.get('backup_verified'))
assert any(x.get('stream_mapping_restored') is True for x in rows)
assert rows[-1]==dict(errors=[],finished=True)
assert next(x for x in rows if 'receiver_exit' in x)['receiver_exit']==1
assert {k:v['rate'] for k,v in r.streams(outputs('mavlink status streams')[-1]).items()}==backup['streams']
ps=outputs('ps')[-1]
assert backup['uart'] in ps and backup['logger'] in ps
assert 'Not logging' in outputs('logger status')[-1]
status=outputs('mavlink status')[-1]
assert '/dev/ttyS2 @115200' in status and '/dev/ttyS3 @115200' in status
assert 'Disarmed' in outputs('commander status')[-1]
assert re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',outputs('param show EKF2_EV_CTRL')[-1])
assert outputs('param show SDLOG*')[0]==outputs('param show SDLOG*')[-1]
assert (here/'topics.txt').read_bytes()==(here/'topics-readback.txt').read_bytes()
summary=json.loads((here/'physical-trial-01/summary.json').read_text())
assert summary['termios_restored'] is True and summary['start_accepted'] is False
assert summary['bytes_reassembled']==0 and summary['error']=='invalid MAVLink data: Bad prefix'
report=json.loads((here/'capture-report.json').read_text())
assert report['tx_write_calls']==0 and report['wire_received_bytes']==21
manifest={str(p.relative_to(here)):hashlib.sha256(p.read_bytes()).hexdigest()
    for p in here.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name!='hashes.json'}
with (here/'hashes.json').open('x') as f: json.dump(manifest,f,indent=2)
print('RESTORATION VERIFIED; ACQUISITION FAILED BEFORE START; NO RETRY')
