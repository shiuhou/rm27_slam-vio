# Bounded startup synchronization — 2026-10-11

## Verdict

**VERIFIED (software):** bounded best-effort/fail-closed pre-START synchronization
preserves saved startup bytes and handles tested late attachment/invalid headers,
without changing post-boundary fail-closed parsing or physical settings.
**PARTIAL:** VIO-S0/VIO-P.
**UNKNOWN / NOT_QUALIFIED:** actual921600 link, current BMI088 source completeness,
clock map, tail completeness and OpenVINS measurement compatibility.
StageA/B evidence remains unchanged; StageC remains NOT_STARTED.

User's "ok do it" authorizes the preceding offline fix/test design, not another
physical trial. Main baseline3ea1e16086965176db68b88e1c42990f92c5913e; existing dirty
controller/docs and unrelated camera_capture.py/tmp retained. No commit/push,
parameter/firmware/baud/wiring changes, device capture, calibration or fusion.
Only Linux research computer ceopc was accessed for isolated virtual-device tests;
no M3C/PX4 access or deployment. Existing dependencies reused, no installation.

## Actual minimal changes

- `controller/startup_sync.py`: startup-only scanner calls the existing pymavlink
  CRC decoder on complete candidate frames; valid outer frames are consumed whole.
  Only disproved flags/known impossible lengths can be skipped. Partial headers
  and plausible bodies are barriers; complete candidates are consumed whole even
  when unknown or CRC-rejected, never scanned for embedded heartbeat bytes.
  Plausible garbage may therefore delay or time out. Buffer retains at
  most279 bytes between reads; total pre-boundary input cap65536 bytes, including
  the entire boundary-containing read conservatively. Current runner reads8192
  bytes maximum.5s initial deadline is unchanged and now also enforced on feed;
  it is an acquisition deadline checked on feed/tick, not a CPU-latency bound.
- `controller/session.py`: use scanner until the first CRC-valid PX41/1 heartbeat
  candidate. Existing unsigned/MAVLink2/PX4 identity/armed checks decide whether
  START may be formed; all same-read later faults still veto TX. Once the candidate
  boundary is found, reuse the unchanged strict stream decoder, never resynchronize
  logging data. A wrong/signed/v1/armed heartbeat does not authorize START.
- `controller/capture_report.py`: versioned raw-to-event replay for startup
  classifications and exact-type summary counter parity; missing policy cannot
  downgrade new capture metadata/events to legacy. Genuine legacy sessions still
  use their original Decoder. Startup
  bytes/offsets retained in wire evidence, not treated as sample loss or appended
  to ULog. `startup_boundary_found` denotes framing only, not authenticated safety,
  transmission or accepted START. Receipt freshness is not proof of FC send age.
- `test_startup_sync.py` and `test_startup_pty.py`: saved21-byte regression,
 20 late attachments,20 clean splits,20 completed-synthetic-prefix-plus-split cases,
  all266 split positions of an untruncated267-byte outer packet with an embedded
  heartbeat, unknown/CRC-rejected opaque candidates, false/signed
  lengths, identities, CRC, armed/same-read veto, deadlines/caps and audit tampering;
  two PTY cases preload bytes and transmit before the receiver opens, checking
  complete synthetic roundtrip or armed refusal and exact termios restoration.
- No edit to uart_session.py, old Decoder/Reassembler or integral input semantics.
  Prior controller snapshot retained at baseline/session.py, SHA256
  `9f30f12bf596a2f452a19d00b1a7e6cbaf50aad7c6a28ba7cb974934c8f2a9fb`.

## Fresh tests and evidence

Commands below use the existing Windows research Python
`.maixpy/imu-offline-20261008/venv/Scripts/python.exe` (3.12; pymavlink2.4.49,
pyulog1.2.4). Linux ceopc uses Python3.12.3 and the same package versions.

| Check | Observed result | Preserved evidence |
|---|---|---|
| TDD before application edits |22 tests,38 expected assertion failures including20 subcases; no errors |tdd-red.txt |
| Review regressions before correction |split outer, summary tampering, unknown/payload cases fail; missing-policy case also RED |review-red.txt / review-red-02.txt / review-red-03.txt |
| Final Windows controller suite |87 run,83 pass,4 POSIX skips |windows-tests-03.txt |
| Final Linux controller suite |87 pass,zero skips; all4 PTY tests pass |linux-tests-03.txt |
| Existing reassembly/decoder/integral/model suites |28+10+9+7 =54 pass; four Python exits0 |related-tests-04.txt |
| Main regressions |226 pass,1 existing skip |root-tests-02.txt |
| Saved BMI270 files in synthetic MAVLink framing |byte-identical6896444/5597928 bytes;391/306 dropouts retained |saved-replay-03.json |
| Historical integrity and compatibility |18 original trial hashes +14 frozen reassembly hashes +StageA/B SHA unchanged; legacy Bad prefix still reproduced |verify.py / verification-03.json |

