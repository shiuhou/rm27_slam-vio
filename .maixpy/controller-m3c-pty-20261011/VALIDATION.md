# M3C controller PTY qualification — 2026-10-11

**55 tests PASS, zero skips/failures**, including both real POSIX PTY tests.
This is board-side software validation; physical high-rate UART remains untested.
VIO-S0/VIO-P PARTIAL; Stage C remains NOT_STARTED.

M3C live hostname maixcam2-9d05/aarch64; Python3.13.2, NumPy2.2.6,
pymavlink2.4.49, pyulog1.2.4. Used system Python/NumPy and existing research
MAVLink venv site-packages. Missing pure-Python pyulog copied from the pinned
Windows research installation into this new isolated directory's research-lib.
No pip/install or system/old-venv modification. No launcher/development-mode
entry, physical UART open, FC query/configuration, new IMU capture or stream.

Deployment: `/root/rm27-controller-pty-20261011.zUIWou/`, fresh mktemp directory.
Relative `.maixpy` import layout preserved; original deployed tests not replaced.
The deployed controller code is unchanged from the local tested working tree.

Archive SHA256s (local/board equal):

- controller-source.tar.gz: b503382fac21f733b2b132cc5cefe2bf5302725013c13bb84933d6b44c333dd3
- pyulog-1.2.4.tar.gz: 10f7915ac46416e9392267334e156f24566ee2df56fcd812c405c427803d3573

Exact test command, from deployment root:

```sh
PYTHONPATH="$PWD/research-lib:/root/rm27-mavlink-test-20261010/venv/lib/python3.13/site-packages" python3 -m unittest discover -s .maixpy/imu-design-20261010/single-uart/controller -p 'test_*.py' -v
```

tests.txt: Ran55 tests in2.293s / OK. Both PTY normal roundtrip and armed refusal
verified exact termios restoration; virtual-device paths came from pty.openpty().
Peer data/ACKs are synthetic; this does not prove UART921600/FC logging performance,
source completeness, sensor timing or OpenVINS admission. No saved-real-log replay
rerun on M3C; existing research-host replay evidence remains separate.

tests.txt SHA256 0e5c70933fae57f31dba2a8c784cc1599bf045182d1a2d0ab7a900dbff387b69;
environment.txt SHA256 a0bd5a0c3199a626600ce900882802981eea28c6d2b08652b091f7ed519ce04e.
Downloaded evidence matches the board copies. No test controller process remains.

Retained operational issues: first remote inline-Python quoting failed before
execution, corrected with stdin script. Board wall-clock predates host file mtimes,
so tar warned future timestamps; no clock setting changed. Wrapper's final tail
argument acquired a CR and exited1 AFTER tests; inspected downloaded full test log
and board copies independently (all55 tests OK). Do not misreport wrapper exit0.

Next: specific runtime communication/logger trial in controller/RUNBOOK.md.
M3C PTY prerequisite is now complete; do not repeat StageA/B or these tests without
code/environment changes. Existing physical UART owner/configuration and FC state
must be freshly backed up for that separate trial. No commit/push/Vault write.
