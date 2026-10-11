# Revised controller M3C PTY precheck — 2026-10-11

User approved running the revised controller's board-side software precheck and
asked why PTY validation is needed. This executes existing tests, not a new
implementation or physical capture. Previous M3C55-test result covers older code.

Scope: same final source archive from imu-startup-fix-20261011; system Python plus
existing pinned research packages. New isolated M3C deployment:
`/root/rm27-controller-startup-pty-20261011.Jg12Lv/`.
Only synthetic peers and dynamically created PTY paths; tests referring to
`/dev/ttyS2` use patched POSIX calls. No physical UART open, PX4 access, baud/logger/
parameter/wiring/firmware changes, arming/fusion/camera/StageC, dependencies,
old deployment overwrite, Git commit/push or Vault access.

Baseline: main3ea1e16086965176db68b88e1c42990f92c5913e, existing dirty source/docs
and tests/camera_capture.py/tmp retained. Previous startup-fix29-entry manifest
verified before this task. Repository copies of mutable reports are preserved
before adding the new result; previous manifests remain historical snapshots.

Commands / completion conditions:

1. Verify live M3C hostname/architecture/Python and ancestor instructions.
2. Copy unchanged controller-source-03.tar.gz and existing pyulog1.2.4 archive to
   fresh directory; verify both SHA256 values before extraction.
3. Record actual imported versions and paths, then run all87 controller tests:
   `PYTHONPATH="$PWD/research-lib:/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages" python3 -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v`.
4. Require87 tests, zero skips/failures and Python exit0; verify all4 PTY cases,
   queued-prefix handling, armed no-TX, byte equality and exact PTY termios restore.
5. Verify deployed source hashes/local equality, download matching raw test and
   environment logs; record board test process cleanup. Update reports/handoff.

PTY tests exercise the real M3C Python/parser/termios/select/exclusive-owner paths
with a controlled synthetic endpoint. They catch software/environment regressions
without involving PX4. They do NOT prove physical921600 driver/line support,
throughput, FC source rate/completeness, clocks, latency or OpenVINS suitability.
No automatic physical retry follows this precheck.
