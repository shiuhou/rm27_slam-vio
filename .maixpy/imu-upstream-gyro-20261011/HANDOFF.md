# Upstream gyro observation handoff — 2026-10-11

Completed ONE stock-firmware bench attempt authorized by `設計完直接上真機吧`.
FAILED at normal logging287:286→288/global19→21. Saved LINK counters isolate one
PX4 TX-buffer rejection, no unaccounted successful writes. No60s qualification.
Settings restoration/scope/raw replay/hash verification PASS; see RESULT.md and
verification.json. VIO-S0/P PARTIAL, Stage A/B preserved, Stage C CLOSED.

Files: observation.py/test_observation.py strict diagnostic profile/source-window
analysis; coordinator.py/test_scope.py scoped stock-firmware setup/restore;
receive.py reuses byte-identical controller; analyze_failure.py and verify_evidence.py
are actual failed-prefix tools. analyze.py is the UNUSED successful-run analysis
prepared before capture; it is not evidence and must not be run on this failure.

Authoritative data: download/physical-trial-01/received-prefix.bin71226bytes,
SHA93343246cbe63075680deb2575ef938f468ce789a46ee103bd65a32f336a4580;
wire.jsonl and summary.json raw; failure-analysis.json verified diagnostics.
Only4SIgyro/1IMU record: rate, original hole correlation and source coverage UNKNOWN.
48 raw reliable291 repeats are not the summary's accepted-prefix retransmissions0.
M3C isolated deployment `/root/rm27-controller-gyro-20261011.OaOhNe/`, stopped;
no UART owner and original exact termios restored. Both PX4 wired communication
settings and logger/topics/streams restored; no firmware/parameters/selection/rate
or wiring touched. Original snapshots/manifests retained.

Useful next scope: NEXT_TRACE_PLAN.md (RAM diagnostics DESIGN ONLY). It requires
consequential firmware approval before any build/flash bench experiment, plus an
exact rollback artifact. Do not treat this general bench authorization as flashing
permission. Do not retry the observer, mask packet gaps, relax200Hz, start sync/
calibration/VIO/fusion/Stage C or push. No Vault access; root VAULT_UPDATE is only
an import proposal. Existing unrelated camera_capture.py/tmp changes belong to user.
