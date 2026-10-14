# Evidence and recovery

- Original committed files: local legacy/slam ->74d44b09c65e2a839b74d834756f0d178207d679.
- Pre-existing dirty files: exact .maixpy/vio-scope-20261013/repo-before copies;
  excludes unrelated untracked files, which were not edited.
- Archive inventory: archive-manifest.json; all retired paths recoverable from
  the pinned archive ref, with before hashes checked prior to deletion.
- Fail-closed VIO-only dispatch/no legacy mappers/tree regression:
  tests/test_vio_repository_scope.py, RED/Green logs under evidence directory.
- Preserved camera prerequisites and metadata semantics:
  prepare_camera_dataset.py, capture_calibration.py, analyze_video.py,
  schema/manifest/trajectory/common and calibration/data-contract templates.
- Original OpenVINS algorithm/runner implementation remains openvins_runtime.py;
  only outer dispatch and legacy online helpers were restricted.
- Current VIO hardware state/evidence: HANDOFF and linked immutable dated reports;
  no device accessed or qualification claimed by this cleanup.

Old published manifests belong to the original evidence/source snapshot, not
this refactored active tree. Historical local artifacts are deliberately retained.
