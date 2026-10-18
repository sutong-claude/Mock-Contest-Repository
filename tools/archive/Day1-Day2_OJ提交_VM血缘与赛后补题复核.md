# Day1-Day2｜OJ 正式提交 × VM 版本映射与赛后补题血缘

> 证据来源：
> - 三包原始 VM ZIP 的 central-directory 文件时间；
> - OJ record source（download / rendered record page 两条路径交叉）；
> - 原题附件与 checker；
> - 本轮独立编译、重放、穷举验证。
>
> 本文件专门解决：
> **“赛时到底交了哪个文件？”、“VM 最终文件是不是提交版？”、“赛后 100pts/70pts 文件夹名能不能直接信？”**

# 1. Day1：两次正式提交都已 exact 映射

## A 记录带｜20 TLE

OJ record：
- id：`6ab6745fb8c09340fef1c02c`
- 2026-09-25 21:17:19
- TLE，20 分

正式 OJ source 与 VM 两个路径逐字规范化 **EXACT**：
- `Day1/problems/T2.cpp`
- `Day1/5622 蜗蜗的记录带/T2.cpp`

两者本身也是同内容副本。

### 文件名反常但证据明确

A 正式提交主体的本地文件名是 **T2.cpp**，而不是 T1.cpp。

因此以后不能靠：
- 题号目录；
- 文件名 T1/T2；
- “看起来应该是哪题”

推断 submitted source。这里必须以内容 hash / exact source mapping 为准。

ZIP central-directory 时间：
- 该 exact 文件：2026-09-25 09:10:14
- OJ submit：21:17:19

这份 VM ZIP 的 central timestamp 与北京提交时刻在 Day1/Day2/Day4 多个 exact file 上都呈现约 **+12h** 对齐关系；详见后文“时间戳修订”。

### 逐点

A：
- subtask #1：20 分全 AC；
- #2 开始 TLE；
- 后续因 group early-stop 大量 Cancelled。

所以“20分”是一个稳定速度边界，不是随机混分。

---

## B 联动面板｜25 WA

OJ record：
- id：`6ab6875ab8c09340fef21c9a`
- 2026-09-25 22:38:18
- WA，25 分

正式 source **EXACT**：
- `Day1/5623 蜗蜗的联动面板/T2.cpp`

ZIP central timestamp：
- 10:37:22
- 按该 VM 的 +12h 对齐 → 22:37:22
- 距正式提交仅约 **56 秒**

所以这是非常强的“最后本地版本 = scored source”证据。

# 2. Day1 B：最后约 13 分钟的 patch 真正换来了 15 分

更早的：
- `Day1/T2.cpp`
- central timestamp 10:24:26

与最终提交主体的主要差异只有新增：

```cpp
if (n <= 2) {
    cout << 1 << '\n' << 1 << '\n';
    return;
}
if (n <= 3) {
    cout << 3 << '\n';
    cout << "1 1 1" << '\n';
    return;
}
```

也就是：
> 最终提交前约 13 分钟加入 n≤2 / n≤3 hardcode。

## 原附件 48 case 独立重放

用题目 checker 语义独立模拟：

### 修改前 root/T2.cpp
- 通过 27 / 48
- 失败 21

### 最终 submitted source
- 通过 31 / 48
- 失败 17

更重要的是按附件分组：

### subtask 2：`a_i=i`，10 分
修改前已经 14/14 通过。

### subtask 3：`a_i=1`，15 分
修改前：
- 11/14 通过；
- n 很小的 3 case 因 K 错误而失败。

最终提交：
- **14/14 全过**。

OJ 实际：
- subtask #2 Accepted 10；
- subtask #3 Accepted 15；
- 合计正好 **25**。

因此可以建立非常强的因果链：

```
最后约13分钟加入 n<=2/3 special
→ 修掉 all-ones 子任务里的3个小 n case
→ subtask3 从“组内有错=0分”变成 15分全拿
→ 实际 OJ 总分 10+15=25
```

