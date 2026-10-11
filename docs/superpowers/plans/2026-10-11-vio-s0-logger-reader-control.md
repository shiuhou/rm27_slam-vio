# VIO-S0 Logger Reader Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test whether fixed-frequency logger reading avoids the observed `vehicle_imu` subscription skip, without conflating that result with source-rate or OpenVINS qualification.

**Architecture:** Reuse the existing single-UART controller, reduced-telemetry coordinator, framing audit and integral-semantic analysis. First prepare/test a narrow reader-profile guard and comparison offline; then, only with approval, perform ONE 60 s physical control with `-r 2500` instead of `-p vehicle_imu`. Keep the publisher, topic bytes and transport treatment unchanged.

**Tech Stack:** Existing Python research venv/pymavlink/pyulog/unittest; M3C Linux POSIX UART; exact PX4 v1.17.0 source `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`.

## Global Constraints

- PLAN READY, NOT IMPLEMENTED OR EXECUTED. This planning turn accesses no devices or SSH.
- Execute inline using executing-plans; no delegation is needed for this bounded change.
- Keep Disarmed, propellers removed and `EKF2_EV_CTRL=0`; no ARM, setpoints, fusion or flight.
- No firmware, parameters, IMU selection/rate, wiring, camera, calibration or full Stage C changes.
- Physical authorization must explicitly cover this ONE trial's temporary UART/logger/telemetry settings. Previous completed-trial approval is consumed; planning is not approval.
- No automatic retry, baud escalation, additional captures, dependency installation, commit, push or Vault access.
- Original source-rate gate remains **>=200 Hz**; do not round 197 Hz into PASS, interpolate, retime or fill gaps.
- `vehicle_imu` contains calibrated/coning-corrected integrals, not instantaneous/raw sensor samples. Diagnostic means are not automatically OpenVINS input.
- Preserve Stage A/B PASS and all historical artifacts. Old BMI270/v1.15.2 evidence is not a BMI088 baseline or restore target.
- Restore fresh backed-up settings, never a historical parameter file. Abort before mutation if the baseline differs from the bounded proposal.

## Baseline and hypothesis

Working-tree main HEAD: `3ea1e16086965176db68b88e1c42990f92c5913e`; already dirty, with no staged changes. Latest evidence:

- `.maixpy/imu-source-diagnosis-20261011/DIAGNOSIS.md` and `analysis.json`: 11,843 selected BMI0880 integrals, **197.215284 Hz**, ONE **4554 us** gyro coverage hole.
- Logger `message_gaps` increases 1->2 across the hole's publication bracket. Only `vehicle_imu0` is full-rate in the custom list. Subscription generation skip is confirmed; the precise logger/Run scheduling trigger is UNKNOWN.
- `.maixpy/imu-uart-reduced-trial-20261011/RESULT.md`: 60 s bounded transport comparison, zero observed global/logging sequence gaps or send rejections. This does not certify source/tail/clock completeness.
- Source cadence also contains longer, fully covered integration windows; one missing integral cannot explain ~197.2 Hz. Accel coverage lacks an independent endpoint.
- Exact `logger.cpp:269-276,665-685,900-935`: `-r 2500`, with NO `-p`, selects a requested 400 us HRT/semaphore wake interval. It does not promise an actual 400 us loop or change sensor/publication frequency.

Hypothesis: fixed reader wakeups may reduce queue-depth-1 overwrites associated with the separate poll cursor. This is a hypothesis, not a proven root-cause fix; extra CPU load or bursts could instead worsen results.

| Factor | Previous retained control | Proposed candidate |
|---|---|---|
| Logger reader | `-p vehicle_imu` | **`-r 2500`, no `-p`** |
| Logger/backend | `-b 64 -t -m mavlink` | Same; MAVLink-only, no SD recording |
| Topic file | Existing 166-byte eight-topic file | Byte-identical readback |
| Source | BMI0880 gyro6684690/accel6946834 | Same, freshly verified |
| Transport | Temporary921600,46080 B/s,Onboard | Same temporary settings |
| Telemetry | Reduced nonessential numerical streams | Same exact treatment/readback |
| Receiver/measurement | Single-owner controller,60 s target,CPU/UART counters | Same algorithms and observation cadence |

