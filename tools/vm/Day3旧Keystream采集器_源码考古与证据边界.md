# Day3 旧 Keystream 采集器｜源码考古与证据边界

> 目的：解释 Day3 的 `keys_20261001_184442.txt` / `events_20261001_184442.jsonl` 到底记录了什么、漏了什么，以及这些边界怎样影响对赛时行为的推断。
>
> 本文只保存采集器源码级结论和脱敏后的行为事实，不公开 raw keyboard 内容。

## 1. 原件与血缘

本轮从三包原件完整读取：

- `模拟赛资料_03_共03包.zip!虚拟机.zip!虚拟机/Desktop/keystream_linux.py`
- `模拟赛资料_03_共03包.zip!虚拟机(1).zip!虚拟机/Desktop/Day3/keystream_linux.py`
- `模拟赛资料_03_共03包.zip!Day6.zip!Day6/Desktop/CSP-S/Day3/keystream_linux.py`

三份内容 SHA-256 完全相同：

`6ad09036fb4b6277529ef0344ef5409c5858d4ed772f3dc588c8869dc60953d9`

Day3 实际输出格式正是这版 v1：

- `keys_20261001_184442.txt`
- `events_20261001_184442.jsonl`

raw 共 **32,890** 个 EV_KEY 事件，时间范围约 0～14569.759 秒。

因此本文讨论的不是“后来升级版理论上怎样”，而是 **Day3 当场真正使用的采集器语义**。

---

## 2. 它真正记录什么 [P/source]

源码直接打开单个 Linux 键盘设备：

`/dev/input/by-id/*-event-kbd`
→ 不存在时退到 `/dev/input/by-path`
→ 再退到 `/dev/input/event*`

使用：

- `os.O_RDONLY | os.O_NONBLOCK`
- `selectors.DefaultSelector`
- x86_64 Linux `struct input_event = llHHi`
- 只处理 `EV_KEY`

对每个 EV_KEY，raw JSONL 写：

`{"t": monotonic_seconds, "code": code, "value": value}`

其中：

- value=0：key up
- value=1：key down
- value=2：auto repeat

所以 `events_*.jsonl` 是这版 recorder 的最高保真键盘层。

### human-readable `keys_*.txt`

它把按键解码成：

- US-layout 字母/数字/常用符号；
- Backspace / Enter / F1～F12 / 方向键等特殊键；
- Ctrl/Alt/Meta 与其他键组成的组合键；
- 连续 printable 输入按默认 **1.5s gap** 聚合成一行。

这解释了为什么 `keys.txt` 很适合看：

- 终端命令；
- 代码输入密度；
- F9 / Ctrl+S / Ctrl+C / Ctrl+V；
- 大致阶段切换。

但它不是 raw 的无损文本化。

---

## 3. `keys.txt` 会静默丢掉哪些键盘事件 [P/source]

最关键的源码分支：

1. raw 先执行 `writer.event(code,value,now)`；
2. key-up 只更新状态，不写 human-readable；
3. Shift/Ctrl/Alt/Meta 单独按下时，只进入 `down` 集合，不写 human-readable；
4. 只有 modifier + 另一个非 modifier 键，才写成 `[CTRL+X]` 等。

因此：

> **`keys.txt` 没有一行 ≠ raw 没有键盘事件。**

Day3 原件已经出现真实例子。

文本回放从约：

- 36:45.8 的 Enter
- 到 46:29.7 的下一次 printable

看起来有约 9m44s“完全沉默”。

但 raw 在约 41:05.1～41:07.3 仍记录：

- Ctrl down；
- 多次 Ctrl auto-repeat；
- Ctrl up。

按住时间约 **2.18 秒**。

这一整段 modifier-only 行为不会进入 `keys.txt`。

所以以后统计“键盘空窗”必须：

`keys.txt` 用于可读行为
+
`events.jsonl` 用于确认真实 EV_KEY 空窗

不能只 grep `keys.txt`。

---

## 4. Day3 v1 没有 pause，所以“raw 空窗”的含义也要精确

这版只有：

- Ctrl+Alt+Q：stop
- Ctrl+C：进程中断

**没有 pause/resume 功能。**

因此，与后来的 `keystream_full_replay.py` / Replay v3 不同：

> Day3 的 raw EV_KEY 空窗不能解释成“用户主动暂停了 recorder”。

在上面那段区间中，raw 真正最长连续无 EV_KEY 的一段约为：

- t=2467.267
- 到 t=2789.702

长度约 **322.436 秒 = 5分22.4秒**。

这只能证明：

> 被选中的那个键盘设备在这段时间没有 EV_KEY。

它**不能**证明：

- 用户没有用鼠标；
- 没在浏览器/OJ/文件管理器操作；
- 没发生下载；
- 没看题面；
- 没切窗口；
- 没等待编译/加载；
- 没读代码；
- 没做口头思考。

---

## 5. v1 完全看不到的证据维度

源码没有：

- mouse capture；
- active-window probe；
- screen recording；
- clipboard content；
- file snapshots；
- file hash / file-change polling；
- process/compile log；
- browser/OJ DOM；
- filesystem watcher。

特别是 Ctrl+C / Ctrl+V：

采集器只知道：

> 某时刻按了 Ctrl+C / Ctrl+V。

它不知道：

- 复制的是什么；
- 从哪个窗口复制；
- 粘贴到哪里；
- 粘贴后文件内容是什么。

因此 Day3 的“复制/粘贴很多”只能作为行为定位信号，不能自动恢复源码版本。

