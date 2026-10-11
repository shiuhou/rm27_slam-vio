# Negotiated single-UART IMU physical trial — 2026-10-11

## Result

**MAVLink2 bootstrap/START/STOP and configuration restoration VERIFIED.
Loss-free high-rate transport FAILED; 60s NOT_COMPLETED; VIO-S0/P remain PARTIAL.**
User's `可上真機` authorized ONE scoped experiment, not automatic retries. This
attempt stopped on `logging sequence discontinuity: expected 435, received 436`.
No complete/framing-valid ULog or qualified OpenVINS input was produced. Earlier
Bad-prefix/pre-peer-order failures and Stage A/B artifacts are unchanged.

| Layer | Actual evidence | Verdict |
|---|---|---|
| Current M3C software | 120 tests, zero skips, 7 virtual-PTY cases; 18 source hashes match | VERIFIED software only |
| Physical startup | CRC boundary found; guarded v1→v2 heartbeat bootstrap; PX4 v2 readback | VERIFIED this attempt |
| Logging handshake | One START and one STOP, both ACCEPTED | VERIFIED |
| Logging continuity | Accepted sequence0..434; next436, missing435 | FAIL |
| Bounded60s capture | Normal-data accepted receipt span2.596507084s before failure | NOT_COMPLETED |
| Retained BMI088 source | 513 integral records, effective196.432901Hz, gaps present | PARTIAL; not≥200Hz PASS |
| Restore/safety | Exact M3C termios, PX4 UART/logger/streams/SDLOG/file absence restored | VERIFIED readbacks |
| Source/tail completeness, clocks, OpenVINS model | Failed prefix, no camera clock map, integral-input gate unchanged | UNKNOWN/unqualified |

Working-tree baseline main HEAD `3ea1e16086965176db68b88e1c42990f92c5913e`.
Fresh FC identity: MICOAIR_H743_V2, PX4v1.17.0,
`d6f12ad1c4f70ad3230afd7d86e971421e02fef4`. Selected BMI088 instance0:
gyro6684690 / accel6946834. Historical BMI270 data is not this source or restore
target. COM19@configured57600 was USB CDC inspection, NOT physical UART baud.

## Deployment and actual scope

New isolated M3C deployment, old deployments unchanged:
`root@10.18.198.1:/root/rm27-controller-negotiated-20261011.ffWOSR/`.
Hostname maixcam2-9d05/aarch64; Python3.13.2, NumPy2.2.6, pymavlink2.4.49,
pyulog1.2.4. Reused existing pymavlink site-packages and an isolated pinned pure
pyulog copy; no installation/production dependency change. `environment.json`,
`board_test.py` and `tests.txt` record actual imports and commands. Source archive
`2686a084b66638e01690f83aceab31c80053c4766ef62e00bf49ca8a9249337d`;
pinned pyulog archive
`10f7915ac46416e9392267334e156f24566ee2df56fcd812c405c427803d3573`.
120 tests PASS in16.584s, Python/SSH exit0; PTYs are software tests, not wire proof.

New `coordinator.py` reuses frozen workflow/guards without editing/running old
coordinators. Five pure scope/readiness tests precede its use. Pre-peer outgoing
version1 OR2 is allowed only with correct port/baud/budget/mode/flow; the actual
same-owner receiver must verify PX4v2 before logging START. The existing final
controller runtime source was not changed in this trial.

Fresh backups/readback in `coordinator.jsonl`: Disarmed/EV0, IMU IDs, original
startup commands, complete wired nominal stream map, eight SDLOG values, logger
idle, custom config ABSENT, FTP/console SD root. Existing card parameters/logs
were not read/imported/overwritten/deleted. Temporarily:

```text
PX4: mavlink start -d /dev/ttyS2 -b 921600 -r 46080 -m onboard -Z -x
PX4: logger start -b 64 -t -m mavlink -p vehicle_imu
M3C: /dev/ttyS2, 921600, 8N1, raw, no flow control, exclusive single owner
```

`-Z` means flow-off, not forcedv2. Minimal8-topic file166bytes was downloaded back
identically before START. Backend MAVLink-only; no new SD ULog recording or
`logger on`. Standard Onboard telemetry was NOT additionally reduced. Temporary
restart's stream configuration was measured, not assumed to equal original.
M3C actual writes: 7 HEARTBEAT, 1 COMMAND_LONG2510 START, 282 LOGGING_ACK,
1 COMMAND_LONG2511 STOP. No ODOMETRY/setpoint/parameter/flight-command TX.
Received outbound PX4 ODOMETRY telemetry does not constitute Stage C.

