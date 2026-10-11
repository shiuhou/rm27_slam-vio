"""ONE approved negotiated trial; existing tested receiver, independent USB restore.

Adapted workflow from immutable prior coordinator; NEVER run that frozen helper.
No firmware/parameter/wiring/sensor changes or automatic second acquisition.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
HASH='d6f12ad1c4f70ad3230afd7d86e971421e02fef4'
REMOTE='/root/rm27-controller-negotiated-20261011.ffWOSR'
START='mavlink start -d /dev/ttyS2 -b 921600 -r 46080 -m onboard -Z -x'
LOGGER='logger start -b 64 -t -m mavlink -p vehicle_imu'
READ={'ver all','commander status','param show EKF2_EV_CTRL','ps','mavlink status',
      'mavlink status streams','logger status','param show SDLOG*','sensors status',
      'listener vehicle_imu_status -i 0 -n 1','listener cpuload -n 1',
      'uorb top -1 vehicle_imu','ls /fs/microsd','ls /fs/microsd/etc/logging','free'}

def check_command(line,original_uart,original_logger,streams):
    allowed=READ|{'logger stop',LOGGER,'mavlink stop -d /dev/ttyS2',START}
    allowed.update(x for x in (original_uart,original_logger) if x)
    if line in allowed: return
    match=re.fullmatch(r'mavlink stream -d /dev/ttyS2 -s ([A-Z0-9_]+) -r ([0-9.]+)',line)
    if (match and match[1] in streams and streams[match[1]] is not None
            and float(match[2])==streams[match[1]]): return
    raise ValueError('Outside exact backed scope: '+line)

def port_block(text,port,baud):
    blocks=[x for x in re.split(r'instance #\d+:',text) if f'{port} @{baud})' in x
            or f'{port} @{baud}\n' in x or x.rstrip().endswith(f'{port} @{baud}')]
    if len(blocks)!=1: raise ValueError('Unique wired port/baud readback missing')
    return blocks[0]

def sdlog_values(text):
    return {m[1]:int(m[2]) for m in re.finditer(r'\b(SDLOG_[A-Z_]+)[^\r\n:]*:\s*(-?\d+)\b',text)}

def receiver_ok(code,summary):
    return code==0 and summary.get('error') is None and summary.get('termios_restored') is True

def validate_pre_peer(text):
    block=port_block(text,'/dev/ttyS2',921600)
    if (any(s not in block for s in ('46080 B/s','flow control: OFF','mode: Onboard'))
            or not re.search(r'MAVLink version:\s*[12]\s*(?:\n|$)',block)):
        raise ValueError('Temporary wired UART settings differ; version1/2 bootstrap only')
    return block

def negotiated_receiver_ok(code,summary):
    return (receiver_ok(code,summary) and summary.get('negotiate_mavlink2') is True
        and summary.get('mavlink2_negotiation_policy')=='GUARDED_V1_HEARTBEAT_BOOTSTRAP_V1'
        and type(summary.get('negotiation_confirmed_mono_ns')) is int
        and summary['negotiation_confirmed_mono_ns']>=0
        and all(summary.get(k) is True for k in ('finite_framing_verified','start_accepted','stop_accepted')))

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    sys.path.insert(0,str(HERE.parent/'imu-offline-20261008'))
    import bench_io as b
    sys.path.insert(0,str(HERE.parent/'imu-transport-20261010'))
    import rate_control as r
    board=json.loads((HERE/'board-preflight.json').read_text())
    assert board['owners']==[] and board['no_setting_change'] is True
    for name,sha in board['source_sha256'].items():
        if digest(HERE.parents[1]/name)!=sha: raise RuntimeError('Local/deployed source differs')
    evidence=(HERE/'coordinator.jsonl').open('x',encoding='utf-8')
    link=None; dirs=[]; topic_attempted=logger_changed=uart_changed=False
    original_uart=original_logger=None; original_streams={}; sdlog={}; errors=[]
    acquisition_errors=[]; process=None; launched=False; last={}; before_other={}
    def emit(**row):
        row['host_monotonic_s']=time.monotonic()
        evidence.write(json.dumps(row)+'\n'); evidence.flush()
    def cmd(line,seconds=3,cleanup=False):
        check_command(line,original_uart,original_logger,original_streams)
        if not cleanup: link.fresh_disarmed()
        emit(command=line,cleanup=cleanup)
        wire=line+'\n'
        for i in range(0,len(wire),65): link.send_shell(wire[i:i+65])
        parts=[]; deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            msg=link.recv_match(timeout=.1)
            if msg and msg.get_type()=='SERIAL_CONTROL' and msg.count:
                parts.append(bytes(msg.data[:msg.count]).decode('utf-8',errors='replace'))
        out=''.join(parts); emit(output=out); last[line]=out
        print(line,out,flush=True)
        if not cleanup: link.guard()
        if 'nsh: ' in out or 'ERROR' in out or 'Connection timed out' in out:
            raise RuntimeError('Console command failed: '+line)
        return out
    def remote(*args,timeout=20):
        return subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10',
                               'root@10.18.198.1',*args],check=True,timeout=timeout)
    try:
        link=b.Link(); link.fresh_disarmed(); link.send_shell('\n')
        if HASH not in cmd('ver all'): raise RuntimeError('Firmware mismatch')
        if 'Disarmed' not in cmd('commander status'): raise RuntimeError('Not disarmed')
        if not re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',cmd('param show EKF2_EV_CTRL')):
            raise RuntimeError('EV_CTRL mismatch')
        selected=cmd('sensors status')
        if 'selected gyro: 6684690 (0)' not in selected or 'selected accel: 6946834 (0)' not in selected:
            raise RuntimeError('Source selection differs')
        imu=cmd('listener vehicle_imu_status -i 0 -n 1')
        if '6684690' not in imu or '6946834' not in imu: raise RuntimeError('IMU identity differs')
        cmd('listener cpuload -n 1'); cmd('uorb top -1 vehicle_imu'); cmd('free')
        if 'Not logging' not in cmd('logger status'): raise RuntimeError('Existing recording refused')
        ps=cmd('ps')
        uart=re.search(r'(mavlink start -d /dev/ttyS2[^\r\n]*)',ps)
        logger=re.search(r'(logger start[^\r\n]*)',ps)
        if not uart or not logger: raise RuntimeError('Startup backup missing')
        original_uart=uart[1].strip(); original_logger=logger[1].strip()
        if original_uart!='mavlink start -d /dev/ttyS2 -b p:SER_GPS1_BAUD -m p:MAV_1_MODE -r p:MAV_1_RATE -s -x':
            raise RuntimeError('Baseline command differs; no mutation')
        if original_logger!='logger start -b 64 -t -m all': raise RuntimeError('Baseline logger differs')
        before_other={port:re.search(r'(mavlink start -d '+re.escape(port)+r'[^\r\n]*)',ps)[1].strip()
                      for port in ('/dev/ttyS0','/dev/ttyS3','/dev/ttyACM0')}
        status=cmd('mavlink status')
        port_block(status,'/dev/ttyS2',115200); port_block(status,'/dev/ttyS3',115200)
        original_streams={k:v['rate'] for k,v in r.streams(cmd('mavlink status streams',6)).items()}
        sdlog=sdlog_values(cmd('param show SDLOG*'))
        if len(sdlog)!=8: raise RuntimeError('Incomplete SDLOG backup')
        b.ftp(link,'list','/fs/microsd')
        listing=cmd('ls /fs/microsd')
        if re.search(r'^\s*etc/?\s*$',listing,re.M): raise RuntimeError('Existing config needs byte backup; refuse')
        emit(backup_verified=True,uart=original_uart,logger=original_logger,
             streams=original_streams,sdlog=sdlog,topic_original='ABSENT',
             unrelated_uart_commands=before_other,props='USER_CONFIRMED_SAME_BENCH_SESSION')
        for d in ('/fs/microsd/etc','/fs/microsd/etc/logging'):
            b.ftp(link,'mkdir',d,timeout=20); dirs.append(d)
        topic_attempted=True
        b.ftp(link,'put',b.TOPIC_PATH,str(HERE.parent/'imu-uart-trial-20261011/topics.txt'),timeout=20)
        b.ftp(link,'get',b.TOPIC_PATH,str(HERE/'topics-readback.txt'),timeout=20)
        if digest(HERE/'topics-readback.txt')!=digest(HERE.parent/'imu-uart-trial-20261011/topics.txt'):
            raise RuntimeError('Topic readback differs')
        logger_changed=True; cmd('logger stop'); cmd(LOGGER)
        logger_status=cmd('logger status')
        if 'Not logging' not in logger_status or 'mode: mavlink' not in logger_status:
            raise RuntimeError('Temporary logger mode/idle mismatch')
        uart_changed=True; cmd('mavlink stop -d /dev/ttyS2'); cmd(START)
        block=validate_pre_peer(cmd('mavlink status'))
        emit(pre_peer_transport_verified=True,outgoing_version_before_peer=re.search(r'MAVLink version:\s*([12])',block)[1],
             protocol_ready='WAIT_FOR_RECEIVER_VERIFIED_V2_HEARTBEAT_NO_PREMATURE_V2_GATE')
        streams=r.streams(cmd('mavlink status streams',6))
        if any(streams.get(name,{}).get('rate',0)==0 for name in ('HEARTBEAT','SYSTEM_TIME')):
            raise RuntimeError('Health/epoch streams missing')
        row=dict(firmware_hash=HASH,ekf2_ev_ctrl=0,disarmed=True,propellers_removed=True,
            uart='/dev/ttyS2',baud=921600,mavlink_datarate=46080,gyro_device_id=6684690,
            accel_device_id=6946834,vehicle_imu_instance=0,logger_backend='mavlink',
            logger_poll='vehicle_imu',configuration_backup_verified=True,heartbeat_negotiation_approved=True)
        with (HERE/'attestation.json').open('x') as f: json.dump(row,f)
        subprocess.run(['scp',str(HERE/'attestation.json'),'root@10.18.198.1:'+REMOTE+'/attestation.json'],check=True,timeout=20)
        with (HERE/'receiver-console.txt').open('x') as output:
            process=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10',
                'root@10.18.198.1','timeout','-s','TERM','-k','8s','90s','python3','-B',REMOTE+'/launch.py'],
                stdout=output,stderr=subprocess.STDOUT)
            launched=True; begin=time.monotonic(); measured=False
            try:
                while process.poll() is None and time.monotonic()-begin<100:
                    link.recv_match(timeout=.1); link.guard()
                    if not measured and time.monotonic()-begin>=30:
                        emit(observation_window='MID_RUN_IF_RECEIVER_STILL_ACTIVE')
                        cmd('logger status'); cmd('mavlink status'); cmd('listener cpuload -n 1')
                        cmd('uorb top -1 vehicle_imu'); measured=True
                if process.poll() is None: raise RuntimeError('Bounded receiver timeout')
                emit(receiver_exit=process.returncode)
                if process.returncode!=0: acquisition_errors.append('receiver exit '+str(process.returncode))
            finally:
                if process.poll() is None:
                    remote('python3','-B',REMOTE+'/stop.py')
                    process.wait(timeout=15)
        for line in ('logger status','mavlink status','listener cpuload -n 1',
                     'listener vehicle_imu_status -i 0 -n 1','sensors status','uorb top -1 vehicle_imu'):
            cmd(line)
    except BaseException as exc:
        emit(error=type(exc).__name__+': '+str(exc)); errors.append(str(exc))
    finally:
        if launched and process is not None and process.poll() is None:
            try:
                remote('python3','-B',REMOTE+'/stop.py'); process.wait(timeout=15)
            except Exception as exc: errors.append('RECEIVER CLEANUP: '+str(exc)); emit(restore_error=str(exc))
        if link:
            def restore(action):
                try: action()
                except Exception as exc: errors.append('RESTORE: '+str(exc)); emit(restore_error=str(exc))
            if logger_changed: restore(lambda:cmd('logger stop',cleanup=True))
            if topic_attempted: restore(lambda:b.ftp(link,'rm',b.TOPIC_PATH,timeout=20))
            for d in reversed(dirs): restore(lambda d=d:b.ftp(link,'rmdir',d,timeout=20))
            if logger_changed: restore(lambda:cmd(original_logger,cleanup=True))
            if uart_changed:
                restore(lambda:cmd('mavlink stop -d /dev/ttyS2',cleanup=True))
                restore(lambda:cmd(original_uart,cleanup=True))
                for name,rate in original_streams.items():
                    if rate is not None:
                        restore(lambda name=name,rate=rate:cmd(r.command(name,rate),.15,cleanup=True))
                def verify_streams():
                    actual={k:v['rate'] for k,v in r.streams(cmd('mavlink status streams',6,cleanup=True)).items()}
                    if actual!=original_streams: raise RuntimeError('Stream mapping not restored')
                    emit(stream_mapping_restored=True)
                restore(verify_streams)
            for line in ('logger status','mavlink status','ps','param show SDLOG*',
                         'commander status','param show EKF2_EV_CTRL','ls /fs/microsd'):
                restore(lambda line=line:cmd(line,cleanup=True))
            if logger_changed or uart_changed:
                def verify_restore():
                    assert 'Not logging' in last['logger status'] and 'mode: all' in last['logger status']
                    assert original_logger in last['ps'] and original_uart in last['ps']
                    assert all(value in last['ps'] for value in before_other.values())
                    port_block(last['mavlink status'],'/dev/ttyS2',115200)
                    port_block(last['mavlink status'],'/dev/ttyS3',115200)
                    assert sdlog_values(last['param show SDLOG*'])==sdlog
                    assert 'Disarmed' in last['commander status']
                    assert re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',last['param show EKF2_EV_CTRL'])
                    assert not re.search(r'^\s*etc/?\s*$',last['ls /fs/microsd'],re.M)
                    emit(px4_configuration_restored=True)
                restore(verify_restore)
            link.close()
        emit(errors=errors,acquisition_errors=acquisition_errors,finished=True); evidence.close()
    return int(bool(errors or acquisition_errors))

if __name__=='__main__': raise SystemExit(main())
