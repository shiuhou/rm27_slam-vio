# Vault update proposal — not ingested

## Publication supplement — 2026-10-12

Pending controller/source-diagnostic reports are being published under the user's
requested new Git identity shiuhou/uhshi371@connect.hkust-gz.edu.cn; old shared
commit emails are not rewritten. `PUBLICATION_20261012.md` and publication
VALIDATION.md distinguish portable tests from saved-data evidence and exclude raw
recordings/credentials/unrelated work. This is publication only, no new hardware
qualification, firmware or Vault action. Stage A/B preserved, VIO-S0/P PARTIAL,
Stage C CLOSED. No Vault ingestion is claimed; this remains a local import proposal.

## Latest upstream-gyro observation FAILED — 2026-10-11

Local report `.maixpy/imu-upstream-gyro-20261011/RESULT.md`: ONE approved
stock-firmware observer attempt stopped at logging286→288/global19→21. One PX4
TX-buffer rejection accounts for the missing position; successful writes match
received frames in all six observed counter intervals. Increased observer load
failed at startup, not60s source qualification. Original logger skip/IMU coverage
and cadence remain UNKNOWN; prior completed control remains unchanged.
Windows34 PASS/3 POSIX skips and M3C27 PASS/zero skips, scope/restoration/hash/
CRC verification PASS; original115200/logger/streams/SDLOG/M3C termios restored.
No firmware, parameters, sensor selection/rates, wiring, fusion or Stage C.
VIO-S0/P PARTIAL, Stage A/B preserved; RAM-trigger trace is DESIGN ONLY pending
firmware authority/rollback. Failed prefix and helper attempts preserved, no
retry/commit/push. NO Vault access or ingestion; this is an import proposal only.

## Latest completed reader control — 2026-10-11

Local evidence `.maixpy/imu-reader-control-20261011/RESULT.md` / `HANDOFF.md`:
ONE approved60s same-condition -r2500 vs historical -p vehicle_imu comparison.
Transport clean in measured window, but11837 records197.104634Hz and TWO
counter-bracketed gyro holes4460/4507us. Hypothesis FAILED, not a loss fix.
Original >=200Hz/continuity and model gates unchanged; VIO-S0/P PARTIAL,
Stage C CLOSED, accel/source/tail/clock UNKNOWN. No rate/firmware/parameter change.
Windows15 new +71 relevant regression tests and M3C48 related tests PASS;
original bytes/hash transfers/AST scope and exact restoration independently
verified. Failed helper attempts and Stage A/B preserved. Fresh UART115200,
logger idleall, EV0/Disarmed; temporary file/empty dirs removed with local copy.
Next needs scoped source execution/generation observability, not blind retry.
No stage/commit/push; NO Vault access/update. This is an import proposal only.

## Next logger-reader experiment PLAN ONLY — 2026-10-11

Local plan: `docs/superpowers/plans/2026-10-11-vio-s0-logger-reader-control.md`.
Offline profile guards/tests and saved-row comparison precede one separately
approved60 s same-condition physical control: -p vehicle_imu -> -r2500 only.
No implementation, new tests/capture or configuration change executed this turn;
no Vault access or Git push. Existing diagnosis28/27 hashes matched before additive
root edits, with matching HANDOFF/VAULT_UPDATE snapshots retained in new repo-before.
Subscription continuity and source cadence are separate gates; >=200Hz unchanged,
integrals are not instantaneous samples, accel/tail/clocks/model unqualified.
VIO-S0/P remain PARTIAL; full StageC CLOSED. Do not import the proposed experiment
as completed evidence or assume fixed reader cadence guarantees more source data.

## Offline residual subscription/cadence diagnosis — 2026-10-11

Proposed durable evidence: `.maixpy/imu-source-diagnosis-20261011/DIAGNOSIS.md`,
analysis.json/verification.json and56 fresh offline tests PASS/zero skips.
No Vault access, no new hardware or runtime change; prior80/36 hashes preserved.
Confirmed4554us coverage hole at LOGGER vehicle_imu subscription queue1/generation
skip, not UART. Exact generation magnitude or scheduling trigger remains UNKNOWN.
197.215284Hz below unchanged200Hz is not explained by a single lost integral;
298 longer accel integral windows, plus exact dual-integrator/callback scheduling,
account for most slower cadence. Period multiples are INFERRED, not hardware counts.
No fixed5ms guarantee, no firmware/parameter fix or VIO suitability claim.
StageA/B unchanged; VIO-S0/P PARTIAL, StageC CLOSED. Next reader-cadence comparison
is a proposal only; original source/per-sensor/run traces remain missing evidence.
Never turn271 large integration endpoints into271 drops or retime/fill the hole.

