# Saved-wire loss attribution — 2026-10-11

User's `do it` resumes OFFLINE diagnosis of the ONE completed physical trial,
not another capture or settings change. Preserve logging435 failure, original
thresholds, StageA/B, raw bytes and previous manifests. No device/SSH/serial,
firmware/parameters/baud/wiring, fusion/camera/calibration/install/Git push/Vault.

Baseline main3ea1e16086965176db68b88e1c42990f92c5913e, dirty reports/controller
and unrelated camera_capture.py/tmp retained. Prior physical58-own/25-external
manifest must verify before updates. Root report copies in repo-before. Reuse
existing raw parser/reassembler/source-semantic tools; do not duplicate an
acquisition framework or emit a repaired/shortened accepted ULog.

1. Trace original source and saved wire; inspect previously unknown diagnostic
   messages and complete metadata records after the failed sequence, without
   admitting the failed session or filling missing data.
2. Check exact PX4 submodule pins/message definition before diagnostic decoding;
   verify CRC, layout, sender and timestamp provenance. Missing/invalid counters
   stay UNKNOWN. No inference from a rate average alone.
3. TDD minimal offline diagnostics for counter discontinuity/wrap/reset, logging
   gaps vs global gaps, post-failure record boundaries and synthetic queue-burst
   sensitivity if useful. Synthetic findings are not live performance evidence.
4. Use actual counters to rank/confirm per-layer causes; separate source integral
   coverage from logging transport. No speculative receiver/firmware fix.
5. Run relevant offline tests and fresh preservation checks; report what is
   established, remaining questions and one concrete instrumented comparison
   proposal. Update existing handoff/proposed Vault update; no Vault access.