`-b 64` is not an enlarged MAVLink/UART ring. The old control is reused, not recaptured. Since trials occur at different times, even a successful candidate is a bounded comparison, not definitive timing causality.

## File map and reusable interfaces

Modify ONLY the profile validator in `.maixpy/imu-design-20261010/single-uart/controller/uart_session.py`. Leave its legacy CLI defaults, `OwnedUART`, controller, framing, ACK/STOP and safety logic unchanged.

Create under `.maixpy/imu-reader-control-20261011/`:

- `test_reader_profile.py`: explicit reader-mode/type/command-scope tests.
- `coordinator.py`: isolated adaptation of the frozen reduced-trial coordinator; independent USB configuration and finally-restoration.
- `receive.py`: isolated adaptation of the frozen reduced-trial receiver; honest fixed-reader attestation, same-owned-FD counters.
- `compare.py`, `test_compare.py`: pure saved-row comparison reusing the existing integral/counter functions.
- `PLAN.md`, `RESULT.md`, `HANDOFF.md`, generated `verification.json`/`manifest.json`: scope, observed results and provenance, not planned PASS.

At execution time, use a new exclusive-output deployment/capture directory and new metadata/log filenames. Reuse frozen `trial_tools.py`, `monitor.py`, `launch.py`, `stop.py` and portable helper snapshots in the isolated deployment; do not edit historical folders or create another transport framework.

Existing APIs:

- `uart_session.validate_preflight(row, now_ns, *, negotiate_mavlink2=False)`; narrow additive profile keyword below.
- `uart_session.run_session(port, output, *, seconds=60, clock=..., preflight=None, negotiate_mavlink2=False)`; unchanged.
- `trial_tools.check_command(line, original_uart, original_logger, original_streams, changes)`, `treatment(table)`, `stream_table(text)`, `uart_counters(fd)`; frozen helpers.
- `capture_report.audit_capture(directory, epoch=...)`, `inspect_imu(raw, instance=0, gyro_device=6684690, accel_device=6946834, epoch=...)` and `ulog_mavlink.validate_ulog(raw)`; unchanged.
- `diagnosis.cadence(rows)` and `correlate(holes, statuses, full_rate_topics)` from the latest diagnosis; pure helpers. Its `analyze(path)` pins the OLD raw SHA: **do not use it on a new capture**.

### Task 1: Offline profile guard and narrow experiment wrapper

**Files:** validator above; new `test_reader_profile.py`, `coordinator.py`, `receive.py`.

**Interfaces:** Add `logger_reader='poll_vehicle_imu'` to `validate_preflight`; allowed explicit alternate is `'fixed_2500hz'`. The new coordinator exports the same five-argument `check_command` API as trial_tools.

- [ ] Save original affected runtime bytes/hashes and Git state into the NEW experiment's `repo-before`; retain the existing manifests. Never stage unrelated edits.
- [ ] Write the following failing profile tests before editing the validator. Put the new test file in the experiment folder; its path setup is repo-relative and imports do not launch a device:

