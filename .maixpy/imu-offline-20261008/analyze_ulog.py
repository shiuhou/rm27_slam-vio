"""Offline evidence analysis; preserves original ULog. No repair/resampling."""
import hashlib
import json
import sys
import zlib
from pathlib import Path
import numpy as np

def timing(timestamps):
    t=np.asarray(timestamps).astype(np.int64)
    d=np.diff(t)
    positive=d[d>0]
    median=float(np.median(positive)) if len(positive) else None
    gaps=d[d>1.5*median] if median else np.array([])
    return dict(count=len(t),first_us=int(t[0]) if len(t) else None,
        last_us=int(t[-1]) if len(t) else None,
        span_s=float((t[-1]-t[0])/1e6) if len(t)>1 else 0,
        effective_hz=float((len(t)-1)*1e6/(t[-1]-t[0])) if len(t)>1 and t[-1]>t[0] else None,
        median_dt_us=median,min_dt_us=int(d.min()) if len(d) else None,
        max_dt_us=int(d.max()) if len(d) else None,
        p95_dt_us=float(np.percentile(d,95)) if len(d) else None,
        nonincreasing=int(np.sum(d<=0)),duplicates=int(np.sum(d==0)),
        gaps_over_1_5_median=len(gaps),
        estimated_missing_from_time_gaps=int(np.maximum(np.rint(gaps/median)-1,0).sum()) if median else None)

def expand_fifo(data):
    times=[]; values=[]
    for k,n in enumerate(data['samples']):
        n=int(n)
        if not 1<=n<=32: raise ValueError('Invalid FIFO sample count')
        dt=float(data['dt'][k]); scale=float(data['scale'][k])
        if not np.isfinite(dt) or dt<=0 or not np.isfinite(scale) or scale<=0:
            raise ValueError('Invalid FIFO dt/scale')
        for i in range(n):
            times.append(int(data['timestamp_sample'][k])-(n-1-i)*dt)
            values.append([int(data[f'{axis}[{i}]'][k])*scale for axis in 'xyz'])
    return np.asarray(times),np.asarray(values)

