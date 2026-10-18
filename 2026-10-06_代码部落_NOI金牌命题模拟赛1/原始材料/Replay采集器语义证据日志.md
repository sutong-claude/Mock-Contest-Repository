# Coderlands 主 Replay｜采集器语义证据日志

> 对应比赛：2026-10-06 代码部落 NOI 金牌命题模拟赛1  
> capture：`contest_capture/20261006_135420`  
> 状态：append-as-you-read 的工具层证据日志。  
> 注意：这里记录 **Replay 本身的证据边界**，不公开 raw keyboard、clipboard、screen 原件。

## E-CL-014｜主 capture 与 v3.0.0 源码完成同源认证

**来源**：

1. `模拟赛资料_01_共03包.zip!虚拟机(2).zip!虚拟机/Desktop/contest_capture/20261006_135420/manifest.json`
2. `模拟赛资料_01_共03包.zip!虚拟机(2).zip!虚拟机/Desktop/contest_replay_capture.py`
3. `模拟赛资料_02_共03包.zip!contest_replay_capture.py`
4. 仓库既有 `资料完整性报告.md`

**证据等级：[P] / 文件哈希交叉认证。**

两份 recorder 源码 SHA-256 完全一致：

`7cdacb9042e630305ed070c9564fc9daab11d99ed6037dbc3bc9ca03d96bcc3e`

manifest 标记 recorder version 为 `3.0.0`，capture 开始/结束：

- 2026-10-06T13:54:21
- 2026-10-06T17:50:43
- stop reason：Ctrl+Alt+Q

因此本场 Replay 的采集语义可以直接按该 v3.0.0 源码审计，而不是凭文档猜。

---

## E-CL-015｜[P] Pause 区间 raw key 仍会被写入

**来源**：v3.0.0 `contest_replay_capture.py` 控制流。

主循环先执行：

```python
writer.add_raw_key(event_now, code, value)
```

随后才：

```python
action = decoder.feed(code, value, event_now)
```

而 pause 检查在 `decoder.feed` 内。

所以：

> Ctrl+Alt+P 暂停后，semantic TYPE/KEY/PASTE 会停，但 `raw_keys.jsonl` 仍会继续收到 EV_KEY。

### 对本场考古的影响

以后若在 `20261006_135420` 中看到：

```text
timeline 静默
raw_keys 仍有事件
```

**不能**直接解释成“用户没有暂停”或“timeline 丢包”。

应先检查 pause/resume status。

这是一条 recorder 自身的已证明语义缺口，而不是选手行为结论。

---

## E-CL-016｜[P] file_changes 缺失不能证明“文件不存在”

v3.0.0 `FileTracker`：

- 启动时只 seed fingerprint；
- 不写现有文件 baseline 内容；
- 约 2 秒轮询一次；
- 跳过 `sample*` / `attachment*` 等目录；
- 只跟踪指定文本扩展名；
- 单文件 snapshot 有约 512 KiB 上限。

所以 `file_changes.jsonl` 没有某个对象，至少有多种解释：

1. recorder 启动前它已经存在且后续没改；
2. 它位于被 skip 的目录；
3. 它不是跟踪扩展名；
4. 它超过 snapshot 上限；
5. 它在两次扫描之间短暂创建/修改/删除；
6. 编辑器状态还没保存。

### 与 tree 样例事故的关系

本场 tree 错格式 sample 包来自下载目录/样例材料。

由于 recorder 本来就会跳过一部分 sample/attachment 目录，
该事故必须继续依赖：

- Replay screen；
- VM 实体文件；
- shell/运行痕迹；

而不能要求 `file_changes` 单独承担证明责任。

这进一步支持现有 E-CL-010 的多证据结论。

---

## E-CL-017｜[P] TYPE 不是最终源码；保存版本仍以 file_changes/正式目录为准

TYPE stream 记录的是输入动作，不是编辑器最终状态。

鼠标移动光标、Backspace/Delete、Undo/Redo、选区替换都可以使：

```text
输入动作序列 ≠ 最后源码文本
```

因此本场 net/game/core/tree 的“第几代代码”仍以：

1. `file_changes.jsonl` 捕捉到的保存状态；
2. 正式提交目录；
3. screen 中未保存状态；

交叉确定。

raw key 只用于补精细动作，不得反向覆盖已落盘源码事实。

---

## E-CL-018｜[E] v3.0.0 screen 采集可能有额外 CPU 浪费

v3.0.0 ffmpeg 命令在 x11grab 输入端没有显式 `-framerate 1`，
而是后续用 `vf=fps=1` 降帧。

本地 ffmpeg help 已验证 x11grab 默认 framerate 为 `ntsc`（约 29.97fps）。

所以存在：

```text
输入端先抓约30fps
→ filter 再丢到1fps
```

的 CPU 浪费风险。

**证据等级：[E]**：
源码未传 input framerate 是 [P]；
但本场 VM 的具体 ffmpeg build 默认值仍待从 VM 二进制/帮助输出进一步钉死。

这条结论当前只用于 recorder 工程改进，
**不用于解释任何一道题的算法表现**，避免过度归因。

---

## E-CL-019｜v3.0.1 最小修复已经独立验证

本轮形成补丁：

`tools/vm/replay_recorder/contest_replay_capture_v3.0.1.patch`

修复：

- pause 时 raw key 也不落盘；
- resume hotkey 仍可识别；
- x11grab 输入端直接使用目标低帧率；
- self-test 增加 pause privacy regression。

本地：

- py_compile：PASS；
- recorder self-test：PASS；
- patched source SHA-256：
  `c51406265925fed1cf9169f240c71ea025c8906687ed2ac652c6ac0821d53754`。

这不改变已经录制的 `20261006_135420`，
只修正以后新 capture 的行为。

---

## 本日志带来的解释规则

对本场 Replay：

> **screen / timeline / file_changes / raw_keys 各有独立缺口，任何一个通道都不能单独升级成“完整赛场真相”。**

最强组合仍是：

```text
录音（为什么）
× timeline（做了什么）
× file_changes（保存成什么）
× screen（当时看见什么）
× VM/正式目录（最终留下什么）
× OJ（最终交付/得分）
```

后续继续处理 `20261006_135420` 时，若发现某个通道互相矛盾，应先按本日志排查 recorder 语义边界，再推断选手行为。