```python
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                     'imu-design-20261010/single-uart/controller'))
import uart_session as u

def legacy():
    return dict(firmware_hash=u.EXPECTED_HASH, ekf2_ev_ctrl=0, disarmed=True,
        propellers_removed=True, uart='/dev/ttyS2', baud=921600,
        mavlink_datarate=46080, gyro_device_id=6684690, accel_device_id=6946834,
        vehicle_imu_instance=0, logger_backend='mavlink', logger_poll='vehicle_imu',
        configuration_backup_verified=True, heartbeat_negotiation_approved=True,
        prepared_m3c_monotonic_ns=1_000_000_000)

def fixed():
    return dict(legacy(), logger_poll=None, logger_rate_hz=2500,
                logger_reader='fixed_2500hz')

class ReaderProfileTests(unittest.TestCase):
    def test_legacy_default_still_valid(self):
        u.validate_preflight(legacy(), 2_000_000_000)
    def test_fixed_requires_explicit_profile(self):
        with self.assertRaises(ValueError):
            u.validate_preflight(fixed(), 2_000_000_000)
        u.validate_preflight(fixed(), 2_000_000_000,
                             logger_reader='fixed_2500hz')
    def test_ambiguous_and_changed_settings_rejected(self):
        for changes in ({'logger_poll':'vehicle_imu'}, {'logger_rate_hz':True},
            {'logger_rate_hz':2499}, {'logger_reader':'poll_vehicle_imu'},
            {'disarmed':False}, {'ekf2_ev_ctrl':1}, {'baud':115200},
            {'gyro_device_id':3604506}, {'configuration_backup_verified':False}):
            with self.assertRaises(ValueError):
                u.validate_preflight(dict(fixed(), **changes), 2_000_000_000,
                                     logger_reader='fixed_2500hz')
        with self.assertRaises(ValueError):
            u.validate_preflight(dict(legacy(), logger_rate_hz=2500), 2_000_000_000)
    def test_unknown_profile_and_stale_attestation_rejected(self):
        with self.assertRaises(ValueError):
            u.validate_preflight(fixed(), 2_000_000_000, logger_reader='arbitrary')
        with self.assertRaises(ValueError):
            u.validate_preflight(fixed(), 70_000_000_000,
                                 logger_reader='fixed_2500hz')
```

- [ ] Run RED: `.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-reader-control-20261011 -p test_reader_profile.py -v`. Expect the explicit fixed-profile test to fail on the missing keyword; preserve actual output, not a simulated result.
- [ ] Apply ONLY this validator change. Retain the original identity/type checks, heartbeat approval and same-M3C freshness checks:

```diff
-def validate_preflight(row, now_ns, *, negotiate_mavlink2=False):
+def validate_preflight(row, now_ns, *, negotiate_mavlink2=False,
+                       logger_reader='poll_vehicle_imu'):
@@
-        logger_backend='mavlink',logger_poll='vehicle_imu',configuration_backup_verified=True)
+        logger_backend='mavlink',configuration_backup_verified=True)
+    if logger_reader == 'poll_vehicle_imu':
+        if 'logger_rate_hz' in row:
+            raise ValueError('mixed poll/rate reader attestation')
+        expected.update(logger_poll='vehicle_imu')
+    elif logger_reader == 'fixed_2500hz':
+        expected.update(logger_poll=None, logger_rate_hz=2500,
+                        logger_reader='fixed_2500hz')
+    else:
+        raise ValueError('unapproved logger reader profile')
```

- [ ] Create the new coordinator using the frozen reduced-trial contents, with ONLY these specified adaptations: import trial_tools from the frozen sibling folder locally; change `HERE`-scoped outputs to the new folder; read a NEW `deployment.json` rather than the historical hardcoded remote directory; use the new command and allowlist below; set the fixed-reader attestation fields; change experimental_factor to `LOGGER_READER_FIXED_2500HZ`. Keep setup, telemetry treatment, monitoring cadence and finally-restoration intact. Add a `--trial-approved` flag checked before any Link/SSH; the flag alone is not authorization.

```python
# New coordinator's profile-specific definitions; c/t are the existing helpers.
LOGGER = 'logger start -b 64 -t -m mavlink -r 2500'

def check_command(line, original_uart, original_logger, original_streams, changes):
    if line == LOGGER:
        return
    if line == c.LOGGER:
        raise ValueError('old poll treatment forbidden in fixed-reader trial')
    t.check_command(line, original_uart, original_logger, original_streams, changes)

# Inside main, BEFORE Link/SSH/configuration; import argparse in the new file.
p = argparse.ArgumentParser()
p.add_argument('--trial-approved', action='store_true')
args = p.parse_args()
if not args.trial_approved:
    p.error('one physical trial requires approval; no devices accessed')
REMOTE = json.loads((HERE/'deployment.json').read_text(encoding='utf-8'))['remote']
if not re.fullmatch(r'/root/rm27-controller-reader-20261011\.[A-Za-z0-9]{6}', REMOTE):
    raise ValueError('isolated deployment path differs')
```

