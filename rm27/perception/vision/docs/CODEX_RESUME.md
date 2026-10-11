# RM27 VIO 接续入口 — 2026-10-11

2026-10-12 发布接续：[发布范围／Git身份](PUBLICATION_20261012.md)。控制器、诊断及下述实测报告已整理为提交范围；
原始录制和完整历史manifest依赖仍在记录的本机／M3C位置，clone不自带实测数据。
新提交署名shiuhou／uhshi371@connect.hkust-gz.edu.cn；不重写旧提交。当前技术结论仍以下方失败报告为准，
不是新实验或修复；Stage A/B保留，VIO-S0/P PARTIAL，Stage C关闭，RAM trace仅设计。

最新：[上游gyro观测启动失败／已还原](../../../../.maixpy/imu-upstream-gyro-20261011/RESULT.md)，同目录 HANDOFF／verification.json。
用户授权的一次 stock-firmware 观测已消耗：新增 sensor_gyro0 后日志286→288缺287，global19→21；同区间一次PX4 TX缓冲拒绝，成功写数＝实收数。
未完成60秒，仅4gyro／1IMU记录，原订阅缺口／源频率原因仍UNKNOWN；之前 vehicle_imu-only 完整传输对照不变，不采用新增负载方案。
原115200／完整stream map／logger／8SDLOG／配置缺省／M3C termios已恢复，Disarmed／EV0。Windows34通过／3平台跳过，M3C27通过／零跳过。
Stage A/B保留，VIO-S0/P PARTIAL，StageC关闭；无固件、参数、传感器、接线或融合变化，不重试、不push、不访问Vault。
下一步[RAM触发轨迹设计](../../../../.maixpy/imu-upstream-gyro-20261011/NEXT_TRACE_PLAN.md)尚未实现／刷写，需要单独固件范围及准确回滚镜像；下文旧下一步只属历史。

最新：已执行唯一一次固定 logger 读法对照，见 [RESULT](../../../../.maixpy/imu-reader-control-20261011/RESULT.md) 及同目录 HANDOFF。
`-r2500` 未修好漏读：11837笔／197.104634Hz，订阅计数增加2，陀螺仪覆盖缺口4460／4507us；UART封包／TX计数在观察窗口完整。
原200Hz与覆盖门槛仍失败，VIO-S0/P PARTIAL，StageC关闭。设置精确恢复115200／原遙测／idle logger，EV0、Disarmed。
新增15＋相关回归71／M3C48测试通过；没有固件、参数、传感器、相机／标定／VIO／融合改动，未push或访问Vault。
不要重跑已消耗授权的coordinator；下一步设计logger实际执行／generation和VehicleIMU端点可观测性。下文旧行动只是历史。

最新离线：[订阅缺口／源频率诊断](../../../../.maixpy/imu-source-diagnosis-20261011/DIAGNOSIS.md)。
4554us已定位logger的vehicle_imu queue1订阅generation漏读，不是UART；精确排程仍UNKNOWN。
197.215Hz未达原200Hz；298较长accel积分与双积分器回调逻辑一致，不可把271长间隔当271丢样。
56离线测试PASS／零跳过，旧80／36文件和14源码hash核验通过。无硬件／运行设置改变。
StageA/B保留；源完整性／时钟／测量模型未合格，StageC CLOSED。后续读取节奏对照仅计划。

最新真机：[一次减遥测对照完成／输入仍未合格](../../../../.maixpy/imu-uart-reduced-trial-20261011/RESULT.md)。
同921600／46080／最小logger，临时停48项非必要数值遥测：正常60.016秒、5001帧CRC通过、日志／全局序号无缺口。
64个LINK计数区间成功写4980＝实收4980、发送缓冲拒绝0；有限传输对照VERIFIED，不是通用固件修复。
11843笔BMI088积分197.215Hz未过原≥200Hz；一个4554us覆盖缺口与logger订阅generation跳号1→2对应，仍非完整VIO输入。
13项新M3C工具测试全部通过／零跳过；Windows17项14过／3POSIX跳过；独立核验exit0，18运行源码及Stage A/B／旧证据不变。
原115200／完整stream map／logger／8SDLOG／配置原缺省／M3Ctermios已还原，Disarmed／EV0，光流ToF正常。
这一项授权已消耗，不重跑日期协调器、不再采集、不推送／不改Vault。下一步离线分析残余订阅缺口／源频率，
不开始同步／标定／真实VIO或StageC；VIO-S0/P仍PARTIAL。下文“减遥测提案未执行”等只属保留历史，本段优先。