这不是无效 patch。

## 但根模型仍然错

代码里：

```cpp
bool ok1 = true, ok2 = true;
...
if (a[i] != 1) ok2 = false;
```

然而 `ok2` **之后完全没有被使用**。

除 `ok1 (a_i=i)` 外，所有输入几乎都直接走：
> 输出 YES + 一套为 all-ones 特判设计的固定操作。

所以：
- subtask 2：身份排列 special 正确；
- subtask 3：all ones special 正确；
- general small：仍会对 infeasible instance 报 false YES。

OJ #1 的明确错误：
`reported YES for an infeasible instance`

说明“25分”应准确归因于：
> **两个 special 子任务被吃掉，不是 general construction 已经接近正确。**

# 3. Day2：六次正式提交的本地身份

| 提交 | OJ结果 | 本地映射 |
|---|---|---|
| A1 `6ab89f59...` | RE0 | **EXACT** `time.cpp` |
| A2 `6ab8a45c...` | WA0 | `time.cpp` 主体完全相同，仅 OJ 版打开 `multiply.in/out` |
| A3 `6ab8ab17...` | AC100 | `duipai_T1/wa.cpp` 主体相同，仅 OJ 版打开 `multiply.in/out` |
| C `6ab8aef5...` | TLE30 | `debug/main.cpp` 主体相同，仅 OJ 版打开 `chess.in/out` |
| D1 `6ab8b124...` | TLE0 | 最终 D 版本加入 `solve2` 前的早期 brute source；VM final 已不再 exact |
| D2 `6ab8b32a...` | CE0 | `problems/T4.cpp` 主体相同，仅 OJ 版打开 `wolf.in/out` |

# 4. Day2 A 第一交：旧复盘核心结论被更强证据推翻

旧复盘曾写：

> A 第一交 RE，是因为提交了 `problems/T1.cpp`，其中
> `while (point <= n || a[point] != 1)`
> 造成越界。

三包原件现在证明这个说法 **[X/obsolete]**。

## 强证据

OJ record `6ab89f59...` 的：
- download source；
- rendered record page source；
- 09/28 归档；
- 10/05 归档；

四条路径都一致显示：

```cpp
while (point <= n && a[point] == 1)
    point++;
```

并且整份 OJ source **EXACT 等于 VM 的 `time.cpp`**。

它的 freopen 是：

```cpp
//freopen ("multiply.in", "r", stdin);
//freopen ("multiply.out", "w", stdout);
```

而 A 第二交 source 与第一交算法主体一致，唯一关键 diff 是：

```diff
- //freopen ("multiply.in", "r", stdin);
- //freopen ("multiply.out", "w", stdout);
+ freopen ("multiply.in", "r", stdin);
+ freopen ("multiply.out", "w", stdout);
```

OJ verdict 同时发生：

```
A1: RE
→ 只打开 traditional IO
A2: WA
```

### 修订结论 [P/source + causal]

因此：
1. `problems/T1.cpp` 中确实存在 `||` 越界 bug；
2. 但**那份不是 A 第一交正式 OJ source**；
3. 第一交实际交的是安全 `&&` 的 `time.cpp` 主体；
4. A1→A2 算法主体没有变化，唯一实质 source diff 是 traditional IO；
5. 所以第一次 RE 应归到 **delivery / traditional file IO 层**，不能再归因于 `||` 数组越界。

这和 Day5 C 的：
`RE → 打开正确 IO → WA`
属于同类证据分层。

# 5. Day2 D：第一交与第二交是“早期 brute → 未编译新 special”

D1 正式 source：
- 只有 brute；
- mask 转 wolves：

```cpp
while (t != 0) {
    wolves.push_back(t % 2);
    t /= 2;
}
```

而 `isValid` 第一行要求：

```cpp
wolves.size() == n
```