Change `cmd` to call this local check_command. In attestation construction replace `logger_poll='vehicle_imu'` with `logger_poll=None, logger_rate_hz=2500, logger_reader='fixed_2500hz'`. The new receiver changes exactly its validator invocation to:

```python
u.validate_preflight(attestation, time.monotonic_ns(), negotiate_mavlink2=True,
                     logger_reader='fixed_2500hz')
```

Do not label a fixed reader as poll mode to bypass the old validator. Preserve the attestation's `OPERATOR_ATTESTATION_NOT_AUTHENTICATED_READBACK` caveat.

- [ ] Add these command-scope tests to test_reader_profile.py; importing the new coordinator must not call main. Keep the test file's existing imports above:

```python
import coordinator as c

class CommandScopeTests(unittest.TestCase):
    def check(self, line):
        c.check_command(line,
            'mavlink start -d /dev/ttyS2 -b p:SER_GPS1_BAUD -m p:MAV_1_MODE -r p:MAV_1_RATE -s -x',
            'logger start -b 64 -t -m all',
            {'HEARTBEAT':1., 'TIMESYNC':10., 'HIGHRES_IMU':50.},
            {'HIGHRES_IMU':0.})
    def test_exact_candidate_restore_and_treatment_allowed(self):
        for line in (c.LOGGER, 'logger start -b 64 -t -m all',
                     'mavlink stream -d /dev/ttyS2 -s HIGHRES_IMU -r 0'):
            self.check(line)
    def test_other_factors_and_unsafe_commands_rejected(self):
        for line in (c.c.LOGGER, 'logger start -b 64 -t -m mavlink -r 5000',
            c.LOGGER+' -p vehicle_imu', 'param set EKF2_EV_CTRL 1', 'param save',
            'commander arm', 'motor_test test', 'offboard start',
            'mavlink stop -d /dev/ttyS3',
            'mavlink stream -d /dev/ttyS2 -s HEARTBEAT -r 0',
            'mavlink stream -d /dev/ttyS2 -s TIMESYNC -r 0'):
            with self.assertRaises(ValueError, msg=line):
                self.check(line)
```

Add these two denial tests. They exercise main without granting authority to open UART:

```python
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'imu-offline-20261008'))
import bench_io

class LaunchGateTests(unittest.TestCase):
    def test_missing_flag_never_constructs_link(self):
        with patch.object(bench_io,'Link',side_effect=AssertionError('device opened')) as link:
            with patch.object(sys,'argv',['coordinator.py']):
                with self.assertRaises(SystemExit) as error:
                    c.main()
            self.assertEqual(error.exception.code,2)
            link.assert_not_called()
    def test_missing_deployment_never_constructs_link(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(c,'HERE',Path(folder)), \
                 patch.object(sys,'argv',['coordinator.py','--trial-approved']), \
                 patch.object(bench_io,'Link',side_effect=AssertionError('device opened')) as link:
                with self.assertRaises(FileNotFoundError):
                    c.main()
                link.assert_not_called()
```
- [ ] Run GREEN with the same command; run the affected existing `test_uart_session.py` suite using `unittest discover` in the controller directory. Save output and real Python exit codes. Existing legacy fixtures must still pass; review that no parser/STOP/OwnedUART logic changed. Review checkpoint, **no commit**.

### Task 2: Offline before/after comparison without altering admission gates

**Files:** new `compare.py`, `test_compare.py`; import frozen diagnosis helpers through importlib with a unique module name and an explicit repo-relative path.

**Interfaces:** `comparison(before_rows, after_rows, after_statuses) -> dict`; rows use the existing original `vehicle_imu` fields/units; statuses use actual logger timestamps/counters, not reconstructed events.

- [ ] Write these complete synthetic-fixture tests in test_compare.py. They are not real synchronized measurements:

