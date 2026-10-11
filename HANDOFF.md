# Engineering Handoff

## CURRENT PUBLICATION — VIO-S0 evidence and corrected Git identity, 2026-10-12

User requested push with `shiuhou <uhshi371@connect.hkust-gz.edu.cn>`. Repository-local
author/committer configured accordingly; GitHub CLI account shiuhou/push permission
verified. Previous three published commits used uhoushi@gmail.com; shared history
is retained, not rewritten. Push will explicitly use the CLI credential helper.
Baseline main/remote3ea1e160; publication report:
`rm27/perception/vision/docs/PUBLICATION_20261012.md` and
`.maixpy/publication-20261012/VALIDATION.md` / curated selection.json.

This publishes pending controller/diagnostic source/tests, plans and measured-result
reports; it is NOT a new hardware run or source fix. Stage A/B bytes unchanged;
VIO-S0/P PARTIAL, original200Hz/continuity/model gates unchanged, Stage C CLOSED.
Raw-inclusive historical manifests require original local evidence and are not
complete clone inventories. Raw recordings/environments/builds and unrelated
camera_capture.py/tmp/PLAN_HISTORY edit excluded; six before-report bodies retained.
No firmware/parameters/baud/wiring/ARM/fusion/Vault changes. RAM trace still DESIGN
ONLY pending firmware authority/rollback binary. Normal commit/push outcome is
verified against remote before the final user report, not assumed in advance.
Below latest dated physical outcome remains the development status, not a retry order.

## LATEST — upstream gyro observation stopped at TX rejection, 2026-10-11

User `設計完直接上真機吧` approved ONE stock-firmware source-observation attempt;
design and bench run completed, no retry. Authoritative evidence:
`.maixpy/imu-upstream-gyro-20261011/RESULT.md`, failure-analysis.json,
verification.json and HANDOFF.md. Added sensor_gyro0 to the same fixed2500Hz
MAVLink logger; temporary921600/80000 budget/reduced telemetry, no firmware,
parameters, sensor changes, wiring, camera, fusion, ODOMETRY or ARM/flight.

FAILED at normal logging startup:286→288 missing287/global19→21. LINK counters
verify ONE PX4 TX-buffer rejection in that interval;461 successful writes equal
461 receipts across six observed intervals. No60s observation, only4gyro/1IMU
record; original subscription-skip cause, source cadence/coverage remain UNKNOWN.
The prior clean60s vehicle_imu-only control is unchanged; this higher-load observer
is NOT adopted. VIO-S0/P PARTIAL; Stage A/B preserved, Stage C CLOSED.

Exact original115200/budget5760/stream map/logger/SDLOG/custom-file absence and
M3C termios/no owner verified restored. Only our182B file/two empty dirs removed,
locally recoverable; SD logs/parameter files untouched.285 USB base29; final
Disarmed/EV0.24 source/9 transferred artifact hashes verified; core unchanged.
Windows34 tests PASS/3 POSIX skips, M3C27 PASS/zero skips; failed helpers preserved.
No stage/commit/push or Vault access. Next RAM-trigger trace is DESIGN ONLY in
NEXT_TRACE_PLAN.md; consequential firmware scope and exact rollback artifact are
prerequisites, not authority granted by this completed bench trial. No blind retry.
Below dated next-action paragraphs are historical snapshots, not current orders.

## LATEST — fixed-reader physical control completed, 2026-10-11

User `ok execute` approved the saved single-reader plan; ONE60s control completed,
no physical retry. `.maixpy/imu-reader-control-20261011/RESULT.md` / `HANDOFF.md`,
raw download, comparison and independent verification are authoritative latest
evidence. Exact PX4v1.17.0d6f12ad1/BMI0880 freshly verified. Only logger reader
changed -p vehicle_imu -> -r2500, keeping same temporary921600/46080/eight topics/
reduced telemetry/receiver. No firmware/parameters/IMU rate/selection/wiring,
camera/calibration/fusion/ODOMETRY/ARM/flight or repeat Stage A/B.

Transport VERIFIED within observed60.0094s:0 global/logging sequence gaps,
0 observed TX rejection/unaccounted writes.11837 integrals197.104634Hz FAIL original
>=200Hz; TWO subscription counter increments bracket4460/4507us gyro coverage
holes. Fixed-reader hypothesis FAILED, NOT adopted as a fix.317 longer inferred
accel windows also remain; accel endpoint/source/tail/clock/model UNKNOWN.
VIO-S0/P PARTIAL, Stage C CLOSED. No new synthetic or synchronized-data PASS.

Only existing runtime edit is additive strict reader-profile validation;
AST equality outside it verifies unchanged owner/parser/ACK/STOP code. Newprofile8/
comparison7 +71 relevant Windows regressions PASS; M3C48 related tests PASS/zero
skips. Failed test fixture/interpreter/probe/discovery attempts retained; no installs.
M3C isolated /root/rm27-controller-reader-20261011.VZQm1z; prior .wiIbkI is
software-only.27 source/11 tool hashes and10 output transfers verified.

Fresh exact UART3 baseline115200/budget5760/Onboard/no-flow/nominal stream map,
logger idleall187/eight SDLOG/custom-path absence restored. M3C exact termios/no
owner/receiver verified. Only our166-byte topic file/two empty dirs removed,
recoverable from readback; SD logs/parameters/flow-ToF untouched.342 monitored
USB base29; fresh Disarmed/EV0. Main HEAD3ea1e160 unchanged; prior dirty work,
old report bodies/manifests and Stage A/B preserved. No stage/commit/push/Vault.

Next: scope source observability (actual logger wake/read/generation and
VehicleIMU Run/readiness/endpoints), NOT another blind reader-rate trial. Exact
trigger cannot be recovered from current evidence. Any firmware/queue/trace or
new physical treatment requires a separate bounded plan; this ONE trial is
consumed. Below NEXT PLAN/older experiment paragraphs are historical snapshots.

## NEXT PLAN — single logger-reader control, 2026-10-11

### Objective / actual changes / repository state

User requested planning only. Added
`docs/superpowers/plans/2026-10-11-vio-s0-logger-reader-control.md`; no runtime,
device/SSH/capture/configuration/parameter/firmware/commit/push/Vault action.
Main HEAD remains `3ea1e16086965176db68b88e1c42990f92c5913e`; pre-existing dirty
work preserved, staged diff empty. Implementation/capture remain NOT EXECUTED.

### Verification / failed attempts / verified facts

PowerShell SHA256/size check matched28 own +27 external entries of the latest
offline diagnosis manifest BEFORE this additive update. Its manifest is unchanged;
the two root snapshots now resolve to matching copies in
`.maixpy/imu-reader-plan-20261011/repo-before/`. Source reader CLI and actual
preflight guard inspected; old validator honestly requires poll mode, so the plan
includes one explicit fixed-reader profile, not a mislabeled attestation.
No new runtime tests run; none claimed PASS. Seven proposed Python code blocks
passed AST syntax checking only, exit0. Two preliminary Windows-quoting scanner
attempts (zero blocks matched, then SyntaxError) were corrected; neither executed
the proposed code or constituted a runtime test. Preservation check is recorded
in `.maixpy/imu-reader-plan-20261011/verification.json`.

### Decision / assumptions / risks / next actions / rollback

Prepare offline guards/comparison/tests FIRST. Only with new bounded trial approval,
run ONE60 s same-condition comparison changing ONLY logger `-p vehicle_imu` to
`-r 2500` (no-p). Retain source,166-byte topics,temporary921600/46080,reduced
telemetry,receiver and independent USB restore. Requested reader400us is not
guaranteed loop timing or source-rate improvement. Exact scheduling cause remains
UNKNOWN; finite successful continuity would not prove universal loss freedom.
Original>=200Hz,source/tail/clock/integral-model gates stay unchanged; VIO-S0/P
PARTIAL,StageC CLOSED. Previous physical authorization is consumed, not renewed
by planning. Restore fresh configuration, no user parameter rollback. Revert only
this additive section using preserved before bytes; do not discard unrelated work.
Vault update below is only a local proposal. Detailed preceding evidence follows.

## CURRENT — offline subscription/cadence diagnosis completed, 2026-10-11

### Repository state / task objective

Main HEAD `3ea1e16086965176db68b88e1c42990f92c5913e`; existing dirty research,
controller/reports and unrelated camera/tmp preserved. User requested OFFLINE
remaining subscription-hole/source-rate analysis. No SSH/device/capture/settings/
firmware/parameters/rates/wiring/camera/VIO/fusion/ARM/dependencies/Git push/Vault.
Previous physical restoration is retained evidence, not a fresh readback now.

### Actual changes / verified facts