## Reduced-telemetry physical comparison — 2026-10-11

Evidence: `.maixpy/imu-uart-reduced-trial-20261011/RESULT.md`, raw outputs,
analysis-02.json/verification-02.json and fresh restore readbacks. ONE approved
run,18 runtime sources unchanged; no firmware/parameters/IMU selection/rates/
wiring/camera/fusion/ARM change or push/Vault access. Same921600/46080/minimal
MAVLink-only logger,48 numerical nonessential streams removed then restored.
Normal data60.016212s completed,5001 framesCRC checked,0sequence/CRC errors,
65LINKsnapshots/64intervals successful-write4980=received4980,rejection0.
Bounded TRANSPORT COMPARISON VERIFIED; universal physical fix not proven.

11843 BMI088 integrals197.215Hz FAIL original200Hz gate. One gyro coverage hole
4554us and logger generation-skip1→2 remain; only vehicle_imu is full-rate in
this custom list and exact source attributes generation detection to logger
subscription. Not UART loss or exact ADC missing sample count.0ULogdropouts
doesn't certify source completeness. Camera/clocks/accel endpoint/tail/OpenVINS
model unqualified, VIO-S0/P PARTIAL, StageC CLOSED. No syntheticPASS/retiming.

13 NEW board tests/zero skips;17Windows tests14PASS/3POSIX skips;4CPU/NaN tests
offline only. Independentverifier exit0,12remote/local hashes agree; prior
33+58+37+44+14+18 evidence and StageA/B preserved. FirstNaN JSON analysis failed,
partial retained; analysis-02 explicitly marks unknown health field, no raw edit.
Sampler270observations from pre-gate:21.476% one core mean/~41.1MiB peakRSS;
UARTsameFD counters supported,no new frame/parity/overrun errors (historicalframe2).

Exact originalUART115200/streammap/loggeridle187/8SDLOG/customfileabsence and
M3Ctermios/noowner restored, flow/ToF retained;337USB heartbeatsbase29/finalEV0.
Only owned166-byte config/two emptydirs removed, recoverable locally. No further
capture. Next OFFLINE source/logger queue/scheduling isolation from complete log;
no sync/calibration/StageC yet. This is LOCAL synthesis for later explicit Vault
import, not a claim Vault or GitHub was updated.

## Offline sender-buffer loss attribution — 2026-10-11

Evidence: `.maixpy/imu-gap-diagnosis-20261011/DIAGNOSIS.md`, pinned source gitlinks,
diagnosis.json/verification.json,15 new and9 existing offline tests PASS/zero skips/
exit0. ONE previous failed trial only; no device/SSH/UART/settings/firmware/capture/
runtime change.18 deployed sources unchanged; old58+25 snapshot/18+37+44+14 artifacts
and StageA/B preserved. Raw previously UNKNOWN diagnostics were not discarded:
all33 now pinned-CRC verified, including10 LINK_NODE_STATUS; all3697 frames checked.

Terminal435 interval: PX4 send-buffer rejection4→5, missing global35 (34→36),
successful-write delta398 equals398 received frames. All nine intervals account
six sender rejections for six missing global positions. Confirmed sender rejection
layer, not exact scheduling/burst/drain trigger or physical fix. Complete packet437
postflight perf metadata reports ulog_stream messages missed0; later truncated
record excluded, no data repaired/admitted. logger_status generation-gap events
rise1→2→3; independent source integral-coverage/rate issues remain.

Reusable distinction: XML message8 ms/overflow-byte labels differ from matched PX4
HRT-us/send-rejection EVENTS; tx_buf/rx_buf TODO-zero are not measured free space.
Source perf_reset_all is file-start-only, not MAVLink-only start. Mean bandwidth
headroom cannot prove instantaneous UART ring space; three full267-byte frames
versus source-modeled799 free bytes is SYNTHETIC, not measured occupancy.

