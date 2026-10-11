"""Saved-source and synthetic protocol diagnosis ONLY; no serial/network IO."""
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'imu-design-20261010/single-uart/controller'))
from session import Controller
from pymavlink.dialects.v10 import common as m1
from pymavlink.dialects.v20 import common as m2
from heartbeat_only import frame_v2

def diagnose():
    receiver=HERE.parent/'mavlink2-20261010/mavlink_receiver.cpp'
    main=HERE.parent/'imu-input-20261010/src__modules__mavlink__mavlink_main.cpp'
    receiver_text=receiver.read_text(); main_text=main.read_text()
    assert 'Upgrade to MAVLink v2 because of incoming packet' in receiver_text
    assert '_mavlink.set_protocol_version(2);' in receiver_text
    assert "case 'Z':\n\t\t\t_flow_control = FLOW_CONTROL_OFF;" in main_text
    rows=[json.loads(line) for line in (HERE/'coordinator.jsonl').read_text().splitlines()]
    outputs=[rows[i+1]['output'] for i,row in enumerate(rows[:-1])
             if row.get('command')=='mavlink status']
    from coordinator import port_block
    live=port_block(outputs[1],'/dev/ttyS2',921600)
    assert 'MAVLink version: 1' in live and 'rx: 0.0 B/s' in live
    results=[]
    for dialect in (m1,m2):
        wire=dialect.MAVLink_heartbeat_message(dialect.MAV_TYPE_QUADROTOR,
            dialect.MAV_AUTOPILOT_PX4,29,0,dialect.MAV_STATE_STANDBY,3).pack(
                dialect.MAVLink(None,srcSystem=1,srcComponent=1))
        c=Controller(0)
        output=c.feed_wire(wire,100_000_000)
        results.append(dict(evidence_kind='SYNTHETIC_NO_DEVICE',incoming_version=1 if wire[0]==254 else 2,
                            output_frames=len(output),state=c.state,error=c.error))
    assert results[0]['output_frames']==0 and 'non-MAVLink2 heartbeat' in results[0]['error']
    assert results[1]['state']=='STARTING' and results[1]['error'] is None
    heartbeat=frame_v2(0)
    message=m2.MAVLink(None).parse_buffer(heartbeat)[0]
    assert message.get_type()=='HEARTBEAT' and (message.get_srcSystem(),message.get_srcComponent())==(1,191)
    assert message.type==m2.MAV_TYPE_ONBOARD_CONTROLLER and message.autopilot==m2.MAV_AUTOPILOT_INVALID
    return dict(observed_failure='COORDINATOR_VERSION2_GATE_BEFORE_PEER_LAUNCH',
        source_supported_cause='PX4 switches outgoing protocol after incoming MAVLink2; -Z only flow-off',
        receiver_readiness_problem='STRICT_CONTROLLER_REJECTS_INITIAL_V1_AND_CANNOT_SEND_BOOTSTRAP_HEARTBEAT',
        source_files={str(path.relative_to(HERE.parent)):hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in (receiver,main)},synthetic_controller_results=results,
        existing_stage_a_heartbeat=dict(wire_hex=heartbeat.hex(),bytes=len(heartbeat),version=2,sysid=1,compid=191),
        physical_transport_qualified=False,hardware_fault_established=False,
        proposed_fix='Separate guarded heartbeat-only negotiation before strict MAVLink2 logging; not implemented or executed')

if __name__=='__main__':
    result=diagnose()
    with (HERE/'protocol-diagnosis.json').open('x') as f: json.dump(result,f,indent=2)
    print(json.dumps(result))
