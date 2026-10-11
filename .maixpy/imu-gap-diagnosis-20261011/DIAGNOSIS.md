# PX4 single-UART logging loss attribution — 2026-10-11

## Result

**The terminal failed logging435 interval is attributable to PX4 send-buffer
rejection, not an identified M3C parser/read loss. VERIFIED offline attribution;
physical fix NOT_VALIDATED, high-rate transport FAILED, VIO-S0/P PARTIAL.**

This reanalyzes ONE existing failed physical trial, not a new capture. No M3C,
PX4, SSH or UART access, setting/firmware/parameter/wiring changes, production
code changes, new dependencies, fusion/camera/calibration, commit or push.
Stage C stays CLOSED. The previous trial report/manifest remain dated snapshots;
their then-UNKNOWN attribution is narrowed here, not retroactively rewritten.

Baseline: main HEAD `3ea1e16086965176db68b88e1c42990f92c5913e`, existing dirty
controller/reports and unrelated camera_capture.py/tmp retained. Exact firmware
evidence is PX4 v1.17.0 `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`.
Selected source in that trial was BMI088 instance0, gyro6684690/accel6946834;
historical BMI270391-dropout data is not this source or result. USB COM19 and the
physical M3C/PX4 ttyS2 UART remain distinct.

## Newly decoded evidence

Installed pymavlink2.4.49 common/development maps omitted message8
LINK_NODE_STATUS. This decoder/schema omission concealed diagnostics; it did
NOT cause physical packet loss. Reused CRC/checksum tools with the firmware's
actual MAVLink XML, not current online/default definitions.

Pins and saved source in `source/`:

- PX4 MAVLink gitlink `33af200d25ec6f0925b49b1ba82bbf1294ea5f72`; pinned
  common.xml SHA256 `bbc1c382a217209f2cb3922416539da3226878dd19c7549f928913a6f72b1498`.
- Its pymavlink generator gitlink `fcaa2c7d25e3169dc66155929c338487941555e9`.
- PX4 NuttX gitlink `fb2fadf6f599c1406f052db013efd00a2518e72c`.
- LINK_NODE_STATUS fixed payload36bytes, CRC_EXTRA117, layout
  `<QIIIIIHHHBB`; v1 full payload and unsigned v2 trailing-zero truncation handled.
  Source/route/header/length/CRC validated, not authenticated identity.

The [matching PX4 LINK_NODE_STATUS implementation](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/streams/LINK_NODE_STATUS.hpp)
is essential to interpret the fields: timestamp is HRT **microseconds**, despite
XML's ms label; tx_overflows is the low16 bits of **send-rejection event count**,
despite XML's byte label. tx_buf/rx_buf are hardcoded TODO-zero, NOT measurements
of available space. rx_overflows describes PX4 input, not M3C's receive driver.

All ten saved LINK_NODE_STATUS frames are CRC-verified. The other23 previously
unknown frames also pass pinned CRC checks: EVENT9, CURRENT_EVENT_SEQUENCE4,
TIME_ESTIMATE_TO_TARGET5, CURRENT_MODE5. Existing wire replay verifies the
other3664 frames. All3697 retained PX41/1 frames are thus CRC-checked; original
rows/UNKNOWN labels remain untouched.

## Sender/receiver accounting

The ten snapshots define nine intervals. `messages_sent` counts successful
full writes into PX4's serial driver, not bytes physically observed on a scope.
The snapshot excludes its own transmission; endpoint frames cancel when comparing
success-count deltas with received frame-index deltas. No counter decreases,
epoch resets or ambiguous reordered sequences were observed in these intervals.

| Interval | Successful-write delta | Received frames | TX rejection delta | Missing global sequence positions |
|---|---:|---:|---:|---:|
| 1 | 358 | 358 | 4 | 4 |
| 2 | 389 | 389 | 0 | 0 |
| 3 | 454 | 454 | 0 | 0 |
| 4 | 379 | 379 | 0 | 0 |
| 5 | 419 | 419 | 0 | 0 |
| 6 | 414 | 414 | 0 | 0 |
| **7: logging435 absent** | **398** | **398** | **1** | **1: 34→36** |
| 8 | 376 | 376 | 1 | 1 |
| 9 | 383 | 383 | 0 | 0 |

