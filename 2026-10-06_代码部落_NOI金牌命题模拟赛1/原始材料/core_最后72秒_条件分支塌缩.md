# core 最后72秒｜“先判 EMPTY”条件如何塌缩成无条件输出

> 原始证据：
> - capture `20261006_135420/timeline.txt`
> - `file_changes.jsonl`
> - 双 ASR 原始录音
> - 工作区 T3 与正式目录 `ZJ-029658/core/core.cpp`
> - 赛后已证明的 `core_Trie容量证明.md`
>
> 目的：把“core 最后只输出 EMPTY”从一句结果，恢复成**正确局部方向 → 条件未物化 → 紧急交付时条件丢失**的完整过程。

# 1. 赛时并不是完全没有 core 数学入口

录音约 02:29～02:37：

1. 开始读 core；
2. 很快识别 LCP / 前缀结构适合 Trie；
3. 主动先问：
   > 能不能让最优 L=0？
4. 进一步把 EMPTY 当作第一目标；
5. 真正卡住的是：
   > 选 k 个字符串时，怎样描述 Trie 各前缀子树的可选容量？
6. 判断 full 成本高，切去 tree。

约 02:45 又短暂回来，仍明确表达：

> “尽可能先让它空串……先看能不能，如果不能再想办法。”

因此赛时的第一层策略其实是健康的：

```
先判最优值 L=0
→ 若可行，直接 EMPTY
→ 否则再进入更深 Trie
```

问题不是“完全不知道 EMPTY 为什么出现”。

# 2. L=0 的判定其实非常便宜 [P]

赛后 full 证明已经给出：

```
globalCapacity[0]
= #长度<=0的输入串
+ #深度1的 Trie 节点
```

输入字符串非空时第一项为0。

所以：

```
globalCapacity[0]
= 不同首字符的数量
```

而“最大 pairwise LCP ≤ 0”等价于：
> 任意两条被选字符串首字符不同。

因此对于 k≥2：

```
EMPTY 可行
iff
不同首字母个数 >= k
```

这甚至不需要真正建 Trie：

```cpp
bool seen[26] = {};
int cnt = 0;
for each s:
    if (!seen[s[0]-'a']) {
        seen[s[0]-'a'] = true;
        cnt++;
    }
if (cnt >= k) cout << "EMPTY";
```

时间 O(n)，额外空间 O(26)。

这说明：
> **赛时已经摸到了一个可以在几十秒内物化的精确 special。**

# 3. 但这个“if”从未进入代码

FileTracker 的 core/T3 只有三次保存。

## v0｜T+03:41:04｜345B

只有：
- `n,k`
- 字符串数组
- 读入 n 个字符串

没有任何判定。

## v1｜T+03:41:23｜373B

新增的核心只有：

```cpp
cout << "EMPTY" << '\n';
```

仍然：
- 不统计首字符；
- 不看 k 是否可由不同首字符满足；
- 没有任何 `if`。

## v2｜T+03:41:37｜377B

只再补：
- `core.in`
- `core.out`

算法仍是无条件 EMPTY。

最终正式：
`ZJ-029658/core/core.cpp`
在 T+03:42:12 创建，SHA 与 v2 一致。

所以 [P/source]：

> **“先判断 EMPTY 是否可行”这个赛时正确局部思路，从未被翻译成程序条件；最后代码把条件分支的输出值直接提升成了全局答案。**

# 4. 最后72秒逐事件

Replay：

- 03:40:35：回到 T3/main.cpp；
- 03:41:04：第一次保存读入框架；
- 03:41:07：开始敲 `cout << "`；
- 03:41:14：出现 `EMP`；
- 03:41:16：补成 `EMPTY`；
- 03:41:23：保存；
- 03:41:33：开始补 `core` 文件名；
- 03:41:37：保存；
- 03:41:56：Ctrl+A；
- 03:42:00：Ctrl+C；
- 03:42:02：粘到新的 Code::Blocks 未命名文件；
- 03:42:09：Save As；
- 03:42:12：正式目录 `core/core.cpp` 创建。

之后直到比赛结束：

- 没有 core/T3 的 F9；
- 没有 g++ core；
- 没有运行 core；
- 没有样例输入；
- 没有 diff/checker；
- 没有新的 core 源码 save。

因此正式 core 文件的状态是：

```
CODED
→ COPIED_TO_DELIVERY
→ NEVER_COMPILED
→ NEVER_SAMPLE_TESTED
```

而不是 VERIFIED/FROZEN。

# 5. 这不是“写了 Trie 但实现 Bug”

core0 的准确错因不能写成：

> “Trie 没写对。”

因为赛时根本没有进入 Trie 实现。

也不能只写：

> “最后为了骗分无条件输出 EMPTY。”

因为这会抹掉前面已经出现的正确数学分层。

更准确的过程：

```
[P方向] LCP → Trie
→ [P方向] 先检查 L=0 / EMPTY
→ [H/unfinished] 不知道怎样处理一般 k-selection capacity
→ 切 tree
→ 最后72秒回 core
→ 没有重新恢复“EMPTY 的可行条件”
→ 只留下 branch payload: EMPTY
→ 未编译 / 未样例
→ 正式0分
```

这是一个很典型的：

> **CONDITION_DROPPED_UNDER_TIME_PRESSURE**

# 6. 为什么这个事故特别值得训练

很多最后时刻 partial 都长这样：

```
if (特殊条件成立)
    输出一个极简单答案
```

在脑子里，用户记住的是：
> “这个 special 的答案是 EMPTY / 0 / n / 某个公式。”

时间一紧，最容易丢的是：
> **特殊条件本身。**

于是代码退化成：

```
cout << special_answer;
```

Day5 A 的 all-d=1 special 写反输出顺序，是“payload 写错”；
core 则是更纯粹的：
> **guard 被整个丢掉。**

# 7. 下一场硬规则：special 必须以 guard+payload 成对存在

任何 partial 先在 notes 写成：

```
SPECIAL:
guard = <精确条件>
payload = <答案/算法>
proof = <为什么 guard 下正确>
test = <一个满足 guard + 一个不满足 guard>
```

例如 core 的 EMPTY partial：

```
guard:
distinct_first_chars >= k

payload:
EMPTY

positive:
k=2, {"aa","ba"} → EMPTY

negative:
k=2, {"aa","ab"} → 不能 EMPTY
```

最后抢分时，**禁止只抄 payload**。

# 8. 证据等级

- “赛时识别 Trie / L=0 / EMPTY 入口”：录音 [C/process]
- “EMPTY iff distinct first chars≥k”：赛后 full 证明的 d=0 特例 [P]
- “最终三版代码无条件 EMPTY”：Replay/file_changes [P/source]
- “正式 core 未编译未样例”：timeline absence + 后续窗口序列 [C/source]
- “最后0分由该代码导致”：正式目录 source + 比赛结果 [C]

