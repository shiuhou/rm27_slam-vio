# ONE upstream-gyro PX4 → M3C observation — 2026-10-11

## Outcome

**FAILED: normal logging transport lost sequence287 at startup; the planned60s
observation did NOT complete. VERIFIED: that interval is attributable to ONE PX4
TX-buffer rejection, with no unaccounted successful writes. VERIFIED: restoration.
UNKNOWN: original vehicle_imu subscription-skip trigger. VIO-S0/P PARTIAL;
Stage C CLOSED.** No loss fix, frequency/clock/model or real VIO PASS.

User `設計完直接上真機吧` approved design followed by ONE bounded stock-firmware
bench observation. One receiver launch, no retry. Same bench propellers-removed
confirmation, independent USB Disarmed guard. No firmware/parameter/IMU rate/
selection/wiring/camera/calibration/ODOMETRY/fusion/ARM/flight, dependency, commit,
push or Vault action. Existing dirty main HEAD3ea1e16086965176db68b88e1c42990f92c5913e
and unrelated changes preserved. Engineering planning/debugging/test/verification
workflow kept before-state copies and original evidence; gates were not relaxed.

Plan: [upstream observation](../../docs/superpowers/plans/2026-10-11-vio-s0-upstream-gyro-observation.md).
This was source observability, NOT a repeated reader-frequency comparison.

## Design and fresh baseline

Actual PX4v1.17.0 full hashd6f12ad1c4f70ad3230afd7d86e971421e02fef4,
selected BMI0880 gyro6684690/accel6946834. Fresh commanderDisarmed, EV_CTRL0,
IMU_INTEG_RATE200, original idle logger/custom topic path ABSENT/readable SD.
Selected driver cumulative generation-gap counters accel1/gyro2 remained the
same in before/after status; retained sensor errors1/1 are NOT zero. No parameter
backup was applied. COM19/configured57600 is USB inspection, not physical baud.

Same fixed2500Hz MAVLink-only logger, original8topics plus `sensor_gyro 0 0`:
9topics/182bytes, uploaded/downloaded byte-identical before START. Same reduced
telemetry48 numerical streams removed, retained health/epoch streams unchanged.
Temporary wired endpoints921600/8N1/raw/no flow; PX4 link budget80000B/s rather
than previous46080. No UART ring enlargement, SD recording or source change.

The core18-source controller/parser/owner/START/STOP/admission implementation is
BYTE-IDENTICAL to the completed reader-control state. New explicit observation
validator checks actual80000 budget, then composes the existing unchanged source/
safety/freshness/fixed-reader guards; raw attestations still contain actual80000.
Only the scoped coordinator, receiver wrapper and offline diagnostics are new.
M3C isolated path `/root/rm27-controller-gyro-20261011.OaOhNe/`; no existing
deployment overwritten or MaixPy application launcher used.

