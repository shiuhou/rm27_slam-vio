# Offline MAVLink2 negotiation fix — 2026-10-11

User's `ok` approves the proposed OFFLINE fix/tests, not another physical trial.
Root cause is captured in ../imu-uart-retry-20261011/RESULT.md and synthetic
protocol-diagnosis.json: PX4 starts v1, upgrades on incomingv2; strict controller
cannot answer initialv1. -Z is flow-off, not a protocol-version flag.

Chosen minimal architecture: explicit opt-in, finite heartbeat-only negotiation
phase in the EXISTING single-owner Controller/runner. Reuse its parser, v2 encoder,
freshness/write recheck, startup byte bounds and same UART descriptor; do not start
a second serial owner or duplicate receive stack. Default strict-v2 behavior is
unchanged. During bootstrap only unsigned/CRC-verified PX41/1 heartbeat and boot
time can usev1; all logging/ACK and post-upgrade safety frames still requirev2.
Preserve same-read fault veto, 1Hz/no catch-up,5s total initial deadline,2.5s safety
freshness, no START until verified PX4v2, no STOP before own START, no flush.

Alternatives: force MAV_PROTO_VER/firmware (outside authority/unneeded given StageA),
remove v2 checks globally (unsafe/doesn't preserve logging semantics), launch
separate heartbeat script with another owner (ownership/handoff/evidence risk).
All rejected. Explicit CLI opt-in + fresh operator preflight negotiation approval
must precede a real open; flags/fixtures alone are not authorization.

TDD: reproduce v1->heartbeat-only->v2->one START, default v1 rejection, deadlines,
same-read armed/CRC/signed/identity veto, ordering/uptime downgrade, runner actual
write recheck and partial-write failure. Capture audit must replay the explicit
mode, prevent metadata downgrade and reject logging TX before v2 confirmation.
Run Windows + research Linux POSIX PTY synthetic peers; no M3C/PX4 device access.

Preserve prior37-entry preparation report/18 original trial/14 frozen reassembly/
StageA/B bytes, historical BMI270391/306 dropouts, and old87-test source snapshots.
Main3ea1e16086965176db68b88e1c42990f92c5913e; unrelated dirty work retained.
Update existing reports/HANDOFF/VAULT_UPDATE after fresh tests and provenance.
No dependency installation, commit/push, Vault, firmware/parameter/baud/wiring,
physical capture/camera/calibration/fusion/StageC. New changed revision requires
one fresh board-side software precheck before a separately approved physical run.
Strict>=200Hz, source/tail/model/clock gates are not relaxed by this software fix.
