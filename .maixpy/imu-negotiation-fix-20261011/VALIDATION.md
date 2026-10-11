# Guarded MAVLink2 bootstrap — offline validation, 2026-10-11

## Outcome and authority

**VERIFIED (software):** existing single-owner receiver now supports an explicitly
opted-in, finite heartbeat-only negotiation phase before strict MAVLink2 logging.
**PARTIAL:** VIO-S0/P unchanged. **UNKNOWN / NOT_QUALIFIED:** actual921600 transport,
selected BMI088 source/tail coverage, >=200Hz input, camera/FC clock map and
OpenVINS observation model. **BLOCKED (later gate):** new revision still requires
board-side software qualification and separately approved physical evidence.
Stage A/B bytes preserved; full StageC remains NOT_STARTED.

User's `ok` accepted the preceding OFFLINE fix/test proposal, not a physical retry.
No M3C/PX4 access or deployment, UART/firmware/parameter/wiring change, fusion,
camera, capture, dependency install, commit/push or Vault access. Research Linux
ceopc was used only for isolated software/PTY tests. Existing dirty controller/
docs and unrelated camera_capture.py/tmp retained; HEAD
3ea1e16086965176db68b88e1c42990f92c5913e. Working-tree state, not a published commit.

## Evidence-led cause and minimum change

Prior `.maixpy/imu-uart-retry-20261011/RESULT.md` / protocol-diagnosis.json and
matching d6f12ad1 source establish a bootstrap circular wait: PX4 startsv1 and
upgrades after complete incomingv2, while the previous coordinator AND Controller
requiredv2 before a companion reply. Saved matching mavlink_receiver.cpp:3231
performs that upgrade; mavlink_main.cpp:2167 shows `-Z` is flow-off, not version2.
The previous retry aborted before receiver/START/IMU. Removing only its coordinator
check is insufficient. Prior Bad prefix trial remains an independent retained failure.

Changed existing `single-uart/controller/` only:

- `session.py`: `negotiate_mavlink2=False` by default. Explicit true accepts
  bootstrap unsigned/CRC-verified PX41/1 HEARTBEAT and SYSTEM_TIMEv1, with PX4
  autopilot/protocol identity, Disarmed and receipt freshness checks. It emits only
  existing companionv2 HEARTBEAT1Hz (sys1/comp191), same encoder/sequence/owner.
  Five-second total initial/negotiation deadline is not extended by v1;2.5s
  freshness, no catch-up burst, no flush and bounded startup scanner unchanged.
  Verified PX4v2 HEARTBEAT permits one START. Any relevantv1 after upgrade, signed,
  CRC, armed, identity or boot-regression fault is terminal; wire order within
  one read matters. Whole-read faults veto output. Logging/ACK never usev1.
  Failed/cancelled bootstrap sends no STOP; existing one-STOP cleanup begins only
  after own START. Already-v2 peer goes directly through the strict logging path.
- `uart_session.py`: opt-in passed through same-owner runner and CLI
  `--negotiate-mavlink2`; real launch also requires fresh operator preflight boolean
  `heartbeat_negotiation_approved=true`. Template defaultsfalse. Actual-write
  freshness recheck and terminal partial-write/no-retry behavior preserved.
  Flags/attestations/tests are not authenticated readback or external authority.
- `capture_report.py`: explicit policy and wire-derived phase timestamp replay,
  event parity, missing-policy/opt-in/type/timestamp tamper rejection. Actual
  TX receipts before verifiedv2 permit only bootstrap heartbeat; premature START/
  ACK/control writes fail. Full intent bytes do not prove partial transmission.
  Historical captures without new metadata remain strict/legacy; no reclassification.
- `test_negotiation.py`:30 synthetic state/runner/audit cases; `test_posix_pty.py`
  adds3 real Linux PTY reactive peers (upgrade only after companionv2, armed no-TX,
  never-upgrades timeout), byte equality/audit and exact termios restoration.
  RUNBOOK/preflight updated, but dated one-off coordinators are immutable and MUST
  NOT be reused. No duplicate serial stack/protocol or production adapter changes.

CRC identifies a valid frame, not authentication. Receipt freshness does not prove
FC emission age. Boot-time monotonic checks are not camera/FC synchronization.
Policy events begin even if no valid heartbeat arrives, preventing an audit from
silently downgrading opted-in failure evidence to historical mode.

## Fresh tests