```powershell
python -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
python -m unittest discover -s .maixpy/imu-design-20261010/single-uart/reassembly -p test_ulog_mavlink.py
python -m unittest discover -s .maixpy/imu-input-20261010 -p test_imu_input.py
python -m unittest discover -s .maixpy/imu-design-20261010 -p test_offline.py
python -m unittest discover -s .maixpy/imu-design-20261010/followup -p test_model_review.py
python -m pytest -q tests --ignore=tests/camera_capture.py
python .maixpy/imu-design-20261010/single-uart/controller/replay_controller.py
python .maixpy/imu-startup-fix-20261011/verify.py
```

Isolated Linux test copy (not the old worktree or M3C deployment):
`/home/shiuhou/Projects/rm27-vio-20261007/startup-sync-review-20261011.UhjZC5/`.
Exact command:

```sh
python3 -m unittest discover -s /home/shiuhou/Projects/rm27-vio-20261007/startup-sync-review-20261011.UhjZC5/.maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
```

Source archive and downloaded test log hashes are checked against the Linux copy;
final source archive controller-source-03.tar.gz SHA256
`cbeb9283d44e46701656bd8c0652cc617d249ebb9bfcdb92d55071f8d531bb57`;
linux-tests-03.txt SHA256
`89990bd829afc857919973b1c8f661ed29bb9fac38755c1d93ca97fe0b708553`.
Current source/evidence hashes are recorded in manifest.json / verification-03.json.
Earlier80-test logs, archives and RED iterations are retained, not final evidence.
No physical port opened by these tests; fixture PTY paths come exclusively from pty.openpty().
Synthetic receipt times and ACKs do not measure actual latency/rate/CPU or current
sensor delivery. Saved BMI270 replays do not represent selected BMI088.

**The saved21 bytes ALONE still cannot PASS:** revised code sends no START/TX,
waits for a verified heartbeat and then times out without additional data. The
original failed hardware result is not reclassified. Only synthetic appended
heartbeats and additional observed bytes demonstrate software behavior. The saved
FE header is UNKNOWN msgid255/payload255; its opaque candidate is263 bytes.
Saved21 + one heartbeat is also insufficient and times out. Successful memory
fixtures use explicitly synthetic completion filler followed by a new heartbeat;
PTY peers send continuous synthetic heartbeats and preserve the raw queued prefix,
allowing additional pre-boundary exclusion. Neither establishes real-stream recovery.

Independent read-only review found and reproduced the incomplete-outer payload
scan and metadata audit gaps; RED tests preceded corrections. Revised code passed
review reproduction and metadata tampering checks; final nonzero payload prevents
MAVLink2 zero-tail truncation and genuinely covers266 splits. No unresolved
Critical/Important code findings. This is not proof that the physical symptom is fixed.

Retained operational issues: first apply_patch was rejected for duplicate target
operations, then combined before any code change. Windows native stderr redirect
adds PowerShell decoration to test logs despite Python exit0; explicit result
counts/exit codes and raw Linux log were read. First combined related-test wrapper
returned shell exit1 despite four passing suites due to native stderr error
records; retained related-tests-03.txt. Rerun explicitly checks all four Python
exits [0,0,0,0] and exits0 (related-tests-04.txt), not inferred from the wrapper.
Linux pip-show noted unrelated
pre-existing pybind11 metadata warning, no packages altered.

## Remaining work / one next physical experiment

Before physical retry, copy this exact revision to a NEW isolated M3C directory
and run the87-test PTY suite; the prior M3C55-test PASS covers the old revision,
not this fix. That is software qualification, not an IMU capture.

After separate approval, **one new bounded60s capture using the existing M3C–PX4
UART connection plus PX4 USB inspection**, with actual fresh backups and the same
temporary921600/46080B/s/minimal logger configuration. Verify successful startup,
then measured selected-BMI088 records, intervals, ordering, gaps/calibration/clips,
wire/ACK rates, CPU and restored settings. Do not repeat StageA/B, change firmware,
rate/sensor/EV parameters or wiring. Use NEW paths, not the one-off failed
coordinator, and never auto-retry. Exact restoration is mandatory.

Source193Hz one-second snapshot remains below the unchanged strict200Hz criterion;
transport success alone cannot qualify source completeness, point-sample semantics,
clock synchronization or real VIO. No calibration or fullStageC until those gates
are supported. Rollback only this bounded startup change/new tests/docs using the
pre-change snapshot; preserve all unrelated user and historical evidence.
HANDOFF/VAULT_UPDATE updated locally; Vault not accessed or ingested.
