# Exact-source supplement

PX4 commit `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`, matching freshly read
flashed firmware. Only two missing source files were fetched for offline failure
attribution; no dataset/redownload, firmware build/flash or device action.

| Local copy | Commit-pinned origin | SHA256 |
|---|---|---|
| mavlink_ulog.cpp | https://raw.githubusercontent.com/PX4/PX4-Autopilot/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_ulog.cpp | 898784d79d5a52d55213cde233814b1b92d79de570c45d192da3a81c8b2ca40b |
| log_writer_mavlink.cpp | https://raw.githubusercontent.com/PX4/PX4-Autopilot/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/logger/log_writer_mavlink.cpp | ae48cc6de1cbfc0edefc0f15c37b2886472caa66f49d4b817a47607eddd35131 |

`mavlink_main.cpp` reused unchanged from
`../../imu-input-20261010/src__modules__mavlink__mavlink_main.cpp`; matching origin
is the same commit's `src/modules/mavlink/mavlink_main.cpp`. Its current hash is
included in this trial manifest, not used to infer missing TX counters.

Source exhibits possible generation skip, unreliable normal logging transfer,
TX rejection/write failure and blocking reliable metadata. Saved evidence does
not individually isolate them; receipt CRC success is not complete delivery.