`.maixpy/imu-source-diagnosis-20261011/DIAGNOSIS.md`, diagnosis.py, test_diagnosis.py,
analysis.json, verify.py/verification.json; reused existing semantic/framing code.
80 own/36 external previous hashes and14 source pins independently checked.
One4554us gyro hole bracketed by logger message_gaps1->2, only vehicle_imu full-rate,
queue1 latest-only generation skip: confirmed LOGGER SUBSCRIPTION layer, not UART.
Exact generation magnitude/Run/logger scheduling trigger UNKNOWN.
11843 BMI0880 integrals197.215284Hz; one-record sensitivity197.231938 still <200.
298 extended accel windows (nearest SI periods5/6/7, not hardware counts) add
~935237us over nominal4-period timing model; source dual-integrator/callback logic
has no fixed5ms publication guarantee.271 large endpoint gaps are not271 losses.
Source/tail/clock/measurement-model unresolved; inputPARTIAL; StageC CLOSED.

### Verification commands and results / failed attempts

Existing venv Python: `-m unittest discover -s .maixpy/imu-source-diagnosis-20261011
-p test_diagnosis.py -v`:19PASS; design `test_offline.py`:9PASS; reassembly
`test_ulog_mavlink.py`:28PASS; zero skips, actual Python exit0. `verify.py` exit0.
RED missing implementations and first GREEN fixture-median failure preserved;
fixture corrected without changing1.5x/200Hz/coverage/admission rules. Real pinned
log and18 synthetic tests clearly distinguished. No firmware fix claimed.

### Decisions / assumptions / risks / next actions / rollback

No production/runtime edits or invented samples. Exact scheduling causality cannot
advance from unrecorded traces. Proposed future SINGLE reader-cadence comparison
(-p versus -r2500), with all other factors fixed/restored, is documented only;
no new physical authorization consumed. Do not blindly raiseIMU_INTEG_RATE: model
200->210 keeps same integration/callback settings. Do not enter sync/calibration/
realVIO. StageA/B/old experiments/manifests unchanged. Root updates additive;
rollback copies in new repo-before; Vault update is only a local import proposal.
Earlier physical CURRENT section below is now a preserved historical snapshot.

## CURRENT — one reduced-telemetry transport comparison completed; input PARTIAL, 2026-10-11

### Repository state / task objective

Main HEAD `3ea1e16086965176db68b88e1c42990f92c5913e`, dirty work preserved;
no stage/commit/push or Vault access. User's latest `do it` approved ONE physical
60s reduced-nonessential-telemetry comparison from the previous NEXT_TRIAL_PLAN.
That authorization is consumed; no retry or further capture. No firmware,
parameter, sensor/rate, wiring, camera, calibration, ARM/flight/fusion change.

### Actual changes / verified facts

See `.maixpy/imu-uart-reduced-trial-20261011/RESULT.md`, coordinator.jsonl,
download/physical-trial-01, analysis-02.json and verification-02.json.18 existing
runtime files unchanged; new one-off scope/CPU/same-descriptor counter tools.
Isolated M3C deployment `/root/rm27-controller-reduced-20261011.NWMjuL/`.
Exact d6f12ad1/NuttX hash, selected BMI0880, Disarmed/EV0 freshly read back.
Temporary921600/46080/minimal8-topic MAVLink-only logger as prior;48 nonessential
numerical streams disabled ONLY on wiredttyS2, health/epoch/diagnostics/unlimited
entries retained/read back. Same-ownerv2 negotiation/START/STOP accepted,exit0.

Normal LOGGING_DATA receipt span60.016212s;3794 total logging packets/framing
verified.5001 PX4frames allCRC-checked (96 unknowns pinned-verified),0 bad data/
global/logging sequence gaps.65 LINK snapshots/64 intervals:4980 successful
writes=4980 received,0 rejection increment/unaccounted sends; postflight ulog
stream missed0. VERIFIED bounded transport comparison, not universal fix.

11843 BMI088 integral records~197.215Hz, stableIDs/calibration1/1/clip0, ordering
valid; original>=200Hz gate FAIL. ONE gyro integration-coverage hole4554us,
coincident logger full-rate generation-gap counter1→2. Only vehicle_imu is
full-rate in this custom list; source shows logger subscription generation skip,
not UART packet loss. Exact trigger/missing hardware count UNKNOWN.0ULog dropouts
is NOT loss-free input. No instant-sample/OpenVINS/accel-endpoint/camera-clock/tail
qualification; VIO-S0/P PARTIAL, full transport_qualifiedfalse, StageC CLOSED.

CPU sampler began before receivergate:270 samples/67.517s,21.476% ONE-core mean,
peak~41.1MiB RSS. Same-FD UART counters supported, frame2→2/parity-overrun-brk0→0;
byte windows differ from buffered user-space reads, not exact wire loss proof.

### Verification / failed attempts / restoration

13 NEW M3C-tool tests PASS/zero skips/exit0 (realPTY/early-exit); unchanged120-board
suite not repeated. FinalWindows17 total/14PASS/3 POSIX skips/PythonExit0;4 new
offline CPU/NaN encoding tests not claimed board tests. Research analysis second
attempt and independent verifier exit0.12 remote/local hashes agree;944329-byte
framed log/prefix SHA658287cb149e1afbd56c9df799807729cd0930e4943190a580fb08b42eebca06.
Preserved SSH glob launcher failure and JSONNaN partial analysis.json; valid
analysis-02.json explicitly labels nonfinite health temperature, no byte repair.
33 diagnosis/58 priortrial/37 prep/44 negotiation/14 reassembly/18 original
artifacts and StageA/B unchanged. Root226/related54 historical tests not rerun.

Independent restore: originalttyS2 startup115200/budget5760/Onboard/no-flow and
exact nominal stream map; original loggeridle/all/187subs;8SDLOG/fileabsence;
M3C exacttermios/noowner/nochild, other startup commands/flow-ToF receive intact.
337 USB heartbeatsbase29; fresh finalDisarmed/EV0. Removed only our166-byte topic
file/two created emptydirs, contents recoverable locally; SD logs/params untouched.

### Decisions / assumptions / risks / next actions / rollback

No threshold relaxation, retiming, data fill, firmware patch or permanent921600
adoption. Single improvement is not repeated robustness or full VIO suitability.
Next OFFLINE: analyze residual logger vehicle_imu subscription skip/sub200Hz
source using this complete recording and pinned code; no new physical action
needed now. Do not rerun consumed coordinator or proceed to sync/calibration/
StageC. Future changed-scope test needs its own bounded plan. Rollback verified
above; six before-reports preserved in new repo-before. VAULT_UPDATE is a LOCAL
proposal, not Vault ingestion. Older CURRENT/next-proposal paragraphs below are
dated snapshots superseded by this first section.

## CURRENT — offline sender-buffer attribution verified; physical fix unvalidated, 2026-10-11

### Repository state / task objective

Main HEAD `3ea1e16086965176db68b88e1c42990f92c5913e`, existing dirty work preserved;
no staging/commit/push. User's `do it` resumes OFFLINE diagnosis of the completed
ONE failed trial, not another capture. No M3C/PX4/SSH/UART/settings/Vault access.

### Actual changes / verified facts

See `.maixpy/imu-gap-diagnosis-20261011/DIAGNOSIS.md`, diagnosis.json,
verification.json, offline diagnose.py/test_diagnosis.py/verify_evidence.py and
NEXT_TRIAL_PLAN.md. Runtime controller18 deployed source files UNCHANGED.
Exact firmware d6f12ad1 full hash and actual MAVLink/NuttX/generator gitlinks
used. Previously UNKNOWN message8 is LINK_NODE_STATUS; all10 instances and23
other unknown frames now CRC-verified from pinned definitions without editing
raw rows. Full saved wire replay remains identical, all3697 frames CRC-checked.

Nine counter intervals show successful writes=received frame counts, six TX
send-buffer rejections=six missing global sequence positions. Terminal logging435
interval has rejection4→5, global34→36, success7317→7715 (398)=received398.
Source assigns global sequence before FIONSPACE/send_start; normal ULog consumes
data without retry/backpressure. VERIFIED sender-buffer rejection layer, not
measured exact burst/driver/scheduling trigger or a physical fix.

Complete packet-local post-failure437 perf metadata: ulog_stream messages missed0;
47 retries deduplicated, next truncated record not decoded/joined. Failed prefix
and admission unchanged. logger_status message_gaps1→2→3 are aggregate generation
EVENTS, not missing sample counts. Source correction: perf_reset_all belongs to
start_log_file, not the MAVLink-only start in this trial; old report is unchanged.
USB inspection is not UART baud proof; live safety/settings are NOT refreshed here.

### Verification commands / observed results / failed attempts

Existing research Python:
`-B -m unittest discover -s .maixpy/imu-gap-diagnosis-20261011 -p test_diagnosis.py -v`
→15PASS/zero skips/exit0; prior-trial `-p 'test_*.py'` →9PASS/zero skips/exit0.
Analysis and independent verifier scripts in new folder exit0. Raw RED12/RED3
and GREEN12/15 logs retained.33 previously unknown CRCs verified;58 previous own/
25 external snapshot/18 original/37 preparation/44 negotiation/14 reassembly
artifacts and StageA/B verified unchanged. Six root before-copies preserved;
new pointer paragraphs supersede old UNKNOWN/next-OFFLINE paragraphs, not their
dated manifests. Prior120-board/226-root/54-related tests not rerun/claimed new.

### Decisions / assumptions / open questions / risks

