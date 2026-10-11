# ONE fixed-reader PX4 → M3C control — 2026-10-11

## Outcome

**VERIFIED:** ONE 60 s transport control completed and settings restored.
**FAILED hypothesis:** replacing `-p vehicle_imu` with `-r 2500` did NOT eliminate
the observed logger subscription skips. **PARTIAL:** VIO-S0 still fails the
unchanged >=200 Hz and retained gyro-continuity gates. Stage C remains CLOSED.
VIO-P and Stage A/B are unchanged. No real VIO/synchronization qualification.

User `ok execute` approved the existing reader-control plan. Same bench
propellers-removed confirmation; independent USB Disarmed monitoring. ONE receiver
launch, no physical retry. No parameter/firmware/sensor selection/rate/wiring,
camera/calibration/fusion/ODOMETRY/ARM/flight, dependency, commit/push or Vault action.
Main working-tree HEAD remains `3ea1e16086965176db68b88e1c42990f92c5913e`.

## Fresh identity, baseline and controlled change

PX4 v1.17.0 `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`, NuttX
`fb2fadf6f599c1406f052db013efd00a2518e72c`, selected BMI0880:
gyro6684690 / accel6946834. Disarmed, EKF2_EV_CTRL0, idle original logger,
readable SD and original custom topic configuration ABSENT. No old parameter
backup was applied. COM19/configured57600 is USB CDC, NOT physical UART baud.

Only data-path treatment differs from the frozen reduced control:

```text
before: logger start -b 64 -t -m mavlink -p vehicle_imu
candidate: logger start -b 64 -t -m mavlink -r 2500
```

Fresh `ps` verifies the candidate command before START. Same166-byte/eight-topic
file uploaded/downloaded byte-identically. Same temporary wired ttyS2 endpoints
921600/8N1/raw/no-flow, PX4 budget46080B/s/Onboard, same48 nonessential numerical
streams removed; HEARTBEAT1/SYSTEM_TIME1/TIMESYNC10/LINK_NODE_STATUS1/SYS_STATUS5/
STATUSTEXT20 and six unlimited entries retained. Other UARTs/flow/ToF unchanged.
MAVLink-only logging is NOT SD recording; `-b64` is not UART ring capacity.
2500Hz is requested logger wake cadence, NOT IMU publication rate or a measured
400us execution guarantee. The exact logger.cpp:665–685,900–935 selects HRT/
semaphore instead of the separate poll cursor; message_gaps semantics are unchanged.

Runtime code change is ONLY an additive strict `validate_preflight` reader profile
in uart_session.py. Legacy defaults, owner/parser/ACK/STOP/admission unchanged
(AST equality outside validator verified). New coordinator/receive wrappers reuse
the frozen reduced trial. Before bytes and failed helpers are preserved.

M3C final isolated deployment:
`root@10.18.198.1:/root/rm27-controller-reader-20261011.VZQm1z/`.
First software-only deployment `.wiIbkI` has NO physical capture and remains.
27 deployed sources/11 tool hashes match; Python3.13.2, numpy2.2.6,
pymavlink2.4.49, isolated pyulog1.2.4. No global installs. Board wall clock remains
different from Windows (tar timestamp warnings); no clock sync/change is claimed.

## Actual comparison — no repaired, interpolated or retimed data

Baseline is the retained prior log, NOT recaptured. Trials are at different times,
not randomized/repeated A–B–A; event counts do not establish statistical worsening.

| Metric | Prior poll reader | Fixed2500 reader |
|---|---:|---:|
| Normal LOGGING_DATA receipt span s |60.016212|60.009399|
| BMI088 integral records |11843|11837|
| Sample-end span s |60.046056|60.049324|
| Retained effective Hz |197.215284|197.104634|
| Observed logger message_gaps increments |1|2|
| Gyro coverage holes >2us |1|2|
| Uncovered gyro sum us |4554|8967|
| Global MAVLink/logging sequence gaps |0/0|0/0|
| TX rejection increments / unaccounted writes |0/0|0/0|
| ULog O / logger writer dropouts |0/0|0/0|

Current hole endpoints/own CURRENT gyro dt, zero-based retained rows:

| Rows | Before/after sample-end us | Interval us | Current gyro dt us | Residual us |
|---|---|---:|---:|---:|
|1373→1374|31667644280→31667654750|10470|6010|4460|
|5280→5281|31687386743→31687397259|10516|6009|4507|

Each surrounds a logger1→2 or2→3 generation-skip bracket in comparison.json.
Only vehicle_imu0 is full-rate in this topic list; exact logger.cpp:443–459 counts
a skipped-generation EVENT, not its magnitude. This establishes logger subscription
path loss despite clean UART delivery, NOT exact hardware missing-sample counts
or a proven scheduler cause. Status window31660665747→31719685088us is59.019341s;
counter starts at1, so pre-first and post-last behavior is unobserved. No backwards/
duplicates/overlaps, nonfinite source vectors, clip flags or calibration epoch change;
IDs stable, calibration counts1/1. Driver/status errors stayed1/1, NOT zero;
selected VehicleIMU cumulative gaps accel1/gyro2 unchanged. No inappropriate
perf subtraction across resets. Accel coverage remains UNKNOWN without its endpoint.

