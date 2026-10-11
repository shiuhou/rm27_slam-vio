"""Approved single trial. Scoped runtime changes with independent USB restoration."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'imu-offline-20261008'))
import bench_io as b
sys.path.insert(0,str(HERE.parent/'imu-transport-20261010'))
import rate_control as r
HASH = 'd6f12ad1c4f70ad3230afd7d86e971421e02fef4'
REMOTE = '/root/rm27-controller-pty-20261011.zUIWou'
START = 'mavlink start -d /dev/ttyS2 -b 921600 -r 46080 -m onboard -Z -x'
READ = {'ver all','commander status','param show EKF2_EV_CTRL','ps',
        'mavlink status','mavlink status streams','logger status','param show SDLOG*',
        'sensors status','listener vehicle_imu_status -i 0 -n 1',
        'listener cpuload -n 1','uorb top -1 vehicle_imu',
        'ls /fs/microsd','ls /fs/microsd/etc/logging'}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    evidence = (HERE/'coordinator.jsonl').open('x',encoding='utf-8')
    link = None
    dirs = []
    topic_attempted = logger_changed = uart_changed = False
    original_streams = {}
    original_uart = original_logger = None
    errors = []
    def emit(**row):
        evidence.write(json.dumps(row)+'\n'); evidence.flush()
    def cmd(s, seconds=3, cleanup=False):
        allowed = READ | {'logger stop','logger start -b 64 -t -m mavlink -p vehicle_imu',
                          'mavlink stop -d /dev/ttyS2',START,original_uart,original_logger}
        stream = re.fullmatch(r'mavlink stream -d /dev/ttyS2 -s ([A-Z0-9_]+) -r ([0-9.]+)',s)
        if s not in allowed and not (stream and stream[1] in original_streams
            and original_streams[stream[1]] is not None
            and float(stream[2]) == original_streams[stream[1]]):
            raise ValueError('Outside exact backed scope: '+s)
        if not cleanup: link.fresh_disarmed()
        emit(command=s,cleanup=cleanup)
        # SERIAL_CONTROL payload is70 bytes; split one shell line, never shell chaining.
        wire=s+'\n'
        for i in range(0,len(wire),65): link.send_shell(wire[i:i+65])
        output=[]; deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            message=link.recv_match(timeout=.1)
            if message and message.get_type()=='SERIAL_CONTROL' and message.count:
                output.append(bytes(message.data[:message.count]).decode('utf-8',errors='replace'))
        out=''.join(output); emit(output=out)
        print(s, out, flush=True)
        if not cleanup: link.guard()
        if 'nsh: ' in out or 'ERROR' in out: raise RuntimeError('Console command failed: '+s)
        return out
    try:
        link=b.Link(); link.fresh_disarmed(); link.send_shell('\n')
        if HASH not in cmd('ver all'): raise RuntimeError('Firmware mismatch')
        if 'Disarmed' not in cmd('commander status'): raise RuntimeError('Not disarmed')
        if not re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',cmd('param show EKF2_EV_CTRL')):
            raise RuntimeError('EV_CTRL mismatch')
        selected=cmd('sensors status')
        if 'selected gyro: 6684690 (0)' not in selected or 'selected accel: 6946834 (0)' not in selected:
            raise RuntimeError('Sensor selection mismatch')
        imu=cmd('listener vehicle_imu_status -i 0 -n 1')
        if '6946834' not in imu or '6684690' not in imu: raise RuntimeError('IMU instance mismatch')
        cmd('listener cpuload -n 1'); cmd('uorb top -1 vehicle_imu')
        if 'Not logging' not in cmd('logger status'): raise RuntimeError('Existing recording; refuse')
        ps=cmd('ps')
        uart=re.search(r'(mavlink start -d /dev/ttyS2[^\r\n]*)',ps)
        logger=re.search(r'(logger start[^\r\n]*)',ps)
        if not uart or not logger: raise RuntimeError('Missing original startup commands')
        original_uart=uart[1].strip(); original_logger=logger[1].strip()
        if original_logger!='logger start -b 64 -t -m all': raise RuntimeError('Unexpected logger')
        if original_uart!='mavlink start -d /dev/ttyS2 -b p:SER_GPS1_BAUD -m p:MAV_1_MODE -r p:MAV_1_RATE -s -x':
            raise RuntimeError('Unexpected original UART')
        before=cmd('mavlink status')
        if '/dev/ttyS2 @115200' not in before or '/dev/ttyS3 @115200' not in before:
            raise RuntimeError('Port baseline differs')
        original_streams={k:v['rate'] for k,v in r.streams(cmd('mavlink status streams',6)).items()}
        sdlog=cmd('param show SDLOG*')
        # Original absence, established by successful root FTP listing, not failed file read.
        b.ftp(link,'list','/fs/microsd')
        root_listing=cmd('ls /fs/microsd')
        if re.search(r'^\s*etc/?\s*$',root_listing,re.M):
            raise RuntimeError('Existing etc requires byte backup; refuse unplanned overwrite')
        emit(backup_verified=True,uart=original_uart,logger=original_logger,
             streams=original_streams,topic_original='ABSENT',props='USER_CONFIRMED')
        for d in ('/fs/microsd/etc','/fs/microsd/etc/logging'):
            b.ftp(link,'mkdir',d); dirs.append(d)
        topic_attempted=True
        b.ftp(link,'put',b.TOPIC_PATH,str(HERE/'topics.txt'))
        b.ftp(link,'get',b.TOPIC_PATH,str(HERE/'topics-readback.txt'),timeout=20)
        if digest(HERE/'topics.txt')!=digest(HERE/'topics-readback.txt'): raise RuntimeError('Topic hash differs')
        logger_changed=True; cmd('logger stop')
        cmd('logger start -b 64 -t -m mavlink -p vehicle_imu')
        if 'Not logging' not in cmd('logger status'): raise RuntimeError('Unexpected recording')
        uart_changed=True; cmd('mavlink stop -d /dev/ttyS2')
        cmd(START)
        configured=cmd('mavlink status')
        block=next(x for x in configured.split('instance #') if '/dev/ttyS2 @921600' in x)
        if '46080 B/s' not in block or 'flow control: OFF' not in block or 'mode: Onboard' not in block:
            raise RuntimeError('Trial UART readback mismatch')
        row=dict(firmware_hash=HASH,ekf2_ev_ctrl=0,disarmed=True,propellers_removed=True,
                 uart='/dev/ttyS2',baud=921600,mavlink_datarate=46080,
                 gyro_device_id=6684690,accel_device_id=6946834,vehicle_imu_instance=0,
                 logger_backend='mavlink',logger_poll='vehicle_imu',configuration_backup_verified=True)
        with (HERE/'attestation.json').open('x') as f: json.dump(row,f)
        subprocess.run(['scp',str(HERE/'attestation.json'),'root@10.18.198.1:'+REMOTE+'/trial-attestation.json'],check=True,timeout=20)
        with (HERE/'receiver-console.txt').open('x') as output:
            process=subprocess.Popen(['ssh','-o','BatchMode=yes','root@10.18.198.1','python3',REMOTE+'/launch.py'],stdout=output,stderr=subprocess.STDOUT)
            deadline=time.monotonic()+95
            try:
                while process.poll() is None and time.monotonic()<deadline:
                    link.recv_match(timeout=.1); link.guard()
                if process.poll() is None: raise RuntimeError('Bounded receiver timeout')
                emit(receiver_exit=process.returncode)
            finally:
                if process.poll() is None: process.wait(timeout=10)
        cmd('logger status'); cmd('mavlink status'); cmd('listener cpuload -n 1')
        cmd('listener vehicle_imu_status -i 0 -n 1')
    except BaseException as exc:
        emit(error=type(exc).__name__+': '+str(exc)); errors.append(str(exc))
    finally:
        if link:
            def restore(action):
                try: action()
                except Exception as exc: errors.append('RESTORE: '+str(exc)); emit(restore_error=str(exc))
            if logger_changed: restore(lambda:cmd('logger stop',cleanup=True))
            if topic_attempted: restore(lambda:b.ftp(link,'rm',b.TOPIC_PATH))
            for d in reversed(dirs): restore(lambda d=d:b.ftp(link,'rmdir',d))
            if logger_changed: restore(lambda:cmd(original_logger,cleanup=True))
            if uart_changed:
                restore(lambda:cmd('mavlink stop -d /dev/ttyS2',cleanup=True))
                restore(lambda:cmd(original_uart,cleanup=True))
                for name,rate in original_streams.items():
                    if rate is not None:
                        restore(lambda name=name,rate=rate:cmd(r.command(name,rate),.15,cleanup=True))
                def verify_streams():
                    actual={k:v['rate'] for k,v in r.streams(cmd('mavlink status streams',6,cleanup=True)).items()}
                    if actual!=original_streams: raise RuntimeError('Original stream mapping not restored')
                    emit(stream_mapping_restored=True)
                restore(verify_streams)
            for query in ('logger status','mavlink status','ps','param show SDLOG*','commander status','param show EKF2_EV_CTRL'):
                restore(lambda query=query:cmd(query,cleanup=True))
            link.close()
        emit(errors=errors,finished=True); evidence.close()
    return bool(errors)

if __name__=='__main__': raise SystemExit(main())
