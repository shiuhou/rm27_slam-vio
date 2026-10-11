# One reduced-telemetry PX4 → M3C trial — 2026-10-11

## Outcome and scope

**VERIFIED: this 60 s transport comparison completed without observed TX buffer
rejection or MAVLink/logging sequence gaps. PARTIAL: VIO-S0 input qualification
still fails the unchanged ≥200 Hz/loss-free-source gates. Stage C remains CLOSED.**

User's latest `do it` approved ONE instrumented comparison from the preceding
NEXT_TRIAL_PLAN. One receiver launch, no retry. Same bench propellers-removed
confirmation, independent USB Disarmed monitoring. No firmware, parameter,
sensor selection/rate, wiring, EKF fusion, ODOMETRY injection, camera, calibration,
ARM/flight, dependency install, commit/push or Vault access. Stage A/B is unchanged.

Current working-tree main HEAD `3ea1e16086965176db68b88e1c42990f92c5913e`.
Existing dirty controller/reports and unrelated camera_capture.py/tmp preserved.
Engineering verification/handoff workflow required exact before-state copies,
bounded cleanup, fresh readback and preserved failed helper output; it did not
change the acceptance criteria. VAULT_UPDATE remains a local import proposal.

## Fresh baseline and treatment

Actual firmware PX4v1.17.0
`d6f12ad1c4f70ad3230afd7d86e971421e02fef4`, NuttX
`fb2fadf6f599c1406f052db013efd00a2518e72c`; selected BMI088 instance0:
gyro6684690, accel6946834. Source `uorb top` one-second observations were
198 Hz before,195 midpoint,198 after; not exact long-window throughput.
Disarmed, EV_CTRL0, idle logger, original custom logger path ABSENT.

Temporary wired endpoints921600/8N1/raw/no flow, PX4 budget46080B/s/Onboard;
same unchanged18-source controller, guarded heartbeat-only MAVLink2 negotiation,
same MAVLink-only logger `logger start -b 64 -t -m mavlink -p vehicle_imu` and
same166-byte8-topic file. This was NOT SD logging;64KiB option is not UART ring
capacity. Command/settings backups and uploaded byte readback precede START.

Only data-load treatment:48 nonessential numerical streams removed on ttyS2.
HEARTBEAT1, SYSTEM_TIME1, TIMESYNC10, LINK_NODE_STATUS1, SYS_STATUS5,
STATUSTEXT20 Hz retained, plus six unlimited entries. Fresh full and treated
maps are in coordinator.jsonl; exact treatment/readback/allowlist verified.
Optical-flow/ToF ttyS3 and USB were not reconfigured. Post-restart temporary link
initiallyv1, then unchanged same-owner bootstrap reachedv2 before logging START.

M3C isolated deployment:
`root@10.18.198.1:/root/rm27-controller-reduced-20261011.NWMjuL/`.
The old negotiated deployment and evidence were not overwritten. Generic Linux
Python was used; no MaixPy launcher or stop-all-app operation.13 NEW-tool board
tests PASS/zero skips; unchanged120-test controller suite was not repeated.

## Actual transport evidence

`download/physical-trial-01/summary.json`: receiver DONE/errornull/exit0,
START/STOP accepted,3794 logging packets,0 retransmissions,finite framing verified.
Normal unacknowledged LOGGING_DATA first-to-last receipt span60.016211987s;
normal transition→actual STOP write60.015915862s. Summary's first-normal→last
logging span60.468319529s INCLUDES reliable stop metadata; do not call all of
that span normal data. Startup exclusion4095bytes is explicitly pre-START and
does not certify preexisting data. STOP ACK/framing is not source-tail completeness.

5001 retained PX41/1 frames: all CRC-checked;96 initially unknown frames verified
offline using prior exact-submodule schemas (LINK_NODE_STATUS, EVENT,
CURRENT_EVENT_SEQUENCE). Raw rows were not rewritten or unknowns silently dropped.
0 bad_data events;0 global MAVLink and0 logging sequence discontinuities.
65 LINK_NODE_STATUS snapshots /64 intervals, starting before START through after
last normal frame:4980 successful-write increments equal4980 received frames,
0 unaccounted sends, TX rejection counters0→0. Before-first/after-last diagnostic
boundaries remain unobserved; unsigned counters are not source authentication.
Complete postflight packet-local metadata reports ulog_stream messages missed0.

