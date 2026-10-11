"""Retain one explicitly synthetic negotiation fixture; NEVER opens serial IO."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'imu-design-20261010/single-uart/controller'))
from test_negotiation import NegotiatingPeer
from test_uart_session import Clock
from test_session import fixture
from uart_session import run_session
from capture_report import audit_capture

def main():
    clock=Clock()
    output=Path(__file__).resolve().parent/'SYNTHETIC-roundtrip-01'
    result=run_session(NegotiatingPeer(clock),output,seconds=1,clock=clock,negotiate_mavlink2=True)
    assert result['error'] is None and (output/'framing-valid.ulg').read_bytes()==fixture()
    audit=audit_capture(output,epoch='SYNTHETIC_TWO_INTEGRAL_RECORDS_NOT_CURRENT_BMI088')
    assert audit['raw_decode_parity'] and not audit['transport_qualified'] and not audit['openvins_admissible']
    with (output/'audit.json').open('x',encoding='utf-8') as report:
        json.dump(audit,report,indent=2,allow_nan=False)
    print(json.dumps(dict(evidence_kind='SCRIPTED_PEER_SYNTHETIC_CLOCK_ACKS_IMU',
        policy=result['mavlink2_negotiation_policy'],byte_exact_fixture=True,
        negotiation_started_order_token=result['negotiation_started_mono_ns'],
        negotiation_confirmed_order_token=result['negotiation_confirmed_mono_ns'],
        raw_decode_parity=True,physical_throughput='NOT_MEASURED',clock_synchronization='UNKNOWN',
        transport_qualified=False,openvins_admissible=False)))

if __name__=='__main__': main()
