# Latest VIO-S0 design pointers — 2026-10-10

Latest ONE upstream-gyro observation: `../imu-upstream-gyro-20261011/RESULT.md`.
FAILED at startup286→288/global19→21; ONE PX4 TX-buffer rejection verified,
successful-write counts match receipts. Added full-rate sensor_gyro observation
did NOT complete60s; only4gyro/1IMU record, original source-skip trigger UNKNOWN.
Prior clean vehicle_imu-only control unchanged; this observer is not adopted.
Settings restored115200/streams/logger/SDLOG/M3C termios; Disarmed/EV0, no firmware/
parameters/sensor changes. Windows34 PASS/3 skips, M3C27 PASS/zero skips.
VIO-S0/P PARTIAL; Stage A/B preserved; Stage C CLOSED. Next RAM trace is DESIGN
ONLY (`../imu-upstream-gyro-20261011/NEXT_TRACE_PLAN.md`), not built/flashed/approved.
Do not rerun the consumed coordinator; older next-action text below is historical.

Latest ONE physical reader control: `../imu-reader-control-20261011/RESULT.md`.
Fixed-r2500 did NOT eliminate subscription skips:197.104634Hz, two gyro holes
4460/4507us, logger increments1->3; UART delivery clean within observation.
Original200Hz/coverage gates remain FAILED, S0/P PARTIAL, StageC CLOSED.
Windows86 related/M3C48 tests PASS; exact restore verified, Stage A/B unchanged.
Next scope source execution/generation observability, not blind rate retry.
No new firmware/parameters/sensor selection/rates or synchronization claims.

**2026-10-11 OFFLINE residual source/subscription diagnosis completed:**
`../imu-source-diagnosis-20261011/DIAGNOSIS.md`, analysis.json/verification.json.
4554us hole confirmed logger vehicle_imu queue1 generation skip, not UART;
exact generation magnitude/Run/logger scheduling trigger UNKNOWN.197.215284Hz
FAIL original200Hz;298 extended accel windows explain most slower cadence versus
nominal dual-integrator timing model, not raw sample loss.271 long endpoints are
not271 drops.19new+37related testsPASS/zero skips;80old-own/36external and14source
hashes checked. No device/capture/settings/firmware/parameters/Git/Vault action.
StageA/B unchanged, VIO-S0/P PARTIAL, StageC CLOSED. Next reader-cadence comparison
(-p versus fixed2500Hz), all other factors constant, is only a separate proposal.

**2026-10-11 ONE reduced-telemetry comparison VERIFIED; source input PARTIAL:**
`../imu-uart-reduced-trial-20261011/RESULT.md`, analysis-02.json/verification-02.json.
Same921600/46080/logger/source,48nonessential numerical streams removed;
normal60.016s,5001framesCRC checked,0global/logging gaps,64LINKintervals
successful4980=received4980/no rejection.18runtimefilesunchanged;13newboard
testsPASS/zero skips;Windows17total14PASS/3POSIXskips;independentverifierexit0.
11843BMI088integrals197.215Hz FAIL unchanged200Hz gate;4554us gyro coverage
hole coincides logger vehicle_imu generation-skip1→2, not UART packet loss.
Full source/tail/clock/OpenVINSinput not qualified, StageC CLOSED, VIO-S0/P PARTIAL.
Exact115200/streammap/logger/SDLOG/customabsence/M3Ctermios restored,Disarmed/EV0/
flow-ToF intact;old evidence/StageA/B unchanged. No retry/push/Vault.
Next OFFLINE residualsource/logger skip/rate analysis; no hardware action now.
Older NOT_EXECUTED/reduced-telemetry-proposal paragraphs below are historical.

**2026-10-11 OFFLINE attribution VERIFIED; physical fix NOT_VALIDATED:**
`../imu-gap-diagnosis-20261011/DIAGNOSIS.md`, diagnosis.json/verification.json.
All33 previously unknown frames pinned-CRC verified (10 LINK_NODE_STATUS);
full3697-frame replay unchanged. Nine intervals account six PX4 send-buffer
rejections for six missing global sequence positions. Missing435 interval:
rejection4→5,global34→36,successful writes398=received398. Complete packet437
perf metadata ulog_stream missed0; no gap repair/admission. Exact burst/drain/
scheduling trigger UNKNOWN.15 new+9 regression tests PASS/zero skips/exit0;
18 runtime sources, prior artifacts and StageA/B unchanged. No device/SSH/UART/
capture/settings/runtime changes. Source~196.43Hz/integral coverage/clock/model
still unqualified, VIO-S0/P PARTIAL, StageC CLOSED. Next ONE proposed separately
scoped reduced-telemetry60s comparison, NOT EXECUTED. Old UNKNOWN/next-OFFLINE
paragraphs below are dated history, not current direction. No commit/push/Vault.

**2026-10-11 negotiated physical trial: bootstrap VERIFIED, continuity FAILED:**
`../imu-uart-negotiated-trial-20261011/RESULT.md`, raw wire/prefix, readbacks,
failure-analysis.json/verification.json. Current M3C120 tests PASS/zero skips
(7 virtual PTY),18 source hashes match. Same-owner heartbeat bootstrap confirmed
PX4v2; START/STOP accepted. Logging434→436 misses435 and stops;60s not completed,
no retry.513 retained BMI088 integral records~196.43Hz/source gaps, not200Hz/VIO.
Exact PX4/M3C settings restored; Disarmed/EV0, flow/ToF retained.9 pure tests and
independent verifier pass; old18+37+44+14 artifacts/StageA/B unchanged. Next OFFLINE
gap attribution/counters/burst plan, no new physical action. Root cause UNKNOWN;
VIO-S0/P PARTIAL, StageC CLOSED. Earlier precheck/first-run directions historical.

