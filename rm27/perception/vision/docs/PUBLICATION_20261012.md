# VIO-S0 publication and Git identity — 2026-10-12

## Scope and identity

User requested publication of the pending RM27 development, using
`shiuhou <uhshi371@connect.hkust-gz.edu.cn>`. Baseline main/remote main:
`3ea1e16086965176db68b88e1c42990f92c5913e`.

The last three published commits had author/committer name `shiuhou` but email
`uhoushi@gmail.com`. Their already-shared history is retained, NOT amended,
rebased or force-pushed. This task corrects the repository-local Git name/email
for new commits; global Git identity is not changed. Historical push authentication
cannot be inferred from a commit's author email.

`gh api user --jq .login` returns `shiuhou`; repository API returns push permission.
The normal push explicitly uses the verified GitHub CLI credential helper rather
than assuming the system Git Credential Manager cache uses the same account:

```powershell
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin main
```

No credentials/tokens/private keys are included. Push completion is only reported
after the command exits successfully and remote `refs/heads/main` equals local HEAD.
This file does not pre-record a future successful push.

## Published development / unchanged qualification

Curated code/tests, plans, measured-result reports and selected JSON summaries:
single-owner UART controller, bounded startup synchronization/heartbeat-only v2
negotiation, initial/negotiated failure records, reduced-telemetry comparison,
sender-loss attribution, residual source diagnosis, fixed-reader negative control
and upstream-gyro observation. Small pinned source/schema snapshots needed by the
diagnostic tools are retained with their existing source provenance.

- Stage A/B remains its original PASS; the report bytes/hash are unchanged.
- Two vehicle_imu-only comparisons completed approximately60s with clean observed
  UART delivery, but197Hz/source coverage did not pass the original200Hz gates.
- Fixed2500Hz reading did NOT eliminate logger subscription skips.
- Adding full-rate sensor_gyro stopped at logging287 missing, attributable to one
  observed PX4 TX-buffer rejection. No60s source observation, no retry or fix.
- VIO-S0/P PARTIAL; original skip trigger/clock/model/tail UNKNOWN; Stage C CLOSED.
- RAM-trigger diagnostics remain DESIGN ONLY; no firmware approval/build/flash.

Historical reports' old "next"/"not executed" paragraphs describe their dated
state. Current root HANDOFF and latest result supersede them; a published bench
coordinator is not authorization to rerun an already-consumed physical trial.

## Evidence availability

Raw ULogs/UART recordings, huge generated logs, environments, binaries/tarballs,
vendor/build trees and old transient consoles remain in their recorded local/M3C
locations; they are not added to Git. Unrelated camera_capture.py/tmp and the
pre-existing PLAN_HISTORY.md edit are excluded and preserved in the worktree.
No hardware/SSH runtime access, capture, parameter/firmware/communication change,
calibration, fusion, ARM/flight or Vault access occurs during publication.

The raw-inclusive dated manifests are historical inventories, NOT a claim that
all listed bytes are in a clone. Dataset-dependent replay and full historical
manifest verification require the original evidence. In particular the full
source-diagnosis suite includes ONE real saved-ULog test; it passes locally with
that data, but is NOT counted as a clone-portable fixture test or silently skipped.
Run the three named synthetic classes when testing a clone without that dataset.
The published JSON summaries are real diagnostic results, not synthetic VIO data.

Curated path/hash/size inventory: `.maixpy/publication-20261012/selection.json`.
Original six root-report before-states are copied locally under this publication's
repo-before; prior experiment reports, raw files and manifests are not rewritten.

## Verification

Fresh worktree checks before packaging:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
py -3 -B -m pytest tests -q
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -B -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
```

Root:226 passed/1 existing skip; controller120 total,113 passed/7 POSIX skips.
Fresh retry5, negotiated9, gap-diagnosis15, source-diagnosis19 PASS/zero skips;
upstream-observer22 total,19 PASS/3 POSIX skips. These are software/replay checks,
not new board or physical qualification. Prior M3C results remain historical.

The staged index is exported to a fresh temporary directory to check that
published imports/fixtures do not depend on ignored source. Exact command results,
portable-vs-dataset-dependent scope, staged byte parity, whitespace and credential
pattern review are recorded in this publication's VALIDATION.md before committing.
No dependency installation, runtime refactoring or threshold relaxation.

## Next / rollback

Current source observability design:
[NEXT_TRACE_PLAN](../../../../.maixpy/imu-upstream-gyro-20261011/NEXT_TRACE_PLAN.md).
Diagnostic-firmware authority and an exact original rollback binary are still
prerequisites; source hash alone is not a rollback image. No new physical step in
this publication. A future rollback can revert this publication commit without
erasing prior experiment evidence; no destructive cleanup or history rewrite.
