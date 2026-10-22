> **2026-10-22：已从用户新上传的双分卷Desktop真正解包，11场Replay／690条保存事件／520份赛时C++源码全文／2,581文件SHA目录进入一手证据库。** 新 AI 请从 [《桌面全量考古：陌生AI首读》](01_2026-10-22_桌面全量考古_陌生AI首读.md) 开始，沿 [690事件](交接/一手证据/2026-10-22_690保存事件_脱敏可搜索.csv) → [520份源码](交接/一手证据/2026-10-22_520份赛时C++非空源码快照.jsonl) → [2581文件SHA](交接/一手证据/2026-10-22_2581桌面文件_SHA256脱敏目录.csv) 自行验证；参见 [11场Replay时间链](交接/2026-10-22_十一场Replay_证据索引.md)、[真实口述改写](交接/2026-10-22_赛时推理口述重整.md)、[新CodeLands3](交接/2026-10-22_CodeLands3_首次考古.md)、[Gemini真假核对](交接/2026-10-22_Gemini_结论与事实分栏.md)。历史录像只建立索引，并非全部逐帧分析；赛后本地AC不得写成OJ-AC。

> **2026-10-18 代码源 Day9 完整复盘**：本场是后藤一里/山田凉/虹夏/子集异或，**不是**旧目录中zerofree/count/color/silent那场。赛时OJ核实 **60/400（A60 B0 C0 D未交）**。新增[长篇复盘](2026-10-18_代码源_CSP-S_day9/复盘报告.md)、[四题独立证明及代码](2026-10-18_代码源_CSP-S_day9/题解.md)、[41事件与65次保存](2026-10-18_代码源_CSP-S_day9/比赛全过程复现_完整版.md)、[离线交互回放](2026-10-18_代码源_CSP-S_day9/可视化复盘/Day9_整场回放.html)。四题最终源码6618例独立真值＋20份附件＋正式IO/UBSan通过，**未新交OJ，不标官方补题400**；25段录像只检查9张关键帧。下一步沿A原倒扫→B插入合法性→C按起点合并→C事件图→D值域分层补题。完整交接见[本场入口](2026-10-18_代码源_CSP-S_day9/README.md)。

> **2026-10-12 补库新状态**：[两分支缺失资产补齐与哈希验收](交接/2026-10-12_漏写资产补齐_两分支回读验收.md)：CodeLands原缺19文件、其它八场/工具原缺84文件，现仅对默认分支缺失路径恢复，共103/103 Git blob SHA精确匹配，不覆盖用户已有同名文件。另将Day8 A/C/D赛后代码、独立D oracle及CodeLands四题28事件交互回放入两个分支，官方赛时成绩不改变。工具运行不等于OJ AC；未深挖录音的任务仍存在。**接班先以实际当前 HEAD 为准**。

> **2026-10-12 产品层已真实更新**：[CURRENT_STATE.md](CURRENT_STATE.md) 记录了赛场星图上线到默认分支、默认分支 Actions #38203544956、施工分支 #38203493728 两套静态+真实 Chromium+390px 手机测试通过的证据；原始交接报告仍见 [万字报告](交接/2026-10-11_主力模拟赛分析_万字接班报告.md)。下一位AI应先核对最新HEAD，再挑 Day8 A70/C23 原始 record 或 Day4 B Oracle 等尚未闭合的工程问题，不要重新造一个只会显示KPI的前端。

> **2026-10-11 最新上下文修订**：请先读 [最新证据接管报告](交接/2026-10-11_主力模拟赛分析_万字接班报告.md) 与 [后续施工与验收](交接/2026-10-11_下一阶段任务与验收.md)。截至本档，代码源赛时八场分数45→130→204→0→15→115→145→15，共669；CodeLands另计200。Day8赛后A70来自用户粘贴OJ逐点文本、C23来自用户自述，均不能回填赛时15，且未独立获取后来新record。Day7/Day8共113个保存事件已逐一核验哈希，但不意味着所有视频逐帧语义完成。公开仓库只保存脱敏接班资料，敏感原件位于授权Library。

# AI 接管指南（最新状态）

> **第一件事：先读 `模拟赛复盘总协议_v2.md` 和 `复盘产物覆盖矩阵.md`。**
>
> 本仓库不是普通题解库，而是用户全部 OI/CSP-S 模拟赛的长期“外部大脑”。

