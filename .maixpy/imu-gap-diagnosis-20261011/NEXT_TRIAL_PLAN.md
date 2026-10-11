# Proposed single-factor reduced-telemetry trial — NOT EXECUTED

## Objective and authority

One future maximum60s normal-data experiment to test whether competing Onboard
telemetry triggers the confirmed PX4 FIONSPACE/send-buffer rejection. Devices:
existing M3C ttyS2↔PX4 UART3 and PX4 USB for independent Disarmed checks/restore.
No rewiring. Requires scope approval for this NEW physical trial; prior ONE
capture authorization was consumed. Current offline work is not permission to
run this file or any old single-use coordinator.

Do not change firmware, parameters (including EKF2_EV_CTRL=0), IMU selection/
rate/calibration, wiring, fusion or fly/arm. Earlier prop-removal confirmation
applies only if that same bench state persists. Stop on an uncertain safety
state, wrong firmware/IDs, another UART owner or backup/readback failure.

## One factor, all other conditions retained

Keep exact firmwared6f12ad1c4f70ad3230afd7d86e971421e02fef4 and current verified
BMI088 instance0 gyro6684690/accel6946834 (re-read; do not force selection if changed).
Temporary wired endpoints921600/8N1/raw/no-flow, PX4 budget46080B/s/Onboard,
same single-owner controller/reliable header/normal data policy and logging topics:

```text
vehicle_imu 0 0
vehicle_imu_status 100 0
sensor_selection 100 0
timesync_status 100 0
logger_status 1000 0
cpuload 1000 0
vehicle_status 1000 0
actuator_armed 1000 0
```

Same logger `logger start -b 64 -t -m mavlink -p vehicle_imu`; no file backend,
SD recording or logger on. The unchanged64KiB option is NOT UART buffer size.
Same finite handshake/CRC/ordering/freshness/timeout/fail-stop gates. Do not
install dependencies or repeat unchanged120-test board precheck unnecessarily.
Verify source18-file parity and run any newly changed OFFLINE scope/sampler tests
before hardware. Use new output/deployment/coordinator paths, not old helpers.

ONLY treatment: reduce nonessential PX4 outgoing stream telemetry. Preserve
HEARTBEAT1Hz, SYSTEM_TIME1Hz, TIMESYNC10Hz, LINK_NODE_STATUS1Hz, SYS_STATUS5Hz
at their backed-up nominal rates, plus asynchronous STATUSTEXT/COMMAND_LONG/
command acknowledgements/events and the ULog channel. Preserve event-driven
entries whose nominal rate is not numerical; do not guess/zero them. Disable
other numerical streams on **this wired instance only**, including HIGHRES_IMU,
ATTITUDE/quaternion, position and outbound ODOMETRY telemetry. This does not change
the sensor/topic source or Stage A/B implementation/parameters. Never stop-all
or alter optical-flow/ToF ttyS3, USB or unrelated instances. Keep STATUSTEXT at
its baseline rate so diagnostic/safety messages remain available.

Take a fresh original and temporary-high-rate nominal stream map before changes;
enumerate exact numerical differences, fail on unknown/nonfinite entries.
Freeze allowlist from those actual maps and the retained list above, not a
hardcoded blanket command. Read back the treatment map. Restore the freshly
backed-up ORIGINAL115200 instance and every nominal stream on exit, not merely
the default Onboard profile. This is a telemetry-load comparison, not proof
that one particular stream caused the old rejection.

## Instrument before START, not after failure

Retain existing raw RX chunks, exact MAVLink frames, TX messages, prefix,
attestation, sequence/freshness errors and actual START/STOP ACK times. Never
flush away bytes or repair/reorder/insert packets. Startup exclusion remains
explicitly separate from normal-data continuity.

1. Start M3C process CPU/RSS and `/proc` scheduling/context-switch sampler before
   launching capture; record wall/CPU clocks and sampling coverage. Sample from
   process birth through cleanup, including early failure. Read UART RX error/
   overrun counters with TIOCGICOUNT only if supported on this actual driver;
   unsupported/errors → UNKNOWN, not zero. Do not create another serial owner
   or read bytes through the sampler. PTY-test sampler behavior if code changes.
2. Decode all saved LINK_NODE_STATUS offline using pinned CRC117/PX4 semantics;
   collect a pre-START snapshot and continued counters. Observation callback
   must not delay acquisition. Missing diagnostic snapshots are a qualification
   limitation, not permission to infer zero errors. No firmware instrumentation.
3. Independent USB readback: firmware, Disarmed/EV0, selected IDs/source rates,
   logger/SDLOG/config presence and heap/cpuload before/after; one midpoint if
   run reaches it. Record actual overhead; no source poll/rate changes.
4. Compare logging sequence gaps with successful-write deltas/TX rejection and
   global sequence gaps. Keep logger message_gaps distinct from exact IMU loss;
   inspect complete packet-local postflight ulog_stream perf counter even if
   the failed session is not admitted. Never join across a missing chunk.

## Acceptance: separate transport and input gates

The original60s and >=200Hz/source/tail/clock/model gates stay unchanged.

- Treatment/setup: measured settings/maps match plan; same firmware/source IDs;
  original configs genuinely backed up, sole M3C owner, safety guard intact.
- Transport comparison:60s NORMAL-data duration actually completes; no logging
  sequence discontinuity, CRC/framing/order errors, or new TX buffer rejection
  from pre-START through observed stop counters. Successful-write delta equals
  retained frame count in all valid counter intervals; no unaccounted sends.
  Require source/ulog generation/dropout diagnostics separately, not just ACKs.
  Finite raw framing audit passes without shortened or repaired output. Any
  unobserved boundary/tail remains UNKNOWN; STOP ACK is not ULog EOF proof.
- Source input: actual selected BMI088 IDs/calibration stable, finite rad/m/s
  integrals and positive own gyro/accel dt, no clips/errors, increasing original
  timestamps, full retained integration-coverage audit and measured >=200Hz.
  A clean ~196Hz delivery may support the TRANSPORT comparison but still fails
  the original rate/input gate. Never retime to5ms or treat averages as raw samples.
- Performance report: actual whole and steady bytes/s separately, packet receipt
  jitter vs source dt separately, max gaps/order/loss, CPU/RSS/sampler coverage,
  exact version/device IDs/calibration and unit assumptions. Receipt minus PX4
  HRT is not end-to-end latency without a clock map.
- Restore/safety: independent fresh readbacks of original UART command115200/
  budget/mode/flow/streams, logger command/idle/allSDLOG/file bytes or absence,
  M3C EXACT termios and no owner; unrelated flow/ToF intact. Only owned temporary
  files/directories may be removed; preserve raw evidence and existing SD files.

First failure stops normal acquisition, then bounded cleanup in finally. No
automatic retry or follow-up matrix. Missing cleanup/backup evidence prevents
success claims. Do not run a camera, inject ODOMETRY, estimate calibration,
raise source rate or start Stage C within this comparison.

## Interpretation / next boundary

Zero rejection and clean delivery would support a practical single-UART capture
prototype, not establish OpenVINS suitability, continuous camera synchronization,
or firmware fix. A repeated rejection with near-empty competing telemetry
justifies further firmware-side queue/backpressure research; it does not authorize
a buffer/firmware change. If source remains below200Hz or has coverage gaps,
that is an independent source/logger qualification problem. Report honestly;
preserve failed bytes and stop at the remaining gate.
