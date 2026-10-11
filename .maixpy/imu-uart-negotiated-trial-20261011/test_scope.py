"""Pure coordinator scope/version readiness tests. No serial/network access."""
import importlib.util
from pathlib import Path
import unittest

OLD=Path(__file__).resolve().parent.parent/'imu-uart-retry-20261011/coordinator.py'
NEW=Path(__file__).resolve().parent/'coordinator.py'
spec=importlib.util.spec_from_file_location('tested_coordinator',NEW if NEW.exists() else OLD)
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def status(version=1):
    return f'''instance #1:
flow control: OFF
tx rate max: 46080 B/s
rx: 0.0 B/s
mode: Onboard
MAVLink version: {version}
transport protocol: serial (/dev/ttyS2 @921600)
'''

class ScopeTests(unittest.TestCase):
    def test_pre_peer_does_not_require_already_negotiated(self):
        self.assertTrue(hasattr(c,'validate_pre_peer'),'Pre-peer v1 bootstrap gate missing')
        for version in (1,2): c.validate_pre_peer(status(version))

    def test_pre_peer_wrong_transport_still_refused(self):
        self.assertTrue(hasattr(c,'validate_pre_peer'),'Pre-peer guard missing')
        for old,new in [('46080 B/s','5760 B/s'),('OFF','ON'),('Onboard','Normal'),
                        ('version: 1','version: 3'),('921600','115200'),('ttyS2','ttyS3')]:
            with self.subTest(old=old),self.assertRaises(ValueError): c.validate_pre_peer(status().replace(old,new))

    def test_receiver_requires_confirmed_negotiation_and_restore(self):
        self.assertTrue(hasattr(c,'negotiated_receiver_ok'),'Negotiated result gate missing')
        good=dict(error=None,termios_restored=True,finite_framing_verified=True,
                  negotiate_mavlink2=True,mavlink2_negotiation_policy='GUARDED_V1_HEARTBEAT_BOOTSTRAP_V1',
                  negotiation_confirmed_mono_ns=100,start_accepted=True,stop_accepted=True)
        self.assertTrue(c.negotiated_receiver_ok(0,good))
        for key,value in [('termios_restored',False),('negotiate_mavlink2',1),
                          ('negotiation_confirmed_mono_ns',None),('negotiation_confirmed_mono_ns',True),
                          ('start_accepted',False),('stop_accepted',False),('finite_framing_verified',False),
                          ('error','failure')]:
            with self.subTest(key=key): self.assertFalse(c.negotiated_receiver_ok(0,dict(good,**{key:value})))
        self.assertFalse(c.negotiated_receiver_ok(1,good))

    def test_command_scope_still_refuses_flight_mutations(self):
        for line in ('commander arm','param set EKF2_EV_CTRL 1','reboot',
                     'mavlink stop-all','logger on','mavlink start -d /dev/ttyS3 -b 921600'):
            with self.assertRaises(ValueError): c.check_command(line,None,None,{})

    def test_restoration_only_exact_backed_rates(self):
        c.check_command('mavlink stream -d /dev/ttyS2 -s HIGHRES_IMU -r 50',None,None,{'HIGHRES_IMU':50})
        with self.assertRaises(ValueError):
            c.check_command('mavlink stream -d /dev/ttyS2 -s HIGHRES_IMU -r 100',None,None,{'HIGHRES_IMU':50})

if __name__=='__main__': unittest.main()