**2026-10-11 guarded heartbeat-only negotiation VERIFIED OFFLINE:**
`../imu-negotiation-fix-20261011/VALIDATION.md`. Same UART owner; explicit opt-in
permits bootstrap PX4v1 heartbeat/uptime only, no logging until verified PX4v2.
Default/logging/ACK/post-upgrade safety stayv2.120 research-Linux PASS/zero skips
(7 PTY),113 Windows PASS/7 skips;54 related and226 root PASS/1 existing skip.
No M3C/PX4 access/deployment/capture/settings. Original37-preparation/18-trial/
14-frozen/StageA/B and391/306-dropout source bytes unchanged. Next changed-revision
M3C120-test PTY precheck, then new scoped coordinator and ONE separately approved
physical trial; never rerun old coordinators. Old87-test board PASS is previous
source. VIO-S0/P PARTIAL; >=200Hz/source/tail/clock/model unqualified, StageC closed.
Earlier "next OFFLINE, not implemented" paragraphs below are historical snapshots.

**2026-10-11 approved physical preparation ABORTED, exact restore VERIFIED:**
`../imu-uart-retry-20261011/RESULT.md`. New coordinator required outgoingv2 before
M3C launch; PX4 remainedv1/RX0 after scoped921600/46080 preparation. No receiver/
START/IMU capture or retry. Source/synthetic evidence locates protocol bootstrap
ordering, not hardware failure. Next OFFLINE guarded heartbeat-only negotiation
before strict logging; do not simply remove the coordinator check (Controller also
rejects initialv1). Not implemented/fixed. Source snapshot197Hz not>=200 PASS;
VIO-S0/P PARTIAL, StageC closed. Older next-run directions below are historical.

**2026-10-11 changed-revision M3C prerequisite complete:**
`../controller-m3c-startup-pty-20261011/VALIDATION.md`.87 tests PASS/zero skips,
all4 PTY cases, unchanged source16-file parity. No physical UART/PX4 access or
new capture. Older next-M3C-PTY directions below are historical; next is one
separately approved physical trial. VIO-S0/P PARTIAL and StageC closed.

**2026-10-11 approved startup fix:** `../imu-startup-fix-20261011/VALIDATION.md`
supersedes the pending diagnosis below.87 Linux tests pass including4 virtual
PTY cases;83 Windows pass/4 POSIX skips. Startup-only bounded CRC synchronization,
raw evidence retained, strict post-boundary parsing unchanged. No new device
access/capture or hardware PASS. Next qualify this changed revision with M3C PTY
tests, then a separately approved one-run physical retry. VIO-S0/P PARTIAL.

**2026-10-11 offline startup diagnosis:**
`../imu-startup-diagnosis-20261011/DIAGNOSIS.md` supersedes earlier next actions.
The approved physical trial failed before START on its first21 bytes; restoration
was verified, no retry. Saved-wire replay and20 synthetic late attachments confirm
a controller pre-START synchronization limitation; physical byte origin remains
UNKNOWN. No fix, hardware access or throughput PASS. Next review bounded startup
synchronization/tests, not another baseline/PTY/physical capture automatically.

**2026-10-11 controller software milestone:** `single-uart/controller/VALIDATION.md`
supersedes the planned-controller next action below. Controller/runner/audit now
implemented:55 Linux tests pass (including virtual PTY),53 Windows pass/2 PTY skips,
54 existing regressions and226 root tests pass/1 existing skip. Saved ULog bytes
remain exact with391/306 dropouts. No M3C/PX4 operation or physical UART test.
`controller/RUNBOOK.md` refines the same proposed trial; temporary921600/46080B/s
and logger profile still need specific approval and actual USB backup/restoration.
Source/tail/clock UNKNOWN, VIO-S0 PARTIAL, Stage C closed. No push in this turn.

**2026-10-11 offline implementation:** `single-uart/reassembly/VALIDATION.md`
records the new strict finite ULog/MAVLink reassembler.28 new +19 existing tests
pass; two real saved ULogs in synthetic MAVLink framing reconstruct byte-identically,
preserving391/306 dropout events. Device rate/clock/source completeness remain
UNKNOWN, OpenVINS admission false. Live controller/ACK timing/restoration is the
next software task; `PROPOSED_TRIAL.md` is not executed or approved by this result.

**New constraint and superseding action:** user reports no second available UART.
Read `single-uart/REVIEW.md` first. Spare-UART pin verification is no longer the
next action. Review found existing MAVLink ULog streaming as a complete-record
acquisition prototype before considering custom firmware. Six offline framing/
arithmetic check groups pass; no streaming/capture/configuration was performed.
115200 cannot carry the modeled200Hz complete records; faster baud/software budget
and logger continuity need separate qualification. VIO-S0 remains PARTIAL.
Older dedicated-UART recommendations below are retained historical alternatives.

Read `followup/REPORT.md` together with the frozen `VIO_S0_INPUT_DESIGN.md`.
The follow-up incorporates the completed interface inventory, metadata-inclusive
bandwidth, a pinned-source synchronous DDS time-sync wait hazard, and7 new offline
tests. 92 related tests pass this turn. No hardware touched; VIO-S0 PARTIAL.

USB fallback is blocked on host ACM support/role/management prerequisites, not a
plug-in option. The next approval-gated step is a power-off physical carrier-pin
verification, NOT repeating software inventory. Previous manifest still describes
the frozen original33 files; followup has its own evidence and manifest.
