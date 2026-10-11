# PX4 to M3C single-UART trial — 2026-10-11

## Result: acquisition FAILED BEFORE START; restoration VERIFIED

User approved one bounded60-second921600baud/46080B/s transport trial with
propellers removed and disarmed. The receiver aborted on its first21-byte read,
before transmitting any heartbeat/LOGGING_START/ACK/STOP. Thus the requested
60-second recording interval never began. Zero ULog packets, zero IMU records,
zero reassembled bytes; no framing-valid.ulg was produced. No automatic retry.
VIO-S0 and VIO-P remain PARTIAL. This does not qualify physical UART throughput,
loss-free IMU transport, camera synchronization or an OpenVINS observation model.

## Actual preparation and source evidence

Independent Windows COM19 USB CDC inspection, not a physical UART baud claim.
PX4 MICOAIR_H743_V2 Release1.17.0 full hash
`d6f12ad1c4f70ad3230afd7d86e971421e02fef4`. Commander Disarmed; EV_CTRL0.
Selected BMI088 vehicle_imu0: gyro6684690, accel6946834. Fresh one-second uORB
snapshot193Hz for instance0 (194Hz instance1); below the unchanged strict200Hz
criterion. Before/after imu_status error counters1/1, clips0; not proof of a
loss-free capture. Raw rate estimates~1997Hz gyro/~1602Hz accel are not the
vehicle_imu publication or UART receive rate. CPU snapshots0.50098 then0.51470
are outside an accepted logging interval and are not streaming load measurements.

Actual original commands backed up in coordinator.jsonl and backup-readonly.txt:

```
mavlink start -d /dev/ttyS2 -b p:SER_GPS1_BAUD -m p:MAV_1_MODE -r p:MAV_1_RATE -s -x
logger start -b 64 -t -m all
```

Successful FTP root listing plus console listing established original absence
of /fs/microsd/etc. Created only our two temporary directories and166-byte topic
file, uploaded/read back with identical bytes. Logger reported8 subscriptions,
mavlink mode and idle. Temporary scoped startup:

```
mavlink start -d /dev/ttyS2 -b 921600 -r 46080 -m onboard -Z -x
logger start -b 64 -t -m mavlink -p vehicle_imu
```

USB readback confirmed baud921600, max46080B/s, Onboard, flowOFF. Only the wired
PX4 instance was restarted. Other UARTs, including flow/ToF ttyS3, preserved.
No PARAM_SET/save, firmware, wiring, arming, camera/calibration or ODOMETRY sent.
Propeller removal is user-confirmed, not remotely observable.

## Receiver evidence and diagnostic limits

M3C maixcam2-9d05, isolated deployment
`/root/rm27-controller-pty-20261011.zUIWou/physical-trial-01`.
`physical-trial-01/wire.jsonl` records exclusive real /dev/ttyS2 at9216008N1,
raw/no-flow with readback and input_flushed=false. Old termios speed fields13
correspond to B9600, not an established application-owned baud. First read:

```
f93bfeffa6ffffff80e0fd885c91fc3452fdffe7d5
```

Parser produced Bad prefix for f93b; strict controller immediately aborted.
summary.json: error='invalid MAVLink data: Bad prefix', start_accepted=false,
termios_restored=true. capture-report.json independently reproduces the decode:
wire_received_bytes21, bad_data_events1, tx_write_calls0,
imu_status=NOT_PARSED_FAILED_SESSION. Received-prefix.bin is empty, SHA256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
This proves startup framing failure, NOT wrong wiring, electrical corruption,
unsupported921600 or sensor/logger loss. Pre-change queued bytes and attachment
mid-frame are candidates, not dynamically isolated causes. No resync/filtering,
flush, synthetic samples, retiming or repaired ULog used to conceal the failure.
FC and camera clock mapping and source/tail completeness remain UNKNOWN.

## Restoration and evidence integrity

Stopped temporary idle logger, removed only our topic file and two newly-created
empty directories; their contents remain in topics.txt/readback. Restored exact
original logger and parameter-referencing UART startup commands, then all backed
finite stream rates. Configured stream mapping equals original, checked by
verify_evidence.py. All eight SDLOG scalar readbacks identical. UART3 is115200,
flow/ToF port remains115200. Fresh final-readonly.txt confirms root etc absent,
logger idle/all, Disarmed, EV_CTRL0. M3C termios restored and no receiver remains.
Original SD logs retained; no new SD ULog was requested.

Logger subscriptions180->187 after restart: configuration restored, NOT an
identical runtime subscription snapshot; optional topic differences not isolated.
Coordinator's outer exit0 denotes its caught-error/cleanup bookkeeping, not
acquisition PASS: receiver_exit1 is explicit. Do not use this one-off coordinator
exit code as an acquisition gate or rerun it. Exclusive evidence paths prevent
accidental reuse. `hashes.json` fingerprints preserved source/config/wire/report
files; no claim of hardware source counters or end-to-end latency.

Fresh verification command:

```
.maixpy/imu-offline-20261008/venv/Scripts/python.exe .maixpy/imu-uart-trial-20261011/verify_evidence.py
RESTORATION VERIFIED; ACQUISITION FAILED BEFORE START; NO RETRY
```

## Next work (not executed)

Offline diagnosis of startup framing and bounded synchronization using the saved
21 bytes and synthetic partial-frame tests; retain fresh/disarmed gates and
strict validation after any startup boundary. A revised physical trial needs
separate approval. No physical action is needed now; do not change wiring on
this evidence. Existing integrated vehicle_imu versus raw-point contract and
193Hz publication limitations remain even if a later transport test succeeds.
No commit/push or Vault modification.
