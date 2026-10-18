# Checker / Stress / Oracle 源码审计｜2026-10-07

> 来源：三包全量展开后的原始源码，不以既有总结为入口。
>
> 目的：回答一个比“有没有 checker / 对拍”更重要的问题：
>
> **这个验证器到底验证了什么？它是不是赛时证据？oracle 的定义域是否被 generator 覆盖？文件名叫 checker 是否真的有 checker 权威？**

# 1. 资产分级

| 对象 | 来源性质 | 本轮结论 |
|---|---|---|
| Day1 B `5623.../checker.cpp` | 题目附件 checker | 高价值；NO/YES 都实际验证，但其 NO 正确性依赖 `a_i<=i` 定理 |
| Day2 A `duipai_T1/ac.cpp` | 赛时/赛后本地 brute oracle | generator 域内 [E] 安全；不能外推到任意长度 |
| Day2 D `chk.cpp` | 题目 checker / validity helper | assignment 语义检查完整；赛时真正 Bug 在 mask 枚举代码，不在 isValid |
| Day4 `T1/checker.cpp` | 本地 comparison utility | **不是正式 checker**；只数两个数组在非 -1 位上的 mismatch |
| Day4 `T2/gen.cpp` | 小随机 generator | 只生成 t=1, n<=10, 值 1..13；覆盖域非常窄 |
| Day3 `stress_A/B/C/D.cpp` | 赛后独立 verifier | 高价值但不是赛时证据；本轮重跑与仓库既有验证报告完全一致 |

---

# 2. Day1 B 联动面板 checker：不是 Day3 B 那种“NO 跳过器”

## 源码契约 [P/source]

`feasible(tc)` 明确执行：

```cpp
for (int i = 1; i <= n; ++i)
    if (a[i] > i) return false;
return true;
```

之后：

- 参与者输出 `NO`：
  - 若 `feasible=true`，直接 WA；
  - 并不是 skipped。
- 参与者输出 `YES`：
  - 检查 `K = n(n+1)/2 - sum(a)`；
  - 每个操作下标；
  - 操作时 `x=a[id]` 必须仍在 1..n；
  - 真正执行 `++b[x]`；
  - 最后逐值检查 1..n 各出现一次。

所以它与 Day3 B 原 checker 的本质区别是：

```
Day3 B:
NO → 不验证 existence

Day1 B:
NO → 用 feasible theorem 主动验证 existence
YES → 再逐步模拟 construction
```

## 附件 48 case 全重放 [E]

原题附件：
- 1-1：2 case
- 2-1：14
- 3-1：14
- 4-1：10
- 5-1：8

合计 **48 case**。

本轮独立解析输入/参考输出并重新执行 checker 语义：

- checker criterion 判 YES：38；
- 参考输出 YES：38；
- criterion / reference verdict mismatch：**0**；
- 38 个 YES 的 K 全等于 forced total increment；
- 所有操作逐步合法；
- 最终 38 个状态全部真实成为 1..n 的排列；
- 10 个 NO 均满足 checker infeasible。

## 独立可达性 BFS [E]

为避免“checker 与参考输出来自同一错误定理”的共因，本轮又不用 checker 输出做 oracle，而是：

- 枚举 n=1..6；
- 枚举所有值域 1..n+1 的非降初态；
- 总计 **1274 个初态**；
- 对每个状态真实 BFS 枚举所有合法操作；
- 目标为最终 multiset = {1..n}。

结果：

```
(a_i <= i for all i)
iff
BFS says target reachable
```

**0 mismatch**。

## 证据等级

仓库 `Day1/题解.md` 已有：
- 必要性：单调初态 + 只增不减的抽屉原理；
- 充分性：归纳 + 链式上推构造。

因此当前可以把：
> `a_i<=i` 是充要条件

保留为题解中的 **[P] 数学结论**；本轮附件重放和 BFS 是额外 [E] 实现/小空间证据。

---

# 3. Day2 A 对拍 ac.cpp：1e4 上界看着危险，但 generator 域内实测安全

## 原始 generator [P/source]

`gen.cpp`：

```cpp
int n = Rand(1, 10);
for (int i=1;i<=n;i++) cout << Rand(0,1);
```

所以对拍域严格是：
- binary string；
- 长度 1..10；
- 数值 `ans in [0,1023]`。

## oracle

