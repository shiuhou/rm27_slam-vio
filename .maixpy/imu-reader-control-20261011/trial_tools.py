"""Pure single-trial scope and read-only sampler helpers; no UART acquisition."""
import errno
import importlib.util
import math
from pathlib import Path
import re
import struct

old_path=Path(__file__).resolve().parent.parent/'imu-uart-negotiated-trial-20261011/coordinator.py'
if not old_path.exists(): old_path=Path(__file__).resolve().parent/'previous_coordinator.py'
spec=importlib.util.spec_from_file_location('previous_trial_helpers',old_path)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

KEEP={'HEARTBEAT','SYSTEM_TIME','TIMESYNC','LINK_NODE_STATUS','SYS_STATUS','STATUSTEXT'}

def treatment(table):
    if not KEEP <= table.keys(): raise ValueError('Missing retained health/epoch/diagnostic streams')
    for name,rate in table.items():
        if (not re.fullmatch('[A-Z][A-Z0-9_]+',name) or rate is not None and
                (type(rate) not in (int,float) or not math.isfinite(rate) or rate<0)):
            raise ValueError('Unreviewed/nonfinite stream backup')
    expected=dict(HEARTBEAT=1,SYSTEM_TIME=1,TIMESYNC=10,LINK_NODE_STATUS=1,SYS_STATUS=5,STATUSTEXT=20)
    if any(table[name]!=rate for name,rate in expected.items()):
        raise ValueError('Retained stream rate differs from same-condition proposal')
    return {name:0. for name,rate in table.items() if name not in KEEP and rate is not None and rate>0}

def stream_table(text,instance=1):
    # Existing parser requires HIGHRES_IMU, which this treatment intentionally
    # removes. Keep the same format, but require actual health/epoch rows instead.
    active=False; result={}
    text=re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',text)
    for line in text.splitlines():
        found=re.match(r'\s*instance #(\d+):',line)
        if found: active=int(found[1])==instance;continue
        if not active or not line.strip() or line.lstrip().startswith(('Name ','nsh>')):continue
        m=re.fullmatch(r'\s*([A-Z][A-Z0-9_]+)\s+(?:([\d.]+)\s+\(([\d.]+)\)|(unlimited))\s*(\d+)?\s*',line)
        if not m: raise ValueError('Unparsed target stream row: '+line)
        if m[1] in result: raise ValueError('Duplicate target stream')
        rate=float(m[2]) if m[2] else None
        if rate is not None and not math.isfinite(rate): raise ValueError('Nonfinite nominal stream')
        result[m[1]]=rate
    if not {'HEARTBEAT','SYSTEM_TIME'}<=result.keys():raise ValueError('Incomplete target stream table')
    return result

def check_command(line,original_uart,original_logger,original_streams,changes):
    try:
        old.check_command(line,original_uart,original_logger,original_streams)
        return
    except ValueError: pass
    m=re.fullmatch(r'mavlink stream -d /dev/ttyS2 -s ([A-Z][A-Z0-9_]+) -r ([\d.]+)',line)
    if m and m[1] not in KEEP and m[1] in changes and float(m[2])==changes[m[1]]==0:
        return
    raise ValueError('Outside exact reduced-telemetry scope: '+line)

def proc_sample(stat,status,*,now_ns,clk_tck,page_size):
    fields=stat[stat.rfind(')')+2:].split()
    if len(fields)<22 or clk_tck<=0 or page_size<=0: raise ValueError('Incomplete /proc stat or clock/page metadata')
    row=dict(receipt_mono_ns=now_ns,clk_tck=clk_tck,utime_ticks=int(fields[11]),
             stime_ticks=int(fields[12]),starttime_ticks=int(fields[19]),
             rss_bytes=int(fields[21])*page_size)
    for key,name in (('VmRSS','rss_kib'),('voluntary_ctxt_switches','voluntary_context_switches'),
                     ('nonvoluntary_ctxt_switches','involuntary_context_switches')):
        m=re.search(r'^'+key+r':\s*(\d+)\b',status,re.M)
        if m:row[name]=int(m[1])
    if 'rss_kib' in row:row['rss_bytes']=row['rss_kib']*1024
    return row

def decode_icount(raw):
    if len(raw)!=80: raise ValueError('Linux serial_icounter_struct must contain20 ints')
    names=('cts','dsr','rng','dcd','rx','tx','frame','overrun','parity','brk','buf_overrun')
    return dict(zip(names,struct.unpack('20i',raw)[:11]))

def uart_counters(fd,*,ioctl=None):
    if ioctl is None:
        import fcntl,termios
        request=getattr(termios,'TIOCGICOUNT',None)
        if request is None:return dict(status='UNKNOWN_UNSUPPORTED_CONSTANT')
        ioctl=fcntl.ioctl
    else:
        request=0  # injected offline unsupported-ioctl test; never a live request
    raw=bytearray(80)
    try:
        ioctl(fd,request,raw,True)
        return dict(status='MEASURED',**decode_icount(raw))
    except OSError as exc:
        return dict(status='UNKNOWN_UNSUPPORTED_IOCTL' if exc.errno in (errno.ENOTTY,errno.EINVAL,errno.ENOSYS) else 'UNKNOWN_IOCTL_ERROR',
                    errno=exc.errno)
