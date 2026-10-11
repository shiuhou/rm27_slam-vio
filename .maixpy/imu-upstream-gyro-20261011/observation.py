"""Stock-firmware observation guards and offline diagnostics; never VIO admission."""
from bisect import bisect_left,bisect_right
import math
from statistics import median

def bandwidth():
    demand=(700*49+200*65)*267/249+3000
    return dict(sensor_gyro_ulog_bytes=49,vehicle_imu_ulog_bytes=65,
        gyro_model_hz=700,imu_model_hz=200,diagnostic_reserve_Bps=3000,
        estimated_wire_Bps=demand,uart_8n1_Bps=921600/10,
        temporary_link_budget_Bps=80000,evidence='ENGINEERING_ESTIMATE_NOT_MEASUREMENT')

def validate_observation(row,now_ns):
    import uart_session as u
    for key,value in dict(mavlink_datarate=80000,observation='UPSTREAM_GYRO0').items():
        if type(row.get(key)) is not type(value) or row[key]!=value:
            raise ValueError('different observation profile: '+key)
    # Explicit composition: validate ACTUAL new budget above, then reuse all
    # unchanged safety/source/reader/freshness guards. Never rewrite evidence.
    base=dict(row,mavlink_datarate=46080)
    u.validate_preflight(base,now_ns,negotiate_mavlink2=True,logger_reader='fixed_2500hz')

def source_windows(imu,gyro):
    if len(imu)<2 or len(gyro)<3:raise ValueError('insufficient retained observations')
    it=[r['timestamp_sample'] for r in imu];gt=[r['timestamp_sample'] for r in gyro]
    for rows,times in ((imu,it),(gyro,gt)):
        if any(type(t) is not int or t<=0 for t in times) or any(b<=a for a,b in zip(times,times[1:])):
            raise ValueError('unordered/invalid sample timestamps')
        pt=[r['timestamp'] for r in rows]
        if any(b<=a for a,b in zip(pt,pt[1:])):raise ValueError('unordered publication timestamps')
    identity=(6684690,6946834,imu[0]['gyro_calibration_count'],imu[0]['accel_calibration_count'])
    for r in imu:
        if (r['gyro_device_id'],r['accel_device_id'],r['gyro_calibration_count'],r['accel_calibration_count'])!=identity:
            raise ValueError('IMU source/calibration epoch changed')
        if type(r['delta_angle_dt']) is not int or r['delta_angle_dt']<=0:raise ValueError('invalid own gyro dt')
    for r in gyro:
        if r['device_id']!=6684690 or type(r['samples']) is not int or not 1<=r['samples']<=32:
            raise ValueError('gyro source/batch identity differs')
        if not all(math.isfinite(r[k]) for k in ('x','y','z')):raise ValueError('nonfinite SI gyro')
    periods=[b-a for a,b in zip(gt,gt[1:])];cadence=median(periods)
    holes=[]
    for idx,(a,b) in enumerate(zip(imu,imu[1:]),1):
        residual=b['timestamp_sample']-a['timestamp_sample']-b['delta_angle_dt']
        if residual<=2:continue
        start=a['timestamp_sample'];end=b['timestamp_sample']-b['delta_angle_dt']
        lo=bisect_right(gt,start)-1;hi=bisect_left(gt,end)
        bracketed=lo>=0 and hi<len(gt)
        intervals=[gt[j+1]-gt[j] for j in range(max(lo,0),min(hi,len(gt)-1))]
        gaps=[dict(before=gt[j],after=gt[j+1],interval_us=gt[j+1]-gt[j])
              for j in range(max(lo,0),min(hi,len(gt)-1)) if gt[j+1]-gt[j]>1.5*cadence]
        label=('UNKNOWN_UNBRACKETED' if not bracketed else
               'UPSTREAM_CADENCE_GAP_OBSERVED' if gaps else 'LOCALLY_INTACT_CADENCE')
        holes.append(dict(row_before=idx-1,row_after=idx,uncovered_us=residual,
            uncovered_interval_us=[start,end],source_samples_inside=bisect_right(gt,end)-bisect_right(gt,start),
            upstream_observation=label,bracketed=bracketed,source_intervals_us=intervals,source_gaps=gaps))
    return dict(imu_records=len(imu),gyro_records=len(gyro),
        imu_effective_hz=(len(imu)-1)*1e6/(it[-1]-it[0]),
        gyro_effective_hz=(len(gyro)-1)*1e6/(gt[-1]-gt[0]),gyro_median_interval_us=cadence,
        gyro_max_interval_us=max(periods),gyro_large_interval_events=sum(p>1.5*cadence for p in periods),
        gyro_batch_sizes=sorted(set(r['samples'] for r in gyro)),
        gyro_retained_error_counts=sorted(set(r['error_count'] for r in gyro)),holes=holes,
        exact_trigger='UNKNOWN',logger_gap_attribution='AGGREGATE_TWO_FULL_RATE_TOPICS',
        source_complete='UNKNOWN',accel_coverage='UNKNOWN_NO_SEPARATE_ENDPOINT',
        tail_complete='UNKNOWN',clock_synchronization='UNKNOWN',openvins_admissible=False,stage_c='CLOSED')
