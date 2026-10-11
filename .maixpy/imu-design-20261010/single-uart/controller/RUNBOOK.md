# Next physical trial — PLANNED, NOT EXECUTED / NOT APPROVED BY OFFLINE TESTS

Latest revision: `../../../imu-negotiation-fix-20261011/VALIDATION.md`.
120 research-Linux tests pass (7 PTY),113 Windows pass/7 platform skips.
This NEW negotiation revision has NOT been deployed/tested on M3C or physically
captured. Prior87-test board PASS is a different preserved revision. One original
physical attempt failed on startup bytes; a later approved preparation aborted
before launching M3C on a premature outgoing-v2 gate. Preserve both RESULT/manifest.
This runbook now describes a separately approved retry, not authority to rerun
the old one-off coordinator. New startup policy bounds synchronization to5s and
65536 input bytes, preserves unframed regions, and never recovers after the PX4
heartbeat framing boundary. All same-read safety/CRC faults still veto START.
No input flush. Startup completeness is NOT_MEASURED_PRE_START, not loss-free.
Plausible headers/bodies wait; unknown/CRC-rejected complete candidates are
excluded whole rather than scanning payload. Saved21 + one heartbeat still waits;
enough subsequent bytes and a later verified heartbeat before5s are required.
Timeout is a valid fail-closed outcome; do not auto-retry or weaken the policy.

This refines `../reassembly/PROPOSED_TRIAL.md`, not a second experiment. Required
devices: existing M3C↔PX4 UART plus independent PX4 USB console; no spare UART.
Obtain specific permission for one temporary921600/8N1/no-flow,46080B/s software
budget and MAVLink-only minimal logger trial. Do not infer it from software tests.
No firmware/parameters/wiring/camera/fusion/setpoints/arming operation.

## Preflight and reversible preparation (independent USB owner)

1. Props removed, fresh commander Disarmed and EKF2_EV_CTRL0; exact firmware
   d6f12ad1c4f70ad3230afd7d86e971421e02fef4. Store actual command outputs, not only JSON.
2. Check source selection/vehicle_imu instance0 gyro6684690/accel6946834 and actual
   publication rate/counters/CPU. A different ID/instance stops the trial; never
   change sensor selection/integration rate to fit the tool. ~198Hz is not strict
   >=200Hz PASS. Preserve heartbeat/SYSTEM_TIME streams for safety/epoch checks.
3. Record exact current MAVLink instance `/dev/ttyS2` start command and per-stream
   rates, flow/ToF `/dev/ttyS3` ownership, logger start command/backend/idle state
   and topic file bytes or absence. If existing recording/another logging client
   active, refuse; don't stop someone else's capture. Retain all SD logs. Do not
   restore old-card/old-firmware or unrelated flight parameters.
4. Confirm both endpoints support921600 and sole UART ownership. Restart ONLY
   the PX4 wired instance, never stop-all; candidate runtime command is
   `mavlink start -d /dev/ttyS2 -b 921600 -r 46080 -m onboard -Z -x` after scoped
   `mavlink stop -d /dev/ttyS2`. This is not a substitute for backing up the actual
   previous command/streams. Read back mode/baud/datarate/flow and unrelated ports.
   Before launching the peer, outgoing MAVLink version may be1 OR2: `-Z` means
   flow-off only, and matching PX4 auto-upgrades after incomingv2. Do NOT repeat
   the frozen retry coordinator's premature version2/RX readiness requirement.
   Use a new reviewed/scoped coordinator; never rerun either dated one-off helper.
5. Apply byte-readback-verified minimal topic list from the existing proposal.
   Candidate logger `logger start -b 64 -t -m mavlink -p vehicle_imu`, NOT default
   all-topics/file logging; poll instance0 must be confirmed. Do not call logger on
   or ARM. Session LOGGING_START initiates the MAVLink backend; no SD capture.
