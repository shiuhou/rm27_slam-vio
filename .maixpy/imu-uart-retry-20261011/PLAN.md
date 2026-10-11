# One revised physical UART trial — 2026-10-11

User's `do it` approves one 60-second accepted interval at temporary921600,
46080B/s, minimal MAVLink vehicle_imu logger. Reuse unchanged 87-test M3C
deployment; no second attempt, parameter/firmware/wiring/fusion/StageC changes.
Fresh actual backups and exact restoration are mandatory even on failure.
Existing original failed trial/StageA/B evidence and unrelated dirty files remain.
Main3ea1e16086965176db68b88e1c42990f92c5913e; no commit/push/Vault access.

The new one-off coordinator reuses bench_io and rate_control, but does not rerun
the frozen old coordinator. Validate its narrow command scope and port/SDLOG
checks before use. Read-only board precheck must confirm no UART owner/console,
921600 termios constant, exact deployed receiver bytes and fresh versions.
Snapshot mutable handoff/report files before additive updates.

Receiver owns one physical UART, no flush, bounded pre-START CRC sync, strict
decoding after heartbeat boundary, one START/STOP and exact termios restoration.
Independent USB monitors disarmed heartbeat throughout. Remote timeout/TERM
bounds own receiver; failed cleanup is reported, never inferred as restoration.
Back up only actual logger/UART commands, stream rates, SDLOG and custom-file
absence; refuse existing custom configuration instead of overwriting it.

Preserve raw wire, complete received prefix even on failure, before/during/after
CPU/source/status windows, matching remote/local hashes, replay audit and exact
restoration readback. Transport, source completeness, tail, interval observation
model and camera clock are separate gates. >=200Hz is not relaxed. No synthetic
repair, instant-sample label or VIO PASS from a transport-success exit code.
