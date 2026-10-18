# Replay 采集脚本｜源码考古与证据能力边界

> 来源：2026-10-07 三包原始资料池。  
> 目的：不是评价“有没有录像”，而是回答 **每一种证据到底记录了什么、没记录什么、什么时候会撒谎，以及赛后 AI 应如何解释它。**

## 0. 结论先行

Replay v3 的总体方向是正确的：

```text
screen      → 当时看到了什么
timeline    → 当时做了什么（语义事件）
file_changes→ 保存到磁盘后的真实源码状态
raw_keys    → 精确键盘底层事件
recording   → 为什么这么想
```

但源码审计后必须补上 5 个边界：

1. **v3.0.0 的 Ctrl+Alt+P 并没有真正暂停 raw key 记录；**
2. **v3.0.0 的 ffmpeg x11grab 没设输入 framerate，可能先抓约 30fps 再用 filter 丢到 1fps，产生不必要 CPU 开销；**
3. **file_changes 不含启动时已有文件的 baseline 内容；**
4. **2 秒轮询无法证明每一次中间保存都被捕捉；**
5. **它主动跳过若干目录/大文件，所以 file_changes 不是完整文件系统审计日志。**

因此：
> Replay 是多层互补证据，不是单一“万能录像”。

---

# 1. 三代脚本演化

## Generation A：`keystream_full_replay_v2.py`

**来源**：
`模拟赛资料_03_共03包.zip!keystream_full_replay_v2.py`

SHA-256：

`9f174477bd8241ed687fc911a25dd09f207041fac82bdb493238870d2e028837`

能力：

- Linux EV_KEY；
- raw key；
- 语义键盘流；
- 活动窗口；
- pause/resume；
- self-test。

缺少：

- screen；
- file snapshots；
- clipboard 内容；
- AI_READ_FIRST。

一个重要事实：
**v2 在 pause 状态下会抑制 raw key 持久化。**

这后来成为审计 v3.0.0 pause 语义的重要对照。

---

## Generation B：`contest_replay_recorder.py`

**来源**：
`模拟赛资料_03_共03包.zip!contest_replay_recorder.py`

SHA-256：

`1e9bc3b54a4d9b8b5591666bbcd0393f0328f0c98482dfffb3be377e3ff923de`

新增：

- screen 录像；
- clipboard；
- video/disk guard；
- 比 keyboard-only 更完整的赛场上下文。

仍缺：

- 保存文件版本链；
- AI_READ_FIRST；
- v3 那套完整 session manifest / evidence reading protocol。

这一代说明演化目标已经从“统计键盘”转成“恢复赛场”。

---

## Generation C：`contest_replay_capture.py` v3.0.0

**来源**：

- `模拟赛资料_02_共03包.zip!contest_replay_capture.py`
- `模拟赛资料_01_共03包.zip!虚拟机(2).zip!虚拟机/Desktop/contest_replay_capture.py`
- VM 内 `Desktop/bag/contest_replay_capture.py`

三份 SHA-256 相同：

`7cdacb9042e630305ed070c9564fc9daab11d99ed6037dbc3bc9ca03d96bcc3e`

说明顶层单文件与 VM 中实际使用副本可以交叉认证。

新增能力：

- `timeline.txt`
- `file_changes.jsonl`
- segmented screen
- raw keys
- manifest
- `AI_READ_FIRST.txt`
- `AI_TEXT_BUNDLE.txt`
- source file tracker
- disk / video guard
- self-test

这是目前三代里最完整的 recorder。

---

# 2. [P] v3.0.0 pause/raw privacy 语义错误

## 用户可见承诺

源码说明写：

```text
Ctrl+Alt+P Pause/resume keyboard and clipboard logging.
```

直觉上“暂停 keyboard logging”应包括 raw keyboard。

## 实际调用顺序

v3.0.0 主循环：

```python
event_now = writer.elapsed()
writer.add_raw_key(event_now, code, value)
action = decoder.feed(code, value, event_now)
```

而 `decoder.feed(...)` 内部才检查：

```python
if self.paused:
    return None
```

因此：

```text
raw_keys.jsonl   ← 先写
decoder.pause    ← 后检查
timeline/TYPE    ← 被抑制
```

结论 [P/source]：

> **v3.0.0 pause 时 semantic timeline 停了，但 raw_keys 仍持续记录 EV_KEY。**

这不是推测，是控制流直接推出的事实。

## 为什么危险

这会同时造成两个问题：

### 证据解释

看到 pause 区间存在 raw key，
不能得出“用户没有暂停”。

### 隐私语义

用户主动触发 pause，却仍留下底层按键，不符合 hotkey 文案表达的隐私预期。

---

# 3. [P] file_changes 的 baseline 缺口

`FileTracker._seed_state()` 启动时只建立现有文件 fingerprint 状态。

它**不会把启动前已经存在的文件内容全部写一份 initial snapshot**。

所以：

- 比赛开始 recorder 前已经写好的源码；
- 预先存在的 notes；
- 已经放在 Desktop 的文件；

如果之后从未修改，它们可能不会出现在 `file_changes.jsonl` 的内容版本链中。

结论：

> “file_changes 没出现某文件” ≠ “那个文件当时不存在”。

需要和 VM 最终快照 / screen / 其他归档交叉验证。

---

# 4. [P] 2 秒轮询意味着版本链不是逐保存完备日志

FileTracker 默认约每 2 秒 scan 一次。

因此理论上会漏：

- 2 秒内连续两次或更多保存的中间版本；
- 2 秒内 create → modify → delete 的短命文件；
- 编辑器未落盘状态。

