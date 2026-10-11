# Next source observability design — NOT built/flashed/approved

## Evidence requiring a different observation method

Stock vehicle_imu-only streaming produced clean60s UART delivery but two logger
generation-counter increments/gyro holes under fixed2500Hz reading. Adding full
sensor_gyro at modeled~54kB/s caused one sender rejection at header→normal
transition, despite921600 capacity. More live topics are not the preferred next
diagnostic. A scheduling/queue trigger remains unobserved; changing IMU rate or
raising polling again is not evidence-based. Stage C stays closed.

## Proposed minimum diagnostic build, only after firmware authority

Base exact d6f12ad1 and matched submodules/board configuration. No queue length,
priority, polling frequency, sensor ODR/selection/calibration, EKF or message
semantics changes. Add compile-time-disabled-by-default RAM tracing, explicitly
enabled only in the diagnostic build. No new custom wire protocol or continuous
topic logging. Original binary must be supplied/identified/hash backed up first;
reported source hash alone is not a reproducible original binary/rollback.

Two independent bounded rings, one writer each:

- Logger ring: recent vehicle_imu copies, HRT at loop begin/copy/end, prior and
  consumed uORB generation, copied publication/sample timestamps, last successful
  copy time and loop's max elapsed time. Trigger on generation discontinuity.
- VehicleIMU0 ring: Run begin/end HRT; gyro/accel consumed generations and sample
  endpoints; counts consumed per Run; separate latest accel/gyro endpoints,
  readiness flags; actual publication/sample-end time, each own integral dt,
  calibration counters and an internal publication ordinal for association.

Size budget initially<=24KiB total (e.g.256×32B logger +256×64B IMU records).
Fields must be packed/sizeof checked BEFORE accepting this proposed layout.
Do not pretend it holds a whole60s trace. Ring overwrite count, oldest/newest
ordinal, disabled/frozen status and trigger HRT must be exported. Freeze both
rings on one source/logger trigger with a small explicitly bounded post-trigger
tail; preserve module-local writer ownership, memory ordering and cross-task
freeze races. No locks/allocations/printing in sensor or logger hot path. Overflow
or unavailable association is UNKNOWN, not silently dropped. Lifecycle/reboot
and calibration changes segment the trace. Actual generation jumps remain
EVENTS, not inferred ADC lost-sample counts.

After STOP, dump the frozen records over USB console using a read-only bounded
command. UART vehicle_imu-only treatment remains same as prior clean transport;
do not carry this failed80000/rawgyro observer profile forward. Before/after
heap/task stacks, timing overhead, integration cadence and safety must be compared
with the original image; RAM/CPU assumptions are not acceptance evidence.

## Offline work required before a later physical step

1. Pin full source/submodules and verify original rollback file/build inputs.
2. Test ring wrap/freeze/post-tail/concurrency/lifecycle and binary/text output
   integrity with synthetic labeled fixtures; bound all memory/counts.
3. Derive exact hook locations/field availability from source; confirm logger
   generations and per-publication ordinals can be associated by exact FC-clock
   timestamp without inventing an accel endpoint or clock mapping.
4. Build both trace-disabled and trace-enabled candidates. Review patch and
   artifact hashes; no upload until firmware authority and rollback exist.
5. Existing200Hz/source completeness and OpenVINS admission requirements unchanged.

## ONE next physical step, conditional and NOT performed

After separate explicit diagnostic-firmware approval and completed offline gates,
connect PX4 USB + existing M3C UART bench link and perform ONE bounded disarmed
trigger-trace comparison, then restore the identified original firmware/config.
It will distinguish actual logger late-copy/generation overwrite from VehicleIMU
publication/integration scheduling, subject to trace overhead and finite window.
This step is not authorized by the completed stock-firmware trial, and no fake
PASS can be obtained merely by reproducing a synthetic ring fixture.
