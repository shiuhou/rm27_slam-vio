# Offline source/subscription diagnosis — 2026-10-11

Only inspect saved artifacts and exact d6f12ad1 source. Diagnose the residual
4554 us gyro coverage hole separately from source cadence, preserving >=200 Hz.
No serial/network/SSH/capture, production/runtime changes, installs or push.

1. Verify frozen prior artifacts and preserve current root pointers.
2. Trace logger subscription/queue/poll behavior and VehicleIMU dual-integrator
   readiness/callback/backup behavior from exact source.
3. Add small diagnostic helpers with labeled synthetic tests; reuse existing
   ULog framing and integral semantic audits. Quantized period multiples are
   inference, not raw sensor sample counts.
4. Replay actual evidence, quantify coverage/cadence/latency and counter brackets.
5. Independently verify and update handoff/pointers without editing old snapshots.
