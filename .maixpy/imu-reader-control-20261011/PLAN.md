# ONE fixed-reader control — execution record, 2026-10-11

User `ok execute` approves execution of the scoped plan at
`docs/superpowers/plans/2026-10-11-vio-s0-logger-reader-control.md`, including ONE
60 s temporary921600/46080/minimal-logger/reduced-telemetry physical control after
offline tests and fresh safety/readback. No automatic retry. Existing same-bench
propellers-removed confirmation applies unless assembly/safety state changed.

Work in the existing dirty main checkout as specified by the approved plan;
preserve unrelated edits and original affected bytes. No staging/commit/push,
dependencies or Vault access. Existing plan/experiments are frozen snapshots;
this folder records execution and any justified implementation adjustment.

- COMPLETED: offline strict fixed-reader profile/command guards and comparison.
- VERIFIED: fresh baseline, isolated board tests, ONE physical control, restoration.
- VERIFIED: saved-wire/source analysis, independent verification, handoff.
- FAILED hypothesis: fixed reader did not eliminate observed subscription skips.
- PARTIAL input qualification:197.104634Hz/two holes; original gates unchanged.

Source,topics,transport treatment,receiver protocol and measurement cadence stay
fixed; ONLY logger reader changes -p vehicle_imu -> -r2500. Frequency>=200Hz,
gyro coverage+/-2us,accel/tail/clock/model unknowns and OpenVINS admission gates
unchanged. Do not interpret finite improvement as universal loss freedom.

Fresh existing runner baseline15tests PASS/zero skips/PythonExit0 before edits
in baseline-runner-tests.txt. Two exploratory reads guessed incorrect probe
paths; session.py resolves the actual existing m3c-ping-20261009/probe.py.