6. Before opening the real UART, run the current120 tests on the M3C's existing compatible
   environment (PTY only, no physical port) and preserve versions/output. Research
   Linux success does not certify M3C driver support/CPU. No production install.
   Deployment must preserve repository relative layout for shared imports; don't
   replace the existing heartbeat/ODOMETRY deployment. The old55-test M3C PASS
   predates the synchronization change; the subsequent87-test M3C PASS predates
   negotiation. Neither qualifies this120-test changed revision.

Populate a new preflight attestation from actual USB readback and backup evidence.
`prepared_m3c_monotonic_ns` must be obtained on this M3C after checks, within60s of
launch. It is a freshness/host-domain check, not a clock map or authenticated proof.
Template intentionally fails until actual disarmed/EV0/props/backup fields are set.
The new heartbeat-only bootstrap is separately explicit: actual operator authority
must cover it, `heartbeat_negotiation_approved` must be boolean true, and the CLI
must use `--negotiate-mavlink2`. A template/test/flag is not permission. Default
remains strict v2-first. No global protocol/parameter change is necessary.

```sh
python .maixpy/imu-design-20261010/single-uart/controller/uart_session.py \
  --trial-approved --negotiate-mavlink2 --preflight actual-preflight.json --seconds 60 --output NEW-capture-dir
```

CLI opens only `/dev/ttyS2` at921600; it does not prepare or restore PX4 settings.
60s begins after accepted START plus first unACKed data. Initial/startup/cleanup
windows are separately bounded. No automatic retry. No ODOMETRY in this trial.
One same-owner descriptor validates CRC/unsigned PX41/1 identity and Disarmed
before emitting only companion MAVLink2 HEARTBEAT1Hz. Initial/negotiation total
deadline5s is not reset by v1 heartbeats; safety freshness2.5s still applies.
Only initial HEARTBEAT/SYSTEM_TIME can usev1. Verified PX4v2 HEARTBEAT authorizes
one START; any subsequent relevantv1 is terminal, even in the same read. Logging/
ACK are alwaysv2. Whole-read armed/CRC/signed/uptime faults veto queued sends.
Preserve policy/start/confirmation events and actual write receipts; partial
bootstrap write is terminal/no retry. Receipt timestamps are not clock sync.

## Stop, restoration and evidence

On completion/timeout/error after its own START: session sends one STOP and observes ACK/tail briefly;
before own START it sends no STOP (including failed/expired negotiation).
finally restores exact M3C termios. If STOP/restore not confirmed, independent USB
control handles cleanup; do not silently retry or unplug while recording is active.
Then restore actual original topic bytes/absence, logger command/backend, PX4
wired-instance startup command and per-stream rates. Verify original baud/flow,
other instance ownership, logger idle, Disarmed and EV0. No PARAM_SET/save.

Preserve wire.jsonl, received-prefix.bin, summary, preflight and fresh before/after
USB outputs/source/logger/cpuload/selection counters. Preserve invalid bytes and
unACKed sequence gaps; never discard startup errors or pad/re-time samples.
Logger start resets performance counters in this source; do not subtract across
that reset or treat a smaller counter as a reboot. Record observation windows.

Offline post-analysis:

```sh
python .maixpy/imu-design-20261010/single-uart/controller/capture_report.py \
  NEW-capture-dir --epoch EXPLICIT-CAPTURE-BOOT-EPOCH --output NEW-report.json
```

Report actual source and receive rates, two dt/units/IDs, ordering, gaps/coverage,
calibration/clips, byte budget, CPU and ACK/header transition. Source/publication
timing uses FC HRT; UART receipt timing uses M3C monotonic and is not exposure time.
Header and post-stop completeness are separate. Known truncated-tail diagnostics
may count complete retained records only; failed session is not fixed by that view.

Qualify only the bounded accepted interval with independently supported source
coverage and no unexplained discontinuity, CRC, ordering, clip or calibration
change. If source/terminal counts remain unavailable, label completeness UNKNOWN
even with continuous packets. Exit0/framing-valid.ulg does not imply transport,
VIO, clock, model, calibration, fusion or flight PASS. Preserve original Stage A/B.
