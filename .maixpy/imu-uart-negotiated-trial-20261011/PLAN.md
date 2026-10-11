# One authorized negotiated UART IMU trial — 2026-10-11

User's "可上真機" authorizes the next ONE bounded60s M3C–PX4 trial described by
the existing RUNBOOK: isolated current120-test board precheck, actual fresh
identity/Disarmed/EV0/source/logger/UART/stream/topic absence backups, temporary
921600/8N1/no-flow/46080B/s minimal MAVLink vehicle_imu logger, explicitly opted-in
heartbeat-only negotiation, then logging START/ACK/STOP and exact readback restore.
Carry previous user-confirmed propeller removal in this same bench session; no
reinstallation reported. Never ARM/motor/setpoint/calibrate/fuse, change firmware/
parameters/sensor rate/wiring/camera, delete old logs, install, push or touch Vault.

Use NEW deployment/output and coordinator. Reuse historical coordinator workflow
and guards, NOT its frozen file/outputs; fix only premature pre-peer version gate
and launch opt-in/current path. Pre-peer status may be1 OR2; actual receiver must
verify PX4v2 before own START. TDD pure scope/preparation/readiness checks precede
authoring new coordinator. No START before config topic bytes/command readbacks
and fresh safety. Any failure ends this one attempt; no automatic second capture.

Baseline HEAD3ea1e16086965176db68b88e1c42990f92c5913e/main; existing dirty controller/
reports and unrelated camera_capture.py/tmp preserved. Inspect exact flashedhash
d6f12ad1c4f70ad3230afd7d86e971421e02fef4 and current selected BMI088 instance0,
gyro6684690/accel6946834; don't interpret old BMI270 logs as current source.
Source197Hz snapshot is not >=200Hz PASS; finite reconstruction/transport does
not qualify source/tail coverage, clock mapping or integral OpenVINS input model.

All preflight/capture/failed bytes/exit/restore commands retained locally. Final
audits distinguish source diagnostics, packet loss and terminal framing; don't
repair received bytes or relabel failed sessions PASS. Update root reports,
HANDOFF/VAULT_UPDATE after fresh evidence. External research not required: exact
matching source, tested protocol and existing helpers already local.