Interval7 HRT11290781844→11291789594us: tx_overflows4→5,
messages_sent7317→7715. Every successful sender write is accounted for by one
received frame. The sole sequence hole35 lies between logging434 and436.
Across all nine intervals, six sender rejections match all six modulo sequence
positions missing from the retained stream. Before the first/after the last
snapshot is unobserved. These are not exact ADC sample-loss counts, authentication,
or proof that every future physical link will be error-free.

The [pinned MAVLink C send helper](https://github.com/ArduPilot/pymavlink/blob/fcaa2c7d25e3169dc66155929c338487941555e9/generator/C/include_v2.0/mavlink_helpers.h)
increments global tx sequence BEFORE MAVLINK_START_UART_SEND. In matching
[PX4 mavlink_main.cpp](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_main.cpp),
send_start calls FIONSPACE; insufficient room increments tx_buffer_overruns and
suppresses send_bytes/write. Full write alone increments tx_message_count.
This explains a consumed global sequence with no successful write/received frame.
The exact contents of absent frame35 cannot be recovered, but logging435 plus
the sole send rejection and no unaccounted successful writes isolate this
terminal interval to the sender rejection layer.

## Upstream and post-failure evidence

Normal [mavlink_ulog.cpp](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_ulog.cpp)
LOGGING_DATA consumes a ulog_stream publication and advances its quota, without
checking free UART space/retrying normal data. Reliable header chunks use ACKs;
that does not make normal logging reliable.

A COMPLETE record wholly inside reliable packet437 (offset97) contains
`char[46] perf_counter_postflight` value:
`mavlink: ulog_stream messages missed: 0 events`.
It was sent after failure, retained48 times;47 byte-identical retries are ignored
for diagnostics. The next record is truncated and NOT interpreted/joined.
No missing packet is fabricated, no shortened/accepted ULog is emitted, and no
post-failure bytes are admitted into the failed prefix. This counter does not
show a ulog_stream generation skip at its observation time; it supports sender
rejection rather than that particular upstream-queue fault for logging435.
It is not a complete postflight/counter-tail or source-completeness certificate.

Retained logger_status snapshots report message_gaps1→2→3, MAVLink backend2,
is_logging1, eight topics; buffer_size/used and file-write fields0. These zero
fields are backend-specific, NOT evidence that a64KiB SD buffer allocation failed.
Logger message_gaps aggregates generation-discontinuity EVENTS of full-rate
subscriptions, not number of missing samples or attribution to one topic.
Separate source/subscription omissions remain relevant even before logging435.

Correction to the prior report's conservative reset warning: matching
[logger.cpp](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/logger/logger.cpp)
calls perf_reset_all in **start_log_file**, NOT start_log_mavlink. The MAVLink-only
trial did not invoke that file-start path. start/stop MAVLink logging write
pre/postflight perf data; stop's executable code does so despite its misleading
comment. Driver pre/post values1/1 are still not zero, nor a missing-sample proof;
any difference claim needs same-counter/lifecycle continuity. Original report
is preserved unchanged; this source-scoped correction supersedes its broad wording.

## Trigger: confirmed layer, bounded hypothesis

| Candidate | Evidence/status |
|---|---|
| PX4 send-buffer rejection | VERIFIED for terminal interval and six observed missing positions |
| M3C parser/read/UART drop | No unaccounted successful writes in nine intervals; not implicated here, not universally excluded |
| ulog_stream generation skip | Complete post-failure counter0; not shown as terminal cause |
| IMU→logger subscription loss | Aggregate logger gaps increase; separate retained gyro coverage gaps, PARTIAL |
| SD write stall | MAVLink-only backend, no new SD recording; not the loss path in THIS experiment |
| Telemetry/ULog burst competition or scheduling/drain delay | Plausible source-supported trigger, not physically isolated |
| Electrical baud/wiring fault | Not established by this evidence |

The matched board defconfig has USART3 TX800bytes. Matched STM32H7 registration,
enabled USART1/2/3 and disabled reordering associate ttyS2 with USART3 in this
source configuration. [NuttX FIONSPACE](https://github.com/PX4/NuttX/blob/fb2fadf6f599c1406f052db013efd00a2518e72c/drivers/serial/serial.c)
reserves one circular-buffer slot, so the empty modeled ring has799 usable bytes.
This is **source configuration**, not a live generated-config/free-space readback.
Three full unsigned ULog MAVLink2 frames require3×267=801bytes with no drain;
this SYNTHETIC sensitivity exceeds799. It does not reconstruct actual queue
occupancy, task timing, DMA/interrupt latency or exact rejected-frame length.

Physical921600/8N1 capacity92160B/s, software budget46080B/s and measured whole
RX average33522.30B/s are compatible with momentary buffer rejection. Mean
headroom is not instantaneous space. Normal telemetry is updated before ULog
in the same MAVLink task; the ULog quota can release several frames per update.
Reducing competing telemetry is a justified next single-factor experiment,
NOT a proven fix. Buffer enlargement/custom firmware is not implemented.

## Source qualification is separate

Prior retained prefix513 BMI088 vehicle_imu integrals:2.606488s,196.432901Hz,
strict ordering/stable IDs/calibration1/1/no clipping. Two gyro coverage residual
gaps>2us sum13520us, before terminal wire loss. Different gyro/accel intervals and
unknown separate accel endpoint must be preserved. Diagnostic delta/dt means
are not instantaneous/bias/noise-calibrated OpenVINS samples. No >=200Hz gate
relaxation, camera clock mapping, temporal/spatial calibration, complete source
or tail/EOF proof. Receiver CPU was NOT_MEASURED in the old run.

## Verification and artifacts

Reused raw wire/prefix/summary and capture replay, existing finite reassembler
and integral auditor. Added only offline `diagnose.py`, `test_diagnosis.py` and
`verify_evidence.py`; diagnostic output `diagnosis.json`, `verification.json`.

```powershell
& .maixpy/imu-offline-20261008/venv/Scripts/python.exe -B -m unittest discover -s .maixpy/imu-gap-diagnosis-20261011 -p test_diagnosis.py -v
& .maixpy/imu-offline-20261008/venv/Scripts/python.exe -B .maixpy/imu-gap-diagnosis-20261011/diagnose.py
& .maixpy/imu-offline-20261008/venv/Scripts/python.exe -B .maixpy/imu-gap-diagnosis-20261011/verify_evidence.py
```

Final new tests15 PASS/zero skips, Pythonexit0 (tests-final.txt;0.034s). Initial12
missing-tool failures and later3 missing-CRC-tool failures preserved as TDD RED;
12 then15 GREEN. Main analysis/independent verifier Pythonexit0. Analysis JSON
is exclusive-create; verifier preserves its first JSON and prints fresh replay
results on rerun. Final verifier output is verification-final-console.txt;
it also verifies all six old report tails byte-for-byte. Do not overwrite dated
outputs. Functions/tests can replay read-only. Raw initial native stderr decoration
is not a Python failure. git diff --check exit0; line-ending warnings are retained
and do not authorize normalizing unrelated files.

Verifier checks58 previous trial files/25 external snapshot files,18 unchanged
deployed sources,18 original/37 preparation/44 negotiation/14 reassembly artifacts,
Stage A/B SHA and full stored wire replay. New root pointers preserve old report
tails in six repo-before copies; older manifests still describe older root states.
StageA/B SHA `d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f`.
Raw prefix SHA `b66b017ab4acbf04a85e76b196f8d98a4752ab885350881c15ab83d9e7505327`;
wire SHA `f424acde1d4a64a51a441ab6e4bbd4c0f8be171eaf419c4b184d8ffed3a97153`.

Fresh prior9 scope/analysis regression results are recorded in
`regression-trial.txt`; no runtime software changed, so120-board/226-root/54-related
results remain prior evidence, not new board validation this turn. No staged diff,
commit, push or Vault access. Local VAULT_UPDATE.md is only an import proposal.

## Handoff / next boundary

Completed: evidence-backed failure-layer attribution and offline diagnostics.
Remaining UNKNOWN: exact burst/driver/scheduling trigger, whole-run loss-free
delivery, actual receiver CPU/UART errors, complete>=200Hz source coverage,
tail and clocks/integral-input model. Hardware-dependent gates remain BLOCKED on
new scoped measurements; VIO-S0/P stay PARTIAL.

Exactly one proposed next physical action is in [NEXT_TRIAL_PLAN.md](NEXT_TRIAL_PLAN.md):
one instrumented60s **reduced-telemetry** comparison on the existing M3C↔PX4 UART
plus PX4 USB, with same921600/46080/source/logger and exact restoration. NOT run
or authorized by this offline turn. Do not rerun frozen coordinators, blindly
retry, fill gaps, lower source thresholds or open full Stage C.