No speculative receiver repair, firmware patch, buffer enlargement, retiming,
data fill, relaxed>=200Hz or fabricated PASS.800-byte TX ring/three267-byte
frames is a pinned-source SYNTHETIC no-drain sensitivity, not live queue occupancy.
Source513 BMI088 integrals~196.43Hz/two coverage gaps remain independent; no
instantaneous OpenVINS input, complete source/tail, receiver CPU or clock/model
qualification. VIO-S0/P PARTIAL; current high-rate transport FAILED; StageC CLOSED.

### Next actions / rollback point

Exactly one proposed next physical action: new separately scoped60s instrumented
reduced-nonessential-telemetry comparison on existing M3C↔PX4 UART plus PX4 USB,
same921600/46080/source/logger, exact restore. NOT EXECUTED or authorized here.
No need rerun unchanged board PTYs/StageA/B or any frozen dated coordinator.
Rollback: no runtime change this turn; original trial artifacts/manifests remain
immutable. Root before-state in new repo-before; VAULT_UPDATE is local proposal
only, not Vault ingestion.

## Previous — negotiated physical IMU trial failed; exact restoration verified, 2026-10-11

User authorized ONE physical run (`可上真機`). See
`.maixpy/imu-uart-negotiated-trial-20261011/RESULT.md`, coordinator.jsonl,
download/physical-trial-01, capture-audit.json, failure-analysis.json and
verification.json. New isolated M3C deployment
`root@10.18.198.1:/root/rm27-controller-negotiated-20261011.ffWOSR/`;
same tested source18-file parity.120 M3C tests PASS/zero skips (7 virtual PTY),
Python/SSH exit0; no install or change to runtime controller source.

Fresh PX4v1.17.0/d6f12ad1c4f70ad3230afd7d86e971421e02fef4, selected BMI0880,
gyro6684690/accel6946834, Disarmed/EV0. Actual backups/file absence read back;
temporary921600/46080B/s/minimal8-topic MAVLink-only logger. Pre-peerv1 accepted;
same-owner guarded heartbeat bootstrap physically confirmedv2; START/STOP accepted.
Accepted logging0..434 then436: expected435 missing, receiver exited1/stopped.
No60s completion, framing-valid ULog, automatic retry or high-rate PASS.

Retained107784-byte prefix/hash unchanged. In-memory complete-record diagnostic
view only:513 BMI088 integral records, source span2.606488s/effective196.432901Hz,
max sample-end interval15.023ms, stable IDs/calibration1/1, clip0/0, valid ordering.
13 long intervals include variable dt;2 gyro coverage residual gaps sum13520us.
Not instantaneous/OpenVINS input, exact sensor loss, clock synchronization or
latency. Full wire has a global seq34→36 gap between logging434/436; root/layer
cause UNKNOWN, not sole SD/wiring/bandwidth proof. M3C receiver CPU NOT_MEASURED
because sampler arrived after exit. No relaxed>=200Hz/source/tail/clock/model gate.

PX4 exact original UART115200/budget5760/Onboard/flowOFF, nominal stream map,
logger start-b64/-t/-mall idle187, eight SDLOG and original config absence restored.
Only our166-byte topic file and two created empty directories removed; recoverable
local readback retained. M3C exact original termios restored/no remaining owner;
unrelated ports/flow-ToF receive retained.228 observed USB heartbeats base29;
fresh final Disarmed/EV0, no ARM/motor/parameter/firmware/wiring/sensor/camera/fusion.

Fresh9 pure scope/analysis tests PASS/zero skips, independent verifier exit0;
6 remote/local artifact hashes agree,18 original/37 preparation/44 offline-task/
14 frozen artifacts and StageA/B unchanged. Prior root226/54 results not rerun this
hardware turn. Failed-helper logs retained; no data repair or fabricated PASS.
Main working-tree HEAD3ea1e16086965176db68b88e1c42990f92c5913e, no staging/commit/push,
Vault untouched; VAULT_UPDATE local proposal only. Existing camera_capture.py/tmp
and previous dirty changes preserved. Current before-report copies in repo-before.

Next OFFLINE: source/wire attribution and instrumentation/telemetry-burst plan,
not another blind capture. Sender generation/TX and UART overrun counters are
missing, so root cause is not proven. Future new trial needs its own scope/new
outputs/backups/counters; do not rerun dated coordinators or completed120-test
board precheck without changed software. VIO-S0/P PARTIAL, StageC CLOSED.

## Previous — offline guarded MAVLink2 negotiation verified, 2026-10-11

User's `ok` accepted OFFLINE implementation/tests only. See
`.maixpy/imu-negotiation-fix-20261011/VALIDATION.md`, PLAN.md, verification-03.json,
raw test logs and SYNTHETIC-roundtrip-01. Existing Controller/runner now explicitly
opt in to same-owner heartbeat-onlyv1 bootstrap; only verified unsigned/CRC PX41/1
Disarmed heartbeat authorizes companionv2 HEARTBEAT1Hz. Verified PX4v2 heartbeat
permits one logging START. Default strict-v2 unchanged; logging/ACK/post-upgrade
relevant frames never acceptv1. Five-second total initial deadline,2.5s freshness,
same-read veto, write-time freshness, no flush/retry and exact termios cleanup kept.
New preflight boolean/CLI opt-in required; flags are not authorization. Capture
audit replays policy/phase timestamps and rejects metadata or premature-TX tampering.

Fresh120 research-Linux tests PASS/zero skips (7 PTY); Windows113 PASS/7 POSIX skips;
54 related tests PASS, root226 PASS/1 existing skip, all final Python exits0.
Self-review missing-null metadata regression RED retained/fixed. Saved BMI270
6896444/5597928-byte synthetic-wire replays preserve391/306 dropouts, not current
BMI088 or actual receive performance.37 prior preparation/18 original trial/14
frozen entries and StageA/B SHA unchanged. Source snapshots, exact commands,
archive/raw Linux log hashes and helper issues recorded. Main working-tree HEAD
3ea1e16086965176db68b88e1c42990f92c5913e; no commit/push or Git staging.

No M3C/PX4 access/deployment/new capture/settings/firmware/parameters/wiring,
camera/calibration/fusion/StageC or install. Only research host ceopc for PTYs.
Live Disarmed/EV0 not refreshed this turn; previous baseline is historical.
Vault not accessed/ingested; VAULT_UPDATE is a local reviewable proposal.
Existing unrelated camera_capture.py/tmp and prior dirty work preserved.

Next software prerequisite: isolated current120-test M3C PTY/source-parity check;
old87-test board PASS does not cover this changed revision. Prepare a NEW scoped
coordinator, accepting pre-peer outgoingv1 ORv2 while still checking baud/budget/
mode/flow; receiver must verify negotiatedv2 before START. Never rerun frozen
dated one-off coordinators. Then one separately approved60s existing M3C↔PX4 UART
experiment plus PX4 USB, with actual backups/temporary921600/minimal logger/restoration.
Verify actual current-BMI088 rates/IDs/dt/gaps/clips/calibration/wire/CPU; no retries.
VIO-S0/P PARTIAL; >=200Hz/source/tail/clock/model unqualified; StageC closed.
Rollback scoped change from this task's baseline/repo-before; don't erase user work.

## Previous — physical preparation aborted on protocol ordering, 2026-10-11

User approved one real60s retry. See `.maixpy/imu-uart-retry-20261011/RESULT.md`,
coordinator.jsonl, verification.json and protocol-diagnosis.json. Fresh d6f12ad1/
Disarmed/EV0/selectedBMI0880 verified; one-second source197Hz, not>=200Hz PASS.
Actual backups/custom-file absence checked. PX4 UART temporarily921600/46080B/s,
minimal8-topic MAVLink logger applied/read back. New coordinator wrongly required
outgoing version2 BEFORE launching the peer; observedversion1/RX0 aborted it.
Receiver never launched, no M3C TX/START/IMU data or60s accepted interval; no retry.
This is software bootstrap ordering, NOT established wiring/baud/SD fault.

Exact PX4 logger/UART/stream mapping/eightSDLOG/custom-file absence restored;
115200, idle187 subscriptions, flow/ToF ownership/receive retained, Disarmed/EV0.
M3C readonly attribute checks show exact termios unchanged/no owner/no receiver.
Independent verifier exit0 confirms18 old trial/14 frozen/16 deployed hashes and
unchanged StageA/B. Five new coordinator scope tests pass/Python exit0. Saved-source
and synthetic diagnosis exit0: PX4 upgrades after incomingv2; -Z only flow-off.
Strict Controller also refuses initialv1 before replying, so removing only the
coordinator check is insufficient. No source/safety guard changes to that receiver.

Next OFFLINE: implement/test finite heartbeat-only v2 negotiation using existing
StageA frame_v2 before strict logging; no START until verified PX4v2, preserve
fresh/disarmed/source/CRC/same-read/timeout/raw/no-flush/restoration guards. This
phase is PLANNED, not fixed. Do not rerun this one-off or unchanged87-test PTY.
VIO-S0/P PARTIAL, clocks/source/tail/model unqualified, StageC closed. Prior failure
and helper errors retained. No commit/push/Vault change; mutable docs snapshotted
under this trial's repo-before. Existing dirty source/docs/camera_capture.py/tmp kept.

