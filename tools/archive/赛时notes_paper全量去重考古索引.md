# 三包赛时 notes / paper｜全量去重考古索引

> 本轮对三包递归展开树中所有非空、可解码、文件名含 `note / notes / paper` 的文本做全文读取与 SHA-256 去重。
>
> 结果：
> - 外观文件：66
> - 唯一文本内容：**20**
> - 其余主要是 VM 后续快照 / Day6.zip / Day7.zip 对历史工作区的重复副本。
>
> 本索引解决两个问题：
> 1. 防止以后把同一 notes 在 3 个 VM 快照里重复当成 3 份独立证据；
> 2. 区分“真正推导草稿”和“只是样例缓存”，避免只因文件名叫 notes 就过度解读。

| SHA前缀 | 副本数 | 场次/题 | 内容性质 | 信息价值 | 当前吸收状态 |
|---|---:|---|---|---|---|
| `b6be015d7487` | 5 | Day2 A `problems/paper.txt` | 长篇 A 乘法推导 + 代码片段 | **高** | 已被 Day2 长复盘/考古大量吸收；继续作为原始思维源 |
| `595378071049` | 7 | Day3 A notes | 样例、贪心、sort/upper_bound 提示 | 中 | 与录音/源码交叉后已吸收 |
| `e60f13c3cb60` | 7 | Day3 B notes | 长篇约简串/猜想/样例/checker 调用记录 | **高** | 已由双ASR+keystream+checker进一步闭合；原文仍保留 |
| `bfeb8d7e41f7` | 7 | Day3 C notes | 单个小树样例 | 低 | 样例资产，不单独升结论 |
| `4a12f84a264a` | 4 | Day4 A notes | equality guess → lower bound → fail 标记 | **高** | 已落 E-D4-011 |
| `02224fd89371` | 4 | Day4 B notes | 滑窗状态 A/B/C、mp/t、样例 | **高** | 与 recovered keystream 对齐；E-D4-002/004 + 新提交Bug共同解释 |
| `06e0de909b78` | 4 | Day4 D notes | 单个图样例 | 低 | 样例资产 |
| `bee3e4b20294` | 3 | Day5 A notes | 单个数组样例 | 低 | 不单独升结论 |
| `b34a431771f6` | 3 | Day5 B notes | 路线箭头 + 子任务分值估算 | 中 | B15 special 已由题面+source严格证明 |
| `b415aa803f71` | 3 | Day5 A 第二代 notes | 三组数值样例 | 低 | 与 Replay 版本链配合，不单独作结论 |
| `19725929c879` | 3 | Day6 A notes | gap 局部约束、求和、`min(a_i,a_{i+1})-1` | **高** | 已落 E-D6-012 |
| `9ff8e14752a5` | 3 | Day6 B notes | time/work 坐标化、手算多组日志 | **高** | 与 B 的点/DAG模型、势函数缺口交叉使用 |
| `c1cbc6374a67` | 3 | Day6 D notes | `phi(i*j)` + 质因子分解方向 + 样例 | 中高 | 已由 file_changes 的 phi(1/2/6) 微探针进一步吸收 |
| `047d5b132088` | 2 | Day7 A notes | 简单分组示意图 | 低 | 录音/源码证据更强 |
| `f7a97e5b1443` | 2 | Day7 B notes | 多组树/负责人手算 | 中 | 已与 stable brute / Replay 对齐 |
| `3ba2a4e5e961` | 2 | Day7 D notes | 三棵小树 | 中低 | D19/5000候选主要靠录音+版本证据 |
| `9fb385331156` | 1 | 代码部落 T1 / net notes | 两棵树样例 | 中 | 作为 net 原始样例资产 |
| `7d2ab5529275` | 1 | 代码部落 T2 / game notes | 二进制局部手算、计数 | 中 | 可与 game 7版本继续交叉 |
| `c0afb7afe4b2` | 1 | 代码部落 T3 / core notes | 仅 `trie` | 低但语义明确 | 证明赛时至少识别到 trie 方向，不能扩写更多 |
| `1c2dae9d551b` | 1 | 代码部落 T4 / tree notes | 两组树/点权样例 | 中 | 与 tree 12版本、错误 sample 包交叉 |

## 高价值 notes 的使用规则

### 1. notes 是“当时写下的对象”，不是最终正确性证明

例如 Day4 A：
- notes 中 `ans = Σ|a-b|` 被自己标记 fail；
- `ans ≥ Σ|a-b|` 保留下来。

因此必须按时间/命题层级拆：
- H：猜想；
- P：已证明必要条件；
- X：反例打掉的上层猜想。

不能把同一个 notes 文件里的所有句子统一标成“赛时结论”。

### 2. notes 要和保存时间 / keystream / source version 对齐

最典型 Day6 A：
- notes 先写出 gap 上界；
- 约86秒后同一数学式进入 main.cpp；
- 再通过版本链补耦合约束；
- 最后 AC。

这种链比单独引用 notes 更有价值。

### 3. 低价值样例 notes 也不删除

“低价值”只表示：
> 当前没有独立新结论。

它仍然用于：
- 复现当时手测数据；
- 对齐 screen/keystream；
- 解释某次代码修改为什么发生；
- 验证历史路径血缘。

所以索引保留全部 20 个唯一文本，不把“没新结论”等同于“垃圾”。

## 当前 notes 线的剩余高价值工作

已全文读完 20/20 唯一 notes。后续深推理优先级：
1. Day6 B：把 time/work 手绘坐标与原始录音中 pair compatibility 的形成逐段对齐；
2. Coderlands game：把二进制手算 notes 与 7 个保存状态逐版本对应；
3. Day4 B：继续把 A/B/C 状态草图与 `t→last→least` 的 keystream 语义迁移做成变量谱系。

这三个属于“已读原文、尚可继续榨取语义”，不是“尚未读”。
