"""Independent saved-data arithmetic, source pins and frozen-before-state audit."""
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
from pyulog import ULog

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TRIAL=HERE.parent/'imu-uart-reduced-trial-20261011'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports={'HANDOFF.md':'HANDOFF.md','VAULT_UPDATE.md':'VAULT_UPDATE.md','new_plan.md':'new_plan.md',
    '.maixpy/README.md':'README.md','.maixpy/imu-design-20261010/LATEST.md':'LATEST.md',
    'rm27/perception/vision/docs/CODEX_RESUME.md':'CODEX_RESUME.md'}

def main():
    frozen=json.loads((TRIAL/'manifest.json').read_text(encoding='utf-8'))
    for entry in frozen['files']:assert sha(TRIAL/entry['path'])==entry['sha256'],entry['path']
    for entry in frozen['external_files']:
        path=HERE/'repo-before'/reports[entry['path']] if entry['path'] in reports else ROOT/entry['path']
        assert sha(path)==entry['sha256'],entry['path']
    assert sha(TRIAL/'manifest.json')=='4998a984647f0be93fba98b099b26c471c0b3916e6a90e7a74122baa9c45f6fd'
    pins=json.loads((HERE.parent/'px4-v117-source-audit-20261009/source-validation.json').read_text(encoding='utf-8'))['manifest']['new']
    source_dir=HERE.parent/'px4-v117-source-audit-20261009/source/new'
    checked={}
    for name in ('src/modules/sensors/vehicle_imu/VehicleIMU.cpp',
        'src/modules/sensors/vehicle_imu/VehicleIMU.hpp','src/modules/logger/logger.cpp',
        'src/modules/logger/logged_topics.cpp','platforms/common/uORB/uORBDeviceNode.hpp',
        'platforms/common/uORB/uORBDeviceNode.cpp','platforms/common/uORB/SubscriptionCallback.hpp',
        'msg/SensorGyro.msg','msg/SensorAccel.msg'):
        source=source_dir/name.replace('/','__')
        assert sha(source)==pins[name]['sha256'],name
        assert '/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/' in pins[name]['url']
        checked[str(source.relative_to(ROOT))]=sha(source)
    other={'imu-transport-20261010': ['src__modules__sensors__Integrator.hpp'],
        'imu-design-20261010':['BMI088_Gyroscope.cpp','BMI088_Accelerometer.cpp'],
        'imu-input-20261010':['msg__VehicleImu.msg']}
    # These sources are already in frozen dated manifests; no downloads.
    for folder,names in other.items():
        directory=HERE.parent/folder
        if folder=='imu-input-20261010':
            path=directory/names[0]
            assert 'ORB_QUEUE_LENGTH' not in path.read_text(encoding='utf-8')
        else:
            entries=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
            for name in names:
                entry=next(x for x in entries if x['path']==name)
                assert sha(directory/name)==entry['sha256']
        for name in names:checked[str((directory/name).relative_to(ROOT))]=sha(directory/name)
    writer=HERE.parent/'imu-uart-negotiated-trial-20261011/source/log_writer_mavlink.cpp'
    assert sha(writer)=='ae48cc6de1cbfc0edefc0f15c37b2886472caa66f49d4b817a47607eddd35131'
    checked[str(writer.relative_to(ROOT))]=sha(writer)
    raw=TRIAL/'download/physical-trial-01/framing-valid.ulg'
    log=ULog(str(raw));assert not log.file_corruption and not log.dropouts
    assert raw.read_bytes()==(raw.parent/'received-prefix.bin').read_bytes()
    d=log.get_dataset('vehicle_imu',0).data
    sample=d['timestamp_sample'].astype(np.int64)
    publication=d['timestamp'].astype(np.int64)
    dt=d['delta_angle_dt'].astype(np.int64)
    residual=np.diff(sample)-dt[1:]
    holes=np.flatnonzero(residual>2)+1
    assert holes.tolist()==[8092] and residual[8091]==4554 and np.count_nonzero(residual < -2)==0
    assert np.all(np.diff(sample)>0) and np.all(np.diff(publication)>0)
    assert int(sample[-1]-sample[0])==60046056
    assert int(dt[1:].sum())==60041502
    assert int(d['delta_velocity_dt'][1:].astype(np.int64).sum())==60040750
    result=json.loads((HERE/'analysis.json').read_text(encoding='utf-8'))
    assert result['cadence']['count']==len(sample)==11843
    assert result['cadence']['retained_hz']==(len(sample)-1)*1e6/(int(sample[-1])-int(sample[0]))
    assert result['cadence']['large_endpoint_intervals']==np.count_nonzero(np.diff(sample)>1.5*np.median(np.diff(sample)))==271
    status=log.get_dataset('vehicle_imu_status',0).data
    period=1e6/float(np.median(status['accel_rate_hz']))
    inferred=np.floor(d['delta_velocity_dt']/period+.5).astype(int)
    assert {str(n):int(np.count_nonzero(inferred==n)) for n in np.unique(inferred)}==result['accel_period_model']['counts']
    assert int(np.maximum(inferred-4,0).sum())==749
    assert int(np.count_nonzero(inferred>4))==298
    assert not log.changed_parameters and log.initial_parameters['IMU_INTEG_RATE']==200
    logger=log.get_dataset('logger_status',0).data
    changes=np.flatnonzero(np.diff(logger['message_gaps'].astype(np.int64)))
    assert len(changes)==1
    i=int(changes[0]);assert (int(logger['message_gaps'][i]),int(logger['message_gaps'][i+1]))==(1,2)
    assert int(logger['timestamp'][i])<int(publication[8091])<int(publication[8092])<int(logger['timestamp'][i+1])
    assert int(sample[8092])-int(dt[8092])==17284907185
    assert set(map(int,d['gyro_device_id']))=={6684690} and set(map(int,d['accel_device_id']))=={6946834}
    assert set(map(int,d['gyro_calibration_count']))==set(map(int,d['accel_calibration_count']))=={1}
    assert not np.any(d['delta_angle_clipping']) and not np.any(d['delta_velocity_clipping'])
    wire=[json.loads(x) for x in (raw.parent/'wire.jsonl').read_text(encoding='utf-8').splitlines()]
    normal=[r for r in wire if r.get('event')=='frame' and r.get('type')=='LOGGING_DATA']
    acked=[r for r in wire if r.get('event')=='frame' and r.get('type')=='LOGGING_DATA_ACKED']
    assert not [r for r in acked if normal[0]['receipt_mono_ns']<r['receipt_mono_ns']<normal[-1]['receipt_mono_ns']]
    # Reuse completed byte replay and LINK/CRC analysis after establishing exact state.
    previous=json.loads((TRIAL/'analysis-02.json').read_text(encoding='utf-8'))
    assert previous['raw_prefix_sha256']==sha(raw) and previous['px4_frames']==5001
    assert not previous['wire']['mavlink_sequence_discontinuities'] and not previous['wire']['logging_discontinuities']
    assert len(previous['link_counters']['intervals'])==64
    assert all(x['tx_rejected_delta']==x['unaccounted_successful_sends']==0 for x in previous['link_counters']['intervals'])
    coordinator=[json.loads(x) for x in (TRIAL/'coordinator.jsonl').read_text(encoding='utf-8').splitlines()]
    tops=[r['output'] for r in coordinator if 'output' in r and 'uorb top -1 vehicle_imu' in r['output']]
    observed=[int(re.search(r'vehicle_imu\s+0\s+\d+\s+(\d+)\s+1\s+64',x)[1]) for x in tops]
    assert observed==[198,195,198]
    stage=sha(HERE.parent/'mavlink2-20261010/VALIDATION.md')
    assert stage=='d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f'
    verified=dict(scope='ENTIRELY_OFFLINE_NO_NEW_DEVICE_ACCESS',
        frozen_own_files=len(frozen['files']),frozen_external_files=len(frozen['external_files']),
        frozen_manifest_sha256=sha(TRIAL/'manifest.json'),raw_sha256=sha(raw),
        exact_source_hashes_verified=checked,stage_ab_sha256=stage,
        independent_arithmetic='VERIFIED',saved_uorb_one_second_rates=observed,
        gyro_hole_us=4554,gyro_hole_interval_us=[17284902631,17284907185],
        actual_generation_magnitude='UNKNOWN',precise_run_logger_scheduling_trigger='UNKNOWN',
        no_reliable_acked_packets_during_normal_stream=True,
        original_minimum_hz=200,rate_gate_pass=False,source_complete='UNKNOWN',
        tail_complete='UNKNOWN',clock_status='UNKNOWN',openvins_admissible=False,stage_c='CLOSED')
    with (HERE/'verification.json').open('x',encoding='utf-8') as output:json.dump(verified,output,indent=2,allow_nan=False)
    print(json.dumps(dict(frozen_own_files=80,frozen_external_files=36,source_hashes=len(checked),
        arithmetic='VERIFIED',stage_ab_unchanged=True,stage_c='CLOSED')))

if __name__=='__main__':main()