最新离线：[发送缓冲拒绝归因](../../../../.maixpy/imu-gap-diagnosis-20261011/DIAGNOSIS.md)。
10笔LINK_NODE_STATUS及另23笔未知帧按精确子模块定义校验CRC，全部3697帧原始重播一致，不改原记录。
缺435区间PX4拒绝计数4→5／global34→36；成功写398＝M3C实收398。九区间六次拒绝对上六个缺序号位置。
发送缓冲拒绝层已验证；突发／调度／驱动排空触发尚未知，未实测修好。packet437完整perf记录ulog_stream missed0，不补包不接纳失败日志。
新15项与既有9项离线测试通过／零跳过，独立核验exit0；18运行源码／旧证据／Stage A/B不变，无设备／SSH／UART访问或设置。
下一步是一项[减遥测对照提案](../../../../.maixpy/imu-gap-diagnosis-20261011/NEXT_TRIAL_PLAN.md)，不是立即重跑旧协调器；本轮未授权新物理采集。
IMU约196.43Hz与积分覆盖／来源／尾部／时钟／模型门槛仍未过，VIO-S0/P保持PARTIAL、StageC关闭。未提交／推送／更新Vault。
下文“归因UNKNOWN／下一步离线定位”是保留的历史快照，本段优先。

最新真机：[协商成功／日志缺包失败／还原报告](../../../../.maixpy/imu-uart-negotiated-trial-20261011/RESULT.md)。
用户“可上真機”授权的一次试验已结束，不重试。M3C新版120项全通过／零跳过，18个源码哈希一致。
同一UART owner完成heartbeat-only协商，真机PX4变v2，日志START／STOP都ACCEPTED；随后434→436缺435而停止，60秒未完成。
失败原始prefix107784字节不改；513笔BMI088实例0积分数据约196.43Hz并有覆盖缺口，仅诊断，不算200Hz／VIO／同步PASS。
两端设置已完整还原；PX4 UART回115200，Disarmed／EV0／光流ToF保留。9项离线测试通过，独立核验exit0。
Stage A/B及旧失败不变。下一步离线定位丢包层／计数器与遥测突发预算，不盲目重跑或要求接线修改。
VIO-S0/P仍PARTIAL，StageC关闭；当前工作树未提交／推送，Vault未修改。下文旧预检／首次实测方向只是历史。

最新软件：[离线heartbeat-only协商验证](../../../../.maixpy/imu-negotiation-fix-20261011/VALIDATION.md)。
复用同一UART owner，明确opt-in后只用PX4v1 heartbeat／uptime作启动协商；确认Disarmed／身份／CRC才回v2 heartbeat，
收到PX4v2后才允许日志START。默认／日志／ACK／升级后的相关安全帧仍严格v2；保留超时／fresh／同批否决／还原。
Linux120项通过／零跳过（含7项真实PTY），Windows113通过／7项跳过，54项相关回归和主工程226通过／1项原有跳过。
本轮无M3C／PX4访问、部署、采集或设置；87项旧M3C预检不覆盖新版。原Stage A/B、失败及391／306 dropout原文件不变。
下一步新版120项M3C软件预检，再用新协调器做独立授权的一次60秒实测；不能直接重跑旧一次性协调器，
也不能在启动M3C前先要求PX4出站v2。VIO-S0/P保持PARTIAL，原≥200Hz／来源／尾部／时钟／模型门槛不变，StageC关闭。
下文“协商未实现”属于保留的历史状态；本段和根HANDOFF的最新段落优先。未提交／推送，Vault未更新。