```python
import unittest
from compare import comparison

def rows(times=(100000,105100,110200), dts=(5100,5100,5100)):
    return [dict(timestamp=t+200, timestamp_sample=t, delta_angle_dt=dt,
        delta_velocity_dt=5000, gyro_device_id=6684690, accel_device_id=6946834,
        gyro_calibration_count=1, accel_calibration_count=1,
        delta_angle_clipping=0, delta_velocity_clipping=0,
        delta_angle=[0.,0.,0.], delta_velocity=[0.,0.,-.049])
        for t,dt in zip(times,dts)]

def statuses(values=(1,1), times=(99000,121000)):
    return [dict(timestamp=t, message_gaps=g, type=0, backend=2, num_messages=8)
            for t,g in zip(times,values)]

class ComparisonTests(unittest.TestCase):
    def test_no_hole_does_not_make_rate_or_vio_pass(self):
        out=comparison(rows(),rows(),statuses())
        self.assertTrue(out['observed_gyro_continuity'])
        self.assertTrue(out['observed_subscription_continuity'])
        self.assertFalse(out['original_rate_gate_pass'])
        self.assertFalse(out['openvins_admissible'])
        self.assertEqual(out['stage_c'],'CLOSED')
        self.assertEqual(out['accel_coverage'],'UNKNOWN_NO_SEPARATE_ENDPOINT')
    def test_hole_has_current_dt_semantics(self):
        candidate=rows((100000,104500,115017),(4500,4500,5963))
        out=comparison(rows(),candidate,statuses((1,2)))
        self.assertEqual(out['candidate']['uncovered_gyro_us'],4554)
        self.assertFalse(out['observed_gyro_continuity'])
        self.assertEqual(out['candidate_logger']['counter_increment_events'],1)
    def test_changed_epoch_order_or_nonfinite_refused(self):
        for key,value in (('gyro_device_id',3604506),('accel_calibration_count',2),
            ('timestamp_sample',100000),('delta_angle',[float('nan'),0.,0.])):
            candidate=rows();candidate[-1][key]=value
            with self.assertRaises(ValueError):
                comparison(rows(),candidate,statuses())
    def test_counter_reset_missing_evidence_or_wrong_backend_refused(self):
        invalid=[[],statuses()[:1],statuses((2,1))]
        wrong=statuses();wrong[-1]['backend']=3;invalid.append(wrong)
        for sample in invalid:
            with self.assertRaises(ValueError):
                comparison(rows(),rows(),sample)
    def test_hole_outside_counter_bracket_stays_unknown(self):
        candidate=rows((100000,104500,115017),(4500,4500,5963))
        out=comparison(rows(),candidate,statuses((1,2),(99000,103000)))
        self.assertEqual(out['candidate_logger']['holes'][0]['attribution'],'UNKNOWN')
        self.assertFalse(out['openvins_admissible'])
```
- [ ] Run RED with `.maixpy/imu-offline-20261008/venv/Scripts/python.exe -m unittest discover -s .maixpy/imu-reader-control-20261011 -p test_compare.py -v`; preserve actual failure.
- [ ] Add this complete compare.py. It loads existing helpers instead of copying their analysis logic:

```python
import importlib.util
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'imu-source-diagnosis-20261011/diagnosis.py'
spec=importlib.util.spec_from_file_location('reader_control_saved_diagnosis',path)
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

def comparison(before_rows, after_rows, after_statuses):
    if len(after_statuses)<2 or any((s['type'],s['backend'],s['num_messages'])
                                  != (0,2,8) for s in after_statuses):
        raise ValueError('at least two full/MAVLink/eight-topic status records required')
    before = d.cadence(before_rows)
    after = d.cadence(after_rows)
    logger = d.correlate(after['gyro_holes'], after_statuses, ['vehicle_imu'])
    return dict(baseline=before, candidate=after, candidate_logger=logger,
        logger_observation_span_us=after_statuses[-1]['timestamp']-after_statuses[0]['timestamp'],
        logger_counter_window=[after_statuses[0]['timestamp'],after_statuses[-1]['timestamp']],
        observed_gyro_continuity=(not after['gyro_holes'] and
                                  after['gyro_overlap_events'] == 0),
        observed_subscription_continuity=(logger['counter_increment_events'] == 0),
        original_rate_gate_pass=after['original_rate_gate_pass'],
        accel_coverage=after['accel_coverage'], source_complete='UNKNOWN',
        clock_status='UNKNOWN', tail_complete='UNKNOWN',
        openvins_admissible=False, stage_c='CLOSED')
```