所以：

> `file_changes` 的一个版本是“被轮询观察到的落盘状态”，而不是“每一个 Ctrl+S 的事务日志”。

它仍然是非常强的证据，但证据含义必须写对。

---

# 5. [P] 主动排除项：file_changes 不是整个 Desktop 镜像

源码主动跳过：

- `.git`
- `.cache`
- `node_modules`
- `build`
- `dist`
- `__pycache__`
- `contest_capture`
- `.local`
- `.config`
- hidden dirs
- 名称以 `sample` 开头的目录
- 名称以 `attachment` 开头的目录

同时只跟踪指定文本扩展名，并设：

- 单文件 snapshot 上限约 512 KiB。

因此：

> sample 包、附件包、二进制输出、超大文本文件可能只在 screen/VM/其他归档中存在，不能要求 file_changes 自己证明它们。

这个边界对 Coderlands tree 的“下载错误样例包”尤其重要：
那类 sample material 本来就更依赖 Replay screen + VM 文件，而不是 FileTracker。

---

# 6. Clipboard / TYPE 的语义边界

## Clipboard

v3 语义化 PASTE 依赖：

- Ctrl+V；
- 可用的 `xclip` / `xsel`。

因此鼠标中键、菜单粘贴、某些 IDE 特殊 paste 不保证进入同一种 PASTE 事件。

## TYPE

TYPE 是“输入动作流”，不是最终文本状态。

光标移动、鼠标改位置、Backspace/Delete、Undo/Redo、整块替换，都可能让：

```text
TYPE stream != final source file
```

所以最终源码以：

1. `file_changes` 保存状态；
2. 正式提交源码；
3. screen 未保存状态

做交叉确认。

---

# 7. Screen 的独立失效模式

screen recorder 有独立 video size / disk guard。

因此可能出现：

```text
screen stopped
timeline/file_changes still running
```

同样，ffmpeg 异常也不等于整个 recorder 停了。

赛后如果 screen 尾段缺失，必须先看 manifest / timeline status，
不能直接判断“后半场没有操作”。

---

# 8. [E] ffmpeg 输入帧率的 CPU 风险

v3.0.0 构造 ffmpeg：

```text
-f x11grab ...
-i DISPLAY
-vf fps=1,...
```

但没有在 x11grab 输入端传：

```text
-framerate 1
```

本地 ffmpeg help 验证 x11grab 的默认 framerate 为 `ntsc`（约 29.97fps）。

因此当前实现可能：

```text
先从 X11 抓 ~30fps
→ 再通过 vf=fps=1 丢掉绝大多数帧
```

这对比赛 VM 是不必要的 CPU 压力。

证据等级标为 **[E]** 而非直接写死比赛机事实：
本地当前 ffmpeg 已验证该默认值，但具体比赛 VM 的 ffmpeg build 后续仍可从 VM 环境再钉一次。

对照：
中间代 `contest_replay_recorder.py` 已经把低帧率直接传给 input。

---

# 9. v3.0.1 修复方案

本轮形成最小修复：

1. VERSION `3.0.0 → 3.0.1`；
2. raw key 写入移动到 `KeyDecoder.feed` 的 pause 检查之后；
3. release event 在非 pause 时仍记录，保持 raw replay 完整性；
4. modifier state 在 pause 时继续维护，以便 Ctrl+Alt+P 能恢复；
5. 增加 pause privacy regression self-test：
   - pause 中输入 `a`：timeline/raw 均不得出现；
   - resume 后输入 `b`：timeline/raw 均必须出现；
6. x11grab input 增加 `-framerate self.fps`；
7. 保留后续 `vf=fps=...` 作为输出节流的双保险。

本地验证：

- `python -m py_compile`：PASS；
- v3 self-test：PASS；
- patched SHA-256：
  `c51406265925fed1cf9169f240c71ea025c8906687ed2ac652c6ac0821d53754`。

仓库补丁：
`tools/vm/replay_recorder/contest_replay_capture_v3.0.1.patch`

---

# 10. 证据等级使用规则

| 事实 | 等级 | 原因 |
|---|---|---|
| v3.0.0 pause 仍写 raw EV_KEY | [P] | 由源码控制流直接推出 |
| FileTracker 无 baseline snapshot | [P] | 初始化实现直接可见 |
| 2s polling 不能覆盖所有中间状态 | [P] | sampling 机制本身决定 |
| sample*/attachment* 被跳过 | [P] | skip 规则直接写在源码 |
| x11grab 未传 input framerate | [P] | 命令构造直接可见 |
| 默认可能约 29.97fps | [E] | 当前 ffmpeg help 实测；VM build 待再核 |
| screen 缺段即“没有操作” | [X] | recorder 各通道可独立继续 |
| raw key pause 区间可证明“未暂停” | [X] | v3.0.0 bug 直接反驳 |

---

# 11. 对赛后考古的直接影响

以后读取 v3.0.0 capture：

```text
timeline silence
+ raw key activity
```

首先检查是否处于 pause 区间，不能把两者冲突直接归因给用户行为。

同时：

```text
file_changes missing
```

必须区分：

- 文件从未修改；
- 文件在 recorder 启动前已存在；
- 被 skip；
- 大于 snapshot 上限；
- 两次 scan 间短暂存在；
- 编辑尚未保存。

因此最稳的证据组合仍是：

```text
录音为什么
× timeline 做了什么
× file_changes 落盘成什么
× screen 当时看见什么
× OJ/正式目录最后交了什么
```

这才是 Replay v3 真正的“证据链”，而不是把任何一个通道神化成绝对真相。
