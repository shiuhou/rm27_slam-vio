# Residual subscription hole and source cadence — 2026-10-11

## Verdict / scope

**VERIFIED:** one retained gyro integration coverage hole aligns with the
logger's vehicle_imu full-rate subscription generation-skip counter.
**VERIFIED:** the saved stream is 197.215284 Hz, below the unchanged >=200 Hz gate.
**PARTIAL:** source cadence is quantitatively explained by variable integral
windows and consistent with the exact dual-integrator/callback logic; precise
Run/queue/poll timing remains **UNKNOWN**. VIO-S0/P remain PARTIAL; Stage C CLOSED.

Entirely OFFLINE: no SSH, COM/UART/device access, new capture, settings, firmware,
parameters, wiring, sensor rate/selection, camera/calibration/VIO, dependencies,
Git stage/commit/push or Vault access. No firmware fix or performance improvement
claimed. Existing dirty work and every dated experiment snapshot preserved.
Main HEAD `3ea1e16086965176db68b88e1c42990f92c5913e`.

Lean engineering/debug/TDD/verification workflow added only diagnostic code,
synthetic tests, saved-data arithmetic and reviewable local handoff. No production
controller/parser/admission changes. Vault templates were not accessed; local
task packet links the repository's existing research/evidence conventions.

## Inputs and provenance

Current-build evidence, NOT historical v1.15.2/BMI270:

- `../imu-uart-reduced-trial-20261011/download/physical-trial-01/framing-valid.ulg`:
  944329 bytes, SHA256
  `658287cb149e1afbd56c9df799807729cd0930e4943190a580fb08b42eebca06`;
  byte-identical received-prefix.bin, valid complete framing, no repair/retiming.
- Original reduced trial RESULT/coordinator/wire/analysis-02/verification-02
  establish exact build `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`, BMI0880 gyro
  6684690 / accel6946834, temporary MAVLink-only logger, configuration restoration.
  They are historical runtime observations, NOT fresh device readbacks this turn.
- 80 prior own / 36 external hashes verified before edits; six root pointer
  states saved byte-for-byte under repo-before. Original manifest unchanged:
  `4998a984647f0be93fba98b099b26c471c0b3916e6a90e7a74122baa9c45f6fd`.
- Exact local source: `../px4-v117-source-audit-20261009/source/new/`,
  `../imu-transport-20261010/src__modules__sensors__Integrator.hpp`, BMI088 driver
  copies in `../imu-design-20261010/`, and previous trial source supplement.
  14 relevant source hashes checked against saved manifests/provenance; no fetch.
- Stage A/B report hash unchanged:
  `d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f`.

## 1. The 4554 us hole is upstream of UART transport

Original zero-based retained rows 8091 -> 8092:

| Field | Before | After |
|---|---:|---:|
| timestamp_sample, gyro endpoint us | 17284902631 | 17284913148 |
| publication timestamp us | 17284902808 | 17284913378 |
| delta_angle_dt us | 4507 | 5963 |
| delta_velocity_dt us | 4991 | 4993 |

Endpoint separation 10517 us minus CURRENT gyro dt5963 us = **4554 us**.
The after-window begins at17284907185 us, leaving uncovered gyro interval
`[17284902631,17284907185]`. This is an interval calculation, NOT recovered data
or an invented missing publication timestamp/payload. Sum of retained gyro dt
excluding first record60041502 us plus this4554 us equals source span60046056 us.
No other positive residual >2 us or negative residual <-2 us.

Logger status increments1 ->2 within bracket17284868840 ->17285869165 us;
both surrounding IMU publication timestamps are inside it. Only vehicle_imu0
is interval0 in the actual eight-topic config; other configured subscriptions
are throttled. Source `logger.cpp:444-469` increments `_message_gaps` only for
full-rate subscription generation discontinuities. Events use a separate path
`975-1032`, not this counter. Thus the in-window skip is attributable to the
logger's vehicle_imu subscription, not another full-rate diagnostic topic.

