"""Bounded research-only serial console/FTP helper. Never sends arming commands."""
import argparse
import collections
import json
import logging
import sys
import time
import serial
from pymavlink.dialects.v20 import common as m
from pymavlink.mavftp import MAVFTP
from capture_guard import check_command, check_heartbeat, check_remote, TOPIC_PATH, download_temp_path

class Link:
    def __init__(self):
        self.source_system = 254
        self.source_component = 190
        self.port = serial.Serial(port=None, baudrate=57600, timeout=.05, write_timeout=2)
        self.port.dtr = self.port.rts = False
        self.port.port = 'COM19'
        self.mav = m.MAVLink(self.port, srcSystem=254, srcComponent=190)
        self.mav.robust_parsing = True
        self.queue = collections.deque()
        self.hb = None
        self.hb_time = None
        self.shell_used = False
        self.port.open()

    def recv_match(self, type=None, timeout=.1, **kwargs):
        deadline = time.monotonic()+timeout
        while time.monotonic() < deadline:
            if not self.queue:
                data = self.port.read(max(1,min(self.port.in_waiting,8192)))
                self.queue.extend(self.mav.parse_buffer(data) or [])
            while self.queue:
                msg = self.queue.popleft()
                kind = msg.get_type()
                if kind == 'HEARTBEAT' and msg.get_srcSystem() == 1 and msg.get_srcComponent() == 1:
                    self.hb, self.hb_time = msg, time.monotonic()
                    print('FC_HEARTBEAT',self.hb_time,msg.base_mode,flush=True)
                if type is None or kind == type or isinstance(type,list) and kind in type:
                    return msg
        return None

    def fresh_disarmed(self):
        deadline = time.monotonic()+4
        previous = self.hb_time
        while self.hb_time == previous and time.monotonic() < deadline:
            self.recv_match(timeout=.1)
        self.guard()

    def guard(self):
        if self.hb is None: raise RuntimeError('No FC heartbeat')
        check_heartbeat(self.hb.base_mode,self.hb.autopilot,1,1,self.hb_time,time.monotonic())

    def send_shell(self, text):
        data = text.encode('ascii')
        if len(data)>70: raise ValueError('Shell command too long')
        self.shell_used=True
        self.mav.serial_control_send(10, m.SERIAL_CONTROL_FLAG_EXCLUSIVE | m.SERIAL_CONTROL_FLAG_RESPOND,
            0,0,len(data),list(data)+[0]*(70-len(data)))

    def command(self,command,seconds=2,cleanup=False):
        check_command(command)
        if not cleanup: self.fresh_disarmed()
        print('COMMAND',command,flush=True)
        self.send_shell(command+'\n')
        out=[]
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            msg=self.recv_match(timeout=.1)
            if msg and msg.get_type()=='SERIAL_CONTROL' and msg.count:
                s=bytes(msg.data[:msg.count]).decode('utf-8',errors='replace')
                print(s,end='',flush=True)
                out.append(s)
        text=''.join(out)
        if not cleanup: self.guard()
        return text

    def close(self):
        try:
            if self.shell_used: self.mav.serial_control_send(10,0,0,0,0,[0]*70)
        finally: self.port.close()

def ftp(link,operation,path,local=None,timeout=600):
    check_remote(operation,path)
    link.fresh_disarmed()
    client=MAVFTP(link,1,1)
    client.ftp_settings.burst_read_size=239
    client.ftp_settings.write_size=239
    if operation=='get':
        client.temp_filename=download_temp_path(local)
        result=client.cmd_get([path,local])
        result=client.process_ftp_reply('get',timeout=timeout)
        print('FTP_GET_SIZE',client.remote_file_size,'READ',client.read_total,flush=True)
    elif operation=='put':
        result=client.cmd_put([local,path])
        result=client.process_ftp_reply('put',timeout=timeout)
    else:
        result=getattr(client,'cmd_'+operation)([path])
    result.display_message()
    print('FTP_RESULT',operation,json.dumps(vars(result)),flush=True)
    if operation=='list': print('FTP_LIST',repr(client.list_result),flush=True)
    if result.return_code != 0: raise RuntimeError('FTP failed: '+str(result.return_code))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('operation',choices=['shell','list','get','put','mkdir','rmdir','rm','crc','capture'])
    p.add_argument('args',nargs='*')
    opts=p.parse_args()
    logging.basicConfig(level=logging.INFO,stream=sys.stdout)
    link=Link()
    try:
        link.fresh_disarmed()
        if opts.operation=='shell':
            link.send_shell('\n')
            for cmd in opts.args: link.command(cmd,3)
        elif opts.operation=='capture':
            # Config was separately uploaded/read back and backed up before this call.
            status=link.command('logger status')
            if 'Not logging' not in status: raise RuntimeError('Logger must be idle')
            status=link.command('sensors status',3)
            if 'selected gyro: 3604506 (1)' not in status or 'selected accel: 3604506 (1)' not in status:
                raise RuntimeError('Unexpected sensor identity/instance')
            try:
                link.command('logger stop')
                startup=link.command('logger start -b 64 -t -r 2500',3)
                if 'ERROR' in startup: raise RuntimeError('Logger startup error')
                link.command('logger on',1)
                started=time.monotonic()
                while time.monotonic()-started<14:
                    link.recv_match(timeout=.1)
                    link.guard()
                link.command('logger status',1)
            finally:
                link.command('logger off',3,cleanup=True)
                link.command('logger status',2,cleanup=True)
                link.command('logger stop',2,cleanup=True)
                # Only this exact temporary file, known absent in preflight, is removed.
                ftp(link,'rm',TOPIC_PATH)
                ftp(link,'rmdir','/fs/microsd/etc/logging')
                ftp(link,'rmdir','/fs/microsd/etc')
                link.command('logger start -b 64 -t',3,cleanup=True)
                link.command('logger status',2,cleanup=True)
                link.command('commander status',2,cleanup=True)
                link.command('param show SDLOG*',2,cleanup=True)
        else:
            ftp(link,opts.operation,opts.args[0],opts.args[1] if len(opts.args)>1 else None)
    finally: link.close()

if __name__=='__main__': main()
