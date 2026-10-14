# RM27 VIO plan and evidence index

## Repository scope — 2026-10-13

Main is VIO-only. The former SLAM roadmap, wrappers, reports and tests are
recoverable from branch `legacy/slam`, snapshot74d44b0. They are not active
main-branch tasks. Renaming the repository alone was not this separation:
the legacy launch paths and documents have been removed from the working tree.

## VIO progression

1. Public OpenVINS/ROS2 build, lifecycle and same-run adapter validation:
   [baseline](VIO_BASELINE_REPORT.md), [lifecycle](ROS2_LIFECYCLE_FIX.md),
   [adapter](OPENVINS_ADAPTER.md).
2. Frozen native repeatability cohort:
   [original study](NATIVE_REPEATABILITY.md). The later finite reliable-input
   candidate is recorded in [.maixpy offline validation](../../../../.maixpy/offline-vio-20261009/OFFLINE_VALIDATION.md);
   it does not turn the overall line into a universal determinism PASS.
3. Real sensor semantics/identity and transport:
   [sensor audit](IMU_SOURCE_AUDIT.md), [data contract](RM27_VIO_DATA_CONTRACT.md),
   [connection](PX4_M3C_CONNECTION.md).
4. Latest one-shot RAM input-loss localization:
   [physical diagnosis](../../../../.maixpy/imu-ram-run-20261012/RESULT.md).

VIO-S0/P remain PARTIAL; original >=200Hz,1cm, source completeness and clock/
calibration gates remain unchanged. Stage A/B is not real VIO; Stage C is closed.
See [active scope](../../../../new_plan.md) and [HANDOFF](../../../../HANDOFF.md).
Dated reports are historical observations, not permission to rerun scripts.
