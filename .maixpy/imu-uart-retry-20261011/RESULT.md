# Revised physical trial — 2026-10-11

## Result: PREPARATION ABORTED; restoration VERIFIED

User approved one 60-second real high-rate IMU trial. Actual preparation reached
PX4 UART921600/46080B/s, but the NEW coordinator demanded MAVLink2 before
launching the M3C peer. PX4 readback was version1/RX0; this gate stopped the run.
The receiver was never launched, no START/STOP/heartbeat/ACK was sent by M3C,
and the60-second accepted interval never began. No new IMU dataset or ULog.
This is a software readiness-order mistake, NOT a measured hardware/baud/loss
failure. No automatic retry. VIO-S0/P PARTIAL; StageC remains closed.

## Fresh baseline and actual operations

- Main3ea1e16086965176db68b88e1c42990f92c5913e; existing dirty source/docs retained.
- Independent COM19 USB: PX4 MICOAIR_H743_V2 Release1.17.0 full hash
  d6f12ad1c4f70ad3230afd7d86e971421e02fef4. Disarmed and EKF2_EV_CTRL0.
  All observed monitored heartbeat base_mode29; props user-confirmed in this bench
  session, not remotely observed. No ARM/parameter/setpoint/fusion/firmware/wiring.
- Selected BMI088 vehicle_imu0: gyro6684690, accel6946834. Fresh one-second
  uORB observation197Hz; not sustained qualification or strict>=200Hz PASS.
  Pre-preparation errors1/1, clip counters0, source discontinuity events1accel/
  2gyro. Prior origin UNKNOWN. Logger start resets perf, so do not subtract these
  against later counters or infer a reboot. No accepted-interval source audit.
- CPU0.50148/RAM0.33642 is a pre-preparation snapshot, not streaming CPU load.
- M3C maixcam2-9d05/aarch64, Python3.13.2/NumPy2.2.6/pymavlink2.4.49/
  pyulog1.2.4. All16 deployed source hashes unchanged from87-test M3C precheck.
  No current PTY rerun; no dependency install. /dev/ttyS2 has no other owner or
  console; B921600 constant exists. Read-only O_RDONLY opens obtained attributes
  without reading UART data, transmitting or changing termios. This does NOT
  establish physical M3C921600 driver/line support.
- Actual original commands/stream rates/eight SDLOG values/other-port commands
  backed in coordinator.jsonl. Successful FTP/root listing proved etc absent.
  Created only our two directories and166-byte topic file; downloaded readback
  SHA256fa434abe98b74a85531a97279c029b6ae8b6061e5d7161cc413e82ebcc105620
  equals unchanged prior proposal topics.txt. Eight subscriptions, idle MAVLink
  logger, `logger start -b 64 -t -m mavlink -p vehicle_imu`.
- Restarted only PX4/dev/ttyS2:
  `mavlink start -d /dev/ttyS2 -b 921600 -r 46080 -m onboard -Z -x`.
  Readback921600/46080B/s/Onboard/flowOFF, version1, RX0.
  TX13655.7B/s/txerr0 before any IMU session is outgoing telemetry only,
  NOT measured M3C received throughput or IMU delivery.

## Confirmed software cause / remaining design change

Saved matching d6f12ad1 source supports incoming-MAVLink2 negotiation:
`../mavlink2-20261010/mavlink_receiver.cpp:3231` switches outgoing protocol when
a complete MAVLink2 packet is parsed. Existing StageA report already records
MAV_PROTO_VER1 yet actual negotiated version2 after companion heartbeat.
`../imu-input-20261010/src__modules__mavlink__mavlink_main.cpp:2167` shows `-Z`
only forces flow control OFF; it does not force MAVLink2. No parameter change
is required solely to replicate the already verified StageA negotiation.

The new coordinator's version2-before-peer gate is therefore premature. There is
also an existing strict-controller bootstrap limitation: session.py rejects a
CRC-valid initial MAVLink1 PX41/1 heartbeat before generating its own v2 heartbeat.
Simply removing the coordinator check would not resolve that circular wait.
Offline diagnose_protocol.py reproduces v1=>zeroTX/DONE versus v2=>STARTING using
explicitly SYNTHETIC packets. It also verifies the existing heartbeat_only.frame_v2
produces the21-byte v2/sys1/comp191 heartbeat. These are code/source evidence,
NOT a second physical negotiation or capture. No safety gate was weakened.

