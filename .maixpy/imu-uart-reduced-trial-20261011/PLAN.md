# ONE approved reduced-telemetry physical comparison — 2026-10-11

User's latest `do it` approves the single60s NEXT_TRIAL_PLAN from the completed
offline diagnosis. Carry the same-session all-propellers-removed confirmation;
fresh Disarmed/EV0/identity/settings checks precede every mutation. No repeated
StageA/B, firmware/parameters/sensor/wiring/fusion/camera/flight/dependencies/push.

Baseline main3ea1e16086965176db68b88e1c42990f92c5913e; existing dirty reports/
controller and unrelated camera_capture.py/tmp preserved. Prior gap-diagnosis
manifest33own/31external and physical trial58own/25external are historical
snapshots, not editable output targets. New before-report copies preserve them.

Reuse existing18-file tested controller/reassembler unchanged, bench Link/FTP,
scope/parsing helpers and exact firmwared6f12ad1. Minimal new one-off coordinator
only changes nonessential numerical telemetry streams on wiredttyS2; retain
HEARTBEAT/SYSTEM_TIME/TIMESYNC/LINK_NODE_STATUS/SYS_STATUS/STATUSTEXT and unlimited
streams. Preserve optical-flowttyS3 and USB. Same921600/46080/MAVLink-only logger/
8 topics/current selectedBMI088 instance0. Actual backups/readback/restore.

TDD new pure treatment/allowlist/CPU-stat/UART-counter tools, then isolated
M3C deployment with source parity and NEW-tool tests. Do not rerun unchanged120
board tests. A parent samples receiverCPU/RSS/context-switches before a start
gate, throughout capture/early failure/cleanup. UART counter ioctl uses ONLY
receiver's owned descriptor (no second port opener); unsupported stays UNKNOWN.

ONE capture only,60s normal-data target, bounded startup/stop, first fault stops.
Preserve failed raw chunks/frames/prefix and no repaired/admitted failed dataset.
Fresh counters/CRC/global vs logging sequence, source coverage/units/IDs/rate,
CPU and restored settings checked offline. >=200Hz/source/tail/clock/model gates
unchanged; send-buffer improvement is not full VIO qualification. Update reports/
HANDOFF/VAULT_UPDATE, no Vault access/staging/commit/push or automatic retry.