- [ ] Test counter reset/wrap, empty/one-status and unbracketed hole cases; do not classify absence of usable counter coverage as verified zero losses. Require at least two ordered statuses with type0/backend2/num_messages8 in the report caller. Initial counter is not an in-window loss count, and after-last-status tail is not certified. Verify unchanged units and integer microseconds through the existing semantic audit.
- [ ] Run GREEN and these exact relevant regressions; retain each real exit code/output. Latest evidence expected19/9/28 respectively, but record the actual fresh results instead of assuming them:

```powershell
$readerPython = '.maixpy/imu-offline-20261008/venv/Scripts/python.exe'
& $readerPython -m unittest discover -s .maixpy/imu-reader-control-20261011 -p test_compare.py -v
& $readerPython -m unittest discover -s .maixpy/imu-source-diagnosis-20261011 -p test_diagnosis.py -v
& $readerPython -m unittest discover -s .maixpy/imu-design-20261010 -p test_offline.py -v
& $readerPython -m unittest discover -s .maixpy/imu-design-20261010/single-uart/reassembly -p test_ulog_mavlink.py -v
```

Reuse the pinned real log via inspect_imu/validate_ulog, pass original rows to comparison, and reproduce11843/197.215284/4554 without rewriting its bytes. Tests using synthetic data remain software tests, not hardware PASS.
- [ ] Assemble report inputs through existing audit_capture, wire_gaps, pinned unknown-frame CRC checking, LINK counter correlation, CPU summary and same-FD UART-counter helpers. Import the helpers only: do not run historical scripts' hardcoded main/analyze/seal functions or overwrite old JSON. Record exact input SHA/epoch and failed outputs. Review checkpoint, **no commit**.

### Task 3: One approval-gated physical control and exact restoration

**Files:** new isolated deployment metadata, preflight/readback/log outputs and RESULT.md. No physical action occurs while executing Tasks1-2 locally.

- [ ] After explicit trial approval, verify propellers remain removed, fresh USB Disarmed/EV0/exact hash/source IDs and no UART owner. If assembly/safety state changed, obtain a fresh safety confirmation; never assume a prior bench state indefinitely.
- [ ] Reuse the existing USB read-only command set and record actual original UART/logger commands, eight SDLOG values, full nominal stream table, unrelated UARTs and topic absence. Refuse pre-existing custom config, non-idle logger, missing diagnostics or changed baseline; do not restore user parameters or kill an owner.
- [ ] Create a new remote folder using `mktemp -d /root/rm27-controller-reader-20261011.XXXXXX`, save the actual returned path in deployment.json. Deploy only scoped source/helper snapshots and compare local/remote SHA. Run new profile tests and affected scripted/PTY restoration tests in that isolated Linux layout with UART acquisition mocked; report any skipped POSIX tests honestly. Do not repeat unchanged Stage A/B or whole historical suites.
- [ ] Prepare the exact old166-byte topics and verify downloaded SHA. Start `logger start -b 64 -t -m mavlink -r 2500`, verify ps has that exact command and NO poll option; verify idle MAVLink backend and the same eight topics. Apply the SAME temporary wired-port restart `mavlink start -d /dev/ttyS2 -b 921600 -r 46080 -m onboard -Z -x`, same retained numerical/unlimited streams and exact removals/readback as the previous control. Neither command writes parameters. Other links stay untouched.
- [ ] Run `.maixpy/imu-offline-20261008/venv/Scripts/python.exe .maixpy/imu-reader-control-20261011/coordinator.py --trial-approved` ONCE. Same-owner guarded MAVLink2 negotiation/LOGGING_START/ACK/STOP,60 s normal-data target,85 s receiver/95 s external timeout and105 s coordinator bound; preserve the previous observation cadence. Record actual spans, CPU and same-owned-FD UART counters. No ODOMETRY output or camera load is added as a second factor.
- [ ] Stop on first safety/freshness/framing/sequence/IO fault. Preserve all raw bytes and partial evidence; no discard-and-retry or repaired dataset. Finally stop only the owned receiver, stop temporary logger, remove only the owned topic file and newly-created EMPTY directories, restart fresh original logger/UART command, restore every backed-up numerical stream and verify the full original table. Confirm exact M3C termios/owner cleanup, Disarmed/EV0/SDLOG/file absence/unrelated links. A cleanup failure is a restoration failure, not a successful experiment.
- [ ] Download once to guarded no-overwrite paths, compare remote/local hashes and independently replay original wire chunks; preserve original prefix/log bytes. If artifacts are incomplete, retain them as failed evidence, not a capture PASS. Analyze with Tasks1-2 and update only NEW results plus additive handoff pointers. Generate a manifest retaining historical snapshots; review diffs. No automatic second trial.