Preferred next implementation: separate finite heartbeat-only negotiation before
strict MAVLink2 logging. Reuse StageA frame_v2, sole-owner UART/raw evidence and
fresh disarmed/CRC/source guards. During bootstrap accept ONLY verified PX41/1
disarmed heartbeat for heartbeat reply; no LOGGING_START/ACK/ODOMETRY. Wait for
verified outgoing PX4v2 heartbeat before the strict logging state. Preserve
same-read armed/CRC veto, timeout, no flush, byte evidence and exact restoration.
Test initial v1, denied negotiation/timeout, stale/armed/signed/foreign/CRC-bad
frames and queued prefixes offline before any further physical attempt.
This phase is PLANNED, NOT IMPLEMENTED, DEPLOYED OR HARDWARE-VALIDATED.
Do not rerun this frozen one-off coordinator or unchanged87-test PTY precheck.

## Restoration and independent verification

PX4 original parameter-referencing UART command restored to115200/5760B/s and
all backed finite stream rates restored; parsed configured mapping identical.
Original `logger start -b 64 -t -m all`, idle187 subscriptions before/after.
Other UART/USB startup commands unchanged; flow/ToF ttyS3 remains115200,
RX3548.3B/s, source1/88 msg106/132~48.2Hz, cumulative lost0 in final snapshot.
Removed only our166-byte topic file and two newly-created empty directories;
contents recoverable from topics-readback.txt and existing proposal. Existing SD
logs/parameters retained. Eight SDLOG values unchanged. Final Disarmed/EV_CTRL0.
M3C exact termios unchanged, no owner/PID/output/preflight from a receiver launch.
Remote board_after.json and local copied bytes preserve this evidence.

Fresh commands:

```text
py -3 -m unittest discover -s .maixpy/imu-uart-retry-20261011 -p test_scope.py -v
5 tests PASS; Python exit0 (scope-green-02.txt).
.maixpy/imu-offline-20261008/venv/Scripts/python.exe .maixpy/imu-uart-retry-20261011/diagnose_protocol.py
exit0; synthetic reproduction and source assertions (protocol-diagnosis.json).
.maixpy/imu-offline-20261008/venv/Scripts/python.exe .maixpy/imu-uart-retry-20261011/verify_evidence.py
exit0; restoration VERIFIED, receiver_launched=false, accepted_capture_seconds0;
18 old trial hashes,14 frozen reassembly hashes,16 deployed source hashes verified.
```

StageA/B report hash unchanged:
d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f.
Old Bad-prefix trial remains intact. Reported zero received records means NO
CAPTURE, not measured100% loss or successful loss-free data. Clock/tail/source/
observation-model/OpenVINS readiness UNKNOWN/unqualified.

## Preserved helper failures and provenance

Incorrect initial probe path exited before opening the physical UART. Board
version probe used absent pyulog.__version__; corrected to installed dist-info
metadata after checking package files. SCP/coordinator were also invoked without
the missing preflight file and exited before creating a session/configuration.
One inline SSH quoting diagnostic failed before executing Python. Initial verifier
used nonexistent frozen hashes.json; corrected to existing14-entry manifest.json.
All failed logs retained. PowerShell native-stderr decoration appears even for
successful unittest output; explicit saved Python exit0 is the test evidence.

Raw outputs are coordinator.jsonl/coordinator-console-02.txt, board-preflight.json,
board-after.json, topics-readback.txt, verification.json and protocol-diagnosis.json.
Source copies inspected here are locally saved representations documented in prior
exact-hash reports, not newly fetched pristine git blobs. No new source download.
Mutable docs were snapshotted in repo-before before additive notices. This new
manifest scopes this folder; earlier manifests remain historical snapshots.
No commit/push or Vault access; VAULT_UPDATE is only an import proposal.