# 1. 项目目标

每场比赛都要尽可能恢复：

- 题面与子任务；
- 最终得分 / 排名 / 逐点；
- 赛时真实思维；
- 中间代码版本；
- 录音与 Replay；
- Debug / 环境事故；
- 正确不变量与错误猜想；
- 最小反例；
- 正解怎么从赛时思路继续推；
- 得分机会成本；
- 独立验证；
- 下一场执行协议。

**不能只看最终代码，也不能只写标准题解。**

# 2. 最新比赛状态

## 代码源系列

Day1～Day7：

**45 → 130 → 204 → 0 → 15 → 115 → 145**

Day7 的旧版结论正在 2026-10-06 二次取证后被纠正：

- A100，约35分钟；
- B45 RE；
- C/D未提交；
- 榜单 66/105；
- B **确实冻结过稳定朴素版**；
- B 赛时已经明确识别 `calc` 重扫是复杂度瓶颈，并想到“离线”；
- 真正没跨过的是“删除分裂 → 倒序加入 → DSU”；
- C 的 v=50 10分性质赛时已发现；
- D 的 N≤100 19分暴力赛时已发现，并口头判断“一定能拿”；
- 但 C10/D19 没有立即变成提交资产；
- D 后来实际写出过完整的 5000 候选算法，最后经过 Debug 证明算法不可行，才推倒。

所以 Day7 不能再简化成“B 吞掉后半场”。

## 代码部落 / NOI金牌命题模拟赛1

- 200/400；
- 当时榜单快照第3/54；
- net100 / game100 / core0 / tree0。

必须注意：
- 榜单 54 行里很多账号当时**尚未开始比赛**；
- 不能拿39个零分账号算“参赛者均分/中位数/非零率”；
- 旧版试卷画像中相关统计必须纠正。

新体系关键证据：
- net 官方100最终源码存在已独立复核的三点链 M=1 反例；
- game 最终代码 n≤7 全穷举145636实例0 mismatch；
- game 赛时并非“一次分类讨论写对”，而是经历多轮真实 Bug 修复；
- tree 最后没有可靠样例验证，VM 已证实下载/复制到 T4 的所谓样例包**输入格式根本不符合 tree 题面**；
- tree 代码本身仍有数学/实现漏洞，样例事故解释的是“为什么验证链被破坏”，不是替代码洗白。

# 3. 复盘必须继承 Claude 早期的完整九大块

完整结构见 `模拟赛复盘总协议_v2.md`：

1. 证据完整性；
2. 比赛总画像；
3. 个人能力定位；
4. 逐题复盘；
5. 争议点深挖；
6. 排名/同分段/机会成本；
7. 时间线/止损；
8. Skill沉淀；
9. 行动清单。

Day3 以后新增：
- 研究过程深挖；
- 赛时代码逐段解剖；
- 键盘/Replay分析；
- 结果核对；
- 资料完整性报告；
- 验证报告；
- 可视化回放；
- 关键历史代码版本。

后面的比赛不得缩水。

# 4. Replay v3 正确读取顺序

不要沿用旧版 handoff 的错误顺序。

捕捉器 `AI_READ_FIRST.txt` 明确要求：

1. `timeline.txt`
2. `file_changes.jsonl`
3. `screen_*.mkv`
4. `raw_keys.jsonl.gz`
5. `manifest.json`

解释：
- file_changes = 保存到磁盘的源码状态；
- screen = 鼠标、窗口、Debugger、网页、未保存状态的权威证据；
- raw_keys = 精确恢复输入与快捷键；
- 录音 = 数学思路/判断/犹豫。

**录音沉默 ≠ 没干活；最终文件短 ≠ 中途没写过完整算法。**

# 5. 每题必须回答

- 题目本质；
- 赛时状态；
- 第1代/第2代/...思路；
- 每代为何合理；
- 正确不变量；
- 第一处错误前提；
- 实现 Bug 与模型 Bug 分开；
- 最小反例；
- 正解突破口；
- 比赛时如何想到；
- partial 哪些是赛时已发现、哪些只是赛后 hindsight；
- 哪个版本应冻结；
- 下一次识别信号。

