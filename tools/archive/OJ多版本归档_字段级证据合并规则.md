# OJ 多版本归档｜字段级证据合并规则

> 三包中同一场代码源 OJ 往往存在多个时间点的完整归档。
>
> 结论：**不能用“最新 ZIP 全面覆盖旧 ZIP”**。正确做法是同一场所有归档快照做内容并集，并按字段选择最强证据。

## 1. 七场归档快照实测

| 场次 | 快照 | 文件数 | 唯一提交 record | 排行榜 CSV |
|---|---|---:|---:|---:|
| Day1 | 2026-09-28 | 76 | 2 | **80行** |
| Day1 | 2026-10-05 | 95 | 2 | 无 |
| Day2 | 2026-09-28 | 88 | 6 | **73行** |
| Day2 | 2026-10-05 | 119 | 6 | 无 |
| Day3 | 2026-10-01 | 60 | 0 | 无 |
| Day3 | 2026-10-02 | 82 | 4 | **109行** |
| Day3 | 2026-10-05 | 107 | 4 | 无 |
| Day4 | 2026-10-03 | 79 | 3 | **111行** |
| Day4 | 2026-10-05 | 101 | 3 | 无 |
| Day5 | 2026-10-04 | 118 | 6 | 无 |
| Day5 | 2026-10-05 | 119 | 6 | 无 |
| Day6 | 2026-10-05 06:35 | 104 | 4 | 无 |
| Day6 | 2026-10-05 12:44 | 107 | 4 | 无 |
| Day7 | 2026-10-06 04:07 | 92 | 2 | 无 |
| Day7 | 2026-10-06 15:10 | 101 | 2 | **105行** |

因此：
- Day1～Day4：较早快照反而保留了排行榜；
- Day5/6：较晚快照主要补 record metadata；
- Day7：较晚快照既补 metadata 又新增105行排行榜。

## 2. 27 个唯一提交中有 9 个 metadata 冲突

三包共有：
- 93 个 record JSON 外观文件；
- 去重后 **27 个唯一提交 ID**；
- 其中 **9/27** 在不同归档快照之间出现字段质量差异。

典型模式：

### Day5 早期归档

部分 record：
- problemTitle = `A 蜗蜗的三角画布`
- time = 空
- memory = 空
- submitTime 甚至被错误写成 `A 蜗蜗的三角画布`
- user = 空

较晚快照补成：
- `P5638 蜗蜗的三角画布`
- time = 28ms
- memory = 4.6 MiB
- submitTime = 2026-10-4 13:03:09
- user = Sutong

Day6 / Day7 的早期 record 也存在同类问题。

## 3. 字段级 Source of Truth

### record score / status

如果同一 record ID 多快照一致：
- 直接确认。

若冲突：
1. 优先 record-route 的完整 record 页面；
2. 再用测试表格逐点和题目列表交叉。

### submitTime / time / memory / user

优先：
1. 字段完整、明确来自 record-route 的快照；
2. 不使用“题名字串占位”的错误值。

### standings

**不能因为快照旧就丢掉。**
只要榜单：
- 来源明确；
- 时间口径可说明；
- 行数/列结构完整；

就应保留为该时点的独立证据。

### 正式提交源码

优先：
1. OJ record source；
2. Replay snapshot exact match；
3. body_without_freopen 只能说明算法主体对应；
4. VM final 不能自动替代 OJ source。

## 4. 不允许再写“主归档=唯一真相”

更准确的模型：

```
contest
├─ archive snapshot A
├─ archive snapshot B
├─ archive snapshot C
└─ merged evidence view
    ├─ records: field-level strongest
    ├─ standings: preserve every useful timestamp
    ├─ sources: content hash / exact body
    └─ statement/subtask: union + conflict log
```

新自动化若发现同一场多个归档：
- 先算 ZIP SHA；
- 再做相对路径 + 内容 SHA diff；
- 新快照只新增“强字段”，不删除旧快照独有证据；
- 所有修订保留 provenance。