最新已批准实测准备：[协议顺序中止／还原报告](../../../../.maixpy/imu-uart-retry-20261011/RESULT.md)。
PX4暂用921600／46080 B/s，但M3C启动前检查要求v2，实际v1／RX0而中止；接收器未启动，没有START或新IMU数据。
全部设置还原；不是已证明接线／SD／高baud故障。源码及合成测试确认：收到M3C的v2 heartbeat才能升级，
而严格Controller也拒收初始v1，不能仅删除协调器检查。下一步离线实现／测试有界heartbeat-only协商；
尚未实现／部署／实测，不自动重试旧协调器，不重跑未改动的87项PTY。来源197Hz单秒快照未达原≥200Hz门槛。
Stage A/B证据未变，VIO-S0/P仍PARTIAL，StageC关闭；以下旧的直接实测方向已被此中止结果取代。

最新板端预检：[M3C新版PTY验证](../../../../.maixpy/controller-m3c-startup-pty-20261011/VALIDATION.md)。
原样部署已审查源码，M3C87项全通过／零跳过（含4项PTY）；16个文件哈希与本地一致。
未开物理UART、未访问PX4或新采集。新版M3C软件前置条件完成，不需重复未改动的PTY。
下一步是另行批准的一次60秒实测；VIO-S0/P仍PARTIAL、StageC关闭。下方旧的“先M3C预检”已被此结果取代。

最新软件修正：[启动同步验证](../../../../.maixpy/imu-startup-fix-20261011/VALIDATION.md)。
有界 pre-START CRC 同步已实现；Linux87项通过（含4项虚拟PTY），Windows83项通过／4项平台跳过。
保守完整候选边界可能等待／超时；saved21＋单个心跳仍不足，不声称真实启动故障已修复。
原实机失败证据不变，未重试。下一步先在M3C隔离目录验证此新版本，再独立批准一次实测。
旧55项板端PASS属于修正前版本，不直接证明新版本。VIO-S0/P仍PARTIAL，StageC关闭。

Latest live trial: read [RESULT.md](../../../../.maixpy/imu-uart-trial-20261011/RESULT.md)
first. One approved60s attempt at921600/46080B/s failed BEFORE START: first21
bytes Bad prefix, zero TX/IMU. Independent restoration verified. No retry.
The subsequent offline startup fix is linked above; VIO-P/S0 PARTIAL unchanged.
Older next-step descriptions below are historical, not permission to recollect.

最新实机接续：COM19只读基线已确认d6f12ad1/Disarmed/EV0、选中BMI088实例0，
vehicle_imu一秒观测190Hz；见根HANDOFF。M3C控制器55项测试已全部通过，含两项
虚拟PTY、零跳过；见[板端验证](../../../../.maixpy/controller-m3c-pty-20261011/VALIDATION.md)。
该软件前置步骤已完成，不重跑。下一步为RUNBOOK中的独立授权高频通信/logger试验。

本文件与根 [HANDOFF.md](../../../../HANDOFF.md) 的最新段落优先于历史记录中的
“CURRENT / Next”。用户要求发布交接资料；没有授权本次改变任何硬件配置。

2026-10-11 软件接续：单 UART controller/runner/audit 已完成离线验证，见
[控制器验证](../../../../.maixpy/imu-design-20261010/single-uart/controller/VALIDATION.md)
与 [实测流程](../../../../.maixpy/imu-design-20261010/single-uart/controller/RUNBOOK.md)。
55 项 Linux 测试（含 PTY）、54 项既有回归及主工程226 项通过；未触碰 M3C/PX4。
本工作树新增内容尚未提交/推送；不要把 GitHub 旧快照当成包含本轮实现。

## 阅读顺序