## Previous — revised controller M3C PTY PASS, 2026-10-11

User approved running the board precheck. Existing final startup-fix source was
copied unchanged to NEW `/root/rm27-controller-startup-pty-20261011.Jg12Lv/`.
Live M3C maixcam2-9d05/aarch64, Python3.13.2/NumPy2.2.6/pymavlink2.4.49/
pyulog1.2.4 using existing packages and isolated pinned pyulog copy, no install.
Exact command, raw logs/hashes and scope:
`.maixpy/controller-m3c-startup-pty-20261011/VALIDATION.md` / environment.json /
tests.txt / cleanup.json.87 tests PASS, zero skips/failures,9.472s, Python/SSH exit0;
all4 PTY tests pass, including pre-open queued input, armed no-TX and exact PTY
termios restoration. All16 deployed Python hashes match local source. No remaining
test process in this deployment. This replaces the old55-test board prerequisite,
not StageA/B or the failed physical trial.

No source changes, physical UART open/PX4 access/settings, new capture, dependency
installation, commit/push or Vault access. Existing dirty files retained. Root
226-pass/1-skip result remains prior evidence, not newly rerun.18 trial/14 frozen
entries and StageA/B verified unchanged. Prior startup-fix29-entry manifest was
verified before updating mutable reports; their snapshots are in this new
directory's repo-before. Old manifest remains historical; new manifest scoped here.
Board wall clock/host mtime mismatch only produced tar warnings, no clock fix.

PTY tests establish target software compatibility, not physical921600/source/
clock/tail/OpenVINS qualification. VIO-S0/P PARTIAL, StageC closed. FC Disarmed/
EV_CTRL state not queried this turn; refresh before physical trial. Next only
separately approved one60s trial under RUNBOOK with fresh backups/outputs/exact
restore; no need to repeat PTY unless source/environment changes. Do not rerun
old coordinator. VAULT_UPDATE remains a proposal, not an ingested Vault record.

## Previous — approved offline startup fix, 2026-10-11

User's "ok do it" approved the preceding bounded pre-START design, not a new
physical run. Working-tree change: startup_sync.py/session.py/capture_report.py
plus test_startup_sync.py/test_startup_pty.py.5s/65536-byte bounded CRC frame
search before the candidate PX41/1 heartbeat; identity/unsigned/MAVLink2/armed
gates unchanged, all post-boundary bytes use strict original Decoder. Every raw
chunk/unframed region retained; no flushing, inferred sample loss or VIO PASS.
Full evidence/commands/scope: `.maixpy/imu-startup-fix-20261011/VALIDATION.md`,
PLAN.md, review-red logs, linux/windows-tests-03.txt, verification-03.json,
saved-replay-03.json and manifest.json.
87 Linux pass/zero skips (4 PTY);83 Windows pass/4 skips;54 existing regressions;
root226 pass/1 skip. Saved BMI270 bytes exact,391/306 dropouts retained.18 failed
trial +14 frozen reassembly hashes and StageA/B unchanged. Saved21 bytes alone
still cannot START/PASS; revised code waits then times out without a valid HB.
Review caught payload scanning inside incomplete outer packets; now plausible
headers/bodies wait and complete candidates are consumed whole (including unknown
or CRC-rejected). All266 split positions covered; startup metadata/types/policy
audited. Saved FE header is UNKNOWN msgid255/payload255: even saved21 + one HB
cannot resolve its263-byte candidate. Memory fixtures use labeled synthetic filler;
continuous-peer PTY success does not prove real-stream recovery. No physical-fix claim.

Only isolated Linux ceopc software tests, no M3C/PX4 access/deployment/settings,
dependencies, new capture, commit or push. Main3ea1e16, prior dirty work and
camera_capture.py/tmp retained. Pre-change session SHA9f30f12b snapshot in this
dated directory; rollback only the new bounded diff, not unrelated state. First
patch duplicate-target rejection and native-stderr log decorations retained.
VIO-S0/P PARTIAL; clock/model/source/tail UNKNOWN; StageC closed. Next deploy
this revision to a fresh M3C directory for87 PTY tests (old55-test PASS is not
this revision), then seek approval for one same-condition60s physical capture
with fresh USB backups/restoration/new paths. Never rerun old coordinator.
Vault untouched; VAULT_UPDATE is a local proposal only.

## CURRENT — offline startup diagnosis, 2026-10-11

Latest diagnosis: `.maixpy/imu-startup-diagnosis-20261011/DIAGNOSIS.md` and
`reproduce.py` / `reproduction.txt`. Saved21-byte RX reproduces Bad prefix for
f93b; remaining19 bytes wait on a263-byte candidate frame. Strict controller
aborts before START, even for a synthetic legal frame tail followed by a valid
heartbeat.20 clean splits work;20 late attachments fail. This confirms a
pre-START synchronization limitation, NOT the physical origin of the saved bytes.
Prior PTY peer starts clean after UART open and did not cover late attachment.
18 original trial hash entries verified unchanged; current suite55 run/53 pass/
2 Windows POSIX skips. Armed/post-START corruption behavior unchanged and checked.
No application fix, hardware access/settings, new capture, dependency or push.
VIO-S0/P PARTIAL; StageA/B preserved, StageC closed. Next: review a bounded
pre-START synchronization boundary and its tests; do not merely ignore all
bad_data or flush evidence. Physical retry is not authorized by this diagnosis.
Git baseline3ea1e16 with prior dirty edits retained. Initial diagnostic-only
import-path failure corrected; no product code edited. Vault untouched;
VAULT_UPDATE is a proposal. Rollback only the new diagnosis/additive pointers.

## CURRENT — physical IMU trial aborted before START, 2026-10-11

One explicitly approved921600/46080B/s60-second trial attempted; first21 bytes
triggered Bad prefix before any receiver TX or LOGGING_START. Zero IMU/ULog
records; no retry and no throughput/loss-free PASS. Evidence:
`.maixpy/imu-uart-trial-20261011/RESULT.md`, wire/summary/capture-report,
coordinator.jsonl and final-readonly.txt. Independent verify_evidence.py passes
restoration checks: exact original UART/logger commands and stream mapping,
all8 SDLOG values,115200 wired link, temporary topic/dirs absent, disarmed/EV0,
M3C termios restored. Logger subscription count180->187 is a runtime difference,
not an identical-state claim. Outer coordinator exit0 is not receiver success;
receiver exit1 preserved. Source instance0 snapshot193Hz; no policy change.
Next OFFLINE startup framing diagnosis only; physical retry needs separate
approval. VIO-P/S0 PARTIAL unchanged, no calibration/EKF/M3C port/commit/push.
Vault untouched. Prior notes below are historical.

## CURRENT — M3C controller PTY verified, 2026-10-11

User authorized board-side virtual serial tests. Live M3C maixcam2-9d05/aarch64:
55 tests pass in2.293s, zero skips, including real PTY roundtrip and armed refusal
with exact termios restoration. Evidence/command/hashes:
`.maixpy/controller-m3c-pty-20261011/VALIDATION.md`, tests.txt/environment.txt.
Fresh deployment `/root/rm27-controller-pty-20261011.zUIWou/` preserves relative
imports. System Python3.13.2/NumPy2.2.6, existing research pymavlink2.4.49 reused;
missing pyulog1.2.4 copied into isolated research-lib, no installs or old-env edits.
Source archive hashes and retrieved log hashes match. No physical UART, FC logger,
streams, launcher, wiring or calibration touched. Previous controller/user edits
preserved. No saved-real-log replay rerun or hardware-rate PASS claimed.

Operational failures preserved: initial remote quote syntax error, future-mtime
warnings from stale board wall clock, final shell tail argument CR. Wrapper exit1
was a display error after tests; full board/local test logs independently confirm55
OK, not a fabricated command-exit0. No time setting changed. Next is separate60s
921600/46080B/s runtime/logger trial under RUNBOOK, with fresh original-state
backups/restoration. PTY prerequisite complete, do not rerun unchanged tests.
VIO-P/S0 PARTIAL, StageC closed. Rollback only new deployment/additive docs;
preserve existing raw evidence and prior tests. No commit/push/Vault write.

## CURRENT — live read-only PX4 baseline, 2026-10-11

User connected FC and requested the preceding read-only audit. COM19 identity
and three console sessions exited0, released shell/closed port. Full evidence
`.maixpy/live-baseline-20261011/{BASELINE.md,identity.txt,status.txt,imu-status.txt,recheck.txt}`.
Live hash d6f12ad1c4f70ad3230afd7d86e971421e02fef4/MICOAIR_H743_V2/PX4v1.17.0;
Disarmed before/after, EKF2_EV_CTRL0. Selected BMI088 instance0 gyro6684690,
accel6946834. BMI270 instance1 remains unselected. One-second vehicle_imu0 rate190Hz
is below strict200Hz; no sustained rate/capture PASS. Existing accel register1,
gyro overflow1 and reset2 each remained unchanged on reread; event origin unknown.
Logger idle180 subscriptions, `logger start -b 64 -t -m all`, no custom topic file
observed. Wired /dev/ttyS2 remains115200/Onboard/budget5760/flowOff, currently
rx0/version1. Flow/ToF ttyS3 at115200 still receiving comp88. This is not a rerun
of StageA/B and does not replace its saved PASS. No M3C operation this pass.

