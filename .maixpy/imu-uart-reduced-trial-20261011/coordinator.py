"""ONE approved reduced-telemetry comparison; independent USB backup/restore."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import trial_tools as t

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REMOTE='/root/rm27-controller-reduced-20261011.NWMjuL'
c=t.old
HASH,START,LOGGER=c.HASH,c.START,c.LOGGER

def main():
    sys.path.insert(0,str(HERE.parent/'imu-offline-20261008'))
    import bench_io as b
    sys.path.insert(0,str(HERE.parent/'imu-transport-20261010'))
    import rate_control as r
    board=json.loads((HERE/'board-preflight.json').read_text())
    assert board['owners']==[] and board['no_setting_change'] is True
    tools=json.loads((HERE/'tools-expected.json').read_text(encoding='utf-8-sig'))
    assert json.loads((HERE/'tools-parity.json').read_text())['tool_sha256']==tools
    assert all(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest for name,digest in tools.items())
    assert hashlib.sha256((HERE/'tool-tests-02.txt').read_bytes()).hexdigest()==board['board_test_sha256']
    for name,digest in board['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    evidence=(HERE/'coordinator.jsonl').open('x',encoding='utf-8')
    link=process=None; dirs=[];topic_attempted=logger_changed=uart_changed=launched=False
    original_uart=original_logger=None;original_streams={};changes={};sdlog={};other={};last={}
    errors=[];acquisition_errors=[]
    def emit(**row):
        row['host_monotonic_s']=time.monotonic();evidence.write(json.dumps(row,allow_nan=False)+'\n');evidence.flush()
    def cmd(line,seconds=3,cleanup=False):
        t.check_command(line,original_uart,original_logger,original_streams,changes)
        if not cleanup:link.fresh_disarmed()
        emit(command=line,cleanup=cleanup)
        wire=line+'\n'
        for index in range(0,len(wire),65):link.send_shell(wire[index:index+65])
        parts=[];deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            msg=link.recv_match(timeout=.1)
            if msg and msg.get_type()=='SERIAL_CONTROL' and msg.count:
                parts.append(bytes(msg.data[:msg.count]).decode('utf-8',errors='replace'))
        out=''.join(parts);last[line]=out;emit(output=out);print(line,out,flush=True)
        if not cleanup:link.guard()
        if 'nsh: ' in out or 'ERROR' in out or 'Connection timed out' in out:
            raise RuntimeError('Console command failed: '+line)
        return out
    def remote(*args,timeout=20):
        return subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10',
            'root@10.18.198.1',*args],check=True,timeout=timeout)
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        link=b.Link();link.fresh_disarmed();link.send_shell('\n')
        assert HASH in cmd('ver all'),'Firmware mismatch'
        assert 'Disarmed' in cmd('commander status'),'Not disarmed'
        assert re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',cmd('param show EKF2_EV_CTRL')),'EV mismatch'
        selected=cmd('sensors status')
        assert 'selected gyro: 6684690 (0)' in selected and 'selected accel: 6946834 (0)' in selected,'Source differs'
        imu=cmd('listener vehicle_imu_status -i 0 -n 1');assert '6684690' in imu and '6946834' in imu
        cmd('listener cpuload -n 1');cmd('uorb top -1 vehicle_imu');cmd('free')
        assert 'Not logging' in cmd('logger status'),'Existing recording refused'
        ps=cmd('ps')
        uart=re.search(r'(mavlink start -d /dev/ttyS2[^\r\n]*)',ps)
        logger=re.search(r'(logger start[^\r\n]*)',ps)
        assert uart and logger,'Startup backup missing'
        original_uart,original_logger=uart[1].strip(),logger[1].strip()
        assert original_uart=='mavlink start -d /dev/ttyS2 -b p:SER_GPS1_BAUD -m p:MAV_1_MODE -r p:MAV_1_RATE -s -x','Original UART differs'
        assert original_logger=='logger start -b 64 -t -m all','Original logger differs'
        other={port:re.search(r'(mavlink start -d '+re.escape(port)+r'[^\r\n]*)',ps)[1].strip()
            for port in ('/dev/ttyS0','/dev/ttyS3','/dev/ttyACM0')}
        status=cmd('mavlink status');c.port_block(status,'/dev/ttyS2',115200);c.port_block(status,'/dev/ttyS3',115200)
        # The nominal table's instance1 must be the explicitly checked wired port.
        wired=re.search(r'instance #1:(.*?)(?=instance #|$)',status,re.S)
        assert wired and '/dev/ttyS2 @115200' in wired[1],'Stream instance/port differs'
        original_streams=t.stream_table(cmd('mavlink status streams',6));t.treatment(original_streams)
        sdlog=c.sdlog_values(cmd('param show SDLOG*'));assert len(sdlog)==8
        b.ftp(link,'list','/fs/microsd');listing=cmd('ls /fs/microsd')
        assert not re.search(r'^\s*etc/?\s*$',listing,re.M),'Existing config requires byte backup; refuse'
        emit(backup_verified=True,uart=original_uart,logger=original_logger,streams=original_streams,
            sdlog=sdlog,topic_original='ABSENT',unrelated_uart_commands=other,props='USER_CONFIRMED_SAME_BENCH_SESSION')
        for directory in ('/fs/microsd/etc','/fs/microsd/etc/logging'):
            b.ftp(link,'mkdir',directory,timeout=20);dirs.append(directory)
        topic_attempted=True
        topics=HERE.parent/'imu-uart-trial-20261011/topics.txt'
        b.ftp(link,'put',b.TOPIC_PATH,str(topics),timeout=20)
        b.ftp(link,'get',b.TOPIC_PATH,str(HERE/'topics-readback.txt'),timeout=20)
        assert sha(HERE/'topics-readback.txt')==sha(topics),'Topic bytes differ'
        logger_changed=True;cmd('logger stop');cmd(LOGGER)
        logger_status=cmd('logger status');assert 'Not logging' in logger_status and 'mode: mavlink' in logger_status
        uart_changed=True;cmd('mavlink stop -d /dev/ttyS2');cmd(START)
        c.validate_pre_peer(cmd('mavlink status'))
        temporary=t.stream_table(cmd('mavlink status streams',6));changes=t.treatment(temporary)
        emit(temporary_streams_before_treatment=temporary,treatment=changes,retained_streams=sorted(t.KEEP))
        for name,rate in changes.items():cmd(r.command(name,rate),.2)
        actual=t.stream_table(cmd('mavlink status streams',6))
        expected={name:rate for name,rate in temporary.items() if name not in changes}
        assert actual==expected,'Treatment map differs from exact intended removals'
        emit(reduced_telemetry_readback_verified=True,actual_streams=actual)
        row=dict(firmware_hash=HASH,ekf2_ev_ctrl=0,disarmed=True,propellers_removed=True,
            uart='/dev/ttyS2',baud=921600,mavlink_datarate=46080,gyro_device_id=6684690,
            accel_device_id=6946834,vehicle_imu_instance=0,logger_backend='mavlink',
            logger_poll='vehicle_imu',configuration_backup_verified=True,heartbeat_negotiation_approved=True,
            experimental_factor='REDUCED_NONESSENTIAL_NUMERICAL_STREAMS',treatment_readback_verified=True)
        with (HERE/'attestation.json').open('x') as f:json.dump(row,f,indent=2)
        subprocess.run(['scp',str(HERE/'attestation.json'),'root@10.18.198.1:'+REMOTE+'/attestation.json'],check=True,timeout=20)
        with (HERE/'remote-launch-console.txt').open('x') as output:
            process=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10',
                'root@10.18.198.1','timeout','-s','TERM','-k','8s','95s','python3','-B',REMOTE+'/launch.py'],
                stdout=output,stderr=subprocess.STDOUT)
            launched=True;begin=time.monotonic();measured=False
            try:
                while process.poll() is None and time.monotonic()-begin<105:
                    link.recv_match(timeout=.1);link.guard()
                    if not measured and time.monotonic()-begin>=30:
                        emit(observation_window='MID_RUN_IF_RECEIVER_STILL_ACTIVE')
                        cmd('logger status');cmd('mavlink status');cmd('listener cpuload -n 1');cmd('uorb top -1 vehicle_imu');measured=True
                if process.poll() is None:raise RuntimeError('Bounded receiver timeout')
                emit(receiver_exit=process.returncode)
                if process.returncode!=0:acquisition_errors.append('receiver exit '+str(process.returncode))
            finally:
                if process.poll() is None:remote('python3','-B',REMOTE+'/stop.py');process.wait(timeout=15)
        for line in ('logger status','mavlink status','listener cpuload -n 1',
                     'listener vehicle_imu_status -i 0 -n 1','sensors status','uorb top -1 vehicle_imu'):
            cmd(line)
    except BaseException as exc:
        emit(error=type(exc).__name__+': '+str(exc));errors.append(str(exc))
    finally:
        if launched and process is not None and process.poll() is None:
            try:remote('python3','-B',REMOTE+'/stop.py');process.wait(timeout=15)
            except Exception as exc:errors.append('RECEIVER CLEANUP: '+str(exc));emit(restore_error=str(exc))
        if link:
            def restore(action):
                try:action()
                except Exception as exc:errors.append('RESTORE: '+str(exc));emit(restore_error=str(exc))
            if logger_changed:restore(lambda:cmd('logger stop',cleanup=True))
            if topic_attempted:restore(lambda:b.ftp(link,'rm',b.TOPIC_PATH,timeout=20))
            for directory in reversed(dirs):restore(lambda directory=directory:b.ftp(link,'rmdir',directory,timeout=20))
            if logger_changed:restore(lambda:cmd(original_logger,cleanup=True))
            if uart_changed:
                restore(lambda:cmd('mavlink stop -d /dev/ttyS2',cleanup=True));restore(lambda:cmd(original_uart,cleanup=True))
                for name,rate in original_streams.items():
                    if rate is not None:restore(lambda name=name,rate=rate:cmd(r.command(name,rate),.15,cleanup=True))
                def verify_streams():
                    assert t.stream_table(cmd('mavlink status streams',6,cleanup=True))==original_streams,'Original stream map not restored'
                    emit(stream_mapping_restored=True)
                restore(verify_streams)
            for line in ('logger status','mavlink status','ps','param show SDLOG*',
                         'commander status','param show EKF2_EV_CTRL','ls /fs/microsd'):
                restore(lambda line=line:cmd(line,cleanup=True))
            if logger_changed or uart_changed:
                def verify_restore():
                    assert 'Not logging' in last['logger status'] and 'mode: all' in last['logger status']
                    assert original_logger in last['ps'] and original_uart in last['ps']
                    assert all(value in last['ps'] for value in other.values())
                    c.port_block(last['mavlink status'],'/dev/ttyS2',115200);c.port_block(last['mavlink status'],'/dev/ttyS3',115200)
                    assert c.sdlog_values(last['param show SDLOG*'])==sdlog
                    assert 'Disarmed' in last['commander status'] and re.search(r'EKF2_EV_CTRL[^\r\n]*:\s*0\s',last['param show EKF2_EV_CTRL'])
                    assert not re.search(r'^\s*etc/?\s*$',last['ls /fs/microsd'],re.M)
                    emit(px4_configuration_restored=True)
                restore(verify_restore)
            link.close()
        emit(errors=errors,acquisition_errors=acquisition_errors,finished=True);evidence.close()
    return int(bool(errors or acquisition_errors))

if __name__=='__main__':raise SystemExit(main())