## Result gates and decision branches

| Gate | Required measurement | Interpretation |
|---|---|---|
| Comparison validity | Same fresh hash/source/topic/treatment, only reader differs; actual60 s target completed; parse/hash/readbacks/restore evidenced | Otherwise FAIL or UNKNOWN; no reader benefit conclusion |
| Bounded transport observation | All pinned CRCs, global/logging sequence and LINK successful-write accounting checked across matching brackets; zero observed rejection/error increments | VERIFIED only for observed window, not complete source/tail |
| Subscription/gyro observation | Ordered stable-identity/calibration records; no observed full-rate counter increment; no gyro coverage residual outside +/-2 us | Finite continuity evidence, NOT universal loss-free raw IMU |
| Original frequency | `(N-1)*1e6/(last-first timestamp_sample) >= 200` | Below200 remains FAIL even if no skips |
| VIO prerequisites | Independent accel endpoint coverage, source tail, clock/exposure mapping and integrated-observation compatibility | Still UNKNOWN/PARTIAL; OpenVINS admission false, Stage C CLOSED |

1. If skip/hole disappears and transport remains clean: retain candidate as a finite improvement only. A later longer/repeated trial is a separate plan; do not declare source frequency or VIO fixed.
2. If skip/hole remains: keep PARTIAL; exact logger/publisher execution trace is the next missing evidence. Do not infer a card/UART fault or change firmware/parameters automatically.
3. If transport or CPU/safety behavior worsens: report candidate failure, restore and diagnose saved evidence offline. Do not escalate reader/baud rates.
4. If source remains~197 Hz: maintain the original gate FAIL. Prepare a separate approved source-trace investigation or evidence-based requirement decision; do not blindly raiseIMU_INTEG_RATE (200->210 preserves the modeled3/4 integration configuration).

**Exactly one next physical action, not executed/approved by this plan:** with M3C and PX4 on the existing UART plus independent PX4 USB control, run the ONE60 s fixed-reader comparison above. It verifies whether logger subscription continuity improves under otherwise retained conditions; it does not verify Camera-IMU synchronization or OpenVINS suitability.

## Planning verification and handoff

This turn inspected the actual source/guards/latest evidence and checked the diagnosis manifest:28 own +27 external files matched before additive handoff edits. Previous HANDOFF.md/VAULT_UPDATE.md bytes are preserved in `.maixpy/imu-reader-plan-20261011/repo-before/` so its historical root snapshots remain recoverable. Seven proposed Python blocks passed AST syntax checking only (exit0), after correcting two Windows shell-quoting scanner attempts; the examples were not executed. No new implementation/runtime-test/capture PASS is claimed. Preservation is recorded in `.maixpy/imu-reader-plan-20261011/verification.json`. The next implementation task starts with Task1's offline RED tests; default execution is inline. Review the plan, command scope, unchanged gate values and preservation checks before crossing the physical approval boundary.
