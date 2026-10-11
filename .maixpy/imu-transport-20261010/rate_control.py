"""Pure, narrowly scoped temporary stream controls; no parameter writes."""
import re

KEEP = {'HEARTBEAT','STATUSTEXT','SYS_STATUS','EXTENDED_SYS_STATE','PING','HIGHRES_IMU'}
READ = {'ver all','commander status','param show EKF2_EV_CTRL','mavlink status',
        'mavlink status streams','listener cpuload -n 10','listener vehicle_imu -n 5',
        'listener vehicle_imu -i 1 -n 5','uxrce_dds_client status','sensors status'}

def streams(text):
    active=False; result={}
    text=re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',text)
    for line in text.splitlines():
        m=re.match(r'\s*instance #(\d+):',line)
        if m: active=int(m[1])==1; continue
        if not active: continue
        m=re.fullmatch(r'\s*([A-Z][A-Z0-9_]+)\s+(?:([\d.]+)\s+\(([\d.]+)\)|(unlimited))\s*(\d+)?\s*',line)
        if m:
            if m[1] in result: raise ValueError('Duplicate stream')
            result[m[1]]={'rate':float(m[2]) if m[2] else None,
                          'scheduled':float(m[3]) if m[3] else None,
                          'size':int(m[5]) if m[5] else None}
    if not {'HEARTBEAT','HIGHRES_IMU'}<=result.keys(): raise ValueError('Incomplete target stream table')
    return result

def changes(table):
    return {name:1 if name=='TIMESYNC' else 0 for name,v in table.items()
            if name not in KEEP and v['rate'] is not None and v['rate']>0 and v['size'] is not None}

def check(command,original):
    if command in READ: return
    m=re.fullmatch(r'mavlink stream -d /dev/ttyS2 -s ([A-Z][A-Z0-9_]+) -r ([\d.]+)',command)
    if not m: raise ValueError('Command outside reviewed scope')
    name,rate=m[1],float(m[2])
    if name not in original or original[name] is None: raise ValueError('Unbacked stream')
    if name in KEEP and name!='HIGHRES_IMU': raise ValueError('Protected health stream')
    allowed={original[name]}
    allowed.update({50,100} if name=='HIGHRES_IMU' else {1} if name=='TIMESYNC' else {0})
    if rate not in allowed: raise ValueError('Unapproved rate')

def command(name,rate):
    return f'mavlink stream -d /dev/ttyS2 -s {name} -r {rate:g}'