Added bounded read-only EV/status-listener allowlist entries to historical console
helper, retained transcripts, and this baseline/handoff/proposal. Original staged
controller and unrelated working-tree changes preserved. No hardware configuration
or new capture; no restoration required. No runtime regressions claimed for docs.
Next follow controller RUNBOOK: M3C PTY checks/current ownership, then separately
scoped921600/46080B/s logging trial with actual backups/restoration. VIO-P/S0 PARTIAL,
StageC closed. No commit/push/Vault write; rollback only this dated additive record.

## CURRENT — single-UART controller offline milestone, 2026-10-11

### Repository state / objective

Windows main `3ea1e16086965176db68b88e1c42990f92c5913e` baseline. User requests
completion of the agreed single-UART receiver/controller and offline tests before
physical high-rate IMU qualification. Existing unrelated untracked
`tests/camera_capture.py` / `tmp/` preserved. New controller is a working-tree
implementation, no new commit/push. No M3C/PX4/Vault access or settings changes.

### Actual changes / verified facts

- `.maixpy/imu-design-20261010/single-uart/controller/`: session state machine,
  bounded exclusive POSIX runner, raw/decoded capture audit, saved-byte replay,
  guarded preflight template, tests, validation and future RUNBOOK. Reuses existing
  Decoder/Reassembler/diagnostics and owners/fresh-disarmed guards; no new framework.
- MAVLink2 source1/191 to1/1; sends only logging start/ACK/stop +1Hz HB, no automatic
  acquisition retry. Freshness rechecked at actual UART writes; errors/cancel/armed/
  stale/CRC/sequence/identity/reboot observations fail closed and retain partial bytes.
- M3C termios save/readback/restore/close paths covered by doubles and real Linux PTY.
  Prefix diagnostics never repair/emit an accepted shortened log. Source/tail and
  clock remain UNKNOWN, OpenVINS admission false, VIO-S0 PARTIAL and Stage C closed.
- Existing Linux research host `ceopc` reached through historical SSH endpoint.
  Isolated test copy `/home/shiuhou/Projects/rm27-vio-20261007/controller-offline-20261011.WhOMGr/`;
  no old Linux Git worktree/M3C deployment overwritten. No dependency installs.

### Fresh verification / failed attempts

Full commands/logs in controller/VALIDATION.md. Linux Python3.12.3/pymavlink2.4.49/
pyulog1.2.4:55 tests pass including both PTY cases. Windows53 pass/2 POSIX skips.
Existing reassembly28 +decoder10 +diagnostic9 +model7 =54 pass. Root pytest226 pass/
1 existing skip. Saved real ULogs in synthetic framing/timing through the controller
reconstruct exact SHA/bytes, preserving391 historical/306 current-A2 BMI270 dropouts;
neither is selected BMI088 capture. Stage A/B SHA remains d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f.
TDD red/green failures (missing features, unsafe intent timing/race, test-double
POSIX constants) retained; final tests pass without lowering criteria. WSL absent;
initial SSH metadata inspection quoting failed, corrected. No failed hardware trial.

### Decisions / risks / assumptions

Implement existing ULog candidate before custom firmware. Pinned writer discards
pending partial chunks at STOP; ACK/quiet/valid boundary is not source-completeness
proof. Receipt timing isn't a camera/FC clock map; deltas/dt aren't admitted point
samples. JSON preflight is operator attestation, not authenticated readback. CPU,
M3C driver, real921600 speed, current BMI088 completeness and ACK/tail behavior
remain hardware-dependent. SIGKILL/power loss aren't solved by finally cleanup.

### Next / rollback

One pending physical experiment: specific approval for existing M3C↔PX4 UART60s
vehicle_imu trial at temporary921600/46080B/s and minimal MAVLink-only logger,
independent PX4 USB backup/control/restoration. No wiring/firmware/parameter changes.
Actual original PX4 command/streams/topic bytes or absence must be backed up and
restored by that coordinator; this UART runner neither changes nor automates them.
Read RUNBOOK, run PTY tests on M3C first, freshly audit exact hash/Disarmed/EV0/IDs.
Do not proceed to calibration/sync/real VIO solely because transport looks clean.
Rollback only this controller and additive docs relative to3ea1e16, not raw evidence,
original Stage A/B, frozen reassembly manifests or unrelated edits. Vault not updated.

## CURRENT — SLAM → VINS/VIO roadmap index, 2026-10-11

- Baseline: Windows main `fba7457bf3656e4c4a5833611190579821f45fb0`, matching
  remote main before this change; untracked `tests/camera_capture.py` / `tmp/` preserved.
- User objective: make the original SLAM plan and later VINS/VIO plan accessible
  to other Codex instances alongside the handoff, then publish to GitHub.
- Verified source state: original 2026-09-20 VSL-0–8 roadmap already tracked since
  `bd25acf`; the 2026-10-07 v1.0 VIO `new_plan.md` was published in `4dba7fd`.
  Neither full original is replaced or duplicated by this documentation task.
- Actual changes: `rm27/perception/vision/docs/PLAN_HISTORY.md`, README and resume
  links; proposal note in VAULT_UPDATE. Explicit historical→current relationship,
  candidate roles, and planned-gate vs measured-result distinctions.
- Decision/risks: reuse existing plans/evidence and unchanged acceptance criteria.
  VINS-Fusion/sqrtVINS remain candidates, not implied completed implementations;
  Stage A/B transport PASS does not imply G4 fusion or real Stage C qualification.
  Some older plan assumptions and next actions are superseded by current reports.
- Verification: 27 published local plan/entry links checked, both full source plans
  confirmed unchanged, and `git diff --cached --check` exited 0. Normal push is
  checked against remote main after completion; no runtime/physical tests or new PASS.
  No failed experiment, remote device access, deployment or Vault write in this task.
- Next: follow CODEX_RESUME's current software task and safety boundary, not every
  old future-stage operation. Rollback only this doc supplement relative to fba7457;
  do not erase source plans, raw evidence, or unrelated work.

## CURRENT — SSH workspace location supplement, 2026-10-11

### Repository state / objective

Windows main at `4dba7fd79cb2ecad739c1abf22c8a0fc577dc07c` before this supplement;
remote main matched. Unrelated untracked `tests/camera_capture.py` / `tmp/` preserved.
User explicitly requested publishing the SSH-host/M3C/local location inventory.

### Actual changes and verified facts

- Added `rm27/perception/vision/docs/WORKSPACE_LOCATIONS.md` and linked it from the
  resume guide. Source locations were checked against saved handoffs, validation
  reports and experiment scripts, not by new SSH/device access.
- Linux research worktree: `/home/shiuhou/Projects/rm27_slam_vio_openvins/` on the
  historically recorded `shiuhou@10.4.135.84`; separate evidence/build/data root
  `/home/shiuhou/Projects/rm27-vio-20261007/`.
- M3C: historical `root@10.18.198.1`, deployments
  `/root/rm27-mavlink-test-20261010/` and `/root/slam-bench-20261007/`.
- Local Windows `.maixpy` holds editing mirrors and later offline IMU/reassembly
  work. Selected publication is not a complete backup or automatic SSH deployment.

### Verification / decisions / risks

Documentation-only: reviewed changed diff; `git diff --cached --check` exited 0,
and the local-link check verified 16 versioned targets with exit 0. Normal push
is verified against remote main after completion, not pre-claimed. No software/hardware tests
rerun and no new runtime PASS claimed. Preserve both historical and current notes.
No failed experiment in this supplement; remote current state remains UNKNOWN.
Addresses/paths can change, old Linux worktree may still be dirty, and deployed
board decoder can predate current local analysis. No credentials included.

### Next actions / rollback

Other Codex instances start with CODEX_RESUME and WORKSPACE_LOCATIONS; inspect
remote identity and dirty Git state before integrating, never blindly overwrite.
VIO software next task and Stage C boundaries below are unchanged. No Vault access.
Rollback only this documentation supplement relative to `4dba7fd`; do not reset
the repository, remote worktree, saved experiments or device deployments.

## CURRENT — portable PX4 / M3C handoff publication, 2026-10-11

This section supersedes older CURRENT/next-action paragraphs below. User explicitly
requested commit/push and connection documentation for other Codex instances.
No hardware or Vault access is part of this publication task.

- Start: `rm27/perception/vision/docs/CODEX_RESUME.md`, then
  `PX4_M3C_CONNECTION.md`, root `new_plan.md` and `.maixpy/README.md`.
- Git baseline: local main b8e7299 fast-forwarded without conflict to existing
  remote main 7a91a02e575794ba6756012d31eeb66d73182f35 (merged OpenVINS checkpoint).
  Windows history preserved in `.maixpy/HANDOFF_WINDOWS_20261011.md`; remote
  history below retained. No reset, force push, or replacement of upstream work.
