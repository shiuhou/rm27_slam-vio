# RM27 VIO repository scope

- Main is for Camera + IMU VIO only. Current implementation is OpenVINS.
- Legacy monocular SLAM wrappers, mapping/loop-closure experiments, VSL plans
  and tests live on legacy/slam. Do not restore/develop them in main or silently
  enable a fallback backend. SLAM research belongs in a separate repository.
- Preserve shared camera/calibration evidence, pose/timestamp contracts and
  VIO-required helpers. Repository names and historical artifact labels are not
  evidence that a module is an active SLAM dependency.
- Keep raw evidence/old manifests immutable. Archived snapshot74d44b0 and
  dated before-edit copies are recovery sources, not current qualification.
- VIO-P/S0 remain PARTIAL until their original gates are actually met.
  Do not relax the >=200Hz/1cm, completeness, clock or observation-model gates.
- Repository cleanup never authorizes a capture, calibration, firmware change,
  EKF integration, arming/flight or execution of a dated hardware coordinator.
  Read the current HANDOFF and specific experiment boundary first.
- Preserve unrelated dirty/untracked work. Commit/push or Vault ingestion needs
  an explicit user request; local branch archival is not GitHub publication.
