# Single-UART session controller implementation — 2026-10-11

Goal: implement the already agreed start/ACK/stop/timeout/restore boundary around
the existing finite ULog reassembler. This is an offline software task, not approval
to change PX4/M3C baud, logger settings, firmware, parameters or wiring.

Baseline: main `3ea1e16086965176db68b88e1c42990f92c5913e`; unrelated
`tests/camera_capture.py` and `tmp/` retained. No repo AGENTS file found on the
applicable ancestor chain. Personal working agreements apply. No Vault access.

## Design and decisions

Reuse `../reassembly/ulog_mavlink.py` and the saved `imu_input.Decoder`. One owner
decodes incoming bytes and schedules outgoing MAVLink2 HEARTBEAT, LOGGING_START,
LOGGING_ACK and LOGGING_STOP only (source1/191, PX4 target1/1). No ODOMETRY,
PARAM_SET, setpoint, shell or automated configuration messages. The alternative
of independent readers/writers loses parser/sequence ownership; custom firmware
is unnecessary for this acquisition prototype. Existing measured/semantic gates
remain unchanged. User's current instruction accepts this previously presented
implementation boundary; no new architecture/approval loop is needed offline.

States: WAIT_HEARTBEAT -> STARTING -> RECEIVING -> STOPPING -> DONE.
Start needs a fresh unsigned PX4 heartbeat, accepted start command and first
unACKed data packet. Reliable header packets are ACKed immediately and identical
retries are idempotent. Capture duration starts at normal-data transition, not
at process launch. Start is never retried automatically. Failure/cancellation
after a start attempt sends only one best-effort stop, with a bounded cleanup
window. STOP IN_PROGRESS is not STOP ACCEPTED; silence is not an EOF.

Finishing a well-framed prefix does NOT prove all source data or terminal packets
arrived. Pinned writer `stop_log()` discards a partial chunk; record tail/source
completeness UNKNOWN even after accepted STOP. Keep partial raw bytes, every RX/TX
wire byte, receipt monotonic time, ACK intents, errors and exact serial restoration.
No interpolation or OpenVINS admission. External PX4 configuration backup/apply/
restore stays with independent USB control and is not implemented by this UART owner.

Linux UART ownership: reuse owners/fresh_disarmed helpers; refuse system console
and busy port, O_NOCTTY/O_NONBLOCK + TIOCEXCL. Save termios, only apply approved
settings, read back, restore in finally and verify; close even on restore failure.
No unbounded drain/write or startup input flush. Windows tests use an explicit
in-memory wire peer and platform syscall doubles; PTY tests skip when unavailable.

## Implementation / verification plan

- [x] Add failing tests in `test_session.py`: safe wire allowlist, ordered start,
  ACK/retry, stale/armed heartbeat, source/route/CRC/gap, accepted/rejected/progress
  commands, bounded startup/data/cleanup, stop/tail uncertainty and finite output.
- [x] Add `session.py` using `Controller.feed_wire(bytes, receipt_ns)` and
  `Controller.tick(now_ns)`; return wire intents, never open hardware on import.
- [x] Add failing runner/ownership tests, then `uart_session.py`: sole UART owner,
  evidence/no-overwrite, exact termios restoration, cancellation and partial writes.
  CLI requires explicit trial approval and fresh external preflight; no live launch.
- [x] Run new tests, reassembler/diagnostic/decoder regressions, saved real-byte
  replay and root pytest using the existing research Python environment.
- [x] Update VALIDATION, existing LATEST/resume, HANDOFF and VAULT_UPDATE proposal;
  review diffs, preserve Stage A/B hash and frozen reassembly manifest.

Commands use `.maixpy/imu-offline-20261008/venv/Scripts/python.exe`:

```powershell
python -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
python -m unittest discover -s .maixpy/imu-design-20261010/single-uart/reassembly -p test_ulog_mavlink.py -v
python -m pytest -q tests --ignore=tests/camera_capture.py
```

TDD red/green output is retained locally. Rollback only these new controller files
and additive documentation relative to the baseline; do not erase historical tests,
raw evidence or user files. No commit/push requested in this development turn.
