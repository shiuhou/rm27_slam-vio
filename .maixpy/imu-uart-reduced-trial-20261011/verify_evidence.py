"""Independent offline scope/restoration/raw replay check, no device access."""
import hashlib
import json
from pathlib import Path
import re
import sys

import trial_tools as t
from trial_analysis import cpu_summary

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REPORT_BACKUPS={'HANDOFF.md':'HANDOFF.md','VAULT_UPDATE.md':'VAULT_UPDATE.md',
    'new_plan.md':'new_plan.md','.maixpy/README.md':'README.md',
    '.maixpy/imu-design-20261010/LATEST.md':'LATEST.md',
    'rm27/perception/vision/docs/CODEX_RESUME.md':'CODEX_RESUME.md'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    rows=[json.loads(x) for x in (HERE/'coordinator.jsonl').read_text().splitlines()]
    backup=next(x for x in rows if x.get('backup_verified'))
    factor=next(x for x in rows if 'treatment' in x)
    def output(command):return [rows[i+1]['output'] for i,x in enumerate(rows[:-1]) if x.get('command')==command]
    assert rows[-1]['finished'] and rows[-1]['errors']==rows[-1]['acquisition_errors']==[]
    assert [x['receiver_exit'] for x in rows if 'receiver_exit' in x]==[0]
    assert any(x.get('stream_mapping_restored') for x in rows)
    assert any(x.get('px4_configuration_restored') for x in rows)
    assert factor['treatment']==t.treatment(factor['temporary_streams_before_treatment'])
    intended={k:v for k,v in factor['temporary_streams_before_treatment'].items() if k not in factor['treatment']}
    assert next(x for x in rows if x.get('reduced_telemetry_readback_verified'))['actual_streams']==intended
    for x in rows:
        if 'command' in x:t.check_command(x['command'],backup['uart'],backup['logger'],backup['streams'],factor['treatment'])
    commands=[x['command'] for x in rows if 'command' in x]
    assert commands.count(t.old.START)==commands.count(t.old.LOGGER)==1
    assert t.old.HASH in output('ver all')[0]
    assert t.stream_table(output('mavlink status streams')[-1])==backup['streams']
    assert t.old.sdlog_values(output('param show SDLOG*')[-1])==backup['sdlog']
    ps=output('ps')[-1]
    assert backup['uart'] in ps and backup['logger'] in ps
    assert all(x in ps for x in backup['unrelated_uart_commands'].values())
    assert 'Not logging' in output('logger status')[-1] and 'mode: all' in output('logger status')[-1]
    restored=t.old.port_block(output('mavlink status')[-1],'/dev/ttyS2',115200)
    assert all(x in restored for x in ('5760 B/s','flow control: OFF','mode: Onboard'))
    flow=t.old.port_block(output('mavlink status')[-1],'/dev/ttyS3',115200)
    assert all(x in flow for x in ('compid: 88','msgid:  132','msgid:  106'))
    assert 'Disarmed' in output('commander status')[-1]
    assert re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',output('param show EKF2_EV_CTRL')[-1])
    assert not re.search(r'^\s*etc/?\s*$',output('ls /fs/microsd')[-1],re.M)
    assert (HERE/'topics-readback.txt').read_bytes()==(HERE.parent/'imu-uart-trial-20261011/topics.txt').read_bytes()
    modes=[int(x) for x in re.findall(r'FC_HEARTBEAT\s+[0-9.]+\s+(\d+)',
        (HERE/'coordinator-console.txt').read_text(encoding='utf-16'))]
    assert modes and all(x==29 for x in modes)
    before=json.loads((HERE/'board-preflight.json').read_text())
    after=json.loads((HERE/'download/board-after.json').read_text())
    assert before['owners']==after['owners']==[] and after['receiver_process_alive'] is False
    assert after['termios_unchanged'] and after['termios_after']==before['termios_before']
    expected=json.loads((HERE/'expected.json').read_text())
    assert before['source_sha256']==after['source_sha256']==expected['source_sha256']
    for name,digest in expected['source_sha256'].items():assert sha(ROOT/name)==digest,name
    tests=(HERE/'tool-tests-02.txt').read_text()
    assert 'Ran 13 tests' in tests and '\nOK\n' in tests and 'PythonExit=0' in tests and 'skipped=' not in tests
    transfers=json.loads((HERE/'download/artifact-sha256.json').read_text())
    for row in transfers:
        local=HERE/'download'/row['path'] if row['path']!='attestation.json' else HERE/row['path']
        assert local.stat().st_size==row['bytes'] and sha(local)==row['sha256'],row['path']
    sys.path.insert(0,str(HERE.parent/'imu-design-20261010/single-uart/controller'))
    from capture_report import audit_capture
    from ulog_mavlink import inspect_imu,decoder_module
    capture=HERE/'download/physical-trial-01'
    audit=audit_capture(capture,epoch='D6F12AD1_REDUCED_TELEMETRY_REAL_UART_TRIAL')
    assert audit==json.loads((HERE/'capture-audit.json').read_text())
    summary=audit['session'];assert summary['error'] is None and summary['finite_framing_verified']
    assert summary['start_accepted'] and summary['stop_accepted'] and summary['termios_restored']
    assert summary['negotiate_mavlink2'] and summary['state']=='DONE'
    raw=(capture/'received-prefix.bin').read_bytes()
    assert raw==(capture/'framing-valid.ulg').read_bytes() and sha(capture/'received-prefix.bin')==summary['received_prefix_sha256']
    wire=[json.loads(x) for x in (capture/'wire.jsonl').read_text().splitlines()]
    tx=[decoder_module.Decoder().feed(bytes.fromhex(x['wire_hex']),x['receipt_mono_ns'])[0]
        for x in wire if x.get('event')=='tx_write']
    assert all(x['crc_status']=='VERIFIED' and x['mavlink_version']==2 and
        (x['sysid'],x['compid'])==(1,191) for x in tx)
    assert {x['type'] for x in tx}=={'HEARTBEAT','COMMAND_LONG','LOGGING_ACK'}
    control=[x for x in tx if x['type']=='COMMAND_LONG']
    assert [x['fields']['command'] for x in control]==[2510,2511]
    assert all((x['fields']['target_system'],x['fields']['target_component'])==(1,1) and
        all(x['fields']['param'+str(i)]==0 for i in range(1,8)) for x in control)
    normal=[x for x in wire if x.get('event')=='frame' and x.get('type')=='LOGGING_DATA']
    span=(normal[-1]['receipt_mono_ns']-normal[0]['receipt_mono_ns'])/1e9
    assert span>=60 and (control[-1]['receipt_mono_ns']-summary['normal_data_start_mono_ns'])/1e9>=60
    analysis=json.loads((HERE/'analysis-02.json').read_text())
    assert analysis['excluded_partial_bytes']==0 and analysis['raw_prefix_sha256']==sha(capture/'received-prefix.bin')
    assert not analysis['wire']['mavlink_sequence_discontinuities'] and not analysis['wire']['logging_discontinuities']
    assert analysis['all_retained_px4_frames_crc_verified'] and analysis['px4_frames']==5001
    assert len(analysis['unknown_frames_verified'])==96
    intervals=analysis['link_counters']['intervals'];snapshots=analysis['link_counters']['snapshots']
    assert len(intervals)==64 and all(x['tx_rejected_delta']==x['unaccounted_successful_sends']==0 for x in intervals)
    assert snapshots[0]['tx_overflows']==snapshots[-1]['tx_overflows']==0
    assert snapshots[0]['receipt_mono_ns']<control[0]['receipt_mono_ns']
    assert snapshots[-1]['receipt_mono_ns']>normal[-1]['receipt_mono_ns']
    metrics=[json.loads(x) for x in (HERE/'download/metrics.jsonl').read_text().splitlines()]
    assert cpu_summary(metrics)==analysis['cpu'] and analysis['cpu']['first_sample_before_gate']
    counts=analysis['uart_counters'];assert len(counts)==2 and all(x['status']=='MEASURED' for x in counts)
    assert all(counts[1][key]==counts[0][key] for key in ('frame','overrun','parity','brk','buf_overrun'))
    imu=inspect_imu(raw,instance=0,gyro_device=6684690,accel_device=6946834,epoch='INDEPENDENT_DIAGNOSTIC_ONLY')
    assert imu['count']==11843 and not imu['openvins_admissible']
    originals=[x['original'] for x in imu['diagnostic_means']]
    values={k:sorted(set(x[k] for x in originals)) for k in ('gyro_device_id','accel_device_id',
        'gyro_calibration_count','accel_calibration_count','delta_angle_clipping','delta_velocity_clipping')}
    gaps=[x for x in imu['gyro_coverage_residual_us'] if x>2]
    assert len(gaps)==1 and sum(gaps)==4554 and imu['source_intervals']['effective_hz']<200
    gap_index=next(i+1 for i,x in enumerate(imu['gyro_coverage_residual_us']) if x>2)
    gap_before,gap_after=originals[gap_index-1],originals[gap_index]
    statuses=analysis['retained_status_records']['logger_status']
    changes=[(a,b) for a,b in zip(statuses,statuses[1:]) if b['message_gaps']!=a['message_gaps']]
    assert len(changes)==1
    a,b=changes[0]
    assert (a['message_gaps'],b['message_gaps'])==(1,2)
    assert a['timestamp']<gap_before['timestamp']<gap_after['timestamp']<b['timestamp']
    topic_lines=(HERE/'topics-readback.txt').read_text().splitlines()
    assert [x.split()[0] for x in topic_lines if x.split()[1]=='0']==['vehicle_imu']
    frozen={}
    for dirname in ('imu-gap-diagnosis-20261011','imu-uart-negotiated-trial-20261011',
                    'imu-uart-retry-20261011','imu-negotiation-fix-20261011','imu-design-20261010/single-uart/reassembly'):
        directory=HERE.parent/dirname
        manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8-sig'))
        for e in manifest['files']:assert sha(directory/e['path'])==e['sha256'],dirname+':'+e['path']
        frozen[dirname]=len(manifest['files'])
        if dirname=='imu-gap-diagnosis-20261011':
            for e in manifest['external_files']:
                path=HERE/'repo-before'/REPORT_BACKUPS[e['path']] if e['path'] in REPORT_BACKUPS else ROOT/e['path']
                assert sha(path)==e['sha256'],e['path']
    original=json.loads((HERE.parent/'imu-uart-trial-20261011/hashes.json').read_text())
    for name,digest in original.items():assert sha(HERE.parent/'imu-uart-trial-20261011'/name)==digest
    frozen['original_trial']=len(original)
    stage=sha(HERE.parent/'mavlink2-20261010/VALIDATION.md')
    assert stage=='d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
    result=dict(single_physical_trial_no_retry=True,command_scope_verified=True,restoration_verified=True,
        px4_uart='115200/5760B_s/Onboard/flow_OFF',px4_stream_map_restored=True,logger_idle_all=True,
        sdlog_restored=backup['sdlog'],original_custom_config_absent=True,m3c_exact_termios_restored=True,
        m3c_no_owner=True,unrelated_uart_and_flow_preserved=True,observed_heartbeat_count=len(modes),
        observed_base_modes=sorted(set(modes)),disarmed=True,ekf2_ev_ctrl=0,
        source_files_verified=len(expected['source_sha256']),board_new_tools_tests=13,board_skips=0,
        remote_local_hashes_verified=len(transfers),frozen_artifacts_verified=frozen,stage_ab_sha256=stage,
        treatment_disabled_numerical_streams=len(factor['treatment']),retained_streams=intended,
        finite_framing_verified=True,normal_LOGGING_DATA_receipt_span_s=span,
        normal_start_to_stop_write_s=(control[-1]['receipt_mono_ns']-summary['normal_data_start_mono_ns'])/1e9,
        transport_comparison='VERIFIED_60S_NO_OBSERVED_REJECTION_OR_SEQUENCE_GAP_IN_THIS_TREATMENT',
        tx_counter_intervals_verified=len(intervals),successful_writes_accounted=sum(x['tx_success_delta'] for x in intervals),
        source_identity_calibration_clip_values=values,gyro_coverage_gap_events=len(gaps),gyro_coverage_gap_us=sum(gaps),
        source_rate_qualification='FAILED_ORIGINAL_200HZ_GATE',source_complete='UNKNOWN',tail_complete='UNKNOWN',
        clock_synchronization='UNKNOWN',transport_qualified=False,openvins_admissible=False,stage_c='CLOSED')
    result['logger_generation_gap_context']=dict(before=a,after=b,gyro_hole_before=gap_before,
        gyro_hole_after=gap_after,full_rate_custom_topics=['vehicle_imu'],
        attribution='LOGGER_VEHICLE_IMU_SUBSCRIPTION_GENERATION_SKIP_NOT_UART_PACKET_LOSS',
        exact_hardware_missing_sample_count='UNKNOWN',precise_scheduling_trigger='UNKNOWN')
    # Preserve the first completed verifier snapshot; this adds source-gap context.
    with (HERE/'verification-02.json').open('x',encoding='utf-8') as out:json.dump(result,out,indent=2,allow_nan=False)
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
