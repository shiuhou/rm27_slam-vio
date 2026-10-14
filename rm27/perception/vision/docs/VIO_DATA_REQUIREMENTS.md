# Camera + IMU VIO evidence requirements

This main-branch index supersedes the archived VSL roadmap, not the data schema
or acceptance gates. See RM27_VIO_DATA_CONTRACT.md and IMU_SOURCE_AUDIT.md for
the source-specific contracts and dated observations.

- Preserve camera frame/source IDs, exposure timestamp semantics, clock domain,
  acquisition uncertainty and original image geometry/bytes.
- Preserve actual gyro/accel identity, sample endpoints, axes, units, calibration,
  filtering, integration/batch semantics and saturation/error information.
- Record missing data, sequence changes and time resets; never fill or retime
  samples to make the >=200Hz/complete-input gate pass.
- FC sample time, FC publication time and M3C receipt time are distinct.
  A measured clock map and uncertainty are prerequisites for a paired dataset.
- Rigid camera/IMU extrinsics, temporal calibration, noise and compatible camera/
  inertial observation models require separately authorized physical evidence.
- Existing metadata/validators/templates and public-sequence1cm gate are unchanged.

Current VIO-S0/P remain PARTIAL. Integrated vehicle_imu window means are diagnostic,
not automatically valid instantaneous OpenVINS samples. Historical/fixture tests
do not qualify real synchronized capture, M3C estimator deployment or EKF fusion.
No physical capture/calibration is authorized by this document.
