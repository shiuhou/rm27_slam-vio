# Publication validation — 2026-10-12

User-authorized normal commit/push of pending RM27 research, using
shiuhou/uhshi371@connect.hkust-gz.edu.cn. Baseline main/remote3ea1e160.
No rewrite/force push, hardware/device/SSH access, dependency installation,
new capture, runtime fix, parameter/firmware/communication change or Vault access.
Root report before-states are copied into local repo-before. Prior experiment
reports/raw artifacts/manifests and Stage A/B are preserved byte-for-byte.

## Fresh worktree tests

Root command: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 py -3 -B -m pytest tests -q`:
226 PASS/1 existing skip, exit0 (15.67s).

Research commands use the existing research Python3.12 environment:
`.maixpy/imu-offline-20261008/venv/Scripts/python.exe -B -m unittest discover -s DIR -p PATTERN -q`.

| DIR under .maixpy | PATTERN | PASS | Windows skips |
|---|---|---:|---:|
| imu-design-20261010/single-uart/controller | test_*.py | 113 | 7 |
| imu-uart-retry-20261011 | test_*.py | 5 | 0 |
| imu-uart-negotiated-trial-20261011 | test_*.py | 9 | 0 |
| imu-gap-diagnosis-20261011 | test_*.py | 15 | 0 |
| imu-source-diagnosis-20261011 | test_*.py | 19 | 0 |
| imu-upstream-gyro-20261011 | test_*.py | 19 | 3 |
| imu-uart-reduced-trial-20261011 | test_*.py | 14 | 3 |
| imu-reader-control-20261011 | test_reader_profile.py | 8 | 0 |
| imu-reader-control-20261011 | test_compare.py | 7 | 0 |
| imu-design-20261010/single-uart/reassembly | test_ulog_mavlink.py | 28 | 0 |

All command exits0:463 PASS/14 skips including root. This is fresh software/
saved-file evidence only; no board/physical tests rerun and no source PASS.
Expected argparse refusal inside scope tests did not open a device.

## Portable export validation

Staged index exported using `git checkout-index --all --prefix=NEW_TEMP_DIR/` to
`C:/Users/USER/AppData/Local/Temp/rm27-publication-20261012-0853c4c0a9104c9ba22c23571fb55e7c`.
Existing Python environments were used, with PYTHONPATH cleared and only exported
source/fixtures. Root226 PASS/1 skip (13.97s); same controller/retry/negotiated/gap/
upstream/reduced/reader/reassembly commands as above all exit0.
Portable source-diagnosis scope explicitly runs
CadenceTests/SourceModelTests/CounterTests (18 synthetic fixture tests), NOT
SavedEvidenceTests (one real-ULog test). The latter passes in the original worktree
above but requires unpublished raw evidence. It is not silently skipped or counted
as a clone pass. Export total462 PASS/14 Windows skips, no failures. No evaluator,
source integrity or200Hz threshold is changed. The absolute existing research
Python path is the environment, not an import of the original ignored source.

Portable source-diagnosis command from its exported directory:

```powershell
python -B -m unittest test_diagnosis.CadenceTests test_diagnosis.SourceModelTests test_diagnosis.CounterTests -q
```

## Publication checks / excluded material

Entry-link review:30 local Markdown links in CODEX_RESUME/PUBLICATION/result
entrypoints resolve to indexed files. Targeted GitHub-token/AWS-key/private-key
pattern scan over curated files found no matches; not a general security audit.
Stage A/B report SHA256 remains
`d9c79727ad749e8ec6ba970a2e41c0ef4aa5ccc3ac6e6e7bc53c0f1bbb7ffd0f`.
Final staged whitespace check exit0. Attributes explicitly preserve research CRLF;
one immutable upstream mavlink_helpers.h snapshot retains its existing whitespace.
No source bytes were changed to silence formatting warnings. No active local
Git hook was found. Indexed hashes were checked for278 curated paths; every
research snapshot matched its original bytes. Final selection.json records both
worktree and Git-blob hashes, so normal documentation newline handling is explicit.

Publication helper failures were not hidden: the first selector used a nonexistent
test_bench_io.py path, corrected after file discovery to the existing guard/tests;
initial format checks flagged retained CRLF and upstream whitespace; documentation patch
attempts with a nonmatching documentation context were rejected without changing
experiment files. A bounded diff-review pipeline returned nonzero; it is not used
as a passing check, and the independent staged check was rerun successfully.
A native Python -c quoting attempt also failed before verification; the same
visible check was then passed intact via a quoting-safe payload and succeeded.
No failed device test was retried or relabeled PASS during publication.

Curated source/test/report/JSON-summary paths are recorded in selection.json.
Raw UART/ULog recordings and local test consoles, virtualenvs, archives/build/vendor
trees remain local. Small pinned diagnostic source/schema snapshots are included
for import/schema closure, not represented as a complete firmware build tree.
Older raw-inclusive experiment manifests do not claim complete clone availability.
Unrelated tests/camera_capture.py/tmp and the pre-existing PLAN_HISTORY.md edit are
preserved and excluded. Historical reports retain their dated no-push/next-action
observations; root current publication notice supersedes only publication state.

Remote authentication was queried using `gh api user --jq .login` (shiuhou) and
repository push permission. Repository-local author/committer name/email readback
matches the user's request. The system/global old email is not changed. New push
uses an explicit CLI credential helper, with no secret/token printed or stored.
Already-shared old-email commits remain intact; normal push result/remote hash
will be checked after the command before reporting completion.

No Vault ingestion, new hardware claims, source fix, VIO synchronization/model
admission or Stage C. VIO-S0/P PARTIAL; Stage A/B unchanged.
