# Single-UART startup diagnosis — 2026-10-11

## Follow-up — approved offline fix

`../imu-startup-fix-20261011/VALIDATION.md` records the subsequent implementation
and tests. Everything below is the retained PRE-FIX diagnosis. The original
reproduce.py expects that older controller; use the new verify.py and preserved
baseline/session.py for legacy/current comparison. No new physical trial or
retroactive PASS; original trial evidence remains unchanged.

## Outcome

**Software startup-boundary limitation VERIFIED; physical byte origin UNKNOWN;
high-rate acquisition still FAILED BEFORE START. No implementation fix.**
This is offline diagnosis of the completed trial, not another device test.
VIO-S0/VIO-P remain PARTIAL; Stage A/B unchanged; Stage C not started.

Baseline: main `3ea1e16086965176db68b88e1c42990f92c5913e`, with existing
uncommitted controller/docs and unrelated `tests/camera_capture.py` / `tmp/`.
No UART, SSH, PX4/M3C access, settings, dependencies, firmware or wiring changes.
No external research needed: saved raw wire, current tested sources and local
pymavlink2.4.49 implementation directly reproduce the abort. Vault not accessed.

## Confirmed observations

- The preserved trial has one21-byte RX chunk, no receiver TX, no LOGGING_START,
  and zero IMU/ULog records. All18 original `hashes.json` entries still match.
- Raw `f93bfeffa6ffffff80e0fd885c91fc3452fdffe7d5` reproduces `Bad prefix`
  for **only the first two bytes `f9 3b`**. The remaining19 bytes are buffered;
  the whole21 bytes were NOT conclusively decoded as invalid/corrupt packets.
- `fe ff` is treated as a candidate MAVLink1 header with payload length255,
  requiring263 total bytes. The parser has not checked its CRC or established
  its actual type/source. Appending one complete synthetic MAVLink2 heartbeat
  still leaves the parser waiting on that candidate.
- `Controller.feed_wire()` aborts on any `bad_data`, including in
  WAIT_HEARTBEAT. Once DONE, later valid frames cannot revive it. This is the
  direct, reproduced software reason why this attempt ended before START.
- All20 legal split positions **from a known heartbeat frame start** work.
  All20 attachment positions **inside an already-running valid heartbeat**, with
  a complete valid heartbeat following the tail, fail before TX. The decoder
  actually finds that following heartbeat, but the controller vetoes the whole
  read because of the leading tail. Thus this is not generic split-read failure.
- The prior PTY peer waits for `uart_opened` and then begins with a complete
  heartbeat. That tested clean startup, not attachment to a continuously
  transmitting physical stream. Its55 passes remain valid for that scope.
- Real trial launch order was PX4 restart at921600, USB status readback,
  attestation transfer, then M3C receiver opening/changing termios. Old M3C speed
  fields13 denote B9600, and input was not flushed. Queued earlier bytes,
  baud-transition reception and late frame attachment are plausible, **not
  separately proven causes**. The coordinator lacks cross-device timestamps
  sufficient to classify the first bytes as old versus new reception.

## Offline checks executed

```powershell
.maixpy/imu-offline-20261008/venv/Scripts/python.exe .maixpy/imu-startup-diagnosis-20261011/reproduce.py
.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py'
```

Reproducer exit0: saved-byte parity/terminal failure,18 immutable hashes,
20 clean splits,20 late attachments, false-prefix buffering, armed/same-read
armed refusal and post-START bad-data STOP behavior checked. Output is retained
in `reproduction.txt`; all synthetic cases are labeled, not hardware PASS.
Existing suite:55 tests run,53 pass,2 POSIX PTY skips on Windows, no failures.
M3C's previously completed55/zero-skip result was not rerun this turn.

First exploratory inline replay failed with ModuleNotFoundError for imu_input:
the reassembler imports it dynamically, not into that import search path.
Corrected only the diagnostic import path; no application edits or installs.

## Proposed next change — NOT IMPLEMENTED

Add a distinct **bounded pre-START synchronization phase**, preserving every RX
byte and rejected/incomplete candidate in evidence. Locate complete
CRC-verified unsigned MAVLink2 PX41/1 heartbeat frames, reject armed/identity
mismatch, and require freshness before any START/TX. Keep deadline/byte limits.
Only locating `fd`/`fe`, ignoring every Bad prefix, or blindly flushing is
insufficient: payload bytes can resemble frame headers and hide later frames.
Do not reinterpret startup bytes as measured packet/sample loss or certify a
loss-free startup interval. After START intent, retain current strict abort,
source/sequence/CRC/heartbeat checks and bounded STOP/restoration.

This changes the controller's fail-closed startup boundary and needs an explicit
reviewed decision before implementation, rather than silently removing a guard.
Add regressions for saved21-byte input, false headers, late attachment, clean
split reads, wrong-source/armed/stale heartbeat, corruption after START, limits
and exact restoration. Then repeat virtual PTY with a peer already transmitting
before receiver open. Any later physical retry requires separate approval.

**No physical action is needed now.** The first chunk alone cannot verify or
disprove electrical921600 support, wiring, sustainable throughput, logger loss,
sensor completeness, synchronization or OpenVINS suitability. Selected BMI088
193Hz snapshot and integrated-measurement contract remain separate unresolved
gates even after a future transport fix.

Original trial files/manifests and controller logic untouched. Added only this
diagnosis/reproducer/output and additive report pointers. No commit/push.
Rollback only this dated diagnosis directory and its additive documentation,
not the preserved hardware evidence or user work.