def analyze(path):
    from pyulog import ULog
    b=Path(path).read_bytes(); u=ULog(path)
    result=dict(file=str(path),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),
        crc32=f'{zlib.crc32(b):08x}',file_corruption=bool(u.file_corruption),
        start_us=int(u.start_timestamp),end_us=int(u.last_timestamp),
        duration_s=(u.last_timestamp-u.start_timestamp)/1e6,
        dropout_events=len(u.dropouts),dropout_duration_ms_sum=int(sum(x.duration for x in u.dropouts)),
        dropout_duration_ms_max=int(max([x.duration for x in u.dropouts],default=0)),
        topics={},safety={},notes=[
            'Time-gap missing counts are estimates, not hardware sequence counters.',
            'FIFO expansion assumes driver last-sample anchor; no sample repair.',
            'Dropout durations can be millisecond-quantized; sum is not a sensor loss fraction.',
            'No camera synchronization, noise calibration or live-transport qualification.'])
    for dataset in u.data_list:
        d=dataset.data; key=f'{dataset.name}:{dataset.multi_id}'
        r=dict(records=len(d['timestamp']),fields=list(d.keys()))
        if dataset.name.startswith('sensor_') and 'timestamp_sample' in d:
            r['sample_time']=timing(d['timestamp_sample'])
            r['publish_time']=timing(d['timestamp'])
            delay=d['timestamp'].astype(np.int64)-d['timestamp_sample'].astype(np.int64)
            r['publish_minus_sample_us']=dict(min=int(delay.min()),median=float(np.median(delay)),max=int(delay.max()))
            r['device_ids']=[int(x) for x in np.unique(d['device_id'])]
            r['sample_counts']={str(x):int(np.sum(d['samples']==x)) for x in np.unique(d['samples'])}
            if dataset.name.endswith('_fifo'):
                t,x=expand_fifo(d)
                r['expanded_sample_time']=timing(t)
                r['scale_values']=[float(x) for x in np.unique(d['scale'])]
                r['dt_values_us']=[float(x) for x in np.unique(d['dt'])]
                r['nonfinite_values']=int(np.sum(~np.isfinite(x)))
                norms=np.linalg.norm(x,axis=1)
                r['si_vector_mean']=np.mean(x,axis=0).tolist()
                r['si_norm']=dict(mean=float(np.mean(norms)),min=float(np.min(norms)),max=float(np.max(norms)))
                r['int16_rail_values']=sum(int(np.sum(np.abs(d[f'{axis}[{i}]'].astype(np.int64)[d['samples']>i])>=32767)) for axis in 'xyz' for i in range(32))
            else:
                r['error_counts']=[int(x) for x in np.unique(d.get('error_count',[]))]
                r['clip_counter_totals']={k:int(v.sum()) for k,v in d.items() if k.startswith('clip_counter')}
                r['nonfinite_values']=sum(int(np.sum(~np.isfinite(d[k]))) for k in ('x','y','z'))
        if dataset.name=='actuator_armed':
            result['safety']['actuator_armed_values']=[bool(x) for x in np.unique(d['armed'])]
        if dataset.name=='vehicle_status':
            result['safety']['arming_state_values']=[int(x) for x in np.unique(d['arming_state'])]
        if dataset.name=='vehicle_imu_status':
            r['health_ranges']={k:[float(v.min()),float(v.max())] for k,v in d.items() if any(s in k for s in ['error','clipping','rate','device_id'])}
        result['topics'][key]=r
    gyro=u.get_dataset('sensor_gyro_fifo',1).data
    accel=u.get_dataset('sensor_accel_fifo',1).data
    common,gi,ai=np.intersect1d(gyro['timestamp_sample'],accel['timestamp_sample'],return_indices=True)
    result['fifo_pairing']=dict(common_batch_timestamps=len(common),gyro_only=len(gyro['timestamp_sample'])-len(common),
        accel_only=len(accel['timestamp_sample'])-len(common),equal_sample_counts=int(np.sum(gyro['samples'][gi]==accel['samples'][ai])))
    result['si_fifo_consistency']={}
    for name,fifo in [('gyro',gyro),('accel',accel)]:
        si=u.get_dataset('sensor_'+name,1).data
        _,fi,si_idx=np.intersect1d(fifo['timestamp_sample'],si['timestamp_sample'],return_indices=True)
        nominal=float(np.median(np.diff(fifo['timestamp_sample'].astype(np.int64))))
        errors=[]
        for f,s in zip(fi,si_idx):
            if f==0 or fifo['timestamp_sample'][f]-fifo['timestamp_sample'][f-1]>1.5*nominal: continue
            n=int(fifo['samples'][f]); prevn=int(fifo['samples'][f-1])
            expected=[]
            for axis in 'xyz':
                prev=int(fifo[f'{axis}[{prevn-1}]'][f-1]); last=int(fifo[f'{axis}[{n-1}]'][f])
                total=sum(int(fifo[f'{axis}[{i}]'][f]) for i in range(n-1))
                expected.append((.5*(prev+last)+total)*float(fifo['scale'][f])/n)
            errors.append(np.max(np.abs(np.array(expected)-[si[axis][s] for axis in 'xyz'])))
        result['si_fifo_consistency'][name]=dict(checked_batches=len(errors),max_abs_error_si=float(max(errors)) if errors else None)
    result['sdlog_initial_parameters']={k:v for k,v in u.initial_parameters.items() if k.startswith('SDLOG_')}
    result['changed_parameter_count']=len(u.changed_parameters)
    return result

if __name__=='__main__':
    print(json.dumps(analyze(sys.argv[1]),indent=2,allow_nan=False))
