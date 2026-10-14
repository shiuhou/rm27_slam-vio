# VIO-only repository update proposal — not ingested

2026-10-13: user requested VIO-only main. Original mixed committed tree74d44b0
is preserved on local legacy/slam. Removed executable monocular SLAM launchers,
their experiment framework/reports/tests; main runner now accepts OpenVINS only.
Shared camera calibration/evidence, pose/timestamp contracts and VIO primitives
remain. Current root HANDOFF summarizes verified VIO state; previous full dirty
handoff/proposal/indices were copied exactly to .maixpy/vio-scope-20261013/repo-before.

This is a repository scope change, not an IMU/estimator fix. VIO-P/S0 remain
PARTIAL; original >=200Hz/1cm/source/model/clock/calibration gates unchanged.
Latest physical RAM trace established one Wait/depth-one overwrite, not global
hardware health. Diagnostic firmware remains installed; keep disarmed/do not fly.
No device action, raw rewrite, dependency, acceptance or Vault change.
On2026-10-14 the user authorized scoped cleanup publication on main and
legacy/slam; raw and unrelated diagnostic work remains excluded.

A later explicitly requested Vault import may record the new ownership boundary
and link the archived snapshot plus current VIO handoff. This file is only a local
proposal, not proof of Vault ingestion or GitHub publication.