- Actual changes: portable wiring/port/source/clock/status summary, curated existing
  research scripts/tests/reports at their original paths, publication index and
  additive README/plan/Vault-proposal pointers. Large raw evidence remains local.
  `.gitignore` keeps generated `.maixpy` content excluded; only selected files
  are explicitly versioned. Unrelated `tests/camera_capture.py` / `tmp` remain out.
- Physical link: M3C UART2 `/dev/ttyS2` ↔ FC UART3/PX4 `/dev/ttyS2`, crossed TX/RX,
  common ground, tested 115200/8N1/no flow. COM19 is independent USB inspection.
  Current audited PX4 v1.17.0 hash d6f12ad1c4f70ad3230afd7d86e971421e02fef4.
- VERIFIED historical Stage A/B: MAVLink2 HEARTBEAT and synthetic ODOMETRY→uORB,
  stop/restart attribution. Preserve, don't rerun. EKF2_EV_CTRL=0 / Disarmed are
  last observed states, not fresh observations from this task.
- PARTIAL VIO-S0: HIGHRES 50Hz transport measured; requested100 capped62.112Hz.
  Integrated measurement semantics, selected BMI088 source completeness, timing
  and camera clock mapping remain unqualified. VIO-P finite reliable-input cohort
  is promising, overall PARTIAL. Stage C remains NOT_STARTED.
- Superseding constraint: user reports no spare UART; no more spare-pad requests.
  USB-host fallback is driver/role/management blocked. Single-UART stock MAVLink
  ULog is a candidate, not a hardware transport or OpenVINS PASS. 921600 is planned,
  NOT applied/approved by this publication.
- Next software work: single-owner live start/ACK/stop/timeout/tail/restore controller
  with offline tests, reusing the finite reassembler and existing decoder. No live
  controller deployment, fusion, calibration, flight or new capture in this task.
- Evidence availability: versioned reports summarize earlier results; original raw
  byte/log/trajectory artifacts and full vendor source builds are not shipped.
  See `.maixpy/README.md` for reproducible fixture commands and local-only limits.

Publication validation is recorded in
`rm27/perception/vision/docs/PUBLICATION_VALIDATION.md`; the resulting commit and
push are identified by Git history/remote state, not a pre-recorded success claim.

## CURRENT — authorized offline BMI270 capture, 2026-10-08

### Repository state / objective
Research worktree remains research/vio-openvins-baseline at13c7a77 with existing
uncommitted VIO work preserved. Objective: short props-off/disarmed FIFO ULog
capture, verify offline data chain, restore original logger settings.

### Actual changes and verified results
One ULog captured through temporary9-topic list, BMI270 instance1/device3604506;
logger reader2500Hz, original64KiB buffer, logger on/off only. User explicitly
confirmed prop removal. No parameter changes. FC original retained at
/fs/microsd/log/sess100/log100.ulg. Two downloads match6,896,444 bytes and SHA256
d94a142c5a474e7a755bffd534a41cf3255081d87d4868dabf63493a5146f46d.
pyulog1.2.4 parses without file corruption. Actual18.122s file/17.9s IMU span.
Gyro/accel FIFO12648/11933 retained samples, median633us cadence but effective
706.681/666.823Hz due to gaps.391 ULog dropouts, max sample gap111.409ms. Sample
times ordered/no duplicates; no NaN/clipping; SI/FIFO scaling association agrees.
No loss-free-data PASS. Audit, contract, status, this handoff, Vault proposal and
validation record updated; new `PX4_IMU_OFFLINE_VALIDATION.md` is detailed report.
Evidence root /home/shiuhou/Projects/rm27-vio-20261007/imu-offline-20261008;
Windows source .maixpy/imu-offline-20261008. Helpers/tests are research-only.

### Restoration, safety and failed attempts
Fresh ps confirms original `logger start -b 64 -t`; idle mode all; seven SDLOG
values unchanged and custom topic file/created dirs absent again. Temporary
file181bytes preserved locally before deletion; no existing logs removed.
Runtime subscription count142->147 is recorded, not hidden; this may reflect
optional-topic availability after restart; exact difference not isolated. ULog records and
observed heartbeats disarmed. Source explains logger-start perf counter reset;
do not mistake lower counters for a reboot or compare them cumulatively.
Remote CRC request failed generically; second independent download/hash used,
not a fabricated remote checksum. Windows helper source-field and Unix-temp-path
issues corrected before capture; failed evidence retained.5 guard +3 synthetic
analysis tests pass, no production regression rerun/claim for doc/helper work.

### Decisions, risks, next action and rollback
VIO-S0 PARTIAL: physical raw export verified, completeness failed for tested
logger config; precise acquisition/exposure timing and synchronization unqualified.
VIO-P unchanged PARTIAL. Do not conflate sensor~1580Hz with logged~667--707Hz.
Next: isolate logger buffer/SD/scheduling bottleneck before any accepted dataset;
no second acquisition or logger tuning performed. No physical action needed now.
Hardware logger config already restored. Revert only this dated documentation
change if needed; docs-before backup is in evidence root, preserve raw ULog and
all older research. No camera calibration, M3C, live stream, firmware, flight
parameters, commit, push or Vault write.

## CURRENT — raw export/timing/transport audit, 2026-10-08

### Repository state and objective
Research worktree /home/shiuhou/Projects/rm27_slam_vio_openvins, branch
research/vio-openvins-baseline, prior recorded HEAD13c7a77; existing dirty VIO
implementation/reports retained. Objective: confirm available PX4 raw export
and clock/transport semantics without collecting data or changing hardware.

### Actual changes and verification
Updated IMU_SOURCE_AUDIT.md, RM27_VIO_DATA_CONTRACT.md, this handoff,
VAULT_UPDATE.md proposal and existing validation record. Windows-local diagnostic
helper gained only logger/SD read-only command allowlist entries. No schema,
adapter, estimator, PX4 config or firmware changes. Exact command/results and
pinned source paths are in the audit's newest section. COM19 logger/parameter/ls
queries exited0: logger idle, profile1/mode0/boot_bat0, SD readable. No tests of
runtime algorithms are claimed for this documentation/diagnostic-only work.

### Findings, rationale and remaining risks
Default sensor_gyro/accel ULog intervals1000ms cannot qualify VIO. FIFO profile
bits target instance0, not selected BMI270 instance1. Proposed first raw export:
explicit instance/device-bound SD ULog then host download, with capture/dropout
qualification still required. HIGHRES/SCALED_IMU are interval-derived; neither
is a raw substitute. Source supports ULog MAVLink streaming for later USB-link
tests; throughput, M3C USB-host/power setup, time mapping and camera exposure
semantics remain unverified. FC timestamps use HRT boot microseconds, driver
DRDY/read-related rather than proven ADC latch. FIFO last-anchor reconstruction
is source-supported, not capture-validated. VIO-P/S0 remain PARTIAL unchanged.

### Failed attempts and verified facts
Custom logger directory/file inspection returned Not a directory; subsequent
ls /fs/microsd succeeded. Do not infer missing SD. Shell sysinit warning persists;
status commands work. Supported source behavior does not prove vendor binary
reproducibility. No sustained export test or new sensor dataset exists.

### Next actions and rollback
Next software action requires approval for reversible logger configuration and
bounded disarmed capture; do not execute from this handoff. User confirms camera
and FC are separate on the desk, superseding the prior photograph request below.
No physical action now. Single later physical step: rigidly mount camera and FC
together when synchronized capture is authorized; do not wire/assemble yet.
Rollback only this dated doc addendum and new local helper allowlist entries;
preserve all previous VIO work. No commit/push/Vault write. Report edits are
working-tree evidence, not a new commit or qualification PASS.

## CURRENT — live COM19 read-only qualification, 2026-10-08

Read official MicoAir manual first; target micoair_h743-v2, BMI088+BMI270,
SPI2/SPI3 corroborated by official v1.16.0 source. Windows COM19 open/read succeeded
at57600; actual ver all says MICOAIR_H743_V2 / micoair-v1.15.2 / hash
4817c0618a1286846116e90c6eb8919efaa013cf, build Dec21 2024. This supersedes
the prior unavailable-FC state and local dd0ad74 source assumption. Device IDs
identify BMI088 instance0, BMI270 instance1 selected. All raw/FIFO/vehicle_imu
topics have two instances. One-second uorb top shows accel/gyro802/666 Hz and
1580/1580 Hz; vehicle_imu199/196 Hz. Internal topic rates only, not link performance.
No raw dataset acquired. Some existing gap counters nonzero; no no-loss claim.

M3C and FC NOT connected (user-confirmed). PX4 USB CDC is current Windows
inspection link; configured57600 is not proof of future UART throughput. DDS
client not running. HIGHRES_IMU remains interval-derived and potentially
estimator-bias corrected; preferred future path preserves one identified
sensor gyro/accel or qualified FIFO pair with sample timestamps and clock mapping.
Raw export, host/FC clock mapping and camera exposure timing are not qualified.
Keep VIO-P and VIO-S0 PARTIAL. Read-only parameter/status checks only; no firmware,
stream settings, parameters, wiring, pinmux, logging, calibration or M3C integration
changed. Diagnostic clients close COM19/release shell ownership. Commands and
observations are detailed in IMU_SOURCE_AUDIT.md; no user console commands needed
to repeat these successful queries. No regression run for documentation-only work.

