"""Offline independent check of this pre-receiver abort and exact restoration."""
import hashlib
import json
from pathlib import Path
import re
import sys
import coordinator as c

here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'imu-transport-20261010'))
import rate_control as r
rows=[json.loads(line) for line in (here/'coordinator.jsonl').read_text().splitlines()]
backup=next(row for row in rows if row.get('backup_verified'))
def outputs(command):
    return [rows[i+1]['output'] for i,row in enumerate(rows[:-1]) if row.get('command')==command]
assert rows[-1]['errors']==['Temporary wired UART readback mismatch']
assert rows[-1]['acquisition_errors']==[] and rows[-1]['finished'] is True
assert not any('receiver_exit' in row for row in rows)
assert any(row.get('stream_mapping_restored') is True for row in rows)
assert any(row.get('px4_configuration_restored') is True for row in rows)
for row in rows:
    if 'command' in row: c.check_command(row['command'],backup['uart'],backup['logger'],backup['streams'])
assert {name:info['rate'] for name,info in r.streams(outputs('mavlink status streams')[-1]).items()}==backup['streams']
assert c.sdlog_values(outputs('param show SDLOG*')[-1])==backup['sdlog']
ps=outputs('ps')[-1]
assert backup['uart'] in ps and backup['logger'] in ps
assert all(value in ps for value in backup['unrelated_uart_commands'].values())
assert 'Not logging' in outputs('logger status')[-1] and 'mode: all' in outputs('logger status')[-1]
c.port_block(outputs('mavlink status')[-1],'/dev/ttyS2',115200)
c.port_block(outputs('mavlink status')[-1],'/dev/ttyS3',115200)
assert 'Disarmed' in outputs('commander status')[-1]
assert re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',outputs('param show EKF2_EV_CTRL')[-1])
assert not re.search(r'^\s*etc/?\s*$',outputs('ls /fs/microsd')[-1],re.M)
assert (here/'topics-readback.txt').read_bytes()==(here.parent/'imu-uart-trial-20261011/topics.txt').read_bytes()
after=json.loads((here/'board-after.json').read_text())
assert after['termios_unchanged'] is True and after['owners']==[]
assert not after['receiver_output_exists'] and not after['receiver_pid_file_exists']
assert not (here/'receiver-console.txt').exists() and not (here/'attestation.json').exists()
old_manifest=json.loads((here.parent/'imu-uart-trial-20261011/hashes.json').read_text())
for name,sha in old_manifest.items():
    assert hashlib.sha256((here.parent/'imu-uart-trial-20261011'/name).read_bytes()).hexdigest()==sha,name
frozen=here.parent/'imu-design-20261010/single-uart/reassembly'
manifest=json.loads((frozen/'manifest.json').read_text())['files']
for item in manifest:
    assert hashlib.sha256((frozen/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
board=json.loads((here/'board-preflight.json').read_text())
for name,sha in board['source_sha256'].items():
    assert hashlib.sha256((here.parents[1]/name).read_bytes()).hexdigest()==sha,name
stage=here.parent/'mavlink2-20261010/VALIDATION.md'
assert hashlib.sha256(stage.read_bytes()).hexdigest()=='d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
result=dict(restoration_verified=True,receiver_launched=False,accepted_capture_seconds=0,
    received_imu_records=0,absence_not_loss_measurement=True,preflight_abort='MAVLINK2_READINESS_ORDER_ERROR',
    old_trial_hashes_verified=len(old_manifest),frozen_reassembly_hashes_verified=len(manifest),
    deployed_source_files_verified=len(board['source_sha256']),
    stage_ab_report_sha256=hashlib.sha256(stage.read_bytes()).hexdigest(),
    transport_status='NOT_MEASURED',source_rate_qualification='PARTIAL_197HZ_ONE_SECOND_SNAPSHOT',
    clock_status='UNKNOWN',openvins_status='NOT_ADMITTED')
with (here/'verification.json').open('x') as f: json.dump(result,f,indent=2)
print(json.dumps(result))
