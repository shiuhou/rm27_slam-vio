# Engineering Handoff — VIO-only scope, 2026-10-13

## Repository state

Windows repository main, base74d44b09c65e2a839b74d834756f0d178207d679.
Working tree includes scoped cleanup plus pre-existing diagnostic work and
unrelated tests/camera_capture.py/tmp. On2026-10-14 the user authorized committing
and pushing this cleanup on main plus the legacy/slam archive. Publication uses
only the reviewed scope files; unrelated/raw/diagnostic artifacts are excluded.
Branch `legacy/slam` preserves the original committed mixed tree.
Before-edit copies of all pre-existing tracked dirty files are retained under
`.maixpy/vio-scope-20261013/repo-before/`; original experiments were not deleted.
Publication outcome is verified against remote refs after push; this document
alone is not proof of remote completion.

## Task objective / actual changes

User requested only VIO content in main, with SLAM archived or removed.
Archived original branch; removed legacy monocular launchers, observer builds,
TUM-only dataset/experiment framework, roadmaps, VSL reports and associated tests.
Main runner now permits only OpenVINS and refuses legacy backends before filesystem
effects. Preserved the exact OpenVINS OnlinePoseRecord validation/data semantics;
removed its legacy state mappers and monocular CSV parser.
Kept camera/calibration evidence and coordinate/timestamp primitives used by VIO.
Updated README/plan/resume indices; no estimator math, raw data, device config,
acceptance gate, dependencies or firmware changed in this task.

## Verification commands and observed results

Scope test before edits:7 failed/1passed as expected; after edits, scope plus
OpenVINS projection/runtime tests33 passed. Full final suite result and deletion/
archive coverage are in `.codex/tasks/2026-10-13-vio-only/validation-report.md`.
Baseline full suite:225passed/1skipped/1failed in an existing legacy subprocess
timeout test; original test remains on legacy/slam, not secretly marked PASS.
Fresh2026-10-14: py -3 -m pytest tests -q --ignore=tests/camera_capture.py:
148passed/1existing ROS2 skip, exit0,4.11s. No physical test performed.

## Failed attempts

First large source-read JSON was truncated by the tool, so no edit was applied.
Repeated with a complete bounded result, then applied the reviewed archive list.
Baseline legacy timeout failure above retained; no timeout policy was weakened.

## Verified VIO facts carried forward

VIO-P PARTIAL. Finite reliable-input PC candidate: five identical state hashes;
original/default asynchronous failures remain. Original1cm criterion unchanged.
VIO-S0 PARTIAL. Latest physical candidate04 RAM observation measured Wait10443us,
two source publications1498us apart and copy generation815904->815906.
Intermediate publication absent from raw ULog;4507us gyro integral coverage hole.
Its link bracket has76successful/76received, no rejection/gap. This establishes
one logger Wait/depth-one input overwrite, not a fix or global hardware acceptance.
Whole capture11788 integrals/196.32949Hz, two holes and a separate startup rejection.
Original >=200Hz/model/source/clock/tail gates remain unsatisfied; Stage C closed.

Evidence: `.maixpy/imu-ram-run-20261012/{RESULT.md,analysis-reviewed.json,verification.json}`,
`.maixpy/offline-vio-20261009/OFFLINE_VALIDATION.md`, native/adapter docs and sensor audit.
Prior runtime restoration: logger/UART/streams/8SDLOG,961 typed parameters and
M3C termios verified; no owner/process.65 observed FC HB armed-clear, ULog armedfalse,
pre/post Disarmed. Stage A/B is only communication/synthetic-ODOMETRY evidence.

## Decisions and rationale / assumptions and open questions

Use branch archival rather than irreversible loss of historical evidence.
Remove only backend-specific paths, not the OpenVINS projection contract.
Historical manifests describe their captured/source snapshots, not this refactor.
Exact Wait poll/wake/notification-copy cause, complete sensor/accel coverage,
camera exposure semantics, FC–M3C clock mapping and rigid/noise calibration remain open.

## Risks / next actions / rollback point

Last verified physical FC still has diagnostic candidate04 ON, not stock:
SHA21f82789fb089c99f3e097c361d1fd1b7e6ffe83f55cea46505709ac512591d9.
Both trace writers frozen; do not arm/fly. No physical access in this cleanup.
Vendor recovery candidate is not proven byte-identical to preflash; no auto recovery.
Next proposed VIO work is offline buffered input design; hardware/firmware/capture/
fusion remain separately scoped. No repeated experiment or estimator promotion.
User approved scoped commit/push of main and legacy/slam on2026-10-14; never
stage unrelated files. Recover retired files from legacy/slam; dirty prior docs
have separate exact backup. Vault not accessed or modified.
