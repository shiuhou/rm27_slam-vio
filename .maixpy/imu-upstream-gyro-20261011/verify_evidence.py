"""Independent offline scope/restoration and upstream gyro verification."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
import coordinator as c
from observation import source_windows

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
    assert rows[-1]['finished'] and rows[-1]['errors']==[]
    assert rows[-1]['acquisition_errors']==['receiver exit 1']
    assert [x['receiver_exit'] for x in rows if 'receiver_exit' in x]==[1]
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
    assert (HERE/'topics-readback.txt').read_bytes()==(HERE/'topics.txt').read_bytes()
    modes=[int(x) for x in re.findall(r'FC_HEARTBEAT\s+[0-9.]+\s+(\d+)',(HERE/'coordinator-console.txt').read_text(encoding='utf-16'))]
    assert modes and all(x==29 for x in modes)
    before=read('board-preflight.json');after=read('download/board-after.json');expected=read('expected.json')
    assert before['owners']==after['owners']==[] and after['receiver_process_alive'] is False
    assert after['termios_unchanged'] and after['termios_after']==before['termios_before']
    assert before['source_sha256']==after['source_sha256']==expected['source_sha256']
    for name,digest in expected['source_sha256'].items():assert sha(ROOT/name)==digest,name
    tests=(HERE/'tool-tests-02.txt').read_text()
    assert 'Ran 13 tests' in tests and '\nOK\n' in tests and 'PythonExit=0' in tests and 'skipped=' not in tests
    for name,count in [('board-observation-tests.txt',6),('board-scope-tests.txt',3),('board-pty-tests.txt',5)]:
        txt=(HERE/name).read_text(encoding='utf-16')
        assert f'Ran {count} tests' in txt and '\nOK\n' in txt and 'skipped=' not in txt,name
    transfers=read('download/artifact-sha256.json')
    for row in transfers:
        local=HERE/'attestation.json' if row['path']=='attestation.json' else HERE/'download'/row['path']
        assert local.stat().st_size==row['bytes'] and sha(local)==row['sha256'],row['path']
    sys.path.insert(0,str(HERE.parent/'imu-design-20261010/single-uart/controller'))
    from capture_report import audit_capture
    from ulog_mavlink import inspect_imu,decoder_module
    import analyze_failure as analyze
    audit=audit_capture(HERE/'download/physical-trial-01',epoch='D6F12AD1_FAILED_UPSTREAM_GYRO_TRANSITION')
    analysis=read('failure-analysis.json')
    assert audit==analysis['audit']
    summary=audit['session']
    assert summary['error']=='logging sequence discontinuity: expected 287, received 288'
    assert summary['finite_framing_verified'] is False
    assert summary['start_accepted'] and summary['stop_accepted'] and summary['termios_restored']
    assert summary['negotiate_mavlink2'] and summary['state']=='DONE'
    raw=(HERE/'download/physical-trial-01/received-prefix.bin').read_bytes()
    assert not (HERE/'download/physical-trial-01/framing-valid.ulg').exists()
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
    assert span<1 and analysis['accepted_normal_window_s']==0
    assert analysis['excluded_partial_bytes']==24 and analysis['raw_prefix_sha256']==hashlib.sha256(raw).hexdigest()
    frames=[x for x in wire if x.get('event')=='frame' and (x.get('sysid'),x.get('compid'))==(1,1)]
    checked=[analyze.link.verify_unknown_frame(x) for x in frames if x.get('crc_status')!='VERIFIED']
    assert checked==analysis['unknown_frames_verified'] and len(frames)==analysis['wire']['px4_frames']
    assert analyze.wire_gaps(wire)==analysis['wire']
    counters=analyze.link.correlate(frames);assert counters==analysis['link_counters']
    attributed=[x for x in counters['intervals'] if x['tx_rejected_delta']]
    assert len(attributed)==1 and attributed[0]['tx_rejected_delta']==1
    assert attributed[0]['verdict']=='ATTRIBUTED_PX4_TX_BUFFER_REJECTION_INTERVAL'
    assert all(x['unaccounted_successful_sends']==0 for x in counters['intervals'])
    metrics=jsonl('download/metrics.jsonl');assert analyze.cpu_summary(metrics)==analysis['cpu']
    counts=jsonl('download/uart-counters.jsonl');assert counts==analysis['uart_counters']
    view,excluded=analyze.complete_record_view(raw)
    assert excluded==24 and len(view)==71202
    _,log=analyze.validate_ulog(view)
    gyros=[{key:values[i].item() for key,values in d.data.items()}
        for d in log.data_list if d.name=='sensor_gyro' and d.multi_id==0 for i in range(len(d.data['timestamp']))]
    imus=[d for d in log.data_list if d.name=='vehicle_imu' and d.multi_id==0]
    assert len(imus)==1 and len(imus[0].data['timestamp'])==1
    assert analysis['measured_imu_hz'] is None
    assert analysis['gyro_hole_correlation']=='NOT_OBSERVED_INSUFFICIENT_RETAINED_IMU'
    assert analysis['logger_gap_attribution']=='AGGREGATE_TWO_FULL_RATE_TOPICS'
    assert len(gyros)==4 and {r['device_id'] for r in gyros}=={6684690}
    full=[(line.split()[0],line.split()[2]) for line in (HERE/'topics.txt').read_text().splitlines() if line.split()[1]=='0']
    assert full==[('vehicle_imu','0'),('sensor_gyro','0')]
    stage=sha(HERE.parent/'mavlink2-20261010/VALIDATION.md')
    assert stage=='d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
    result=dict(single_physical_trial_no_retry=True,command_scope_verified=True,restoration_verified=True,
        logger_reader=c.LOGGER,observed_heartbeat_count=len(modes),observed_base_modes=sorted(set(modes)),
        ekf2_ev_ctrl=0,px4_uart_restored='115200/5760B_s/Onboard/flow_OFF',exact_stream_map_restored=True,
        logger_idle_all=True,sdlog_restored=backup['sdlog'],original_custom_config_absent=True,
        m3c_exact_termios_restored=True,m3c_no_owner=True,source_files_verified=len(expected['source_sha256']),
        board_tests_pass=27,board_skips=0,remote_local_hashes_verified=len(transfers),stage_ab_sha256=stage,
        core_runtime_change='NONE_BYTE_IDENTICAL_TO_READER_CONTROL',
        failure=summary['error'],normal_LOGGING_DATA_RECEIVED_span_s=span,accepted_normal_window_s=0,
        normal_start_to_stop_write_s=(control[-1]['receipt_mono_ns']-summary['normal_data_start_mono_ns'])/1e9,
        transport_observed_sequence_gaps=len(analysis['wire']['mavlink_sequence_discontinuities']),
        transport_observed_logging_gaps=len(analysis['wire']['logging_discontinuities']),
        matched_tx_rejection_events=1,unaccounted_successful_sends=0,
        source_gyro_holes='UNKNOWN_INSUFFICIENT_WINDOW',upstream_gyro_hz=None,
        retained_hz=None,original_rate_gate='NOT_QUALIFIED_FAILED_SESSION',
        source_complete='UNKNOWN',tail_complete='UNKNOWN',clock_synchronization='UNKNOWN',
        transport_qualified=False,openvins_admissible=False,stage_c='CLOSED')
    with (HERE/'verification.json').open('x',encoding='utf-8') as out:json.dump(result,out,indent=2,allow_nan=False)
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