275 long endpoint intervals are NOT275 losses. In source-timing.json the same
tested model yields three gyro/four accel updates, nominal accel4992.616us
(200.296Hz), but317 retained accel integrals have longer inferred5–7-update
windows. These are status-derived period classifications, NOT hardware counts.
Mean endpoint5073.447us and variable fully covered windows explain why simply
eliminating two skips would not prove a >=200Hz publisher. Precise VehicleIMU
Run/readiness timing is still UNKNOWN; no rate parameter adjustment is justified.
Covered gyro60040357us + holes8967us exactly equals span60049324us. Gyro span
minus accel dt sum10263us is NOT an accel coverage measurement. Integrals are
calibrated/rotated/coning-corrected rad and m/s with own microsecond dt; diagnostic
division is not automatic OpenVINS sample admission. No camera clock or dataset.

## Transport and CPU evidence

Receiver DONE/errornull/exit0, START/STOP accepted,3793 logging packets,
0 retransmissions, complete framing. Normal first-to-last receipts60.009399195s;
normal transition→actual STOP write60.008451653s. Summary60.441655778s includes
reliable stop metadata, not just normal data. Pre-START sync excluded1byte,
explicitly outside capture completeness; no source-tail guarantee from STOP ACK.

4984 retained PX41/1 frames all CRC-verified, including96 initially unknown
frames checked offline with pinned firmware-submodule schemas.0 bad_data events,
0 global/logging discontinuities.65 LINK snapshots/64 intervals:4979 successful
write increments equal4979 received frames;0 TX rejection increments/unaccounted
sends. Boundaries before-first/after-last and authentication remain unverified.
Complete packet-local postflight ulog_stream messages missed0.

3458 normal LOGGING_DATA frames /920790 wire bytes (~15344B/s for that class);
956902 total frame bytes within the normal receipt window (~15946B/s).
Midpoint PX4 TX15999.1B/s,txerr0,rate multiplier1,v2. Not a115200-rate validation;
921600/8N1 nominal capacity92160B/s does not prove burst-free scheduling.
Logging packet READ intervals: median16.2695ms,p9524.4374,p9927.0159,max31.3762;
not IMU cadence or end-to-end latency. No FC↔M3C clock mapping.

Receiver266 samples/66.512376s,14.5CPU seconds =21.800454% of ONE core average,
peak observed RSS43479040bytes, max sampler interval0.252789s. Includes startup/
normal/stop, not exact process lifetime or absence of brief stalls. PX4 cpuload60
samples,50.444–51.497%, median51.0323% (prior~48.83%). Higher observed aggregate
load does not measure logger wake/read latency or prove starvation.
Same-descriptor UART counters rx1378546→2427724,tx19467→26259; frame2→2,
parity/overrun/buf_overrun/brk0→0. No new reported UART error; byte accounting
boundaries differ and are not exact physical loss/latency evidence.

## Transfer, restoration and verification

10 remote/local hash+size entries agree. Original prefix/framing-valid.ulg identical:
944060bytes, SHA256
`ef75d77e74c5183f87c56ed0ab0d137a03fd17c4fa2a75b8ed5fe78eda94e394`.
Wire10733430bytes, SHA256
`68a782052cfba3549ec8f82527843589a13ef34017130cc5a6bd359bf3fb0d8e`.
Raw bytes/unknown rows unchanged; no repair/fill. Changed parameters0.

Fresh restore: UART3 ttyS2 back115200/budget5760/Onboard/no-flow and EXACT original
nominal stream map; original logger `logger start -b 64 -t -m all` idle187
subscriptions. Eight SDLOG unchanged, original custom path absent. Removed ONLY
our166-byte topic file and two created empty directories; readback preserves
recoverable contents. Existing SD logs/parameter files untouched. M3C exact termios
restored, no owner/live receiver. Other startup commands and flow/ToF ttyS3
comp88 msg132/106 retained.342 monitored USB heartbeat modes all29; pre/post
Disarmed/EV0. Retained armed false/state1. Observations do not certify every
instant, but no arming/control commands were sent.

Windows new profile8/comparison7 + relevant runner15/diagnosis19/semantic9/
reassembly28 tests PASS (86 distinct tests), zero skips in these targeted suites.
M3C root-tool13/profile8/comparison7/runner15/realPTY5 tests PASS (48), zero skips.
analysis, source-timing and independent verification all exit0. Not a repeat of
unchanged120-test full controller/Stage A/B/root regressions; not claimed as such.

Failures preserved: board guard tests initially imported Windows bench_io/pyserial
in two test fixtures; replaced device import with a denied module boundary, no
runtime guard weakened/install. A Windows launch used system Python without
pyulog; corrected to existing research venv. Old read-only probe refused EV
query before device access; permitted probe and coordinator fresh EV read used.
Aggregate discovery collided with copied test_supervisor names after sibling
path setup; targeted isolated suite launches passed. No retries of acquisition.
NONFINITE_DIAGNOSTIC explicitly preserves NaN gyro health temperature; integral
vectors remain finite. PowerShell stderr wrappers are not Python failures.

## Decision / remaining boundary

Do NOT adopt fixed2500Hz as a fix: its necessary no-skip prediction failed.
The separate poll cursor is therefore NOT necessary for this observed failure;
its possible contribution in other runs is not excluded. SD media and UART
packet delivery cannot explain these retained, counter-bracketed subscription
holes in this MAVLink-only run. Exact logger read latency, generation jump size,
queue overwrites and publisher Run timing were not recorded and cannot be
recovered. Queue1 vulnerability/source scheduling remain hypotheses, not proven
root causes. No universal loss-free or source-rate claim.

Next work: scope a source-observability change, not another blind reader-rate
trial. Required evidence is per-reader consumed/published generation and actual
wake/read timing plus per-sensor endpoints/VehicleIMU Run readiness. A firmware/
queue/trace treatment needs a separate reviewable plan and approval before
execution; none is implemented or authorized here. Do not rerun coordinator.
No sync/calibration/real VIO or full Stage C until original input gates pass.
