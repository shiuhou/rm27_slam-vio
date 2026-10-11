# Single-UART controller offline validation — 2026-10-11

## Latest — guarded MAVLink2 negotiation revision

See `../../../imu-negotiation-fix-20261011/VALIDATION.md`: explicit opt-in finite
heartbeat-only bootstrap on the SAME UART owner, no logging START until verified
PX4v2 heartbeat. Default strict-v2 remains; no version1 logging/ACK/post-upgrade
safety acceptance.120 research-Linux tests PASS/zero skips (7 PTY),113 Windows
PASS/7 POSIX skips;54 related regressions and226 root PASS/1 existing skip.
30 new unit/state/runner/audit tests +3 PTY cases. Saved391/306-dropout BMI270
files and original18-trial/37-preparation/14-frozen/StageA/B evidence unchanged.
No M3C/PX4 access/deployment/new capture/settings/commit/push. Old87-test board
PASS does NOT qualify this changed revision. Next new-board software precheck,
then one separately approved physical capture, never rerun dated coordinators.
VIO-S0/P PARTIAL; source/tail/clock/model UNKNOWN/unqualified, StageC closed.

## Previous — startup synchronization revision

See `../../../imu-startup-fix-20261011/VALIDATION.md`: approved offline pre-START
fix,87 Linux tests pass/zero skips (4 PTY),83 Windows pass/4 POSIX skips,
54 existing regressions and226 root passes/1 skip. Startup bytes are preserved;
post-boundary validation remains strict. No M3C/PX4 access/new physical trial.
The completed first physical attempt failed before START; original evidence
unchanged. Prior55-test M3C result below covers the old source revision only.
VIO-S0/P PARTIAL, StageC closed. Physical retry needs new approval/paths/backups.

## Board-side follow-up — 2026-10-11

M3C55/55 tests now pass, including both real virtual-PTY cases, zero skips.
See `../../../controller-m3c-pty-20261011/VALIDATION.md` for deployment, dependencies,
command/log hashes and wrapper limitations. No physical UART/FC operation occurred.
This supersedes the M3C-PTY prerequisite below, not the pending high-rate trial.

## Result and scope

**VERIFIED:** bounded controller, decoder/reassembler integration, scripted wire
round-trip, Linux virtual-PTY round-trip and exact termios restoration in tests.
**PARTIAL:** VIO-S0. Physical 921600 UART, current selected BMI088 completeness,
ACK/scheduling performance, latency and observation-model suitability unqualified.
**UNKNOWN:** source/tail completeness, camera clock map. **BLOCKED:** new physical
trial pending specific communication/logger approval. Stage C remains NOT_STARTED.

Main working tree baseline `3ea1e16086965176db68b88e1c42990f92c5913e`;
unrelated `tests/camera_capture.py` / `tmp/` preserved. No M3C/PX4 access, actual
capture, baud/parameter/firmware/wiring changes, calibration, fusion or flight.
Only the existing Linux research host was accessed for isolated virtual-PTY tests.
No installation, dependency change, Vault write, commit or push.

## Actual implementation

- `session.py`: single decoder/sequence owner; MAVLink2 source1/191, target1/1;
  fresh unsigned PX4 HEARTBEAT gate; LOGGING_START once, LOGGING_ACK for verified
  reliable packets/retries, LOGGING_STOP once, companion HEARTBEAT1Hz. No parameter,
  setpoint, shell, ODOMETRY or firmware API. CRC is not signature authentication.
- 5s initial heartbeat, 15s startup, at most60s after accepted start plus first
  normal-data transition, 2.5s heartbeat/stream idle guards, 3s stop cleanup and
  250ms quiet observation. IN_PROGRESS does not equal ACCEPTED. Late packets
  before close retained. Same-read armed/error frames cancel prior intents; actual
  write rechecks freshness. No automatic acquisition retry or catch-up HB burst.
- `uart_session.py`: existing ownership helpers, console/busy/race refusal,
  exclusive nonblocking descriptor, bounded write/read, saved/applied/restored
  termios readback, finally close even on restoration error. SIGTERM/interrupt
  cleanup, no unbounded drain, no silent initial input flush or log overwrite.
- Every RX chunk/decoded row, TX intent/write/cancellation, packet receipt, ACK
  retry and error recorded. Raw received prefix retained even on failure. A
  `framing-valid.ulg` is written only after finite framing checks, never named
  complete/loss-free. Preflight JSON is preserved as an **operator attestation**,
  not authenticated controller readback. No live run was launched.
- `capture_report.py`: raw/decoded parity, SHA/reassembly equality, packet receipt
  distribution, wire throughput, source IDs, dt, source order/gaps/calibration/
  clipping and publication-minus-sample diagnostics; reuses existing audit.
  Receipt burst timing is not per-IMU jitter/latency or synchronization.
  A known truncated ULog tail may expose complete retained records for diagnostic
  statistics in memory only: excluded byte count reported, original file untouched,
  no shortened/repaired ULog emitted and failed session remains failed.