# 6. 证据等级

- [P] / PROVED
- [E] / BRUTE-VERIFIED
- [C] / statement-checker fact
- [H] / HYPOTHESIS
- [X] / COUNTEREXAMPLE
- OJ-AC 仅表示官方数据通过

禁止 OJ-AC 自动升级 PROVED。

# 7. 仓库完工定义

完整4小时比赛原则上至少检查是否需要：

- README
- 复盘报告
- 题解
- 全过程复现
- 研究过程深挖
- 赛时代码逐段解剖
- Replay×录音时间线
- 结果核对
- 资料完整性报告
- 验证报告
- 赛时代码 + 关键历史版
- 正解代码
- 暴力/验证脚本
- 原始材料索引
- 可视化

根目录同步：
- README
- 错因档案
- 赛前执行卡
- 阶段总结
- 本文件
- 覆盖矩阵

具体缺项见 `复盘产物覆盖矩阵.md`。

# 8. 隐私

不能公开：
- raw keyboard；
- clipboard；
- 原始 screen 录像；
- 未脱敏账号页；
- 个人身份/联系方式/地址等。

但是**不公开 ≠ 不读取**。

正确做法：
- 私有原件作为证据；
- 仓库存 capture ID、文件清单、时间节点、脱敏结论、关键源码。

# 9. 已知必须纠正的旧结论

1. Day7 不是“D最后25分钟才开始”。
2. Day7 B 不是“没冻结 partial”；稳定版保存过 WA.cpp。
3. Day7 B 不是“没意识到复杂度”；赛时明确说 calc 慢，并想到离线。
4. Day7 不能再写“赛时已知 score floor=174”。正确状态是 A100[SCORED] / B?[FROZEN] / C10[PROVED] / D19[PROVED]；174只是在已知最终B45后的赛后反事实。
5. 新体系榜单的39个0分行很多是尚未开始账号，不能做最终参赛者统计。
6. 新体系 tree 的错误测试文件不是简单“旧目录污染”；Replay 证明赛时确实从下载包复制进 T4 并用于验证，但格式与题面不符。

# 10. 最后一条

如果用户指出“你没看录音 / 没解 ZIP / 没看捕捉器”，不要争辩。

先重新取证，再改仓库。

**仓库里的错误分析也必须允许被后来的更强证据推翻。**


# 11. 2026-10-07 新增接管信息

## 七场代码源原始归档重新交叉验证

不要只沿用旧总结数字。现有：

- `tools/archive/代码源Day1-Day7_归档证据清单.csv`
- `tools/archive/代码源Day1-Day7_来源与交叉验证.md`

record score 可直接恢复：

`45 → 130 → 204 → 0 → 15 → 115 → 145`

Day7 后续以 2026-10-06 15:10 新归档为主；它包含 105 行榜单。旧 04:07 版只做归档工具差异对照。

## BAG

当前推荐是 `tools/vm/bag_v4_flat/`。

理解重点：
- V4 强不在脚本多；
- 强在一份 main.cpp + 一池 testcase；
- 官方样例 / 手工 Debug / stress 反例全部自动进入同一回归系统；
- 工具目标是让正确动作成为默认动作。

先读：
- `tools/vm/BAG_演化史与赛场工作流.md`
- `tools/vm/虚拟机赛场工程经验.md`

## Coderlands

底层 OJ 引擎未确认。

禁止仅凭 Vue / Element UI 写成 Hydro/HUSTOJ 改版。

当前可靠的是 DOM 采集规格，见：

`tools/archive/Coderlands_平台与采集路径初步勘查.md`

后续应先做正常登录浏览器 DOM adapter；观察到真实只读 API 后再升级数据层，禁止猜接口。


## 接手控制平面（10/7）

第一入口改为：
`总览/AI直接接手入口.md`

全 32 题统一索引：
- `总览/全题总表_32题.md`
- `总览/全题总表_32题.csv`

阶段经验：
- `总览/每场比赛经验纪要.md`
- `总览/阶段数据与预测.md`
- `总览/可视化/阶段成长仪表盘.html`

下一场直接执行：
- `执行包/下一场比赛_赛前执行包.md`