Next ONE proposed reduced-telemetry60s comparison on existing M3C↔PX4 UART plus
USB, same source/rates and exact backup/restore, NOT executed/authorized here.
VIO-S0/P PARTIAL, transport FAILED, physical fix/source/tail/clocks/model unqualified,
StageC CLOSED. No commit/push or Vault access; this remains an import proposal.
Previous report is an unchanged historical snapshot, superseded only in attribution.

## Negotiated physical IMU trial / confirmed gap — 2026-10-11

Evidence: `.maixpy/imu-uart-negotiated-trial-20261011/RESULT.md`, raw wire/prefix,
coordinator readbacks, failure-analysis.json and independent verification.json.
ONE approved trial; current source18-file parity / isolated M3C120 tests PASS,
zero skips (7 virtual PTY). Physical same-owner guardedv1→v2 bootstrap and logging
START/STOP verified. Accepted sequence0..434, next436: missing435 stops receiver,
exit1;60s NOT_COMPLETED, no transport PASS or automatic retry.

513 retained BMI0880 integral records /2.606488s /196.432901Hz, ordering/IDs stable,
calibration1/1 and clipping0/0; source coverage gaps, original>=200Hz gate unchanged.
Diagnostic complete-record view only in memory; raw107784-byte prefix unchanged,
no repaired/shortened qualified dataset. Global MAVLinkseq35 absent in same logging
gap interval, but sender/queue/UART/driver/scheduling attribution UNKNOWN. MAVLink-
only logger avoids this experiment's SD record path; not historical SD-loss fix.
Receiver CPU/tail/source completeness/camera clock/model remain unqualified.

Exact PX4 UART115200/nominal streams/idle logger/eightSDLOG/file absence and M3C
pretrial termios restored; no remaining M3C owner, flow/ToF preserved. Fresh
Disarmed/EV0;228 observed heartbeat base29, no flight/parameter/firmware/wiring/
fusion/camera actions.6 transfer hashes/18 deployed source hashes/old18+37+44+14
artifacts/StageA/B verified unchanged. Fresh9 offline tests pass, verifier exit0;
old root226/54 results historical, not rerun this turn.

Next OFFLINE: attribution/counter/telemetry-burst plan; no blind retry. VIO-S0/P
PARTIAL, StageC CLOSED, thresholds unchanged. No commit/push or Vault access;
this is a reviewable import proposal, not an ingested experiment record.

## Offline guarded MAVLink2 negotiation — 2026-10-11

Evidence: `.maixpy/imu-negotiation-fix-20261011/VALIDATION.md`, source working-tree
state, verification-03.json and final raw tests. Existing single-owner Controller
now has explicit finite heartbeat-only bootstrap from PX4v1, then verifiedv2 gate
before logging START. Default strict-v2 and logging/ACK/post-upgrade safety kept;
no protocol/parameter change, no duplicate owner. Policy/phase audit prevents
silent metadata downgrade or pre-confirmation logging TX. Receipt timing is not
clock mapping/authentication. Five-second total deadline/2.5s fresh/same-read veto/
no retry/no flush/actual-write recheck/restoration maintained.

120 research-Linux tests PASS/zero skips (7 PTY),113 Windows PASS/7 platform skips;
54 related tests and226 main passes/1 existing skip, explicit final exits0.37 prior
preparation/18 original trial/14 frozen entries/StageA/B unchanged; preserved real
BMI270 bytes still contain391/306 dropouts through synthetic framing. No current
BMI088 throughput/source/VIO inference. TDD/self-review failures retained.

No M3C/PX4 access/deployment/capture/settings/install/commit/push/Vault modification.
Next current120-test isolated M3C software precheck, then new reviewed coordinator
and ONE separately approved bounded60s existing-UART+PX4-USB capture/restoration.
Old87-test board PASS is previous source. VIO-S0/P PARTIAL; source/strict200Hz/
tail/clock/model remain unqualified; StageC closed. Import proposal only.

## Physical preparation abort / protocol ordering — 2026-10-11

Evidence: `.maixpy/imu-uart-retry-20261011/RESULT.md`, raw coordinator/board logs,
verification.json and protocol-diagnosis.json. Approved retry reached temporary
PX4921600/46080B/s/minimal MAVLink logger, then aborted on premature outgoing-v2
check before M3C launch. No capture/TX/START, no hardware fault or transport PASS.
Matching source and synthetic replay expose circular bootstrap: incomingv2 causes
PX4 upgrade, but coordinator/strict receiver require v2 before heartbeat reply.
-Z is only flow-off. Preserve existing StageA/B, no parameter change needed solely
for its already demonstrated negotiation. Finite guarded heartbeat-only bootstrap
is the next OFFLINE design/test, not implemented or physically verified yet.