Single next physical verification: photograph current camera/FC placement with
the FC direction arrow visible, to check relative orientation and rigid mounting;
do not alter wiring or assemble a new setup. Official manual says45deg mounting,
current SENS_BOARD_ROT=0: do not infer a correction without actual mounting evidence.

Changes: audit, contract, status, handoff and Vault proposal; read-only helper
scripts remain Windows-local under .maixpy/s0-audit-20261008. No push/Vault write.

## Historical PX4 correction before COM19 inspection

User confirms PX4, not ArduPilot, on the actual FC. All earlier ArduPilot/local
ICM pairing recommendations below are superseded for this VIO line. Prioritize
OS04A10 + actual PX4 gyro/accel; M3C onboard ICM is NOT assumed. VIO-P PARTIAL
and its reproducibility gate remain unchanged; S0 PARTIAL for missing deployed
identity, link and timing/rate evidence.

Read-only source audit: clean legacy PX4 checkout dd0ad74fdadc68a62b479129ca3f382c006426f4
provides sensor_gyro/accel and FIFO definitions, candidate MicoAir target drivers,
vehicle_imu integration, HIGHRES_IMU, DDS topic list and TIMESYNC implementation.
It is not the installed firmware. sensor_* carries SI rates/accel and driver
sample times; FIFO can be averaged. HIGHRES_IMU uses sample time but derives
interval averages and may remove estimator bias; do not call it raw acquisition.
Default inspected DDS list does not export raw sensor topics. All actual rates
and synchronization quality remain unmeasured. Camera VIN PTS remains opaque.

M3C reachable; no identified FC USB or bridge endpoint found. Windows serial
inventory shows Bluetooth ports only; host no ttyACM/ttyUSB. UART wiring absence
is NOT proved. No serial reads, sample collection, parameters, firmware, pinmux,
calibration, EKF2 integration or M3C port performed. Updated audit/contract/status
and Vault proposal only; no push. Source hashes are in IMU_SOURCE_AUDIT.md.

One next physical verification step: connect PX4 FC to Windows by USB data cable
without the propulsion battery, to permit read-only board/firmware/IMU identity
inspection. No speculative UART wiring. Earlier completed USB action referred
to M3C and does not establish FC connectivity.

## Subsequent connectivity correction — 2026-10-08

User reconnected M3C; helper and SSH now succeed at 10.18.198.1. Read-only sysfs
shows generic spidev1.0/2.1/2.3 and platform ADC, not an identified IMU. Bundled
imu_ahrs app is code presence only. No acquisition/register probe/configuration
performed. Earlier unreachable status and requested USB action below are
superseded; S0 remains PARTIAL for unverified sensor identity/timing, not network.

## 2026-10-08 VIO-S0 continuation — PARTIAL

VIO-P study closed with the actual repeatability result below; no forced PASS,
threshold change or algorithm fix. S0 now identifies CODE-SUPPORTED local
ICM-42688-P SPI/FIFO tooling in camera source snapshot c7d47b2, previously omitted
from the audit. Existing OS04A10 + local ICM is the preferred conditional pairing,
not a confirmed available device. Separate camera-board IMU remains UNKNOWN;
MicoAir743v2 BMI088/BMI270 and filtered/send-time HIGHRES_IMU are fallback source
evidence, not a verified direct M3C acquisition path. Live M3C check timed out from
Windows; Linux host returned No route to host. No new raw data was collected.

Updated `IMU_SOURCE_AUDIT.md`, `RM27_VIO_DATA_CONTRACT.md`, `VIO_STATUS.json` and
Vault proposal. Corrected obsolete adapter-not-implemented text; schema/code
unchanged. Source review distinguishes sensor PLL time, opaque VIN PTS, software
receipt after FIFO/file write, and FC send-time clock. All mappings/offsets/drift,
mounting transform and real sensor noise remain unqualified. Fresh evidence:
helper connectivity result, source/hardware records and SHA256 values in audit.
Documentation-only validation; no new regression or runtime PASS claimed.
External research unnecessary: this is availability/source audit, not datasheet
qualification. Main workspaces, physical settings and Vault unchanged.

Exactly one next physical action: reconnect M3C's existing USB data link to the
Windows computer to restore `10.18.198.1` for read-only inventory. No SPI rewiring,
FC connection, capture or calibration authorized by this handoff. Audit remains
PARTIAL until current device identity/access evidence can be obtained.

## Native repeatability study — completed 2026-10-08, cause unresolved

Ten frozen native runs plus three separate configuration controls completed;
all 39 native/player/recorder exits are zero, final frozen hash check passed.
See `rm27/perception/vision/docs/NATIVE_REPEATABILITY.md` and external
`repeatability-20261008/analysis-13.json` for per-run and all-pair evidence.
Baseline ATE 5.432--7.653 cm, mean 6.608 cm, sample SD 0.689 cm; 15/45 pairs
exceed 1 cm. First saved states agree; sustained divergence starts at 5.65--10.95 s
of dataset time. OpenCV single-thread/publisher-thread-off controls still vary
(ATE 5.551--6.604 cm). No unique cause proved; async dispatch and a reference
capture lifetime risk need dynamic tracing. The 1 cm gate is not demonstrated
as a native repeatability guarantee, but remains unchanged. VIO-P PARTIAL.
Only experiment evidence and documentation changed. No new regression-suite
claim: prior 226 pass/1 skip plus ROS2 7/7 are historical. Next action is isolated
worker-lifetime/callback-order diagnosis, not hardware. No push or Vault write.

## Historical active-diagnosis checkpoint — superseded above

Native repeatability cohort is RUNNING; do not mark completed. See
`rm27/perception/vision/docs/NATIVE_REPEATABILITY.md` for frozen artifacts,
controller, source audit, interim results and planned separate configuration
control. First two of target ten new native runs: ATE6.3969/6.7431 cm, each
2800 poses. Existing adapter/math/data/1cm gate unchanged; VIO-P stays PARTIAL.
App heartbeat `rm27-vio` will resume checking and final analysis; never start a
duplicate batch. No final population range or causal root-cause claim yet.

## Latest continuation — runtime adapter implemented, acceptance PARTIAL

See `rm27/perception/vision/docs/OPENVINS_ADAPTER.md`. The existing experiment
runner dispatches OpenVINS to a frozen EuRoC VIO loader, isolated container run,
live input/output observer, exact output reconciliation, normalization and SE3
evaluation. Legacy monocular handling and LocalizationEstimate v2 are unchanged.
Unknown tracking/publish evidence still produces incomplete v2 projections.

`adapter-runtime03`: all four processes exit 0; all 2912 image bytes and 29120
raw IMU samples/time/order match ASL. Live 2800 visual +27980 propagated states
match independent MCAP exactly. Adapter and same-run native metrics are exact.
ATE 5.7385 cm; 1s RPE 4.4005 cm /0.476994 deg; path bias -1.50394%, no rescaling.
All 17 final immutable-artifact checks pass; binary/config/data remain unchanged.

**Overall VIO-P remains PARTIAL**: ATE differs from historical native02 by
1.2729 cm, above the predeclared 1 cm limit. Other metric/coverage checks pass.
This is not waived because the new error is smaller. Raw upstream states first
diverge at row188, before adapter conversion. Cause is not yet established.
Failed runs01/02 and run03's rejected gate are preserved; no cherry-picking.
Native-only control03 also exits0 with 2800 poses: ATE 6.2403 cm, 1s RPE
4.4959 cm /0.477945 deg. Native variability exists independently of adapter,
but one control does not establish its full cause or bound. Historical baseline
and acceptance thresholds remain unchanged; no PASS granted from this control.

Fresh tests: 226 passed /1 ROS-only skip; separate sourced ROS2 suite 7/7 pass.
Independent read-only review findings on coverage and propagated-stream checks
were fixed and re-reviewed. Changes remain uncommitted on HEAD `13c7a77`.
No hardware, main-checkout modification, Vault write, commit or push.

Next action is software-only: resolve historical native-run reproducibility /
acceptance discrepancy before granting VIO-P PASS. Do not weaken the fixed
comparison thresholds or start downstream hardware work to bypass this gate.

## Latest continuation — native SE3 evaluated, adapter started

See `rm27/perception/vision/docs/NATIVE_SE3_EVALUATION.md` for exact commands,
policies, hashes and limitations. Existing clean run02: 2780/2800 poses within
reference overlap, SE3 scale fixed 1, ATE RMSE 0.0701139912 m, 1s RPE RMSE
0.0452377799 m / 0.477985477 deg. Path-length ratio 0.980585754 is a diagnostic
only, never a correction. Independent SciPy cross-check PASS. Original GT
orientation caveat retained; bounded reference quaternion normalization explicit.

