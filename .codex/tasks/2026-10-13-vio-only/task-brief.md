# Objective and constraints

Main contains only VIO implementation, shared prerequisites and evidence.
Archive executable stella_vslam/ORB-SLAM3 wrappers, monocular observer/parser,
TUM-only experiment framework, VSL roadmap/reports and tests on legacy/slam.
OpenVINS runtime dispatch and observation validation must remain intact.

Baseline main74d44b09c65e2a839b74d834756f0d178207d679 with pre-existing dirty
diagnostic work and unrelated camera_capture.py/tmp. Archive ref pins that
committed state; before-edit copies additionally preserve existing dirty docs.
No estimator math/physical data/acceptance/dependency/device/firmware change.
No stage/commit/push, no Vault read/import. User fixed the ownership boundary;
no new external architecture research or physical experiment needed.