Fresh firmware/source selection/Disarmed/EV0; one-second vehicle_imu197Hz not>=200
PASS. Exact PX4 logger/UART/stream/eightSDLOG/file absence restored. M3C readonly
attributes unchanged/no receiver. Five scope tests pass; independent verifier
exit0/18 old trial/14 frozen/16 deployed hashes/StageA/B unchanged. Helper failures
retained. VIO-S0/P PARTIAL; source/tail/clock/model unqualified; StageC closed.
No further automatic retry, push or Vault modification. Import remains proposed.

## Revised controller M3C PTY verification — 2026-10-11

Unchanged final startup-fix source deployed to isolated M3C directory
`/root/rm27-controller-startup-pty-20261011.Jg12Lv/`;87 tests PASS/zero skips,
all4 PTY cases, Python/SSH exit0. All16 source hashes match local; actual
Python3.13.2/aarch64/NumPy2.2.6/pymavlink2.4.49/pyulog1.2.4 recorded.
Evidence: `.maixpy/controller-m3c-startup-pty-20261011/VALIDATION.md` plus matching
raw environment/test/cleanup logs and manifest. No source/dependency/system change,
physical UART/PX4 access, new capture, fusion, commit/push or Vault modification.
Replaces the old55-test board software prerequisite, not physical qualification.
VIO-S0/P PARTIAL; source/200Hz/clock/model gates unchanged. Next independently
approved one60s transport trial with actual backups/restoration, not another PTY
run. Original18 trial/14 frozen entries and StageA/B unchanged. Board wall clock
is not synchronization evidence. Mutable earlier reports snapshotted before update.

## Approved offline startup fix — 2026-10-11

Added bounded pre-START CRC synchronization with complete raw startup evidence;
post-boundary strict guards unchanged.87 Linux pass (4 virtual PTY),83 Windows
pass/4 platform skips;54 existing regressions and226 root passes/1 skip.
Original failed trial18 hashes, frozen reassembler14 hashes, StageA/B and saved
BMI270391/306 dropout evidence unchanged. See
`.maixpy/imu-startup-fix-20261011/VALIDATION.md` and root HANDOFF.
Review corrected incomplete-outer payload scanning and startup metadata audit
gaps. Plausible candidates are opaque barriers, possibly causing bounded timeout.
Saved21 + one heartbeat still cannot start; synthetic completion/continuous-peer
tests are not evidence that the real startup symptom is fixed.
No M3C/PX4 access/new hardware PASS. Changed source still needs M3C PTY run and
separately approved physical capture; source/rate/clock/model gates not relaxed.
This is a proposed durable record, not a Vault modification.

## Offline startup-boundary diagnosis — 2026-10-11

Saved21 bytes reproduce controller's pre-START abort; a legal partial-frame tail
followed by a complete valid heartbeat also aborts.20 clean split reads work,
20 late attachments fail. Original18 trial hashes unchanged; fresh Windows
controller tests53 pass/2 POSIX skips. See
`.maixpy/imu-startup-diagnosis-20261011/DIAGNOSIS.md` / `reproduce.py`.
Physical byte origin and high-rate suitability remain UNKNOWN/NOT_QUALIFIED.
No code fix or device retry. Proposed bounded startup synchronization must be
reviewed without weakening post-START checks. Vault not accessed or ingested.

## Physical transport startup failure — 2026-10-11

Approved single60s921600/46080B/s trial aborted on first21 bytes Bad prefix,
before receiver TX/LOGGING_START; zero IMU records, no retry. Full evidence and
verified restoration in `.maixpy/imu-uart-trial-20261011/RESULT.md`.
Do not infer wiring fault or baud infeasibility; startup queued bytes/partial
frame remain candidates. Next offline framing diagnosis; new hardware run
requires approval. VIO-P/S0 PARTIAL; source snapshot193Hz and integrated-data
contract remain limiting. Proposal only, Vault not modified.

## Board-side controller test — 2026-10-11