`ac.cpp` 把字符串转成整数 ans，然后：

```cpp
for (int i = 0; i <= 1e4; i++)
    minimize popcount(i) + popcount(i + ans);
```

从源码表面看，`i<=10000` 是一个需要审计的**人工截断**。

## 本轮独立扩域核验 [E]

对 generator 的**完整数值定义域**：

```
ans = 0..1023
```

逐个比较：

```
min over i=0..10000
vs
min over i=0..65535
```

结果：
- 1024 个 ans；
- mismatch = **0**；
- 在扩展域中，首次达到最优值的 i 最大只有 **170**。

所以：

> **这个 ac.cpp 作为该 gen.cpp 的 oracle，在 generator 域内没有发现截断错误。**

但证据边界必须保留：
- 这不是“对任意长度二进制数都证明 i<=10000 足够”；
- 不能把它脱离 gen.cpp 当通用正解。

这是一个典型的“oracle 可靠性必须和 generator domain 一起陈述”的案例。

---

# 4. Day2 D chk.cpp：checker helper 没有制造赛时漏枚举

`chk.cpp` 的 `isValid` 真正检查：

- 相邻不能同时为狼；
- 对每个非狼村民：
  - 按 L/R 看指定邻居；
  - 超出边界视为好人；
  - 两个被观察者中狼的数量必须等于 b[i]。

输出：
- candidate `-1` 而 jury 有合法 assignment → WA；
- candidate 给 assignment → 逐条 `isValid`；
- 若 jury 是 -1、candidate 却给出 valid assignment → checker FAIL，说明 jury 错。

因此已有 Day2 D 的真实失败仍应归因于：
> **赛时代码把 mask 转长度 n 的狼数组时没有补满高位，枚举空间缺了一部分。**

不能把这个锅转嫁给 `isValid` / checker。

---

# 5. Day4 T1/checker.cpp：文件名具有误导性

完整源码只做：

```cpp
read n
read a[1..n]
read b[1..n]
for i:
    if (b[i] == -1) continue;
    if (a[i] != b[i]) cnt++;
cout << cnt;
```

它：
- 不读 testlib；
- 不读取题目输入语义；
- 不判断 candidate 可行性；
- 不验证最优性；
- 把 b=-1 的位置直接跳过。

所以它的正确分类是：

> **local comparison utility / mismatch counter**

而不是：
- official checker；
- brute oracle；
- correctness validator。

以后任何证据日志出现“Day4 T1 checker 通过”，都必须先确认说的是哪个程序；仅凭文件名 `checker.cpp` 不得升级证据等级。

---

# 6. Day4 T2/gen.cpp：generator 覆盖极窄

源码只生成：

- t=1；
- n in [1,10]；
- 每个值 in [1,13]。

所以它适合：
- 小数据结构反例；
- brute/candidate smoke test。

不适合证明：
- 大 n 性能；
- 大值域边界；
- 特殊构造族。

这进一步解释为什么“对拍跑很多轮”必须同时问：
> generator 到底覆盖了什么分布？

---

# 7. Day3 stress_A/B/C/D：高价值，但不能误记成赛时能力

这四份源码位于三包顶层分析资产附近，是**赛后正解验证器**。

本轮重新编译并实际执行：

| stress | 本轮实际结果 |
|---|---:|
| A | PASS **1,021,844** cases |
| B | PASS **1,160,593** cases；其中 YES=179,368，构造区间逐个反验 |
| C | PASS **1,015,405** instances |
| D | PASS **1,088,572** arrays |

合计仍是 **4,286,414** 个实例，和仓库现有 `Day3/验证报告.md` 完全一致。

因此本轮**不创造一个新的“Day3 更强了”结论**，而是确认：
- 现有验证报告数字可复现；
- stress 源码真实存在；
- 这些是赛后 [E]，不能回写成“赛时已经有百万级对拍”。

---

# 8. 新的统一验证器分级

以后三包里发现文件名含：
- checker
- chk
- ac
- brute
- stress
- gen

必须先归类：

```
A. official construction/existence checker
B. local semantic validator
C. brute truth oracle
D. candidate pretending to be ac
E. generator
F. post-contest stress verifier
G. mere comparison utility
```

然后记录四件事：
1. 它验证的命题；
2. 没验证的命题；
3. generator/domain；
4. 它属于赛时还是赛后。

**文件名不是证据等级。**
