# Bounded startup synchronization implementation plan

**Goal:** implement the pre-START boundary proposed in the preceding diagnosis
and approved by the user's "ok do it"; no physical retry is included.
**Architecture:** a small startup-only candidate scanner reuses pymavlink's
complete-frame CRC decoder. It retains evidence and skips headers only when
their flags/known lengths disprove them. Plausible incomplete headers/bodies
are barriers, not permission to scan payload. The existing decoder/controller owns every byte after the first
CRC-valid PX4 heartbeat candidate; existing identity/armed gates still decide TX.
**Tech stack:** existing Python/pymavlink2.4.49/pyulog1.2.4; no new dependencies.

## Constraints / reviewed decision

Baseline main3ea1e16 and dirty controller/docs retained, no Vault access.
The approved design changes only pre-START treatment of unframed bytes. No
arming/fusion/parameter/baud/logger/wiring changes, no capture/commit/push.
Use5s initial deadline and65536 total pre-boundary bytes; bound buffered memory
by one maximum MAVLink frame (280 bytes), after each feed, plus one read chunk.
Preserve RX chunks, unframed regions, source offsets and the candidate boundary.
CRC is framing integrity, NOT authenticated identity or fresh physical sample
evidence. Startup bytes/timing are excluded from any logging completeness claim.

Alternatives: blind flush loses provenance and does not prevent mid-frame
attachment; ignoring all BAD_DATA lets false length prefixes hide heartbeats and
weakens post-START checks. Neither is chosen. A bounded scan of complete known
CRC-valid frames is chosen, with unchanged strict decoder after the boundary.
Plausible complete candidates, including unknown IDs and bad CRC, are consumed
whole; never scan inside their payloads. Plausible noise may delay or time out. A
wrong-source heartbeat cannot start; known PX4 signed/v1/wrong identity/armed
heartbeats fail closed. Same-read later faults veto queued START as before.

No second approval loop for the already approved offline change. Work inline in
the user's existing tree; no branch/worktree/history mutation or implementation
delegation. One read-only independent code review checked the changed safety gate.

## Tasks (TDD; exact commands use the existing research Python)

- [x] Create controller/test_startup_sync.py with regressions for the saved21
  bytes plus explicit synthetic opaque-body completion and a later heartbeat,
  all20 late attachments and clean splits,
  false lengths, wrong-source/signed/v1/armed/identity, same-read faults,
  deadline/byte cap, post-boundary CRC failure, and preserved evidence.
  Minimal intended assertion:
  ```python
  c = Controller(0)
  assert c.feed_wire(saved_21_bytes, 0) == [] and c.error is None
  assert c.feed_wire(synthetic_tail + heartbeat(), 100_000_000) and c.state == 'STARTING'
  ```
  Run `python -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p test_startup_sync.py -v`
  and retain the expected failures before modifying code.
- [x] Create controller/startup_sync.py and integrate it only in Controller's
  WAIT_HEARTBEAT path. Interface `StartupSync.feed(bytes, receipt_ns)` returns
  evidence/frame rows; `complete`, `received_bytes`, `excluded_bytes` record the
  boundary. On transition feed residual bytes to the existing Decoder, not a
  new stream protocol. Extend summary with policy version/counters. Run the same
  tests and all existing controller tests, preserving safety expectations.
- [x] Extend capture_report.py to replay the versioned startup classification
  independently, compare raw-to-event parity, and exclude startup-unframed rows
  only from ULog framing. Legacy captures retain their original Decoder behavior.
  Test successful synthetic capture with startup garbage and tampered evidence.
- [x] Add POSIX PTY cases where bytes exist before UART open; ensure parser sync,
  START/ACK/STOP roundtrip, armed refusal and exact termios restoration. Run on
  an isolated Linux research-host directory, never a physical device.
- [x] Run existing reassembly/decoder/integral/model tests, saved-byte replay and
  root pytest. Verify original trial18 hashes, StageA/B and frozen source evidence.
  Update versioned validation, RUNBOOK, LATEST, HANDOFF and VAULT_UPDATE proposal.
  Commit/push deliberately omitted; rollback only the bounded diff/snapshots.

Plan review: no new IMU model, no relaxed sample/rate criteria, no clock mapping,
no overwrite of original failed-trial files. Virtual PTY cannot qualify921600.

## Review-driven acceptance refinement (completed)

The first scanner searched inside an incomplete valid outer packet; the review
reproduction failed before correction (review-red.txt / review-red-02.txt).
The final test uses an untruncated267-byte LOGGING_DATA with an embedded heartbeat
and checks all266 split positions without TX. Unknown and CRC-rejected candidates
are also consumed whole, rather than scanning their payloads.

This deliberately narrows the original minimal saved21 + one heartbeat assertion:
the actual saved FE header has UNKNOWN msgid255/length255, not a known impossible
length. Its263-byte opaque candidate must finish before looking for a later
heartbeat. The saved21 bytes plus one heartbeat still wait then time out. Fixture
completion bytes are explicitly SYNTHETIC, never attributed to the failed capture.
Continuous-peer PTY tests exercise conservative delay without physical evidence.
The5s feed/tick deadline is an acquisition deadline, not a CPU-latency bound.
Summary counter/types and missing-policy downgrade are independently audited.