M3C maixcam2-9d05/aarch64/Python3.13.2 passed55 controller tests, no skips,
including real virtual-PTY normal/armed paths and termios restoration. Isolated
deployment/source hashes/logs retained under controller-m3c-pty-20261011;
pyulog1.2.4 copied into research-lib, existing NumPy/pymavlink reused, no install.
No physical UART/FC/configuration/sample capture. This completes the board-side
software prerequisite only. Next separately scoped high-rate runtime/logger trial;
VIO-P/S0 PARTIAL/StageC closed. Vault remains untouched.

## Live read-only baseline — 2026-10-11

Current COM19 readback confirms d6f12ad1/PX4v1.17.0, selected BMI088 instance0
(gyro6684690/accel6946834), Disarmed/EV_CTRL0, idle logger64KiB/all/custom-file
absent. One-second vehicle_imu0 publication190Hz, not strict200Hz PASS. Existing
register/overflow/reset events static on reread; source completeness not verified.
Wired PX4 UART115200; flow/ToF remains active. Current RX0/version1 does not erase
historical StageA/B MAVLink2 results. See `.maixpy/live-baseline-20261011/BASELINE.md`.
No settings change/capture/M3C operation; VIO-P/S0 PARTIAL. Vault not accessed.

## Single-UART controller evidence proposal — 2026-10-11

Current repository working tree now includes controller/runner/audit and55 passing
Linux tests including virtual PTY,53 Windows passes/2 POSIX skips,54 existing
regressions and226 root passes/1 skip. See controller/VALIDATION.md and root HANDOFF.
Two saved BMI270 ULogs remain byte-exact with391/306 dropout evidence. Only the
existing Linux research host was used for isolated software tests, not M3C/PX4.
No device settings, dependencies, commits/push or Vault ingestion. The durable
decision is to preserve tail/source UNKNOWN after STOP and keep integrated
observations/clock/model gates separate from framing. Next physical trial needs
specific reversible921600/logger scope and independent USB restoration evidence.

## Roadmap continuity proposal — 2026-10-11

`rm27/perception/vision/docs/PLAN_HISTORY.md` links the preserved 2026-09-20 SLAM
roadmap and 2026-10-07 VINS/VIO plan, explains candidate roles and planned vs
observed gates. Original plans/criteria unchanged; no new validation/deployment.
This repository note is not Vault ingestion.

## SSH workspace inventory supplement — 2026-10-11

`rm27/perception/vision/docs/WORKSPACE_LOCATIONS.md` consolidates saved Linux
research/worktree/evidence locations, M3C deployments and Windows editing mirrors.
It distinguishes historical path evidence from UNKNOWN current remote state and
GitHub's curated publication from full disk backup or deployment. No SSH, hardware
or Vault access in this documentation supplement; no credentials are published.

## Publication proposal — 2026-10-11 (not ingested)

The current portable summary is `rm27/perception/vision/docs/PX4_M3C_CONNECTION.md`
and `CODEX_RESUME.md`. Preserve UART2↔UART3 crossed wiring, verified115200/MAVLink2,
exact d6f12ad1 firmware, separate USB management, Stage A/B scope and later VIO gates.
User reports no spare UART; prior spare-pad next actions are superseded. Stock
single-UART MAVLink ULog remains a candidate with an offline reassembler only.
No new hardware observation or Vault access. Root handoff and selected research
are being published at the user's explicit request. Windows proposal history is
`.maixpy/VAULT_UPDATE_WINDOWS_20261011.md`; older Linux proposal below is retained.

## Latest authorized offline experiment, 2026-10-08

One props-off/user-confirmed, disarmed PX4 BMI270 FIFO ULog capture completed;
instance1/device3604506 verified in raw data.18.122s file,17.9s IMU span; two
independent downloads SHA256-identical. Raw export/parse proven, completeness
FAILED:391 logger dropouts and111.409ms max sample gap. Sensor local cadence
~1580Hz; recorded gyro/accel effective706.681/666.823Hz, not lossless capture.
See `PX4_IMU_OFFLINE_VALIDATION.md` for immutable-file hash and bounded conclusions.
Original logger config restored and verified; no flight/control/firmware or
camera/M3C change. VIO-S0 and VIO-P remain PARTIAL. Proposed durable finding:
raw IMU source exists, but this logger/SD configuration does not yet provide a
complete offline VIO input. This repository proposal is NOT a Vault update.

## Latest export/timing decision, 2026-10-08