## Raw evidence and failure attribution

Raw local evidence: `download/physical-trial-01/` and same relative remote folder.
435 accepted ULog chunks reassembled107784bytes:
`b66b017ab4acbf04a85e76b196f8d98a4752ab885350881c15ab83d9e7505327`.
`wire.jsonl` SHA256:
`f424acde1d4a64a51a441ab6e4bbd4c0f8be171eaf419c4b184d8ffed3a97153`.
Six independently queried remote SHA256 values match local transfers, including
raw wire/prefix/summary/attestation/test log/after-readback. No bytes were repaired.
Both receiver/coordinator exit1 are preserved; cleanup errors[] / acquisition
errors[`receiver exit 1`]. One attempt only, no follow-up capture.

`capture-audit.json` verifies complete stored RX-chunk/decoded-row replay parity.
All3697 retained PX41/1 frames include484 logging frames: post-failure packets
and reliable retries are retained raw, NOT admitted into the435-chunk prefix.
Startup295 unframed bytes are explicitly retained/excluded by pre-START sync;
not a loss-free startup claim. Zero bad-data events AFTER the boundary does not
prove all frames were delivered. Stop ACK/silence does not establish ULog EOF.

Confirmed: logging435 is absent between434 and436. The retained global MAVLink
sequence also jumps34→36 within that interval (logging434 has seq20; logging436
has seq41). Five global discontinuities across the entire retained frame stream
sum to six modulo256 sequence positions; this is NOT an exact sensor-loss count.
The missing globalseq35 is consistent with a whole frame being omitted between
serialization and stored receive evidence, but its contents are unknown. Sender
TX rejection, UART/driver/read loss, scheduling and upstream ulog_stream queue
loss are NOT individually isolated. There is no authenticated per-layer counter
trace. Do not infer electrical wiring failure or sole SD failure from this.

Matching source review:

- [mavlink_ulog.cpp](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_ulog.cpp)
  copies ulog_stream generations and counts discontinuities before sending;
  normal LOGGING_DATA is not retransmitted. Reliable chunks wait/retry for ACK.
- [log_writer_mavlink.cpp](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/logger/log_writer_mavlink.cpp)
  increments logging sequence after publication; reliable writes block the logger
  awaiting ACK; stop discards pending partial chunk. Copied source in `source/`.
- [mavlink_main.cpp](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_main.cpp)
  checks free TX buffer and can reject a send; write failure is another path.
  Reused cached `.maixpy/imu-input-20261010/src__modules__mavlink__mavlink_main.cpp`.
  Saved status txerr0 is a different observation window, not proof no transient
  TX failure. No missing generation/TX-overrun counter trace was captured.

The nominal physical921600/8N1 capacity is92160B/s/direction, software budget
46080B/s and nominal70% ULog share32256B/s; previous200Hz packed-ULog model is
13939.76B/s before health/metadata/telemetry. These models do NOT eliminate queue
or burst pressure. Whole RX324434bytes/9.678155713s gives33522.30B/s across startup,
header, telemetry, normal data and failed-stop tail: NOT steady IMU throughput.
435 accepted packet intervals: median11.161146ms, p9524.377108ms,
p9927.352638ms, max32.097750ms; receipt batching, NOT per-sample/end-to-end latency.

## Diagnostic IMU prefix — not a qualified dataset

`analyze_failure.py` uses only complete retained records in an IN-MEMORY view:
107657bytes, excluding127 trailing partial bytes. Original107784bytes/hash remain
unchanged; no shortened `.ulg` is emitted. Full failed session remains unqualified.
Existing pinned-schema/units/integral audit is reused, not a new OpenVINS exporter.

- 513 instance0 BMI088 records; both hardware IDs stable. Calibration counters1/1
  remain stable; clipping masks0/0; finite delta vectors and positive intervals.
- Source timestamp_sample span2.606488s; strictly increasing, zero duplicates or
  backwards timestamps; effective196.432901Hz, median4508us, maximum15023us,
  13 intervals>1.5×median. These include variable integration duration, not13
  proven missing IMU messages. Publication ordering also valid.
