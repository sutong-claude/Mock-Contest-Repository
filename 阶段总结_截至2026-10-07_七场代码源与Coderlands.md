# 阶段总结｜截至 2026-10-07：七场代码源 + Coderlands + 赛场工程系统

> 这份总结把“算法能力”和“比赛系统能力”分开。
>
> 七场代码源可以纵向比较；Coderlands / 代码部落是另一套赛制，不用裸分硬比。

## 1. 七场代码源分数已由原始归档重新核对

```text
Day1   45
Day2  130
Day3  204
Day4    0
Day5   15
Day6  115
Day7  145
```

这些分数现在都能从本轮重新读取的 7 个归档中的 record score 字段逐题恢复。

## 2. 分数像过山车，但瓶颈持续向后移动

### Day1
主要断点：
`题意 / 总范围 / 复杂度 / 部分分`

### Day2
主要断点：
`时间分配 / 提交版本 / RE CE / 假对拍`

### Day3
开始拥有：
`大样例研究 / checker / brute / 结构发现`

但出现：
`P/H 混淆；checker 只验证一半`

### Day4
第一次真正把：
`generator + brute + candidate + diff`
跑起来。

同时发现：
`oracle 也会错；环境也会炸；partial 没冻结`

### Day5
数学已经能推到：
`min j>i such that r[j]>r[i]`

瓶颈后移到：
`数学 query → 正确数据结构接口`

### Day6
瓶颈继续后移：
`数学判定是否必要且充分`

因此建立：
`对象 / 必要性 / 充分性 / 实现契约`

### Day7
B 已经做到：
`正确 brute → 找准 calc 瓶颈 → 会回滚冻结 → 甚至想到离线`

真正没跨过：
`删除分裂 → 倒序加入 → DSU`

同时 C10 / D19 已经 PROVED，却没有快速物化成代码资产。

---

## 3. Coderlands / 代码部落带来的新赛制问题

这场不是代码源 Hydro 风格页面，而是教学/竞赛一体化 SPA，且比赛组织方式不同。

前两题 net / game 可以稳定到 100，说明：

> 在高强度陌生题里，已经能完成“建模 → 反例 → 重构 → Debug → 交付”的完整闭环。

后两题暴露的新问题：

> **捆绑评分下，多个半成品 partial 没有价值；必须逐包闭合。**

另外，页面榜单快照包含尚未开始的账号，所以不能把 0 分行直接当最终参赛者统计。

---

## 4. 这个阶段真正形成的是一套“比赛操作系统”

### 算法研究
```text
题意
→ 最机械 brute
→ 找重复工作
→ 做等价改写
→ 最后才出现算法名
```

### 证据管理
```text
[P] proved
[E] brute-verified
[C] statement/checker contract
[H] hypothesis
[X] counterexample
```

### 得分资产
```text
IDEA
→ PROVED
→ CODED
→ VERIFIED
→ FROZEN
→ SUBMITTED
→ SCORED
```

### 工程系统
```text
BAG V4
+ Replay
+ OJ archive
+ audio
+ VM evidence
```

---

## 5. BAG V4 为什么是阶段性的重大升级

它把过去分裂的：
- official samples
- 手工 Debug
- stress counterexample
- submission source

统一成：

> **一个目录、一份 main.cpp、一池 testcase。**

任何对拍反例一旦出现，就直接变成 `debug_XXX.in/out`，从此每次 `bash run.sh` 都自动回归。

这是一种很重要的方法论：

> **工具最强的地方不是功能多，而是把正确动作变成默认动作。**

以前很多事故需要“人记住不要犯”：
- 测过的不是交的那份；
- 反例没有回归；
- 编译失败仍跑旧 binary；
- debug 工程与当前代码漂移。

V4 是把这些约束直接编码进工作流。

---

## 6. 下一阶段最重要的四个自动触发器

### A. 固定顺序删除导致分裂
自动尝试：
`倒序加入 → 合并 → DSU`

### B. 一旦说“这分一定能拿”
10 分钟内：
`PROVED → CODED → VERIFIED → FROZEN`

### C. 自由度已经很低
例如 k=2 只有一刀：

> 停止猜结构，直接枚举全部自由度。

### D. 捆绑子任务
一次只闭合一个包：

`证明 → 编码 → 专项测试 → 冻结 → 再开下一包`

---

## 7. 仓库现在的角色

这个仓库不能再只是题解库。

它应该是下一位 AI 可以直接接管的外部大脑，至少同时维护：

1. 原始来源 / 哈希 / 完整性；
2. 赛场全过程；
3. 思维考古；
4. 代码版本考古；
5. verifier / brute / counterexample；
6. BAG / VM / Replay / 归档工具；
7. 下一场执行协议。

所以本轮新增：
- 七场原始归档证据清单；
- Coderlands 采集路线；
- BAG 演化史；
- VM 赛场工程经验；
- 归档与证据链方法。

以后阶段总结必须同时回答：
- 算法能力变了什么；
- Debug 行为变了什么；
- 工具链变了什么；
- 证据质量变了什么；
- 下一场默认动作是什么。
