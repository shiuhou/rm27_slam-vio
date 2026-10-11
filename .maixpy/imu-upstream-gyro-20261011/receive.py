"""Reuse the unchanged receiver; ioctl snapshots on its SAME owned descriptor."""
import argparse
import json
import os
from pathlib import Path
import select
import signal
import sys
import time

from trial_tools import uart_counters

def main():
    p=argparse.ArgumentParser();p.add_argument('--gate-fd',type=int,required=True);args=p.parse_args()
    if not select.select([args.gate_fd],[],[],5)[0] or os.read(args.gate_fd,1)!=b'G':
        raise RuntimeError('Receiver gate absent/stale; no UART opened')
    os.close(args.gate_fd)
    root=Path(__file__).resolve().parent;os.chdir(root)
    sys.path.insert(0,str(root/'.maixpy/imu-design-20261010/single-uart/controller'))
    import uart_session as u
    attestation=json.loads((root/'attestation.json').read_text())
    attestation['prepared_m3c_monotonic_ns']=time.monotonic_ns()
    from observation import validate_observation
    validate_observation(attestation,time.monotonic_ns())
    with (root/'preflight.json').open('x') as f:json.dump(attestation,f,indent=2)
    with (root/'uart-counters.jsonl').open('x') as counters:
        def emit_counter(phase,fd):
            counters.write(json.dumps(dict(phase=phase,receipt_mono_ns=time.monotonic_ns(),
                same_receiver_descriptor=True,**uart_counters(fd)))+'\n');counters.flush()
        class InstrumentedUART(u.OwnedUART):
            def __enter__(self):
                result=super().__enter__();emit_counter('before_capture',self.fd);return result
            def __exit__(self,*exc):
                try:emit_counter('after_capture_before_restore',self.fd)
                finally:super().__exit__(*exc)
        signal.signal(signal.SIGTERM,lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
        port=InstrumentedUART('/dev/ttyS2',921600,approved=True)
        summary=u.run_session(port,'physical-trial-01',seconds=60,preflight=attestation,negotiate_mavlink2=True)
    print(json.dumps(summary,allow_nan=False),flush=True)
    return int(summary['error'] is not None or summary['termios_restored'] is not True)

if __name__=='__main__':raise SystemExit(main())