考古新增硬规则：
- `模拟赛考古纪要协议.md`
- 读取原始证据后必须 append-as-you-read；
- 不得只把智能纪要当作已读原始材料；
- OJ-AC、[P]、[E]、[H]、[X] 必须区分。


# 12. 三包长期原始资料池（2026-10-07 固定）

后续模拟赛仓库持续经营只从以下三包继续做原始证据考古：

- `/CSP-S模拟赛资料/原始三包/模拟赛资料_01_共03包.zip`
- `/CSP-S模拟赛资料/原始三包/模拟赛资料_02_共03包.zip`
- `/CSP-S模拟赛资料/原始三包/模拟赛资料_03_共03包.zip`

它们已经保存到 ChatGPT Library，不再依赖本次聊天附件生命周期。

接手先读：

1. `tools/archive/三包原始资料_处理台账.md`
2. `tools/archive/三包递归扫描_统计摘要.md`
3. `tools/archive/recursive_zip_inventory.py`
4. `证据阅读台账.md`

2026-10-07 depth≤3 首轮 inventory：

- 9,073 rows；
- 195 个 nested ZIP 成功打开；
- 0 个 ZIP open error；
- 34 组重复 nested-ZIP 内容哈希；
- 169 个 ZIP 路径落在重复哈希组里。

所以后续工作单位优先改成：
`content hash + provenance + contest mapping + extraction status`，
不要把重复 VM 快照里的相同 ZIP 当成全新材料重复分析。

Replay recorder 源码审计已新增：

- `tools/vm/Replay采集脚本_源码考古与能力边界.md`
- `tools/vm/replay_recorder/contest_replay_capture_v3.0.1.patch`

其中 v3.0.0 已证明存在 pause/raw 语义缺口；以后解释 raw_keys 与 timeline 冲突时必须先查 recorder 版本与 pause status。


# 13. 2026-10-07 三包深挖第二轮

## Day7 主 capture 已做 file_changes 全量版本考古

入口：
- `2026-10-06_CSP-S模拟赛day7/回放数据/file_changes_完整版本时间线_20261006_080043.md`
- `2026-10-06_CSP-S模拟赛day7/逐段考古纪要.md` E-D7-011/012

关键事实：
- 59 条 file_changes；
- B stable→失败重写→exact rollback→WA.cpp freeze→最终只补 IO；
- C 没有 T3/main.cpp 保存事件，最终仍 starter template；
- D 有 20 个 main 保存状态，1663B 候选后主动推倒到 583B；
- capture 早期出现的 `CSP-S/Day6/foo*.cc` 属历史目录事件，不应计入 Day7 T1~T4 研究量。

## Day6 已完成“正式提交源码 ↔ Replay snapshot”精确映射

入口：
- `2026-10-05_CSP-S模拟赛day6/回放数据/file_changes_语义版本时间线_20261005_101100.md`
- `tools/archive/replay_submission_matcher.py`

四份 OJ source 均得到唯一 exact normalized-content match：
- A → T1 save #9；
- B → T2 save #6；
- C → T3 save #30；
- D → T4 save #10。

新硬规则：
> VM 最终工作区不能默认当正式提交源码；先用 OJ source 与 file_changes 内容精确匹配。

Day6 额外新证据：
- B 12 分钟内把实现/类型错误修干净，但错误数学 predicate 不变；
- D 主动用 `phi(1), phi(2), phi(6)` 做最小微型探针，随后修边界与 leftover prime 条件；
- C 四分类真实进入代码的窗口约 13:30～13:32，后来发生语义退化。

## 旧 VM 血缘已闭合到 Day3→Day4

入口：
`tools/archive/旧VM快照_血缘与Day3Day4迁移.md`

03包：
- `虚拟机.zip` 410 文件；
- `虚拟机(1).zip` 595 文件；
- 338 个同路径共同文件中 310 个同 SHA，只有 28 个同路径内容变化；
- 旧快照根 T1～T4 有 60 个文件在新快照 `Desktop/Day3/T1~T4` 中原 SHA 迁移保存。

因此旧快照要做 path-move/content-hash 去重，不能重复读 310 个纯副本。

## Day4 新钉死事实