Native accuracy evaluation integrity is PASS, not flight qualification. Broader
VIO-P remains PARTIAL: adapter projection implemented and exact against 2800
saved raw poses, but no new runtime adapter replay/parity. Unknown state and
publish/completion times stay missing; output is not a complete v2 estimate.
Fresh regression: 208 passed / 1 ROS skip; separate ROS2 tests 7/7 passed.
The earlier lifecycle-only sections below are historical; latest authorization
now permits adapter work after evaluation. No hardware/Sim3/push/Vault changes.

Next software action: EuRoC framework loading and runtime dispatch, then full
native/adapter replay parity. The historical physical-action suggestion below
is **not** a requested action for this no-hardware continuation.

## Latest verified result — lifecycle task

**VIO-P PASS for the current request's native execution/lifecycle gate.**
Designation: **pinned OpenVINS + explicit ROS2 lifecycle compatibility patch**.
The original broader adapter/parity/SE3 roadmap is still incomplete, and those
items were explicitly not started in this task. This is not flight or M3C
qualification. See `rm27/perception/vision/docs/ROS2_LIFECYCLE_FIX.md`.

Gdb proved DDS factory static destruction preceded the global visualizer's
publisher destruction after main returned. Only ROS2 `sys`/`viz` ownership
was moved into main; ROS1 behavior and all three algorithm-library binaries
are unchanged. The original four header substitutions are retained separately.

- No-data regression: before 2/2 abort; after 10/10 clean exit 0, publisher
  thread on/off. Gdb after-fix confirms visualizer destruction precedes factory.
- Full data: `native-ros2-run02-lifecycle`, 2,912 camera-update logs, exactly
  2,800 online states and 2,800 `/poseimu` messages, native/player/recorder exit 0.
- Existing suite: 190 passed, 1 ROS-only skip; ROS2-specific suite: all 7 pass,
  including that skipped case. Evidence is under `lifecycle-debug/`.
- Original failed run01, no-data crash logs, old source/build and gdb traces
  remain intact. No data download/regeneration, main-workspace or Vault change.

Source `upstream/openvins-jazzy-lifecycle`, build `native-ros2-lifecycle`, under
`/home/shiuhou/Projects/rm27-vio-20261007`. Patch is
`tools/openvins/ros2-lifecycle.patch`; smoke test and gdb commands are alongside.
Research changes remain uncommitted; no push/mainline merge performed.

## Latest transport decision — 2026-10-07

The user superseded the ROS1-first baseline choice: prefer official ROS2 data and
the pinned native ROS2 path; host stays ROS2-oriented, future M3C ROS-free where
practical. See `rm27/perception/vision/docs/ROS2_DATASET_REVIEW.md` for source
checks and the observed official Drive HTTP 404. That review predates successful
ASL intake and ROS2 packaging above. No algorithm modification performed. The earlier ROS1 instructions
below describe historical attempts, not a requirement to continue with ROS1.
External evidence has moved to `/home/shiuhou/Projects/rm27-vio-20261007`.
The earlier M3C SSH timeout is historical: a subsequent read-only check connected
and saw an ADC plus generic spidev devices, not a verified IMU stream.

## Repository state

- Project: RM27 OpenVINS public qualification and IMU preparation.
- Repository: `/home/shiuhou/Projects/rm27_slam_vio_openvins` on `10.4.135.84`.
- Branch: `research/vio-openvins-baseline`.
- Commit: `13c7a77bbe0fd256e6765efd4459fbca3426e0b7` (authorized integration merge).
- Working tree: IMU implementation/tests, container recipe, VIO reports and this
  handoff are uncommitted task changes. No push or mainline merge performed.
- Linux primary checkout remains `acc70e3`; Windows primary remains `b8e7299`
  with its original unrelated modified/untracked files preserved.

## Task objective

Current task: fix only the evidenced ROS2 shutdown lifetime defect and qualify
no-data/full-data clean exits on the existing pinned public baseline. Completed
for this scoped gate. Original roadmap's adapter, parity and SE3 evaluation are
still pending; no authorization to start them in this task. VIO-S remains
PARTIAL; VIO-R/B/I/M remain NOT_STARTED.

## Actual changes

- Added `ros2-lifecycle.patch`: one upstream ROS2 entry file, local instead of
  global ownership. Algorithm shared-library hashes unchanged.
- Added real-runtime `lifecycle_smoke.py`, debugger image recipe and gdb command
  files; documented root-cause order and clean full rerun in ROS2_LIFECYCLE_FIX.

- Created sibling worktree; imported Windows commits via bundle and merged with
  host baseline. Resolved only the fixture launcher conflict by retaining both
  platform behaviors. Baseline suite: 163 passed.
- Extended existing `experiments/vio.py` without changing the sample schema or
  LocalizationEstimate: sequence/time/device validation, gap and saturation
  observations, optional static statistics/overlapping Allan deviation and CLI.
- Added 21 synthetic tests and a nullable capture metadata template.
- Added `IMU_SOURCE_AUDIT.md`, `RM27_VIO_DATA_CONTRACT.md`,
  `VIO_BASELINE_REPORT.md`, and `VIO_STATUS.json` under vision docs.
- Added pinned `tools/openvins/Dockerfile` and native-resume instructions.
- Retrieved pinned Docker base and official source archive outside the repo;
  retained selected input snapshots/hashes and failure logs.
- Created `.codex/tasks/2026-10-07-vio-openvins/` lean evidence packet and
  `VAULT_UPDATE.md` proposal. No Vault content was read or modified.

## Verification commands and observed results

From the research worktree:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/shiuhou/venvs/mujoco/bin/python -m pytest tests -q
git diff --check
```

Current lifecycle validation: **190 passed / 1 skip**, plus **7/7 ROS2-specific**
tests and **10/10** real no-data lifecycle cases. Full playback exits 0 with
2,800 online poses; see latest report for exact commands and hashes.
Historical initial IMU implementation: **184 passed**, diff check clean. Evidence logs
under `/home/shiuhou/rm27-vio-20261007/`. `imu-tests-red.log` records 18 expected
missing-feature failures; `imu-tests-red2.log` records the receipt-clock regression
before its correction. Tests are not physical sensor or real backend evidence.

## Failed attempts

- Preserved header-only full run: shutdown SIGSEGV/139; no-data SIGABRT. Gdb
  isolated global/static teardown ordering and the minimal patch fixes it.
- The following download/connectivity attempts are historical, not blockers:

- Full and shallow Git clones failed (EOF/index-pack); official commit archive
  succeeded. Source remains an extracted archive, not a Git checkout.
- Initial Docker base pull timed out, retry succeeded. Dependency image build
  subsequently had repeated package download failures and was deliberately
  canceled. No native compilation or execution took place.
- Official EuRoC bag download failed through HTTP/HTTPS and direct attempts;
  local Windows download also timed out. No substitute dataset used.
- M3C SSH at `10.18.198.1` timed out; board-side inventory unavailable.

## Decisions and rationale

- Preserve the user's native-first gate: do not implement/claim a runtime wrapper
  before the native program is qualified. Adapter and evaluation remain pending.
- Selected ROS2 Jazzy container isolates research dependencies; Noetic was a
  historical attempt, not an RM27 architecture choice. No host apt/proxy changes.
- Hardware source code is CODE-SUPPORTED, not proof of the installed board.
- Unknown IMU timing/units/extrinsics/noise remain unknown; no flight integration.

## Verified facts

- Upstream revision: `69488123ed9362dd44b6f28e7f4680abbff1442b`; archive and base
  image hashes appear in `VIO_BASELINE_REPORT.md`.
- Pinned native code has a truth-initialization option; do not set estimator
  `path_gt`. It also distinguishes camera/state/IMU propagation times.
- Candidate MicoAir743v2 hwdef supports BMI088 via SPI2 and BMI270 via SPI3.
- Inspected HIGHRES_IMU sender uses `AP_HAL::micros64()` at send time, not a
  verified acquisition timestamp. This does not prove live telemetry availability.

## Assumptions and open questions

Actual IMU identity, firmware, output configuration, wiring/transport, samples,
acquisition clock and synchronization remain unverified. Public data is verified
and native runtime metrics exist; RM27 adapter/parity and SE3 accuracy metrics
do not. The propagated-odometry publication count is not an IMU receipt count.

## Risks

An online saved trajectory must not be labeled optimized. Original V1_01_easy
orientation truth has a documented limitation. No host result may be presented
as M3C VIO throughput. The old camera geometric result does not qualify camera–IMU
timing/extrinsics. Avoid copying simulation parameters to real hardware.

## Next actions

Stop at this task's verified native/lifecycle gate. Adapter, M3C, autopilot,
alternative estimators and unrelated refactors were not started. Any later
adapter/parity/SE3 work must be a separate authorized continuation. Follow
`tools/openvins/README.md`; preserve failed and clean runs.

Exactly one next physical action: photograph the intended IMU/flight-controller
board so its model and revision markings are legible. Generic SPI devices and
historical firmware definitions do not identify the actual raw-IMU source.

## Rollback point

Pre-feature baseline is merge `13c7a77`; both parent commits and main checkouts
remain intact. Review/revert individual task diffs if desired; do not reset or
clean the user's repositories or delete external evidence directories.
