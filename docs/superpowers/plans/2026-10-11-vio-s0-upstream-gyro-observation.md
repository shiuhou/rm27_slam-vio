# VIO-S0 upstream gyro observation — 2026-10-11

User `設計完直接上真機吧` authorizes designing and then executing ONE bounded
stock-firmware bench observation. No firmware/parameter/sensor-rate/selection,
wiring, fusion, ARM/flight, camera/calibration/VIO/Stage C, dependency or push.
Same propellers-removed bench confirmation applies unless the assembly changed.

## Question, not a proposed fix

The completed fixed2500Hz-reader control retained two gyro coverage holes and
two logger generation-skip increments. Do not repeat that reader comparison.
Add full-rate selected `sensor_gyro` instance0 to the same eight-topic log, so
the upstream SI gyro timestamps can be compared with downstream `vehicle_imu`.
SI gyro is driver averaged/rotated, not untouched ADC. It has queue8 versus
vehicle_imu queue1. No new independently serialized accel endpoint is available.

This is an OBSERVABILITY experiment, not a one-factor fix comparison. Observer
load can itself change scheduling. Aggregate logger message_gaps will now cover
TWO full-rate topics and MUST NOT be attributed solely to vehicle_imu. An intact
observed upstream SI series across a downstream hole narrows its location; it
does not distinguish an unpublished integration from a skipped logger copy or
measure actual wake/read generations. No hole observed is not loss-free proof.

## Feasibility and unchanged gates

Exact SensorGyro serialized fields sum44 bytes; ULog data record adds5. At a
conservative700Hz:34300B/s. vehicle_imu has60 serialized bytes plus5, at200Hz:
13000B/s. LOGGING_DATA packs249 ULog bytes into267 MAVLink2 wire bytes. With a
conservative3000B/s diagnostic reserve, modeled demand is about53.7kB/s.
921600/8N1 capacity92160B/s. MAVLink ULog's finite100ms quota must be checked
against matching source; temporary link budget80000B/s is chosen for quota
headroom. Matching `mavlink_main.h:498` passes0.7 to MavlinkULog; its constructor
uses ceil(0.1*0.7*budget/267), so80000 gives21frames/100ms (56070wireB/s quota).
This is NOT an observed throughput or burst guarantee. Full-rate accel
is deliberately excluded to avoid near-saturation. No UART/SD buffer enlargement.

>=200Hz, no unexplained coverage loss, identity/calibration stability, explicit
clock/accel/tail/model evidence and OpenVINS admission remain unchanged. Stage C
closed. Synthetic fixtures cannot pass physical gates.

## Execution checklist

1. Preserve before-state reports, old manifest, Stage A/B and runtime hashes.
   Work in requested existing dirty checkout; do not stage/commit or replace
   unrelated changes. Keep a separate `.maixpy/imu-upstream-gyro-20261011` packet.
2. Test-first: exact command/profile guards, bandwidth calculation, source-window
   diagnosis including upstream gaps/partial windows, identity/order/nonfinite
   refusals, and no false source/clock/model PASS. Reuse controller/PTY tests.
3. Fresh read-only M3C/PX4 audit: hashd6f12ad1 full match, selectedBMI0880 IDs
   6684690/6946834, Disarmed/EV0, idle logger, original UART115200 and other ports,
   exact streams/SDLOG backup, readable SD and actual absent custom path,
   unowned M3CttyS2/not console. Any mismatch stops before mutation.
4. Isolated M3C software deployment, source-byte parity and new tests. No MaixPy
   launcher/stop-all, no new dependencies. UART runner remains same-owner with
   finite heartbeat-only v2 negotiation and existing START/STOP/ACK protocol.
5. ONE60s normal receive window: endpoints921600/8N1/raw/no flow, temporary PX4
   budget80000, same reduced telemetry, MAVLink-only logger fixed2500Hz and the
   original8topics plus `sensor_gyro 0 0`. Read back uploaded bytes and exact
   commands. Independent USB safety monitoring. No automatic retry.
6. Finally stop only our receiver/logger and restore exact original commands,
   stream map, custom-file absence and M3Ctermios; preserve flow/ToFttyS3 and USB.
   Only our temporary topic file/created empty directories may be deleted.
7. Hash/size transfer parity, raw MAVLink replay/CRC/sequences/TX counters, ULog
   framing, source rates/timestamps/identity, gyro-hole source windows, aggregate
   counter brackets, CPU/UART diagnostics. Do not equate read receipt and latency.
8. Update RESULT/HANDOFF and root HANDOFF/VAULT_UPDATE/latest pointers additively;
   verify original bytes and seal manifest. No further physical trial this turn.

## Decision after observation

- Upstream gap: source/observer completeness unresolved; do not blame logger only.
- Upstream series locally intact across an IMU hole: narrow downstream integration/
  subscriber boundary; exact trigger remains UNKNOWN without generation/Run trace.
- Clean finite run: useful observation only; no frequency/continuity gate waiver.
- Firmware-level bounded RAM trace, if later justified, requires separately
  scoped firmware approval and reproducible build/rollback; it is NOT authorized.