- A OJ CE 的具体原因已定位：正式提交的 `freopen ("Thermokinesis.out, "w", stdout);` 字符串引号错误；赛后 VM 版本已把两行 freopen 注释，所以只看最终本地文件会漏掉事故。
- B OJ source 与 `虚拟机(1).zip!Desktop/T2/main.cpp` 完全一致。
- D OJ submitted source 与 VM 后续版发生结构性分叉，不能互相替代。

## Recorder baseline 措辞修正

v3.0.0 的 FileTracker **有** `_seed_state()` fingerprint 基线；缺的是“启动时把全部现有文件内容写入 file_changes 的 initial snapshot”。以后禁止简写成“没有 baseline”。


# 14. Day3 checker 真反例 + Day5 提交链

## Day3 B：不是“样例没卡到”，是 checker 把官方反例吞了

原版 T2/AC.cpp + checker + sample1～8 已重新编译重放。

sample7 第4 case：
- candidate：NO
- official：YES 62528 125010
- checker：Skipped (NO is not verified)
- 整份仍 exit 0

并且 OJ B65 正式提交源码去掉 freopen 后，与该 T2/AC.cpp 完全一致。

所以以后准确写：
> 官方 sample7 已经卡掉最终 B 算法主体；本地 checker 由于不验证 NO，没把错误暴露出来。

入口：
- 2026-10-01_CSP-S模拟赛day3/原始材料/keystream_20261001_184442_checker假安全链.md
- 2026-10-01_CSP-S模拟赛day3/原始材料/OJ提交源码与VM_AC对齐.md
- tools/archive/checker_coverage_probe.py

## Day5 Replay 已找到，不要再重复“定位原件”

主 capture：
03包 → Day6.zip → Desktop/CSP-S/Day5/contest_capture/20261004_090304

99 条 file_changes，25 段 screen，约4小时完整覆盖。

六次 OJ 提交已与 Replay 对齐，见：
2026-10-04_CSP-S模拟赛day5/回放数据/Replay与六次OJ提交映射_20261004_090304.md

必须记住：
- A 第一交是 T2/WA.cpp 的 417B 临时 special，不是前两小时 T1 full 主体；
- B15 来自 T2/main.cpp 输出 a[n] 的正确 partial；
- C 两次 RE exact 命中本地保存版，第三交主体相同但补 Hina IO 后变 WA；
- T4 在赛场真实改名为 T4(now T1)，用于 A 第二代；
- 多次 traditional IO 在 OJ 网页提交链最后修改；
- A 两次临时/新增 special 在写完到复制提交之间没有新的 F9 验证。

## 新提交一致性规则

FROZEN/VERIFIED 只对具体字节内容成立。

任何网页提交框里的二次修改都产生新版本：
VERIFIED/FROZEN → MODIFIED_UNVERIFIED。

理想证据必须是：
OJ source exact match 本地最后 VERIFIED/FROZEN source。

仅 body_without_freopen 一致表示算法主体对应，但交付链仍有 divergence。


# 15. 三包全量处理状态已升级（2026-10-07）

不要再沿用“depth≤3 inventory = 当前最高完成度”的说法。

本轮已经做到：
- ZIP magic 递归展开全部容器；
- 235 个容器实例 / 97 个唯一容器 / 0 解压错误；
- 展开树 7,324 文件；
- 逐路径处理审计 missing=0；
- 3,701 个文本类文件全文读取；
- 82 PDF 全文文本提取；
- 2,370 个 .in/.out 全字节扫描；
- 239 媒体全字节哈希 + 元数据；
- raw-key gzip 全量解压；
- ELF/.o 全字节哈希；
- DOCX/XLSX clean text 提取。

详细：
`tools/archive/三包全量递归展开与读取审计_2026-10-07.md`

**新的欠账定义**：
文件“索引/读取覆盖”已经不是瓶颈；后续重点是把已读原始内容继续转化成：
- 逐段考古；
- 题解；
- 提交链；
- 反例；
- 机会成本；
- 跨场经验。

## OJ 快照新硬规则

同一场多个 OJ archive **不能 latest-wins**。

实测：
- Day1～Day4 较早快照有榜单 CSV，较晚快照反而缺；
- Day5～Day7 较晚快照补全 record metadata；
- 27 个唯一提交 ID 中 9 个存在快照字段质量差异。

以后：
> 所有 snapshot 做并集，按字段选 strongest evidence，保留 provenance。