1. [PX4 ↔ M3C 接线、端口、命令与边界](PX4_M3C_CONNECTION.md)。
   同时读 [SSH 主机、板端部署与本地资料位置](WORKSPACE_LOCATIONS.md)，不要混淆
   Linux 工作树、外部实验目录、M3C 部署与 GitHub 发布子集。
2. 根 [new_plan.md](../../../../new_plan.md)：原 VIO 目标和验收门槛不放宽。
   [计划历史索引](PLAN_HISTORY.md) 同时链接早期 SLAM 原文，并说明 VINS-Fusion /
   OpenVINS / sqrtVINS 的计划角色，不表示这些候选全已验证。
3. [Stage A/B](../../../../.maixpy/mavlink2-20261010/VALIDATION.md) 和
   [IMU 50/100 Hz 测量](../../../../.maixpy/imu-transport-20261010/VALIDATION.md)。
4. [最新单 UART 设计](../../../../.maixpy/imu-design-20261010/LATEST.md) →
   REVIEW → reassembly/VALIDATION → PROPOSED_TRIAL（提案，不是已执行实验）。
5. [离线 VIO / OpenVINS 进展](../../../../.maixpy/offline-vio-20261009/OFFLINE_VALIDATION.md)。
6. [已发布文件与离线测试入口](../../../../.maixpy/README.md)。

## 状态与下一工作

| Gate | 状态 | 意义 |
|---|---|---|
| Stage A/B | VERIFIED / PASS | 当前 d6f12ad1 上 MAVLink2、HB、合成 ODOMETRY、uORB 和停/启归因；不重做 |
| VIO-S0 | PARTIAL | 50 Hz transport 测得；完整高频选中 BMI088 输入、时钟、观测模型尚未合格 |
| VIO-P | PARTIAL | 保存数据 finite 五次 candidate 同轨迹，完整 adapter 原 gate 通过；不是普遍确定性保证 |
| ULog 离线重组 | VERIFIED | fixture / 保存日志合成封装逐字节一致；没有 live UART streaming PASS |
| Stage C / real RM27 VIO | NOT_STARTED | 禁止拿合成 ODOMETRY 或诊断均值绕过真实输入、标定与同步门槛 |

已完成的软件任务：复用 receiver/decoder/reassembler，实现并离线/PTY 测试
single-owner、fresh-disarmed-heartbeat、start/ACK/stop、超时与 M3C termios 还原。
startup/tail 被显式记录，但无独立源计数时完整性仍 UNKNOWN；不能插值或报 PASS。
PX4 通信/logger 的实际备份、变更与还原由独立 USB 协调端执行，并未被 UART
controller 自动化或实机验证。当前下一步是批准范围内的高频实测，而不是重写控制器。

实机前先在 M3C 跑同一组 PTY 软件测试，再按 RUNBOOK / PROPOSED_TRIAL 的具体范围取得
通信/logger 变更授权。用户已否定第二个可用 UART；不要重新要求找备用焊盘。
USB host/CDC 路径仍受内核、角色、SSH 管理条件限制。

## 证据与源码

PX4 当前已核实 hash：`d6f12ad1c4f70ad3230afd7d86e971421e02fef4`。
后续源码必须匹配此 hash，不能用标签或历史 micoair-v1.15.2 偷换。
[精确版本源码入口](https://github.com/PX4/PX4-Autopilot/tree/d6f12ad1c4f70ad3230afd7d86e971421e02fef4)。
本仓库保留小型 `.msg` 定义和研究脚本依赖，未发布整个第三方源码 / 构建树。

这些报告是保存观察的总结。本次推送不重新观测 Disarmed、EV_CTRL 或设备连接。
实际硬件任务开始前要重新核对固件、Disarmed、EV_CTRL=0、所有权与原始配置。
不自动恢复旧 SD 卡 / 旧固件参数，不动用户其他飞控参数。

完整 raw 证据未上传，fixture tests 可在 clone 中运行；完整保存日志重播要取得
既有本地文件并先比 SHA，不重新下载已有公共数据集。绝对路径和日志文件缺失
应报告为当前主机不可用，不得伪造验证成功。