Engineering estimate: gyro700Hz×49ULog bytes + vehicle_imu200Hz×65, ×267/249
MAVLink2 packing +3000B/s diagnostic reserve ≈53719B/s, below92160B/s nominal
8N1 capacity. Exact [mavlink_main.h:498](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_main.h#L498)
passes0.7; the saved constructor permits21frames/100ms at80000 (56070wireB/s
quota). These are models, NOT a live burst/free-space guarantee. Stock source
models USART3 TX800/799usable; three267B frames already exceed that with no drain.
No live ring occupancy or actual rejected-frame length was captured.

## Actual failure evidence

`download/physical-trial-01/summary.json`: receiverexit1/DONE, START and STOP
accepted, finite_framing_verifiedfalse. MAVLink2 negotiation succeeded first.
First normal LOGGING_DATA286 retained; next is288, not287. Global sequence19→21
has the matching missing20. Receiver immediately aborts/STOPs; accepted normal
first-to-last window0s, not60s. Six received normal frames span12.465875ms;
actual normal-start→STOP-write12.208167ms, not a useful source-rate measurement.

468 retained PX41/1 frames: all CRC checked, including19 initially unknown
LINK/EVENT/current-event frames using prior pinned exact-submodule XML.
Raw receive replay matches decoded rows;0 bad_data. Seven LINK_NODE_STATUS
snapshots/six intervals: total461 successful writes =461 observed frames,
0 unaccounted successful sends. The interval with the only sequence hole has
TX rejection0→1,96 successful writes/96 receipts and one missing sequence.
This verifies the send-buffer-rejection layer for this failure, not an electrical
fault or M3C dropped successful write. Before-first/after-last remain unobserved;
unsigned counters are not authentication or ADC sample-loss counts.

The source advances MAVLink global sequence before send_start; insufficient
FIONSPACE suppresses the write but increments rejection. Normal ULog send consumes
the ulog_stream record without backpressure/retry. Matching details/source pins
already exist in `../imu-gap-diagnosis-20261011/DIAGNOSIS.md`; they were reused,
not reimplemented. Exact burst/task/driver-drain trigger remains UNKNOWN.

Complete packet-local metadata inside post-failure reliable logging291 reports
`mavlink: ulog_stream messages missed: 0 events`. That supports the send-rejection
attribution, not whole-run source completeness.48 repeated reliable291 frames
are seen on raw wire after abort; summary retransmissions0 describes the accepted
prefix only. Do not claim zero retransmissions over ALL observed wire. No joining
of truncated metadata across missing packets or repairing/filling a lost packet.

Received wire94624B/6.230664045s≈15186.8B/s includes negotiation/reliable header/
STOP traffic, NOT steady IMU throughput. Low whole-window mean does not contradict
TX rejection. M3C CPU34 samples/8.068379s/3.05CPU seconds≈37.802% of ONE core,
peak observed RSS39915520B, max sample interval0.252424s; mostly startup/abort,
not60s steady CPU or proof against stalls. UART same-FD frame2→2, other reported
error counters0→0; RX2427725→2522348, TX26260→30976. Boundaries differ from wire
totals; do not infer exact physical byte loss from their one-byte difference.

## Source observability remains unresolved

Original failed prefix71226B SHA256
`93343246cbe63075680deb2575ef938f468ce789a46ee103bd65a32f336a4580`.
No framing-valid.ulg exists. An in-memory complete-record view excludes24 trailing
bytes and retains just4 sensor_gyro publications, ONE vehicle_imu integral, one
health/selection record and2 events. It is not an accepted or repaired dataset.
4 gyro publications each summarize3 raw samples; SI rad/s in board-FRD frame,
not untouched ADC. The single integral is body-FRD rad/m/s with own4553/4992us
dt and stable shown IDs/calibration1/1. One record cannot establish an epoch or
rate. NaN gyro temperatures are explicit NONFINITE_DIAGNOSTIC, not converted to0.

There is no logger_status record or adequate IMU window to correlate the previous
4460/4507us holes. Adding sensor_gyro creates TWO full-rate subscriptions, so any
future aggregate logger message_gaps must not be assigned solely to vehicle_imu.
Sensor/IMU source chronology, continuity and >=200Hz qualification were NOT tested
to acceptance by this aborted run. Original completed reader-control evidence
still stands; this higher-load failure does not change its clean60s transport or
prove why its two subscription skips occurred. No new accel endpoint, camera
mapping, noise/extrinsic calibration, OpenVINS compatibility or tail evidence.

## Restoration and tests

Independent `verification.json` exit0: exact original PX4 ttyS2 command115200/
budget5760/Onboard/no flow and full nominal stream map restored; original logger
`logger start -b 64 -t -m all` idle, eight SDLOG unchanged, custom path absent.
Deleted ONLY our182B topic file and two created empty directories (recoverable
from local topics/readback). Existing SD logs/params untouched. Other startup
commands unchanged, optical-flow/ToFttyS3 still comp88 msg132/106 receiving.
285 observed USB heartbeats allbase_mode29, fresh final commanderDisarmed/EV0.
No arming command; observations do not certify every instant. M3C exact termios
restored/no owner/no remaining receiver. Nine remote/local artifact hashes/sizes
agree;24 packaged source files agree before/after. Stage A/B hash unchanged.

Windows22 local tests:19PASS/3 POSIX skips; unchanged runner15PASS/zero skips,
34 passing tests total. M3C13tool+6observation+3scope+5realPTY=27PASS/zero
skips. Synthetic/PTY tests are software evidence only. The original full120
controller/root226 suites were not rerun or claimed new. New source-window tests
cover own-dt holes, upstream cadence gaps/partial windows, stable source/order/
calibration, actual budget/guard composition and no fabricated admission.

Preserved helper failures: system Python lacked pyulog (existing venv used);
initial absent-feature RED6/3; initial aggregate discovery resolved a duplicate
test_supervisor through old sys.path, fixed only the NEW coordinator import to
an explicit old-helper module. Independent verifier initially had an escaped
newline check and same-name analyze_failure circular import; fixed local tool
binding, no numerical algorithm, device source or capture changed. Verification
third run exit0. Correct new header downloaded once; two incorrect filename/fork
404 lookups did not change source. Archive future-time warnings reflect the
known unsynchronized M3C wallclock, which was not changed or used as clock mapping.

Final Windows log `tests-final-03.txt` repeats22 tests/19PASS/3 POSIX skips,
PythonExit0 after report updates. Offline `seal.py` records current file hashes,
old dated manifest verification, pinned source/core hashes, exact retained root
report bodies and Git diff/staging checks. `preservation-check.json` and
`manifest.json` seal this experiment snapshot; old manifests are not rewritten.
Its first helper check rejected Windows CRLF in a test-log marker; the second
expected an exit marker not captured in the verifier's JSON-only console.
Log decoding now normalizes line endings only and compares the complete printed
verification JSON to its artifact. A third check used the download path for the
attestation stored at experiment root; corrected to the same path mapping as the
independent verifier. Failed consoles are retained; raw data and byte-preservation
checks are not normalized or changed.

## Next decision

Do NOT rerun this dated coordinator or adopt this higher-load profile. Its mean
bandwidth feasibility did not protect startup bursts. Stock source observation
has exposed an observer-induced transport failure before the original question
could be answered. Preferred next source diagnostic is a bounded, trigger-frozen
in-RAM logger-generation/VehicleIMU Run trace, extracted AFTER stopping, rather
than adding more live UART topics. [Design only](NEXT_TRACE_PLAN.md); not built,
flashed or authorized as a firmware change. A changed firmware experiment needs
explicit firmware/build/rollback scope. No further physical action in this run.