入口：
`tools/archive/OJ多版本归档_字段级证据合并规则.md`

## 录音新硬规则

Day3 / Day5 / Day6 / Day7 / Coderlands 各存在两份**同一音频的平行 ASR 转写**。

它们用于互相纠错，不是两份独立录音证据，禁止重复加权。

入口：
`tools/archive/录音双转写_配对与证据规则.md`

## Day5 提交链补强

六次 OJ source：
- 2 次 exact Replay snapshot；
- 4 次只差最后 freopen 两行。

所以 FileTracker 的 2 秒 polling 缺口已有真实比赛证据。

入口：
`2026-10-04_CSP-S模拟赛day5/回放数据/OJ正式提交与file_changes逐提交对齐.md`


# 16. 2026-10-07 新增硬证据：不要再用单层错因解释 Day4/Day6/Day7

## Day4 B

准确故障树：

```
small partial:
正确 brute 思路
→ solve2 重复读取 testcase
→ subtask1 TLE

full:
solve1 允许把右端点当删除值
→ n=21: 2..21,1 输出21，truth20

stress:
AC oracle 同样没检查 v != endpoints
→ [2,1] truth1, AC2, WA2
→ common-mode fake green
```

所以 Day4 B 是仓库里“oracle 与 candidate 共模错误”的标准教材。

## Day4 D

RE 不应再笼统写“运行时错误”：
- Fusion freopen 注释；
- 本地主体 exit0；
- 不生成 Fusion.out；
- OJ 1ms RE。

修 IO 后仍会因无条件 n! 直接 WA sample1。

## Day6 B

最终源码同时有：
- average-speed 数学 predicate 双向错误；
- n/m 数学对象身份混淆；
- 全局日志数组跨 testcase 残留；
- same testcase 可因 prefix 不同产生不同答案。

以后讲 Day6 B 时，不要只说“差一个势函数”。

## Day6 C

官方 sample1 是一个危险教材：
- local predicate 已错；
- 但 d=(1,1) 的 expectation 恰好抵消成8/9；
- 所以 submitted source sample1 完全通过。

必须强调：
> 概率题不能只验证 aggregate expectation；要先验证 local predicate / state set。

## Day7 B

45 RE 的直接原因已经不是猜测：
- 256MiB limit；
- 无用 unordered_set 在递归中 retained；
- path case RSS 近 Θ(n²)；
- 256MiB 下 bad_alloc 可复现；
- OJ 107MiB / 227MiB 曲线与本地 n=2000/3000 对齐。

删 set 后可过附件1~3且 n=1e4 最坏链很轻，但 full仍 Θ(n²)。

这些结论的详细原件入口均已写进对应 `逐段考古纪要.md`。


# 20. 2026-10-07 Day3 旧键流证据边界 + Day7 ID 修订

## Day3 v1 keystream

新增源码审计：
`tools/vm/Day3旧Keystream采集器_源码考古与证据边界.md`

Day3 当场使用的是旧 `keystream_linux.py`，不是后来的 Replay v3。

必须记住：
- raw JSONL 记录全部 EV_KEY up/down/repeat；
- `keys.txt` 省略 key-up 与 standalone modifier；
- v1 没有 pause；
- v1 没有 mouse/window/screen/clipboard/file-change；
- 所以 readable text 空窗不能写成“用户没操作”。

Day3 B checker provenance 新闭合：
- checker.cpp 出现在 B 刚开始后的赛中窗口；
- 双 ASR 同期明确说“既然提供了校验器……先把这些东西全下载下来”；
- 当前可标 [E]“赛中取得的随题/赛场提供资产”；
- 不能继续写“可能赛前已有”；
- 但具体 URL/按钮仍未恢复，不得冒充 [P]。
- checker.cpp 取得后未见源码改写，所以 false-NO coverage hole 不是后来改坏。

Day3 对应事件：
- E-D3-015
- E-D3-016

## Day7 事件 ID

历史上两个不同事件都叫 `E-D7-013`。

从现在开始 canonical：
- E-D7-013a：B45 官方子任务/资源边界；
- E-D7-013b：retained unordered_set → Θ(n²) 峰值内存 → bad_alloc/RE 根因。

裸 `E-D7-013` 视为 legacy ambiguous ID。
修订规则已经写入：
`Replay逐段考古协议.md`