因此只有最高 bit 已经到第 n 位的 mask 才可能被验证，也就是有效搜索只覆盖约一半 mask 空间。

D2：
- 在此基础上插入 `if (n > 20) solve2(n);`
- 但 `solve2` 定义在 `solve` 之后且无前置声明；
- 正式 CE。

VM final 与 D2 主体一致，仅 freopen 又被注释回去。

这证明：
> Day2 D 的提交链是“早期 brute 本体真的被提交 → 最后临时加 special → 没 final compile”，不是赛后总结猜出来的。

# 6. VM ZIP 时间戳的修订

旧 Day2 报告曾写：
> 桌面导出 ZIP 时间 +8h = 北京时间。

对当前三包中的原始 VM ZIP central directory，这条不能继续照搬。

多个 exact mapping：

- Day1 B：10:37:22 → OJ 22:38:18
- Day2 D final：02:09:22 → OJ 14:09:46
- Day4 B：10:16 左右 → OJ 22:16 左右

都稳定表现为：
> **VM central time + 约12h ≈ 北京 OJ 时间**

更合理的解释是：
- VM/打包环境当时处于 UTC-4 / EDT 类本地时间；
- ZIP central directory 保存的是该本地时间字段。

因此后续必须写：
> **时间偏移要对具体归档版本用 exact submission 对齐校准，不能全局假定 +8 或 +12。**

旧报告中的 +8 可以作为“早期提取层观察”保留，但不能再作为三包 VM ZIP central timestamps 的事实。

# 7. 赛后补题资产：文件名不能代替验证

## Day1 `A_100pts/main.cpp`

时间晚于正式比赛，属于赛后补题。

本轮验证：
- 原附件 5/5 exact；
- n=1..7 **全部排列共 5,913 个实例**；
- 独立 brute 枚举所有翻转区间求最大逆序对；
- mismatch = **0**。

证据等级：
> [E] 高可信赛后正解实现；不是赛时能力证据。

## Day1 `T2_100pts/main.cpp`

本轮：
- 原附件 48 case 全部输出合法；
- 其中 38 YES / 10 NO，与 checker criterion 对齐；
- 再枚举 n≤7、值域 1..n+1 的所有非降数组：
  **4,706 个实例**；
- 对 YES：K、每个操作、最终排列逐步模拟；
- 对 NO：feasible criterion 核验；
- **0 mismatch**。

证据等级：
> [E] 高可信赛后补题实现。

## Day2 `T2_100pts/main.cpp`

时间为赛后 09/29。

本轮用 B 字符串题 5 份官方/附加 sample：
- sample1..5
- **5/5 输出逐 token exact**。

这是一个真实的赛后满分候选资产，但当前未把它冒充 OJ-AC；后续若需要满分实现级证明，应再加独立 brute/stress。

## Day2 `T3_70pts/main.cpp`

虽然目录名叫 `T3_70pts`，但源码主体只是：
- 读入；
- 判断两个 special flag；
- `if / else if / else` 三个分支 **全部为空**；
- 最终无答案输出。

所以：
> **它是未完成/占位资产，不是“70分代码”。**

这条是“名字不是证据”的直接实例。

# 8. 新的资产分类硬规则

以后 VM 里看到：
- `100pts`
- `AC.cpp`
- `70pts`
- `正解`
- `WA.cpp`

只能先当 **label**。

必须再问：
1. 时间是在赛中还是赛后？
2. 是否 exact 对齐 OJ source？
3. 是否有 OJ score？
4. 是否有附件/独立 brute/stress？
5. 文件名与源码实现是否一致？

推荐分类：

```
SCORING_SOURCE   = 正式 OJ source
IN_CONTEST_ASSET = 赛中保存但未必提交
POSTCONTEST_E    = 赛后且独立验证
POSTCONTEST_H    = 赛后未充分验证
PLACEHOLDER      = 名字强但主体未完成
```

这比“按文件夹名判断完成度”可靠得多。