---

## 6. checker.cpp 的来源：本轮从“未知”推进到“赛中获取” [E]

旧纪要留下欠账：

> checker 是赛前已有、赛中下载，还是赛中生成？

本轮把三类原件对齐：

### 文件元数据

旧 VM：

- `Desktop/checker.cpp`
- `Desktop/T2/checker.cpp`

两份：

- size = 3461 B
- SHA-256 = `14281b5f2127adce25edc1a980b52d5ff09c8f7520af914b8a0449c871311278`
- ZIP mtime = 2026-10-01 07:23:36

按 Day3 已验证的 VM ZIP 时间约 +12h 对齐北京时间：

> 约 19:23:36，即 keystream T+38:54 左右。

而 A 的 OJ 提交是 19:20:20，B 刚开始不久。

### 双 ASR 原文

同一音频的两份转写在 B 开始后明确出现：

- ~40:16：“还有个 checker”
- ~40:48：“既然提供了校验器……先把这些东西全下载下来”
- ~41:42：“Checker 读懂”
- ~44:10/44:19：明确读到“不验证，无解判断”

录音与 keystream 有约 2 分钟左右的起点偏移；把偏移考虑进去后，`checker.cpp` 文件出现时间与“下载这些东西”的语音窗口高度吻合。

### 键盘层

checker 出现的这一段恰好位于 v1 看不到鼠标/窗口的稀疏区。

因此当前最强、但不过度的结论是：

> **[E] 这份 checker 不是赛前 bag 里原有的旧验证器，而是在 Day3 B 进行过程中取得的随题/赛场提供资产。**

目前仍不能 [P] 写成：

- “一定从某 URL 下载”；
- “一定点了某个按钮”；
- “一定是官方作者提供的源码”。

因为 v1 没有 screen/window/browser provenance。

---

## 7. checker 源码在取得后没有被赛中改写 [P/source metadata]

`T2/checker.cpp` 的保存时间保持在约 19:23:36。

后来：

- T+1:58 左右已经调用 `./checker`；
- T+3:03～3:09 又进行最终 sample1～8 回归；
- 保留下来的 checker binary 时间约 21:48:58（最终一轮重新编译）；
- 但 `checker.cpp` 本身 mtime 没有随之变化。

结合两份 VM 快照和 SHA：

> [P/source metadata] **从取得这份 checker 源码到比赛结束，现有证据没有任何 checker.cpp 内容变化。**

因此 E-D3-007 里的 false-NO coverage hole 不是“后来不小心改坏 checker”造成的。

更准确的因果链是：

`赛中取得一个本来就只验证 YES construction 的 local checker`
→ 本人 44 分钟左右已经读到 NO 不验证
→ 后续仍把 checker green 心理升级成“AC”
→ false-NO 存活
→ 正式 B65。

---

## 8. 证据可靠性分层

### 可以较强证明

- 某个 EV_KEY 是否发生；
- key down/up/repeat；
- F9 / Ctrl+S / Ctrl+C / Ctrl+V 等键盘动作；
- 连续 printable 的近似文本；
- 采集器启动/结束时间；
- raw 的真实键盘空窗。

### 只能作为线索

- 输入发生在哪个应用；
- Ctrl+C/V 的内容；
- GUI 是否点击；
- 浏览器是否下载；
- 文件是否保存；
- 代码某一刻的完整内容；
- 鼠标操作；
- 用户是否“没干活”。

### 必须与别的证据交叉

- 源码版本：VM file / OJ source / file_changes；
- 窗口/UI：screen / Replay；
- 思路：录音；
- 正式提交：OJ record source；
- 文件取得来源：screen / browser/download provenance / 录音 + 文件时间。

---

## 9. 与后续 recorder 的演化关系

Day3 v1：
`keystream_linux.py`

解决：
> 有 raw EV_KEY + 基础 human-readable keyboard。

后来 `keystream_full_replay.py` 增加：
- active window；
- pause/resume；
- 更完整的 replay 文本。

再后来 contest replay recorder / capture 增加：
- screen；
- timeline；
- file_changes；
- manifest；
- AI_READ_FIRST；
- 更明确的证据读取顺序。

后续版本的详细源码审计见：

`tools/vm/Replay采集脚本_源码考古与能力边界.md`

本轮新增的历史结论是：

> **Day3 v1 的最大缺口不是“键盘没录全”，而是它只知道键盘，不知道键盘发生在什么 UI/文件状态里。**

这正是为什么 Day3 可以精确知道“什么时候按了什么键”，却很难仅凭 keystream 恢复：
- checker 下载/复制的完整 provenance；
- 中间源码每一版；
- 鼠标驱动的 IDE/浏览器行为。

---

## 10. 后续读取 Day3 keystream 的硬规则

1. 不得用 `keys.txt` 的文本空窗直接写“没有操作”。
2. 先查 raw JSONL 是否真无 EV_KEY。
3. 即使 raw 真空窗，也只能写“该键盘无 EV_KEY”，不能写“用户闲置”。
4. Ctrl+C/V 只证明组合键发生，不证明 clipboard 内容。
5. v1 没有 pause；不要把 raw 空窗解释成主动 pause。
6. 涉及 GUI / 下载 / 文件版本时，必须叠加 VM metadata、录音、OJ 或后续 Replay 证据。
7. Day3 checker 的 provenance 当前标 [E]“赛中取得”，不要升级成具体下载 URL 的 [P]。