Wire received1053861bytes over65.163710906s (first/last chunk window),16172.514B/s
including startup/header/stop overhead.3460 normal LOGGING_DATA frames carry
921412 wire bytes over60.016212s (~15352.7B/s for this message class, not ALL
steady UART traffic). PX4 midpointtx16300.0B/s,txerr0.0,rate multiplier1.000,
MAVLink2. The115200 transport was not tested at this rate. At921600/8N1 the
nominal byte capacity is92160B/s; mean headroom does not prove burst-free queues.
All logging-packet receipt intervals (header/normal/stop): median17.0865ms,
p9524.37545ms,p9926.92357ms,max30.965417ms. These are batched packet READ receipts,
not IMU sample cadence or end-to-end latency; no FC↔M3C clock map was estimated.

This is an observed improvement over the prior same921600/full-Onboard trial
which stopped at missing435 after~2.6s. It supports reducing competing telemetry
for this prototype, not a universal firmware fix, proof of one offending stream,
or repeated-run robustness. Minimal ioctl/CPU instrumentation was also added;
this is not a randomized/repeated A-B-A experiment.

## Source/input audit: not a VIO dataset PASS

11843 actual BMI088 vehicle_imu records, sample-end span60.046056s,
effective197.215284Hz: FAIL unchanged≥200Hz gate. Timestamp_sample/pub timestamps
have0 duplicate/backward events; stable IDs and calibration counts1/1,
clip flags0/0; finite integrals/positive own gyro and accel dt. Source fields are
rad delta_angle and m/s delta_velocity with microsecond dt in FC HRT domain.
These are calibrated/rotated integrals, not instantaneous or untouched ADC samples;
diagnostic division by each own dt is not automatic OpenVINS admission.

Median gyro dt4507us/max10563us; median accel dt4991us/max8738us.
271 endpoint intervals >1.5×median are NOT271 lost samples: variable integration
duration matters. Exactly ONE retained gyro coverage residual >2us:4554us.
Rows8091→8092 (zero-based) sample endpoints17284902631→17284913148us,
interval10517us,current gyro dt5963us => uncovered4554us. Accel coverage remains
UNKNOWN: no independently serialized accel end timestamp; do not assign gyro
endpoint to accel or retime both to5ms.

logger_status message_gaps1→2, bracketed by publication timestamps17284868840
and17285869165us, contains that gyro hole. Exact logger.cpp:443–459 increments
this counter when a full-rate subscription jumps uORB generation. Here the
custom8-topic list has only vehicle_imu at interval0; event records use separate
handle_event_updates, and custom topics replace defaults (logged_topics.cpp:531+).
Thus the new observed generation-skip event is in the logger's vehicle_imu
subscription path, independently of clean UART frame delivery. This is not an
exact hardware missing-sample count; precise scheduling/queue-overwrite trigger
and generation jump magnitude are NOT measured. Source/queue semantics were
not modified. Driver selected0 cumulative gap counters stayed accel1/gyro2,
and retained sensor error counters stayed1/1, not zero. No cumulative subtraction
across reset is used; matched source resets perf on FILE start, not this MAVLink-only start.

ULog O dropouts0; logger status write dropouts0. This alone does NOT prove source
completeness: the generation-skip/coverage hole above remains. Source tail,
camera clock/sync, calibration/model compatibility and sustained≥200Hz remain
UNKNOWN/unqualified. capture_report/verification keep transport_qualifiedfalse
and openvins_admissiblefalse; only the explicitly bounded TRANSPORT COMPARISON
is VERIFIED, not full input qualification. VIO-P remains PARTIAL unchanged.

## CPU and physical UART diagnostics

Receiver CPU sampled before its gate and through exit:270 observed samples,
67.517371533s span,14.5CPU seconds =>21.47595% of ONE core average;
peak observed RSS43061248bytes (~41.1MiB),max sampler interval0.254743s.
This covers startup/normal/stop but not exact process birth-to-exit accounting;
it does not rule out brief scheduling stalls. No misleading late-process snapshot.
Retained PX4 cpuload60samples~48.39–50.21%, median~48.83%; not global saturation
or absence of per-task starvation proof.

