# Day3 keystream 高信息片段｜checker 假安全链

> 原件：
> - `模拟赛资料_03_共03包.zip!虚拟机(1).zip!虚拟机/Desktop/Day3/keystream/keys_20261001_184442.txt`
> - 同目录 `events_20261001_184442.jsonl`
> - `Desktop/Day3/T2/AC.cpp`
> - `Desktop/Day3/T2/checker.cpp`
> - `Desktop/Day3/T2/sample1..8.in/out`
>
> raw keyboard 不公开；这里只保存脱敏后的操作级结论与可重复验证结果。

# 1. 这份 keystream 是真实赛场长记录

- Start：2026-10-01 18:44:42
- End：2026-10-01 22:47:32
- raw EV_KEY events：**32,890**
- human-readable key stream：约 **185 KB**

它属于 Day3 VM 血缘中已归档到 `Desktop/Day3/` 的原始证据。

# 2. 两段高密度 checker 使用

## T+1:56～2:09

键流明确记录：
- `g++ AC.cpp -o AC -O2`
- 运行候选生成 `ans.out`
- 多次执行 `./checker sampleX.in ans.out`
- sample1 → sample4 连续手工核验

这说明：
> Day3 B 后半段不是“完全没验证”，而是已经开始建立本地候选 + checker 工作流。

## T+3:03～3:09

又出现更完整的一轮：
- 先误打 `g++ AC.cpp -o AC -=O2`，随后立即修正；
- 编译 `checker.cpp`；
- 依次运行 sample1～sample8；
- 对每个 sample 先跑候选，再喂给 checker。

这是明确的“官方样例批量回归”行为。

# 3. checker 的能力边界写在源码第一行

`checker.cpp` SHA-256：

`14281b5f2127adce25edc1a980b52d5ff09c8f7520af914b8a0449c871311278`

源码注释：

```cpp
// Local construction checker: checker <input_file> <output_file>
// NO is skipped. This program does not decide whether a solution exists.
```

遇到候选输出 `NO` 时：

```cpp
if (verdict == "NO") {
    cout << "Skipped (NO is not verified)\n";
    ++skipped;
    continue;
}
```

最后甚至明确打印：

```
NO answers are not verified; this is not a full verdict.
```

因此 [P/source]：
> 这个工具只能验证 YES 构造是否合法；不能验证 NO 判定是否正确。

# 4. 直接重放 8 份官方样例：checker 全绿，但 sample7 已有现成反例

本轮使用 VM 原件重新编译：

- `AC.cpp` SHA：
  `3b8d3e5cdc0b4703b94fe06dba344a8eb654e325ffaab1d15970eca1a555a4ed`
- `checker.cpp` SHA：
  `14281b5f2127adce25edc1a980b52d5ff09c8f7520af914b8a0449c871311278`

两者均 `g++ -O2 -std=c++17` 编译成功。

对 sample1～sample8：
- 候选全部正常运行；
- checker 对 8 份样例都返回 exit code 0；
- 所有候选 YES 构造均被判合法；
- 候选 NO 全部被跳过。

但是只比较每个测试的 **YES/NO verdict token** 与官方 sample output：

| sample | verdict 是否一致 |
|---|---|
| 1 | ✅ |
| 2 | ✅ |
| 3 | ✅ |
| 4 | ✅ |
| 5 | ✅ |
| 6 | ✅ |
| 7 | **❌ 第4个 case** |
| 8 | ✅ |

## sample7 的决定性反例

候选输出：

```
YES 125000 187500
NO
NO
NO
```

官方输出：

```
YES 1 62501
NO
NO
YES 62528 125010
```

也就是说第4个测试：

```
candidate: NO
official:  YES ...
```

但本地 checker 输出：

```
Test Case #4: Skipped (NO is not verified)
...
All checked constructions are valid.
NO answers are not verified; this is not a full verdict.
```

并返回 exit code 0。

[P + E] 这不是“理论上 checker 可能漏错”，而是：

> **官方样例本身已经包含一条候选 false-NO 反例，而赛时使用的 checker 恰好把它跳过了。**

# 5. 为什么这条证据比“checker 不完整”更重要

旧结论只是：
> NO 不验证，所以 checker 不能当完整 oracle。

现在因果链可以写得更具体：

```
候选在 sample7 case4 真错
↓
错误类型恰好是 false NO
↓
checker 设计上 skip NO
↓
整份 sample7 checker exit=0
↓
多轮“全样例验证”仍可能产生错误安全感
```

这解释了：
- 为什么赛时已经做了大量验证动作；
- 为什么这些动作没有杀死错误模型；
- 问题不是“完全没验证”，而是**验证器的覆盖面与错误类型错位**。

# 6. 新的 verifier 契约

以后构造题 checker 至少拆成两层：

## 层1：construction validator

验证：
- YES 给出的构造是否有效。

这就是 Day3 checker 已经做对的部分。

## 层2：existence oracle / NO validator

对小数据：
- brute 枚举所有区间/构造；
- 判断是否存在答案；
- candidate NO 必须和 oracle 对比。

正式回归条件：

```
candidate YES -> validator must accept
candidate NO  -> oracle must prove no solution
```

不能再用：

```
checker exit 0
=> 整题 verdict 正确
```

# 7. 赛时机会成本的重新评价

Day3 B 的问题不是简单“应该写 checker”。

事实上：
- checker 写了；
- checker 编译了；
- checker 连续跑了多个官方样例；
- 后段甚至 sample1～8 批量跑完。

真正缺口是：
> **checker 自己没有覆盖 false-NO，而没有另一个 brute/oracle 检查它。**

因此更准确的下一场触发器：

> 一旦 checker 中出现 `Skipped` / `not verified` / 某一类 verdict 不校验，就必须给这类输出补独立 oracle；否则“全绿”只能证明被检查的那一半。

# 8. 后续继续挖

- 把 sample7 case4 压成更小反例，和现有 B 最小反例库交叉；
- 对 T+1:56 与 T+3:03 两轮 checker 运行之间的源码版本差异做精确恢复；
- 对照录音找出“已 AC/样例全过”类判断发生在哪个时间点；
- 恢复 checker 是赛前已有、赛中下载还是赛中生成，并确认其来源可信度。
