# ONE upstream gyro observation — engineering record

Working-tree main HEAD `3ea1e16086965176db68b88e1c42990f92c5913e`.
User authorized design then one stock-firmware bench test; trial consumed, no retry.
No firmware/parameter/sensor selection/rate/wiring/EKF/ARM/flight/Stage C changes.
Canonical experiment report: `.maixpy/imu-upstream-gyro-20261011/RESULT.md`.
Scope, exact baseline, design, raw evidence, tests, failed helpers, restoration
and pending RAM-trace decision are recorded there and in its HANDOFF.md.

VERIFIED: scope, restoration, CRC/hash parity, one sender rejection interval.
FAILED: upstream-gyro observation transport at startup, logging287 absent.
UNKNOWN: original subscription-skip trigger and source cadence/coverage.
VIO-S0/P PARTIAL; Stage A/B unchanged; Stage C CLOSED.

Windows34 tests PASS/3 POSIX skips, M3C27 tests PASS/zero skips.
No claim of loss repair,200Hz, clock synchronization, calibrated input or VIO.
Six root report before-bodies retained in experiment repo-before; original
controller and historical experiment manifests are preserved. Root HANDOFF.md
and VAULT_UPDATE.md updated; no Vault access, stage/commit/push or dependencies.
