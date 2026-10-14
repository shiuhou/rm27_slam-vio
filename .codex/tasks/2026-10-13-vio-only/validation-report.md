# Validation

Baseline full Windows suite, before new scope tests:225 passed,1 skipped,
1 legacy subprocess timing failure (0.2s budget yielded TIMEOUT rather than
PROCESS_NONZERO_EXIT). No test weakened; original remains on archived branch.

TDD scope RED:7 expected failed,1 passed. Restricted dispatch/tree/mappers and
existing OpenVINS projection/runtime GREEN:33 passed. Exact logs in
.maixpy/vio-scope-20261013/tests-red.txt and tests-green.txt.

Final remaining main-suite:148 passed,1 existing ROS2 skip, exit0, with only the
unrelated hardware program tests/camera_capture.py excluded. This is not a
reclassification of the archived legacy timeout failure: the legacy suites are
no longer part of main and remain recoverable on the archival branch.
Command: py -3 -m pytest tests -q --ignore=tests/camera_capture.py.
Final log: .maixpy/vio-scope-20261013/tests-final-02.txt (148/1, exit0,7.21s).
Archive coverage and protected
VIO source integrity are checked separately in archive-manifest.json.
ROS2 hardware/runtime performance is not requalified by pure Windows tests.
All prior VIO gates remain unchanged/PARTIAL. No physical or publication action.

## Authorized publication verification — 2026-10-14

User requested commit and push of main cleanup and legacy/slam archive.
Fresh py -3 -m pytest tests -q --ignore=tests/camera_capture.py:148passed,
1existing ROS2 skip, exit0,4.11s. Archived42 paths are checked against legacy/slam
and current active-tree absence; OpenVINS runtime/math/tools unchanged.
Commit includes only scope source/docs/tests/task packet. Pre-existing ignored
RAM evidence, diagnostic task packets, .maixpy/README and IMU_SOURCE_AUDIT edits,
unrelated tests/camera_capture.py/tmp remain outside this publication.
The no-publication statements above refer to the original cleanup turn.