## 2026-10-08 Day5 D 满分数学闭合（仍非 OJ-AC）

- 原始来源严格为 03 包：Day5 2026-10-05 OJ 完整归档中的 D 官方题面；`2026-10-03 20_53 记录_原文.docx` 的 T+02:16 / T+02:30；`Day6.zip` 中 `contest_capture/20261004_090304/timeline.txt` 与 `file_changes.jsonl`。
- 赛时 D **仍是0分、未提交**；音频/Replay 证明只做过收益扫描且把 T4 改为 T4(now T1) 服务 A。不能把赛后算法回写到赛时能力。
- 新成果：D 已得到完整 GF(2) 影响向量/两两独立/二阶矩公式，并实现按影响指令位集精确分组 + 加权前缀平方统计，覆盖 `n≤1000,q≤1e5,a_i,x<128`。
- [P] 完整证明与样例推导：`2026-10-04_CSP-S模拟赛day5/题解.md` 中 D1-D8；[E] 10,119组小域全穷举+650组随机，0 mismatch，两官方样例全过；C++ / 独立真值脚本分别在 `正解代码/D_灯光预案_二阶矩_确定性位集.cpp`、`验证/D_灯光预案_独立穷举对拍.py`。
- 考古节点：`2026-10-04_CSP-S模拟赛day5/逐段考古纪要.md` E-D5-017；同见 `证据阅读台账.md` 2026-10-08 段。
- **验收边界**：这是「赛后 full [P math]+[E local test]」，未执行 OJ 正式提交，禁止写为 OJ-AC；GitHub 代码仍可由下一 agent 直接运行仓库自带脚本重新验证。
- Day5 B/C 的 full 仍待补，整场「题解」在 `复盘产物覆盖矩阵.md` 标 **△**，不冒充整场闭合。下一高增益目标建议 Day5 B 的 full 题意→路线或 Day4 C/D 未充分利用的原始研究材料。


# 2026-10-11 Day8 新增审计（请优先于上面截止10-07的32题旧总表）

**新场次已真实落仓库**：`2026-10-11_CSP-S模拟赛day8/README.md`（commit da811f65afbea7fb51c8bc19b5576c0f01e83170）。这次正式成绩是A15、B0、C0、D0，总分15/400；2026-10-07旧“32题/七场”基线此后应理解为**历史截面**。新增后代码源八场32题共669/3200（均分83.625；旧七场654/2800，不可拿新旧口径混算）；另有独立CodeLands四题。

原件审计：VM 138条目，Replay 54保存事件（A34、C10），25录像段代表抽帧，OJ两份正式提交及子任务结果，两份原文平行ASR；更多校验细节看Day8 README和 Library `/CSP-S模拟赛资料/Day8_深度复盘/`。A数学分类已经成立而d=m被abs伪造非法路径，最小一行patch本地14400/14400；B三点反例、链端点15分；C k[i]错位、赛后40分联合partial；D旧图度≤2、性质B赛后50分联合partial。**所有赛后程序未OJ AC，不回填得分。**

下一次更新canonical全题表时，应新增四行并标明旧表发布日期、真实得分和证据等级；不能因为赛后A新程序正确就把A15升级为100。


## 2026-10-11 第三版深复盘与C全范围赛后候选
- [三版复盘_推理模型与证据修订.md](2026-10-11_CSP-S模拟赛day8/三版复盘_推理模型与证据修订.md)：不以最终源码代替赛时研究，以原始03:44语义和54条保存事件重建数学演化。
- [C_观测记录_20bit拆半DP.cpp](2026-10-11_CSP-S模拟赛day8/赛后正解/C_观测记录_20bit拆半DP.cpp)：独立推导20bit二分10+10，O(n*1024)，44MiB最佳前驱表；本地120小随机与五份官方附件输出最优长度3/1119/99999/7066/21981全部相同且路径合法。**未OJ重交，不得说AC。**
- Library 全量教学长文：`/CSP-S模拟赛资料/Day8_深度复盘/Day8_第三版_赛时推理与完整算法教学.md`。
- A的一行d<m修数学错误并不等于100：原代码每个calc求逆元是O(∑n logP)，A仅1000ms；须压大数据性能、预处理invfact。赛时A15分不改。
