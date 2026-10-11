# PX4 disarmed offline FIFO validation

Authorization: user approved short disarmed capture, logging-only changes,
backup/restore. User explicitly confirmed all propellers removed. No arming,
firmware, flight-control params, camera calibration, M3C or live streaming.

Baseline: COM19 PX4 heartbeat base_mode29 (armed bit clear), commander Disarmed.
logger idle, process `logger start -b 64 -t`; SDLOG profile1/mode0/boot_bat0,
dirs_max0/mission0/utc_offset0/uuid1. Custom logging path absent. BMI270 selected
gyro/accel device3604506, instance1. Evidence: identity-before.txt,
preflight-backup.txt. Existing research worktree dirty state preserved.

1. Test command/path authorization and fresh disarmed heartbeat guards before
   using a bounded console/FTP helper. Existing pymavlink FTP library reused.
2. Back up runtime/params and confirm custom file absent via FTP/console. Write
   only the temporary logger topic file; verify round-trip bytes. No params set.
3. Stop idle logger, restart with existing64KiB buffer/date naming plus2500Hz
   reader. Custom list contains BMI270 FIFO/SI/health and arming evidence. Start
   recording using logger-only override for15sec, then stop in finally. Monitor
   FC heartbeat disarmed; never send an arm command. Restore config even on error.
4. Download exact new ULog, verify remote CRC/local hash and parse using isolated
   pyulog research dependency if unavailable. Report IDs, units, timestamp order,
   effective rates, FIFO batches, time gaps, dropouts, clipping/errors and arming.
   No fabricated missing samples or inferred synchronized camera dataset.
5. Restore original absence of custom list and original `logger start -b64 -t`
   behavior, verify params/status. Preserve original ULog and failed attempts.
6. Update research audit/contract/status/handoff; VIO-P remains PARTIAL. No push.

Stop conditions: armed/missing stale heartbeat, changed identity/selection,
unbacked existing config, logger already recording, failed restoration. Keep
original evidence and report unresolved issues instead of forcing PASS.