- Controller itself changes no PX4 configuration. The independent USB coordinator
  must back up/apply/restore/read back the actual UART instance, streams and logger
  topic bytes/absence/command. No claim those external mutations are automated or
  tested here. This runner is an acquisition prototype, not a real-time VIO frontend.

## Fresh verification

Research Windows Python3.12 / pymavlink2.4.49 / pyulog1.2.4 reused. Linux `ceopc`
Python3.12.3 / pymavlink2.4.49 / pyulog1.2.4 freshly checked, no installs.

```powershell
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
.maixpy/imu-offline-20261008/venv/Scripts/python.exe .maixpy/imu-design-20261010/single-uart/controller/replay_controller.py
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-design-20261010/single-uart/reassembly -p test_ulog_mavlink.py -v
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-input-20261010 -p test_imu_input.py -v
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-design-20261010 -p test_offline.py -v
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-design-20261010/followup -p test_model_review.py -v
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m pytest -q tests --ignore=tests/camera_capture.py
```

All command exits0. Windows controller **53 pass /2 POSIX skips**, Linux **55 pass**
including both real PTY cases; existing reassembly28 +decoder10 +diagnostic9
+model7 = **54 regressions pass**. Root **226 passed /1 existing skip**.
Linux PTY is software evidence, NOT a physical UART speed/error qualification.

Exact Linux command (SSH host verified `ceopc`):

```sh
python3 -m unittest discover -s /home/shiuhou/Projects/rm27-vio-20261007/controller-offline-20261011.WhOMGr/.maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
```

Isolated copy inside the existing external research root; no old Linux Git worktree
or M3C deployment overwritten. Files copied for tests only, no raw datasets copied.
Logs: `tests-final-windows-02.txt`, `tests-final-linux-02.txt`, `regression-*.txt`,
`root-pytest.txt`, `replay-controller-01.txt`. They are local evidence, not all
automatically included in Git. Archive `offline-bundle.tar` predates the final
individual file transfers; use current file hashes, not the old archive as HEAD.

Two existing real saved ULogs, **synthetic MAVLink framing/ACKs/receipt times**:

| Saved original | Exact bytes through controller | Original SHA256 prefix | Dropouts retained |
|---|---:|---|---:|
| Historical micoair-v1.15.2 BMI270 |6896444|d94a142c…|391 /9804ms|
| d6f12ad1 A2 BMI270 instance1 |5597928|3815e9e8…|306 /8325ms|

Neither is selected BMI088 evidence. No artificial receipt time is used to claim
rate, latency or throughput. Synthetic fixture200Hz is arithmetic/test evidence only.
Stage A/B report SHA remains
`d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f`.
Frozen reassembly files/manifests are unchanged; this directory has its own manifest.

## Failed attempts / limitations

TDD evidence retained: red-01 missing controller24 failures; red-02 missing runner12;
first runner pass had5 Windows-double errors for missing POSIX open constants,
fixed in doubles rather than removing production POSIX flags. Red-03 found
same-chunk armed and stale-ACK guards plus missing uptime-regression detection;
red-04 missing report5; red-05 ownership race1; red-06 actual-write freshness and
preflight capture; red-07 partial-prefix diagnostics. All reproduced then passed.
Windows WSL absent; no WSL installed. Initial SSH Python-version command had a
quoting SyntaxError, corrected; no device configuration involved.

Normal STOP is not EOF: pinned writer drops a pending partial chunk in `stop_log()`.
The [exact writer source](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/logger/log_writer_mavlink.cpp)
and [ACK/retry transport](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_ulog.cpp)
were rechecked. Silence/valid final boundary cannot exclude omitted packets,
queue1 overwrite or loss before logging. The finite parser has64MiB raw/300000
packet caps, not a64MiB total-RAM or bounded-latency guarantee. CPU/storage stalls,
SIGKILL/power loss and privileged competing owners are not solved by these tests.

An integrated delta/dt mean is still not an admitted OpenVINS point sample.
Independent accel endpoint, actual camera exposure clock mapping, calibration and
noise remain unqualified. No acceptance criterion was relaxed.

## Next / rollback

Read `RUNBOOK.md`. One next physical experiment: approved existing-link60s
BMI088 vehicle_imu ULog trial at temporary921600/46080B/s, independent PX4 USB
backup/control/restoration; both M3C and PX4 needed, no new wiring. First validate
source/transport and restore all temporary communication/logger settings. Only
later consider synchronization/calibration/real VIO; transport alone cannot open
those gates. No synthetic ODOMETRY coexistence trial in this first capture.

Rollback new controller directory and additive pointers relative to baseline;
preserve old raw evidence, original Stage A/B, unrelated changes and frozen manifests.
