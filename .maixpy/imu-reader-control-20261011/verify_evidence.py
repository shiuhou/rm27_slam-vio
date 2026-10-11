"""Independent offline scope/restoration and original-row comparison verification."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
import coordinator as c
from compare import comparison

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((HERE/name).read_text(encoding='utf-8-sig'))
def jsonl(name):return [json.loads(x) for x in (HERE/name).read_text().splitlines()]

def main():
    rows=jsonl('coordinator.jsonl')
    backup=next(x for x in rows if x.get('backup_verified'))
    factor=next(x for x in rows if 'treatment' in x)
    def output(command):return [rows[i+1]['output'] for i,x in enumerate(rows[:-1]) if x.get('command')==command]
    assert rows[-1]['finished'] and rows[-1]['errors']==rows[-1]['acquisition_errors']==[]
    assert [x['receiver_exit'] for x in rows if 'receiver_exit' in x]==[0]
    assert any(x.get('stream_mapping_restored') for x in rows)
    assert any(x.get('px4_configuration_restored') for x in rows)
    assert factor['treatment']==c.t.treatment(factor['temporary_streams_before_treatment'])
    intended={k:v for k,v in factor['temporary_streams_before_treatment'].items() if k not in factor['treatment']}
    assert next(x for x in rows if x.get('reduced_telemetry_readback_verified'))['actual_streams']==intended
    commands=[x['command'] for x in rows if 'command' in x]
    for line in commands:c.check_command(line,backup['uart'],backup['logger'],backup['streams'],factor['treatment'])
    assert commands.count(c.START)==commands.count(c.LOGGER)==1 and c.c.LOGGER not in commands
    assert next(x for x in rows if x.get('logger_reader_readback_verified'))['logger_command']==c.LOGGER
    assert c.HASH in output('ver all')[0]
    assert c.t.stream_table(output('mavlink status streams')[-1])==backup['streams']
    assert c.c.sdlog_values(output('param show SDLOG*')[-1])==backup['sdlog']
    ps=output('ps')[-1]
    assert backup['uart'] in ps and backup['logger'] in ps
    assert all(x in ps for x in backup['unrelated_uart_commands'].values())
    assert 'Not logging' in output('logger status')[-1] and 'mode: all' in output('logger status')[-1]
    restored=c.c.port_block(output('mavlink status')[-1],'/dev/ttyS2',115200)
    assert all(x in restored for x in ('5760 B/s','flow control: OFF','mode: Onboard'))
    flow=c.c.port_block(output('mavlink status')[-1],'/dev/ttyS3',115200)
    assert all(x in flow for x in ('compid: 88','msgid:  132','msgid:  106'))
    assert 'Disarmed' in output('commander status')[-1]
    assert re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',output('param show EKF2_EV_CTRL')[-1])
    assert not re.search(r'^\s*etc/?\s*$',output('ls /fs/microsd')[-1],re.M)
    assert (HERE/'topics-readback.txt').read_bytes()==(HERE.parent/'imu-uart-trial-20261011/topics.txt').read_bytes()
    modes=[int(x) for x in re.findall(r'FC_HEARTBEAT\s+[0-9.]+\s+(\d+)',(HERE/'coordinator-console.txt').read_text(encoding='utf-16'))]
    assert modes and all(x==29 for x in modes)
    before=read('board-preflight.json');after=read('download/board-after.json');expected=read('expected.json')
    assert before['owners']==after['owners']==[] and after['receiver_process_alive'] is False
    assert after['termios_unchanged'] and after['termios_after']==before['termios_before']
    assert before['source_sha256']==after['source_sha256']==expected['source_sha256']
    for name,digest in expected['source_sha256'].items():assert sha(ROOT/name)==digest,name
    tests=(HERE/'tool-tests-02.txt').read_text()
    assert 'Ran 13 tests' in tests and '\nOK\n' in tests and 'PythonExit=0' in tests and 'skipped=' not in tests
    for name,count in [('board-guard-tests-02.txt',8),('board-compare-tests-02.txt',7),('board-runner-tests-02.txt',15),('board-pty-tests-02.txt',5)]:
        txt=(HERE/name).read_text(encoding='utf-16');assert f'Ran {count} tests' in txt and '\nOK\n' in txt and 'SSHExit=0' in txt and 'skipped=' not in txt
    transfers=read('download/artifact-sha256.json')
    for row in transfers:
        local=HERE/'attestation.json' if row['path']=='attestation.json' else HERE/'download'/row['path']
        assert local.stat().st_size==row['bytes'] and sha(local)==row['sha256'],row['path']
    sys.path.insert(0,str(HERE.parent/'imu-design-20261010/single-uart/controller'))
    from capture_report import audit_capture
    from ulog_mavlink import inspect_imu,decoder_module
    import analyze
    audit=audit_capture(HERE/'download/physical-trial-01',epoch=analyze.EPOCH)
    assert audit==read('capture-audit.json')
    summary=audit['session'];assert summary['error'] is None and summary['finite_framing_verified']
    assert summary['start_accepted'] and summary['stop_accepted'] and summary['termios_restored']
    assert summary['negotiate_mavlink2'] and summary['state']=='DONE'
    raw=(HERE/'download/physical-trial-01/received-prefix.bin').read_bytes()
    assert raw==(HERE/'download/physical-trial-01/framing-valid.ulg').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==summary['received_prefix_sha256']
    wire=jsonl('download/physical-trial-01/wire.jsonl')
    tx=[decoder_module.Decoder().feed(bytes.fromhex(x['wire_hex']),x['receipt_mono_ns'])[0] for x in wire if x.get('event')=='tx_write']
    assert all(x['crc_status']=='VERIFIED' and x['mavlink_version']==2 and (x['sysid'],x['compid'])==(1,191) for x in tx)
    assert {x['type'] for x in tx}=={'HEARTBEAT','COMMAND_LONG','LOGGING_ACK'}
    control=[x for x in tx if x['type']=='COMMAND_LONG']
    assert [x['fields']['command'] for x in control]==[2510,2511]
    assert all((x['fields']['target_system'],x['fields']['target_component'])==(1,1) and all(x['fields']['param'+str(i)]==0 for i in range(1,8)) for x in control)
    normal=[x for x in wire if x.get('event')=='frame' and x['type']=='LOGGING_DATA']
    span=(normal[-1]['receipt_mono_ns']-normal[0]['receipt_mono_ns'])/1e9
    assert span>=60 and (control[-1]['receipt_mono_ns']-summary['normal_data_start_mono_ns'])/1e9>=60
    analysis=read('analysis.json')
    assert analysis['excluded_partial_bytes']==0 and analysis['raw_prefix_sha256']==hashlib.sha256(raw).hexdigest()
    frames=[x for x in wire if x.get('event')=='frame' and (x.get('sysid'),x.get('compid'))==(1,1)]
    checked=[analyze.link_diagnostics.verify_unknown_frame(x) for x in frames if x.get('crc_status')!='VERIFIED']
    assert checked==analysis['unknown_frames_verified'] and len(frames)==analysis['px4_frames']
    assert analyze.wire_gaps(wire)==analysis['wire']
    counters=analyze.link_diagnostics.correlate(frames);assert counters==analysis['link_counters']
    metrics=jsonl('download/metrics.jsonl');assert analyze.cpu_summary(metrics)==analysis['cpu']
    counts=jsonl('download/uart-counters.jsonl');assert counts==analysis['uart_counters']
    actual=inspect_imu(raw,instance=0,gyro_device=6684690,accel_device=6946834,epoch='INDEPENDENT_DIAGNOSTIC_ONLY')
    baseline=HERE.parent/'imu-uart-reduced-trial-20261011/download/physical-trial-01/framing-valid.ulg'
    old=inspect_imu(baseline.read_bytes(),instance=0,gyro_device=6684690,accel_device=6946834,epoch='INDEPENDENT_BASELINE')
    original_rows=[x['original'] for x in actual['diagnostic_means']]
    compared=comparison([x['original'] for x in old['diagnostic_means']],original_rows,analysis['retained_status_records']['logger_status'])
    assert compared==read('comparison.json')==analysis['comparison']
    assert not compared['openvins_admissible'] and compared['stage_c']=='CLOSED'
    # AST review: ONLY validator changed; no parser/owner/STOP code changes.
    def unchanged_nodes(path):return [ast.dump(n) for n in ast.parse(path.read_text(encoding='utf-8')).body if not isinstance(n,ast.FunctionDef) or n.name!='validate_preflight']
    guard=ROOT/'.maixpy/imu-design-20261010/single-uart/controller/uart_session.py'
    assert unchanged_nodes(guard)==unchanged_nodes(HERE/'repo-before/uart_session.py')
    stage=sha(HERE.parent/'mavlink2-20261010/VALIDATION.md')
    assert stage=='d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
    result=dict(single_physical_trial_no_retry=True,command_scope_verified=True,restoration_verified=True,
        logger_reader=c.LOGGER,observed_heartbeat_count=len(modes),observed_base_modes=sorted(set(modes)),
        ekf2_ev_ctrl=0,px4_uart_restored='115200/5760B_s/Onboard/flow_OFF',exact_stream_map_restored=True,
        logger_idle_all=True,sdlog_restored=backup['sdlog'],original_custom_config_absent=True,
        m3c_exact_termios_restored=True,m3c_no_owner=True,source_files_verified=len(expected['source_sha256']),
        board_tests_pass=48,board_skips=0,remote_local_hashes_verified=len(transfers),stage_ab_sha256=stage,
        core_runtime_change='ONLY_validate_preflight_AST_VERIFIED',
        normal_LOGGING_DATA_receipt_span_s=span,normal_start_to_stop_write_s=(control[-1]['receipt_mono_ns']-summary['normal_data_start_mono_ns'])/1e9,
        transport_observed_sequence_gaps=len(analysis['wire']['mavlink_sequence_discontinuities']),
        transport_observed_logging_gaps=len(analysis['wire']['logging_discontinuities']),
        source_gyro_continuity=compared['observed_gyro_continuity'],subscription_counter_increment=compared['candidate_logger']['counter_increment_events'],
        retained_hz=compared['candidate']['retained_hz'],original_rate_gate_pass=compared['original_rate_gate_pass'],
        source_complete='UNKNOWN',tail_complete='UNKNOWN',clock_synchronization='UNKNOWN',
        transport_qualified=False,openvins_admissible=False,stage_c='CLOSED')
    with (HERE/'verification.json').open('x',encoding='utf-8') as out:json.dump(result,out,indent=2,allow_nan=False)
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