Read-only logger query: idle, SDLOG_PROFILE1/SDLOG_MODE0/SDLOG_BOOT_BAT0;
microSD readable. Source at reported4817c061 shows default sensor topic interval
1000ms and raw FIFO profile default instance0, not selected BMI270 instance1.
Propose explicit instance/device-bound ULog on SD then host export as first
raw-data qualification, not an already-working synchronized dataset path.
MAVLink ULog streaming/USB is a later candidate; performance and M3C host mode
unverified. HIGHRES/SCALED_IMU remain processed interval-average paths.
FC sample timestamps are driver-related boot HRT, not proven ADC latch; camera
exposure timing and cross-device mapping remain open. No raw capture, firmware,
parameters, stream settings, schema, algorithm or wiring changed. VIO-P/S0 PARTIAL.
User says hardware is separate on the desk: prior photograph request superseded,
no physical action now; rigid mounting is needed later for synchronized capture.
This is a repository proposal only. The Vault was not read or modified.

## Latest live FC evidence, 2026-10-08 (supersedes unavailability below)

COM19 Windows read-only queries succeeded. MICOAIR_H743_V2; micoair-v1.15.2;
reported hash4817c0618a1286846116e90c6eb8919efaa013cf. Official manual confirms
the AIO uses micoair_h743-v2, BMI088 SPI2 and BMI270 SPI3; both drivers active.
Selected BMI270 device3604506. Internal one-second topic rates documented in
audit, not transport rate/ODR qualification. FC and M3C not connected; DDS stopped;
raw export/clock mapping/exposure timing unresolved. No captures or settings
changes. VIO-P and S0 stay PARTIAL. Next physical verification is a photograph
of current camera/FC mounting relationship, not wiring or calibration.
No Vault write; proposed durable facts must retain source/runtime distinction.

## CURRENT correction: PX4 real flight controller (2026-10-08)

User explicitly states PX4, superseding prior ArduPilot assumptions for VIO.
Prioritize PX4 sensor_gyro/accel (or qualified FIFO) + OS04A10; do not assume local
ICM hardware. Local clean PX4 dd0ad74 is source evidence only, not deployed
version. HIGHRES_IMU here is sample-timestamped but interval-derived and possibly
estimator-bias corrected; previous ArduPilot send-time interpretation must not be
reused. No actual FC USB/bridge identity or measured rates yet. VIO-S0 and VIO-P
stay PARTIAL. See current audit/contract/handoff; older recommendations below
are historical. No Vault write or broader hardware-ledger edit was performed.

## 2026-10-08 real sensor-chain audit proposal

VIO-P remains PARTIAL after completed repeatability experiment. S0 also PARTIAL:
current M3C SSH unavailable. Source snapshot c7d47b2 contains a local ICM-42688-P
SPI/FIFO collector with gyro+accel, nominal 1/4 kHz, filtered sensor output and
separate sensor/batch timestamps. This supports prioritizing OS04A10 + local ICM
for physical verification, not asserting installed hardware or synchronized data.
FC BMI088/BMI270 are firmware-supported alternatives; HIGHRES_IMU uses filtered
values and send-time timestamp. See updated audit/contract for hashes, gaps and
the single next physical action. No data collection, calibration, integration,
hardware changes, commit, push or Vault ingestion occurred.

## 2026-10-08 native repeatability evidence — proposal only

Ten frozen native runs: ATE 5.432--7.653 cm (mean 6.608, sample SD 0.689 cm),
15/45 pair differences >1 cm, 2800 poses each. Three separate OpenCV-thread=1 /
publisher-thread-off controls also vary (5.551--6.604 cm); fixed RNG seed already
exists. All process exits zero and frozen manifest verification passed.
See `rm27/perception/vision/docs/NATIVE_REPEATABILITY.md` for artifacts and
limits. Native variation is confirmed independently of adapter conversion;
root cause is not proved. Current 1 cm gate is empirically unreliable as an
adapter discriminator, remains unchanged, and VIO-P stays PARTIAL. Any future
Vault synthesis should retain these distinctions, not import transient logs.
No Vault was read or modified by this task.

## Latest runtime adapter result — PARTIAL

Runtime integration and exact same-run pose/velocity/time conversion are
implemented, not merely a saved-message importer. All 2912 images/29120 IMU
samples reached the observer unchanged. 2800 visual and 27980 propagated outputs
match independent raw MCAP; all processes exit 0. Tests 226 pass/1 skip plus
7/7 ROS2. Original binary/config/input hashes remain intact.