- Gyro retained coverage residual (`next sample end - prior end - next dt`) has
  two>2us gaps, sum13520us/max9013us. This exposes incomplete retained integral
  coverage, NOT exact ADC sample loss or isolation of source vs subscription loss.
  These gaps occur within the retained contiguous logging0..434 prefix, before
  the terminal logging435 loss; fixing that wire loss alone would not prove
  complete source/subscription coverage.
- Gyro dt median4508us/max10561us; accel dt median4992us/max8738us. Different dt
  and unknown separate accel endpoint must be retained; do not zip/retime them.
- Delta units rad and m/s, dt/us; dividing by each own dt gives diagnostic means
  rad/s and m/s², NOT equivalent instantaneous OpenVINS samples. No bias/noise/
  extrinsic/temporal calibration or model acceptance follows from decoding.
- Publication minus gyro-end median225us, p954697.8us/max4774us on the SAME FC
  clock, not measured PX4→M3C/camera latency. No clock mapping/synchronization.
- Zero ULogO events in this prefix does NOT refute wire435 loss or coverage gaps.
  Two retained cpuload samples0.52908/0.53344 do not qualify CPU/latency.
  M3C `/proc` sampler arrived after exit (`receiver_alive=false`): receiver CPU
  NOT_MEASURED. No30s midpoint because acquisition failed early.
- Fresh one-second uorb snapshots199Hz before /198Hz after are snapshots only;
  original≥200Hz requirement is NOT relaxed. Driver error counts1 before/after,
  not zero; perf reset on logger start prevents cumulative-difference claims.

## Restoration and safety

Independent `verify_evidence.py` → `verification.json`, final Pythonexit0:
PX4 exact original startup commands restored, UART115200/budget5760/Onboard/
flowOFF, complete nominal stream map identical, logger`start -b 64 -t -m all`
idle187 subscriptions; all eight SDLOG values unchanged. Only our166-byte topic
file and two newly-created empty directories removed; contents recoverable from
`topics-readback.txt`/old topics.txt. SD original files remain. Unrelated UART
commands unchanged; flow/ToF port still receives compid88/msgids132/106~48Hz.
M3C exact pretrial termios restored, no process/UART owner remains; do not invent
its saved termios baud from the PX4 baseline.

228 observed USB heartbeat base_mode29, fresh commanderDisarmed/EV0 and retained
armedfalse/arming_state1; no arming commands. Prop removal USER_CONFIRMED earlier
in this same bench session, not a new visual inspection. Gaps limit continuous
log-only claims. No parameters/firmware/wiring/sensor-rate/fusion/camera changes.

Fresh9 offline scope/analysis tests PASS, zero skips, Pythonexit0; TDDRED logs
retained. Independent verifier checks18 original trial/37 aborted preparation/
44 prior offline task/14 frozen reassembly artifacts and StageA/B unchanged.
Earlier root226/54 regression results are historical final-software evidence,
not rerun/claimed new here. StageA/B report SHA:
`d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f`.

Helper issues preserved: first read-only helper refused an unsupported read
command BEFORE serial open; corrected read-only query succeeded. Initial offline
verifier treated "skipped" in a test NAME as a skip, then encountered a BOM in
an old manifest; fixed result-marker/utf-8-sig handling and third verifier exit0.
No physical retry. Tar future-mtime warnings were not clock synchronization.
PowerShell native-stderr decoration is not a Python failure when explicit exit0.

## Next boundary

Do not rerun this coordinator/launch/board_test: no-overwrite single-use artifacts.
Next OFFLINE: correlate this exact raw gap with sender generation/TX paths and
plan explicit per-layer counters, receiver UART overrun/CPU sampling from start,
and telemetry burst budget. Do not silently drop/reconstruct packets or lower
thresholds. Root cause cannot be confirmed from this evidence alone. A future
separately authorized bounded trial may compare reduced nonessential telemetry
with the same source/rates; it must restore baseline and instrument counters.
No current authorization for that additional capture/settings change.

VIO-S0/P PARTIAL; high-rate receive gate failed, full Stage C CLOSED. Clock,
calibration and integral-observation-model prerequisites remain. Root reports
updated additively; previous manifests remain historical. No commit/staging/push
or Vault access; VAULT_UPDATE.md is a local proposal only.
