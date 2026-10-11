# Live PX4 read-only baseline — 2026-10-11

User connected hardware and requested the proposed read-only baseline check.
Windows repository HEAD3ea1e16086965176db68b88e1c42990f92c5913e; existing controller,
plan and handoff working-tree changes retained. Evidence: identity.txt, status.txt,
imu-status.txt and recheck.txt. All three console runs and identity query exited0;
each serial owner released the MAVLink shell and closed COM19 in finally.

## Current observed state

- COM19 USB VID:PID1B8C:0036; opened at nominal57600. Initial serial enumeration
  preceded the PnP appearance; subsequent identity confirmed the actual endpoint.
- MICOAIR_H743_V2, PX4 Release1.17.0,
  hash d6f12ad1c4f70ad3230afd7d86e971421e02fef4, build May13 2026.
- Commander Disarmed before/after; first heartbeat base_mode29; EKF2_EV_CTRL0.
- Selected gyro6684690/accel6946834, BMI088 instance0/SPI2. BMI2703604506 remains
  instance1/SPI3, not selected. Selection unchanged from saved latest records.
- BMI088 status snapshot raw estimates: accel1609.5658Hz, gyro1997.6769Hz;
  sensor publication estimates804.7829/665.8923Hz (FIFO/batch publications differ
  from individual sample rate). Second status1608.9933/1997.6314Hz raw.
- One-second uORB top: sensor_accel0=804Hz, sensor_gyro0=666Hz;
  vehicle_imu0=190Hz, vehicle_imu1=194Hz. This single diagnostic window is not
  sustained rate qualification or strict >=200Hz PASS. Never change integration
  rate/selection solely to make a planned test fit.
- BMI088 accel bad register1/reset2, gyro overflow1/reset2; error_count1 for
  each. First/second driver readings and vehicle_imu_status error counts unchanged
  across approximately32s sample-timestamp separation. Origin of earlier events
  unknown; not evidence of continuous new errors or certified healthy acquisition.
- Clip counters0 in retained status snapshots; gyro temperature nan is a status
  field, not a nonfinite gyro-vector measurement. BMI270 status errors0, reset1.
- CPU load one snapshot0.50655, RAM usage0.33597. Not a performance benchmark.
- Logger idle, mode all,180 subscriptions; process `logger start -b 64 -t -m all`.
  SDLOG_BACKEND3/BOOT_BAT0/DIRS_MAX0/MISSION0/MODE0/PROFILE1/UTC_OFFSET0.
  `ls`/`cat` custom logging path returned Not a directory; no custom file backed
  up or created. Serial helper conservatively redacted UUID-named lines, including
  SDLOG_UUID; reread that nonsecret scalar before a later complete config backup.
- Wired PX4 /dev/ttyS2 instance1=115200, Onboard, no flow, forwarding off,
  tx budget5760B/s, rx0B/s, current negotiated version1. Saved StageA/B MAVLink2
  PASS remains historical; current rx0 does not prove cable failure or qualify
  live M3C ownership. No sender opened on M3C this pass.
- Flow/ToF /dev/ttyS3 instance2=115200, RX3548.1B/s, sys1/comp88, lost0;
  not changed. UART0 and USB maintained; USB reported receive-loss counter cannot
  be treated as M3C link-loss evidence (management requests used separate sessions).

## Operations and limits

Status-only allowlist expanded with EKF2_EV_CTRL and bounded status listeners.
Exact query text is in the transcripts. No parameter writes, logger starts/stops,
sample-log capture, rate/stream requests, firmware, wiring or M3C operations.
No settings restoration was needed; final logger idle/commander Disarmed readback.
No raw IMU export, high-rate UART or source completeness PASS obtained here.

## Next

Current baseline matches the selected BMI088/d6f12ad1 prerequisites of the
single-UART controller RUNBOOK, with existing cumulative sensor events documented.
Further work: M3C PTY-only controller tests and current owner/termios inspection;
then the separate bounded communication/logger trial from RUNBOOK. It changes
runtime baud115200→921600 and budget5760→46080B/s plus logger profile, so it is
outside this read-only action. Back up the actual current state before that trial
and restore that state afterwards. The interval-derived vehicle_imu observation
model, startup/tail completeness, camera time and >=200Hz gate stay unresolved.
VIO-S0/VIO-P PARTIAL and StageC NOT_STARTED. No commit/push/Vault write.