Do not record overall PASS: adapter03 ATE 5.7385 cm differs by 1.2729 cm from
native02 (7.0114 cm), exceeding unchanged 1 cm run-consistency tolerance. Same-run
adapter/native metrics are exact, and upstream states themselves diverge before
conversion. Specific execution-variation cause is unconfirmed. See
`OPENVINS_ADAPTER.md`; no scale correction or falsified complete v2 state.
Native-only control03 independently gives ATE6.2403 cm, confirming some native
run variability without proving its full cause or waiving the historical gate.
This is a proposal only. Vault and hardware were not touched.

## Latest proposal — native SE3 evaluation

The native clean run now has independently cross-checked SE3-only metrics:
2780 matched poses; ATE RMSE 7.0114 cm; 1s RPE 4.5238 cm / 0.47799 degrees.
Applied scale is 1. Path ratio 0.980586 is reported separately, not corrected.
Original orientation-truth limitation and explicit quaternion normalization
are documented in `NATIVE_SE3_EVALUATION.md`. Adapter output projection has
started, but runtime dispatch/new replay parity remain incomplete. Broader
VIO-P is PARTIAL. Tests: 208 passed/1 skip, separate ROS2 7/7. These supersede
the older pending-SE3 statements below. No hardware or Vault modification.

## Current addendum — 2026-10-07

ROS2 is the selected host baseline path; ROS1/Noetic below is historical.
The official-source-attributed ASL archive is now available and validated.
All 2,912 cam0 images and 29,120 IMU samples passed complete ASL-to-ROS2
read-back comparison; 18 calibration comparisons match pinned upstream.
A pinned ROS2 container dependency image now builds without host changes.
The earlier four-include-only build failed at shutdown. Gdb now proves the
root cause: global visualizer publishers were destroyed after the Fast DDS
static factory. The explicit ROS2 lifecycle patch moves only entry-point
ownership into main; algorithm-library hashes are unchanged. Ten no-data exits
and a full sequence with the same 2,800 online poses now return 0.
Designation: pinned OpenVINS + explicit ROS2 lifecycle compatibility patch.
See `rm27/perception/vision/docs/ROS2_LIFECYCLE_FIX.md` for evidence and patch.
VIO-P PASS is scoped to this latest native/lifecycle task; original broader
adapter/parity/SE3 work remains incomplete and was not started. Do not infer
accuracy, flight readiness or M3C performance from this result.
Regression tests: 190 passed, 1 ROS2-specific skip, with all 7 transport tests
passing separately under Jazzy. This is not metric accuracy qualification.
The prior M3C connectivity failure was superseded by a read-only connection,
but no actual raw IMU stream has been verified. VIO-S remains PARTIAL.

The Vault was not modified. This is a reviewable proposal for a separately
authorized future project-bridge task, not a dump of chat, logs or artifacts.

## Durable decisions

- Qualify native OpenVINS mono+IMU on public data before an RM27 adapter or M3C
  port. Selected Jazzy container keeps host dependencies unchanged; ROS1 was
  historical, not an RM27 architecture decision.
- ROS resource owners must be destroyed before their process-static middleware
  factories; main-scoped ownership fixed the measured OpenVINS shutdown defect.
- Raw IMU acquisition time, telemetry send/receive time and camera timing are
  different evidence. HIGHRES_IMU naming does not prove acquisition semantics.
- Keep `T_imu_camera` as camera-to-IMU and reuse LocalizationEstimate v2.

## Verified work worth retaining

Dedicated research branch merged Linux/Windows baselines at `13c7a77`; scoped
working-tree IMU sequence/static-analysis preparation has 184 passing tests.
Tests are synthetic and do not qualify the sensor or VIO algorithm. See root
HANDOFF and three VIO reports for exact source pins and evidence references.

## Open questions

The original broader plan and VIO-S remain PARTIAL. Adapter/parity/SE3 and real
IMU evidence remain absent. The native lifecycle failure is resolved. No claim of
M3C 15–30 Hz VIO or flight readiness. No new physical calibration was performed.

Do not ingest raw build/download logs, datasets, credentials, temporary files or
unverified hardware guesses. Import only reviewed synthesis with provenance.