`vehicle_imu` has live-saved queue depth1 (`uorb top`: #Q1); unlike SI gyro/accel
queues8. `uORBDeviceNode.hpp:225-260` copies latest data/generation for queue1.
If two publications occur before this subscriber's next copy, an intermediate
integral is overwritten for that subscriber. Each subscriber has its own cursor:
this does NOT prove the estimator or other consumers also missed the integral.

**Confirmed mechanism/layer:** latest-only subscription overwrite/generation skip.
**UNKNOWN trigger:** exact generation jump magnitude, logger scheduling/lock/loop
delay, poll wake/acknowledgment interleaving, or publisher burst at that instant.
The logger main loop copies each topic once, then `-p vehicle_imu` polls a separate
subscription and clears its notification (`logger.cpp:747-855,901-917`). Poll's
20 ms is a fallback timeout, NOT a hard50 Hz rate limit. No thread scheduling trace
was recorded. The initial counter1 precedes the first status; do not sum1+2 or
attribute that initial event to the in-window hole.

Saved transport analysis remains applicable after hash verification:5001 PX4
frames CRC checked, zero global/logging sequence gaps,64 LINK intervals successful
sends4980=received4980, no TX rejection. No LOGGING_DATA_ACKED was received during
the normal unacknowledged stream; reliable start/stop metadata blocking therefore
is not established as this mid-run trigger. No SD logging in this experiment:
the historical391 SD ULog dropouts are a DIFFERENT experiment. File-backend buffer
stats/dropouts0 do not prove source completeness or logger scheduling perfection.

Selected VehicleIMU cumulative accel/gyro generation-gap counters1/2 and sensor
error counts1/1 were unchanged before/after in saved readbacks. They are not zero,
and do not count the independent logger subscriber's skips or certify ADC loss0.
M3C average CPU21.48% of one core / PX4 median48.83% from prior verified data do
not exclude short scheduling stalls. No evidence justifies a firmware patch yet.

## 2. Why ~197 Hz despite IMU_INTEG_RATE=200

Saved initial parameter200; changed parameters0.11843 retained records over
60.046056 s sample span -> `(11843-1)/span` = **197.2152842145 Hz**.
Source-side one-second observations198/195/198 Hz support a genuinely sub200
publisher cadence, not merely a low M3C receive rate. Those snapshots do not give
an exact total publisher count. Full one-second retained bins range192..201.

Even a sensitivity calculation adding ONE record to the interval count gives
197.231938 Hz, still below200. This is arithmetic only: no sample inserted or
claim that the unlogged generation jump was exactly one.

Source-status median rates (measured by PX4 interval statistics, not independent
hardware sequence counters):

| Path | Gyro Hz | Accel Hz |
|---|---:|---:|
| Driver SI publications consumed by VehicleIMU | 665.639648 | 801.414246 |
| Raw-rate estimate from interval / message samples | 1996.918945 | 1602.828491 |
| Retained vehicle_imu paired integral publications | 197.215284 | same records |

The roughly3:1 gyro and2:1 accel ratios are FIFO-batch estimates, not individual
ADC records in this ULog. `sensor_gyro`/`sensor_accel` were NOT logged here.
Gyro mean SI period1502.314356 us, accel1247.794141 us.

Exact `VehicleIMU.cpp:681-739` rounds requested5000 us to3 gyro SI updates
(4506.943 us), then4 accel updates (4991.177 us). Model configuration:
gyro readiness minimum3756 us /3 updates, accel4367 us /4 updates;
gyro callback after3 unread updates; backup schedule4991 us. Integrator source
`Integrator.hpp:98` uses **sample-count OR minimum-dt**, not a fixed5000 us timer.
`VehicleIMU.cpp:167-268` publishes only when BOTH integrators ready, catches accel
up to the gyro endpoint, has latency/gap catch-up branches, and breaks after one
Publish per Run. Accel has no independent scheduling callback in this class.

This source explains why config200 is not an exact publication-rate guarantee.
Timing model uses saved mean periods and positive C-style half-away rounding;
it is NOT a bit-exact float32 scheduler simulation or a substitute for Run traces.

Observed original integral durations, classified by nearest measured SI period:

| Accel integral period multiple (INFERRED) | Records | Approx dt us |
|---|---:|---:|
| 4 | 11545 | 4991 |
| 5 | 37 | 6239 |
| 6 | 71 | 7487 |
| 7 | 190 | 8735 |

298 extended accel integrals,749 period-equivalents over the4-period baseline.
Residuals to this classification only-11.177..10.823 us; raw per-record sample
counts/endpoints are absent, so these are NOT exact missing hardware sample counts.
Gyro nearest multiples3:8019 /4:3554 /5:20 /6:154 /7:96. Ordinary3/4 gyro mixtures
are consistent with following the slower4-accel window, not inherently losses.

Excluding first record, retained accel dt totals60040750 us; modeled4-period
windows for11842 intervals total59105512.860 us. Extended windows add935237.140 us
over that baseline. This accounts quantitatively for most of the slower cadence
relative to model200.354 Hz: integrated data is packed into fewer, longer windows,
not simply thrown away as packets. Gyro span minus accel dt sum5306 us is NOT
an accel coverage-hole measurement: the independent accel endpoint is unavailable.
Publish-minus-gyro-end median218 us, max4794 us; this software interval is not
ADC latency or camera synchronization. No universal clock/ODR correction justified.

271 endpoint intervals >1.5x median are NOT271 dropped integrals: all but the
one4554 us residual are covered by their own variable gyro dt. Changing200 ->210
in the configuration model leaves the same3/4 updates, thresholds and callback;
blindly raising this parameter slightly is not a demonstrated fix (no parameter
was changed). Exact cause of the298 extended windows remains UNKNOWN without
original SI traces and Run/callback execution timing. Dual-clock phase/readiness,
queue accumulation and workqueue delays are candidate mechanisms, not separately
proven causes. No calibration change, clipping, nonfinite source vector, duplicate
or backward source/publication timestamps observed.

## Tools / validation

`diagnosis.py`: reuses existing strict ULog framing/schema/identity parser and
integral semantic audit; adds cadence accounting, source configuration model,
labeled period classification and counter brackets. Does not emit OpenVINS input.
Exclusive output prevents overwriting previous evidence. `verify.py`: independent
NumPy/pyulog arithmetic, raw-byte/parity, source pins and prior manifest audit.

Existing research Python3.12 / pyulog1.2.4 environment; no installs. Commands:

```powershell
$py = '.maixpy/imu-offline-20261008/venv/Scripts/python.exe'
& $py -m unittest discover -s .maixpy/imu-source-diagnosis-20261011 -p test_diagnosis.py -v
& $py .maixpy/imu-source-diagnosis-20261011/diagnosis.py --output <NEW-output.json>
& $py -m unittest discover -s .maixpy/imu-design-20261010 -p test_offline.py -v
& $py -m unittest discover -s .maixpy/imu-design-20261010/single-uart/reassembly -p test_ulog_mavlink.py -v
```

Fresh19 diagnostic +9 semantic +28 reassembly tests PASS, zero skips (56 total).
18 synthetic /1 real pinned-data test: synthetic fixtures are labeled and not
claimed as hardware/synchronization PASS. All Python exit0; verification exit0
checks80 own /36 external old files and14 relevant source hashes. Logs, analysis
and verification.json preserved. Unchanged broader/production/M3C suites not rerun.

Failures retained: RED17/18 unimplemented diagnostics; first GREEN17/18 passed,
one fixture incorrectly expected a9 ms interval to exceed1.5x the median of just
4.5/9 ms. Corrected fixture includes two normal intervals so its median is4.5 ms;
analysis threshold unchanged. Final19/19 PASS. Native PowerShell stderr wrappers
around unittest output are not failed tests; actual Python exit statuses checked.

## Remaining work and next diagnostic decision

OFFLINE attribution/arithmetic/tests complete for the available observations.
BLOCKED BY NEW EVIDENCE: exact logger read/poll execution at the skip and
VehicleIMU callback/Run sequence producing extended windows were not recorded;
source generation magnitude and accel endpoint cannot be recovered from this log.
Do not fabricate them, interpolate4554 us, retime to5 ms, relax200 Hz or claim
OpenVINS suitability. Source/clock/model/tail gates remain unresolved.

Preferred NEXT comparison to scope separately, NOT executed or newly authorized:
keep selected sensor, parameters, firmware, temporary921600/46080/reduced streams
and same topics; vary ONLY logger reader from `-p vehicle_imu` to fixed polling
`-r 2500` with fresh backup/restore and heap/CPU monitoring. Use the same controller
and saved-wire auditing; do not replay Stage A/B. Compare generation counter delta,
gyro coverage residuals, retained/source rates and TX counters. This can test
logger wake/read behavior, not by itself fix or prove the source cadence. A later
source-level trace would require separately scoped higher-load SI logging or
instrumented firmware; neither is authorized here. No physical action requested
or performed this turn.
