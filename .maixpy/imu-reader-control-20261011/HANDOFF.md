# Fixed-reader control handoff — 2026-10-11

## Completed and observed

Approved plan executed ONCE. See RESULT.md, coordinator.jsonl, original download,
analysis.json/comparison.json/source-timing.json and verification.json. Temporary
logger reader changed ONLY from `-p vehicle_imu` to `-r2500`; same selected BMI088,
topics,921600/46080/reduced streams and receiver. Fresh build d6f12ad1 verified.

60s transport completed with no observed global/logging sequence gaps or TX
rejection;11837 integrals197.104634Hz. TWO logger subscription counter increments
and4460/4507us gyro coverage holes. Fixed-reader hypothesis FAILED; no fix adopted.
Source>=200Hz/continuity remain FAILED, overall VIO-S0/P PARTIAL, Stage C CLOSED.
Accel endpoint, source/tail completeness, clock map and OpenVINS model UNKNOWN.
317 longer inferred accel windows, not275 lost samples. No interpolation/retiming.

## Files and tested working-tree state

Only existing runtime change: strict additive reader profile in
../imu-design-20261010/single-uart/controller/uart_session.py; AST equality elsewhere
verified against repo-before. New coordinator/receive/comparison wrappers reuse
frozen implementations. Runtime legacy owner/parser/ACK/STOP/admission unchanged.
Newprofile8/comparison7 and71 relevant Windows regressions PASS; M3C48 related
tests PASS/zero skips. Failed fixture/interpreter/probe/aggregate-discovery outputs
retained. No dependency, commit/push or Vault access. Main HEAD3ea1e160 remains;
unrelated camera_capture.py/tmp/PLAN_HISTORY and old report bodies preserved.

M3C final deployment /root/rm27-controller-reader-20261011.VZQm1z; first
.wiIbkI is software-only/no capture.27 source hashes,11 tools and10 transferred
evidence hashes verified. Frozen prior artifacts/Stage A/B unchanged. Local
HANDOFF/VAULT_UPDATE are reviewable working-tree evidence, not Vault ingestion.

## Safety and restoration

Fresh PX4 exact original UART3 ttyS2 command115200/budget5760/Onboard/no-flow,
nominal stream map, logger idleall187, eight SDLOG and original custom-path absence
restored. Only our166-byte config/two empty dirs removed; local readback retains
contents. M3C exact termios restored/no owner/receiver. Flow/ToF and unrelated
startup commands unchanged.342 monitored USB base29; Disarmed/EV0. No ARM,
parameter/firmware/sensor/wiring/camera/calibration/fusion/ODOMETRY operation.

## Next boundary — NOT authorized for another capture

Do not rerun coordinator or blindly increase reader rate. Available data cannot
recover actual logger wake/read execution, published/consumed generation magnitude,
VehicleIMU Run readiness or accel endpoint. Scope instrumentation/queue observability
with separately reviewed firmware/trace changes before a future physical test;
retain original >=200Hz/continuity/model gates. This run neither proves fixed
timer worse statistically nor establishes poll as the sole cause. No Stage C.

Offline reproduction in existing research venv:

```powershell
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -B -m unittest discover -s .maixpy/imu-reader-control-20261011 -p test_reader_profile.py -v
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -B -m unittest discover -s .maixpy/imu-reader-control-20261011 -p test_compare.py -v
```

analyze.py/verify_evidence.py generate exclusive outputs; do not overwrite the
completed evidence to rerun them. Reuse their pure imported APIs or copy into a
new offline output directory with explicit provenance. No live device work needed
to inspect this report. manifest.json seals this dated working-tree snapshot.