M3C TIOCGICOUNT supported, snapshots on SAME receiver descriptor:
rx328553→1378545,tx4789→19466,frame2→2; parity/overrun/buf_overrun/brk0→0.
No new reported UART errors; historical two frame errors were not erased.
Driver byte counters and user-space wire/chunk totals have different boundaries
and preexisting buffered bytes; do not equate them or infer exact physical byte loss.

## Transfer, restoration and safety VERIFIED

12 remote/local output hashes/sizes agree.944329-byte original prefix and
framing-valid.ulg are identical, SHA256:
`658287cb149e1afbd56c9df799807729cd0930e4943190a580fb08b42eebca06`.
wire.jsonl10739619bytes SHA256:
`2e09f701d269c1143d3ce244b8ee5fb9afab7dd649ddda4620c63e7c98d7ba1a`.
summary SHA256:
`a0d7caa84cff53e1ba6b0e61d14e295cc96a9445ea74ea12380aee759c345c89`.
No repair, filled packet/sample, interpolation or fabricated synchronized data.

Fresh postflightreadback: original ttyS2 startup command115200/budget5760/
Onboard/no-flow and EXACT original nominal stream map restored; logger original
`logger start -b 64 -t -m all` idle187subscriptions. Eight SDLOG unchanged.
Original custom config absence restored. Removed ONLY our166-byte file and two
created empty directories; their content is recoverable from topics readback.
Existing SD logs/parameter files untouched. M3C exact termios restored, no UART
owner or remaining receiver. Other startup commands unchanged; flow/ToF still
comp88 msg132/106~48Hz receiving on ttyS3.337 observed USB heartbeats allbase29;
fresh final commanderDisarmed/EV0. Retained60 armed records false/arming_state1.
Observed records do not certify every instant; no arming/control commands were sent.

## Verification, failed helpers and next step

`py -3 -B -m unittest discover -s .maixpy/imu-uart-reduced-trial-20261011 -p 'test_*.py' -v`:
17 total,14 PASS/3 Windows POSIX skips, PythonExit0 (`tests-final.txt`).
M3C `board_tools_test.py`:13 NEW tests PASS/zero skips/PythonExit0
(`tool-tests-02.txt`, includes real PTY/early-exit sampler). Four later CPU/
nonfinite-encoding tests are OFFLINE Windows tests, not claimed as board tests.
Research venv `trial_analysis.py` second analysisexit0; independent
`verify_evidence.py` exit0 (verification.json and augmented verification-02.json)
verifies scope, one run, exact restoration, raw wire
replay, all hashes, source identity/coverage and frozen prior artifacts.

Preserved failures: first SSH glob/quoting test launcher failed before capture,
then corrected argv test runner passed; first JSON analysis rejected an actual
NaN gyro-health-temperature and left partial analysis.json. It is retained,
NOT the valid report. analysis-02.json uses tested explicit NONFINITE_DIAGNOSTIC
markers; it never turns unknown temperature into0 or changes integral values.
RED/GREEN logs preserved. A diagnostic one-liner initially lacked reassembly
import path, corrected by existing capture_report import; no recapture.

Prior33 diagnosis/58 negotiated/37 preparation/44 negotiation/14 reassembly/
18 original artifacts verified; diagnosis31 external snapshots and StageA/B
unchanged. Root226/related54/unchanged120 board regressions not rerun or claimed new.
Six before-report copies are retained. New manifest records current evidence;
older dated manifests describe their own snapshots, not additive root notices.

Next OFFLINE task: isolate the residual vehicle_imu logger subscription skip
(queue/poll/scheduling) and sub200Hz source publication using this complete log
and pinned source, then propose a justified change/test. No additional physical
run or firmware/rate/queue/parameter change is authorized by this consumed ONE
trial. Do not rerun this coordinator, start sync/calibration/real VIO or Stage C.
Any later changed-scope physical experiment needs a separately bounded plan;
no reconnection or wiring action is required now.
