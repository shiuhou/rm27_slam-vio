# Revised controller M3C PTY qualification — 2026-10-11

## Verdict

**VERIFIED:87 tests PASS, zero skips/failures, Python/SSH exit0.** All4 real POSIX
PTY integration cases passed on M3C, including pre-existing input with a peer
already transmitting, synthetic roundtrip, armed no-TX and exact PTY termios
restoration. This completes the changed revision's board-side software precheck.
**PARTIAL:VIO-S0/VIO-P. UNKNOWN/NOT_QUALIFIED:** physical921600 link, selected
BMI088 source rate/completeness, clocks, source tail and OpenVINS suitability.
StageA/B remains unchanged; StageC remains NOT_STARTED.

User approved this precheck ("跑吧") and asked why PTY is needed. PTY supplies a
controlled endpoint to test the real M3C Python/parser/select/termios/exclusive
owner paths, so software and target-environment failures can be isolated without
changing PX4. Previous55-test M3C result predates the startup fix; the separate
Linux research-host PASS does not establish Python3.13/aarch64 board compatibility.
PTY success does NOT measure physical UART baud support, throughput, jitter,
sensor delivery, synchronization or VIO performance. It is not simulated IMU PASS.

## Scope and repository state

Main3ea1e16086965176db68b88e1c42990f92c5913e. Existing dirty controller/docs and
unrelated tests/camera_capture.py/tmp retained. No source changes, dependencies,
commit/push, Vault access, physical UART open, PX4 query/configuration, logger,
firmware/parameter/baud/wiring changes, arming/fusion, camera or physical capture.
Tests mentioning /dev/ttyS2 use patched syscalls; actual ports exclusively come
from pty.openpty(). Physical FC disarmed/EV_CTRL state was NOT newly queried here;
the prior bench readback is historical and must be refreshed before a real trial.

Ancestor AGENTS files were checked: none observed locally on the applicable
ancestor chain or at /AGENTS.md,/root/AGENTS.md on the board. Supplied user working
agreements applied. Existing engineering verification/handoff process retained;
no external research or new implementation was needed.

## Board and deployed revision

Live hostname maixcam2-9d05, aarch64; Python3.13.2, NumPy2.2.6,
pymavlink2.4.49, pyulog1.2.4. Imported NumPy from the existing system location;
pymavlink from /root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages;
pyulog from the new isolated research-lib copy of the already pinned archive.
No pip/install or old deployment/environment overwrite. python3 -B suppresses
bytecode writes. Exact versions/import paths are in environment.json.

Fresh deployment: `/root/rm27-controller-startup-pty-20261011.Jg12Lv/`.
Relative .maixpy import layout preserved. All16 deployed Python file hashes
matched current local files; unchanged final startup-fix archive reused:

- controller-source-03.tar.gz SHA256
  `cbeb9283d44e46701656bd8c0652cc617d249ebb9bfcdb92d55071f8d531bb57`.
- Existing pyulog-1.2.4.tar.gz SHA256
  `10f7915ac46416e9392267334e156f24566ee2df56fcd812c405c427803d3573`.

Both archive hashes matched on M3C before extraction. Prior deployments,
HEARTBEAT/ODOMETRY scripts and all physical interfaces were left untouched.

## Fresh verification commands and evidence

From that deployment root, exact test command:

```sh
PYTHONPATH=$PWD/research-lib:/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages python3 -B -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
```

Observed final result: `Ran 87 tests in 9.472s` / `OK`. Python exit0 was propagated
through the SSH wrapper. Downloaded raw tests.txt was read in full and independently
checked for87 individual pass lines and no skips/failures. All4 PTY case names:

- test_real_pty_roundtrip_and_termios_restore
- test_real_pty_armed_refusal_and_restore
- test_preexisting_input_roundtrip_and_restore
- test_preexisting_input_armed_refusal_and_restore

Tests also preserve CRC/order/gap failures, startup5s/65536-byte bounds, all266
splits of a267-byte outer frame with an embedded heartbeat, metadata tampering
and legacy-policy downgrade rejection. Saved21 + one heartbeat still waits and
times out: unknown263-byte outer candidate is a barrier, not permission to scan
payload. Synthetic completion/continuous heartbeats are not real-stream recovery
proof. Exact byte comparisons and fixture-only sample diagnostics do not admit VIO.

Downloaded board evidence SHA256s matched board copies:

- tests.txt:`7025db48adc361230557683b496571928fa139eda9c3dccacf2f08b767be4f53`.
- environment.json:`cb80eb6cecfe5328e335c16ce01713f06430ff8fdf7288fb46c256978d33b0c8`.
- cleanup.json records zero remaining unittest processes in this deployment and
  matching archive/environment/test hashes. Test workers closed/joined per assertions.

Existing `python .maixpy/imu-startup-fix-20261011/verify.py` rerun exit0:
18 original physical-trial entries,14 frozen reassembly entries and StageA/B
SHA256 unchanged; original failed capture retains Bad prefix/zeroTX and is NOT
reclassified. No root suite rerun needed: application/test source unchanged;
prior226-pass/1-skip root regression remains a separate prior result.

Before report updates, all29 entries in the preceding startup-fix manifest
matched. Mutable root reports are now intentionally updated; repo-before preserves
their earlier bytes. That old manifest remains a historical snapshot, not a
manifest of today's updated handoff. New scope hashes are in this manifest.json.

## Failed attempts / operational limitations

No test failure or retry. Extraction warned that host file mtimes were in the
future relative to the board's wall clock (also observed in the prior deployment).
No clock setting was changed; this is not clock synchronization evidence.
No live source/baud/latency/CPU measurements were made. PTYs can accept termios
B921600 without proving the hardware ttyS2 driver or electrical link supports it.

## Next action and rollback

No repeat PTY precheck needed without source/environment changes. Next physical
step, after scoped communication/logger approval: one bounded60s selected-BMI088
ULog-over-MAVLink trial over the existing M3C↔PX4 UART, plus PX4 USB inspection,
temporary921600/46080B/s/minimal vehicle_imu logger, fresh baseline/backup and exact
restoration. Use NEW outputs/coordinator, never rerun the old one-off trial or
auto-retry. Verify actual firmware hash/Disarmed/EV_CTRL=0, source identity,
startup, received source rate, gaps/order/calibration/clips, wire/ACK rates and CPU.
Preserve strict200Hz gate; source193Hz historical snapshot remains below it.
Transport success would not establish instantaneous samples, clock mapping or VIO.

Rollback: deployment is an isolated directory, not an installed service; no
physical configuration restoration is required because none was changed. Leave
the evidence copy intact, or use a fresh directory for later revisions. Restore
only this task's report additions from repo-before if needed; preserve all other
user work. HANDOFF/VAULT_UPDATE updated locally; Vault was not accessed or ingested.