| Check | Observed result | Evidence here |
|---|---|---|
| TDD before implementation |22 expected assertion failures, no errors |tests-red.txt |
| First negotiation green |22 PASS |tests-green-01.txt |
| Self-review missing-null field regression |30 run,1 expected KeyError in audit; corrected to explicit ValueError |tests-audit-red-01.txt |
| Final Windows controller |120 run,113 PASS,7 POSIX skips, Python exit0 |tests-controller-03.txt |
| Final research Linux controller |120 PASS,zero skips,7 PTY,14.199s, Python/SSH exit0 |linux-tests-02.txt / linux-console-02.txt |
| Existing decoder/reassembly/integral/model suites |28+10+9+7=54 PASS, four exits0 |tests-reassembly/imu-input/integral/model-01.txt |
| Main regression, camera bench excluded |226 PASS,1 existing skip, exit0 |tests-root-01.txt |
| Persisted scripted negotiation roundtrip |byte-exact two-record synthetic fixture, raw decode parity; no transport/VIO admission |SYNTHETIC-roundtrip-01/ / synthetic-console-01.txt |
| Saved real BMI270 bytes through synthetic framing |6896444/5597928 bytes identical;391/306 dropouts retained |saved-replay-01.json |
| Provenance and old failed-capture compatibility |37 preparation +18 original trial +14 frozen entries, StageA/B unchanged; saved21 alone still no TX/START and timeout |verify.py / verification-03.json |

Windows reused Python3.12/pymavlink2.4.49/pyulog1.2.4; research Linux ceopc
Python3.12.3/pymavlink2.4.49/pyulog1.2.4/NumPy1.26.4, no installations.
Final isolated software copy:
`/home/shiuhou/Projects/rm27-vio-20261007/negotiation-review-final-20261011.1IPcAQ/`.
Earlier118-test copy/log and RED stages retained, not final acceptance evidence.
Both source archive and downloaded raw Linux log hashes match the remote outputs:

- controller-source-02.tar.gz:
  `2686a084b66638e01690f83aceab31c80053c4766ef62e00bf49ca8a9249337d`
- linux-tests-02.txt:
  `cb887229468c3c389bae748a3ecd0928754116ae1caa4c2c08504970dd808f46`

Final Python code hashes are in verification-03.json and manifest.json. Archive
was made before final documentation updates; runtime/test Python matches final
local source, not a claim of byte-identical later documentation.
Six changed/relevant Python files independently match remote extracted-source
SHA256 readback in remote-source-sha256-02.txt. git diff --check exits0; older
unchanged document tails retain their original mixed line endings. New dated
raw artifacts/tests are local ignored research paths unless explicitly curated
in a later publication task; no Git staging was performed this turn.

```powershell
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m pytest -q tests --ignore=tests/camera_capture.py
.maixpy/imu-offline-20261008/venv/Scripts/python.exe .maixpy/imu-negotiation-fix-20261011/verify.py
```

Linux exact executed test command in the isolated copy:
`python3 -B -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v`.
linux_test.sh records versions, actual exit and hashes; PTY paths come exclusively
from pty.openpty(), never a physical UART. Synthetic20/40ms phase order tokens and
synthetic200Hz two-record fixture are NOT measured negotiation delay/IMU rate.
Historical BMI270 replays do not establish current selected BMI088 completeness.

Retained tool issues: an rg wildcard path was rejected on Windows; first SSH inline
Python command lost quotation and failed before test execution (no device work).
The first provenance read rejected the old UTF-8-BOM manifest; read fixed to
utf-8-sig without changing any old file. Empty failed verification-01.json retained.
Windows native stderr redirection adds PowerShell decoration even for exit0;
counts and explicit exits were read, plus raw Linux log. Linux pip-show reports
pre-existing unrelated pybind11 metadata warning; no package changed. An early
unrun fixture-clock draft was corrected before running that test; no claim of a
red/green implementation finding from that draft. Self-review missing-field RED
and all earlier runs are preserved.

## Remaining gates / concrete next step

New source has NOT been copied to M3C. Its old87-test PTY PASS covers a different
revision. Next software step: isolated current120-test M3C PTY precheck using
existing packages, source-hash parity, no physical UART opened. Prepare a NEW
reviewed coordinator: pre-peer validate baud/mode/flow/budget, allow observedv1
ORv2; let opted-in same-owner receiver verify the upgrade before own START.
Do not run the frozen failed one-off coordinators or simply strip all v2 guards.

Exactly one later physical verification, after distinct authority:
**one bounded60s capture over the existing M3C↔PX4 UART, with PX4 USB for independent
inspection/restoration**, fresh actual backups and approved temporary921600/
46080B/s/minimal MAVLink logger. Verify negotiation/ACK startup, then measured
selected-BMI088 intervals/rate/IDs/gaps/calibration/clips, wire and CPU evidence,
and exact restoration. No auto-retry, firmware/rate/sensor/EV/wiring changes,
camera/calibration/fusion or StageC. Prior firmware/Disarmed/EV0 observations are
historical this turn, not refreshed live; refresh before any physical trial.

Source197Hz one-second snapshot is still not strict>=200Hz PASS. Software
roundtrip/transport success cannot qualify integral-to-point measurement semantics,
source/tail coverage or clock mapping. Keep those original acceptance gates.
Rollback only this scoped negotiation change/tests/docs using baseline snapshots;
preserve unrelated edits and all historical evidence. HANDOFF/VAULT_UPDATE are
local proposals/records; canonical Vault not accessed or ingested.
