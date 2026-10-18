# Day3 OJ 正式提交源码 × VM AC.cpp 对齐

> 原件：
> - 三包03 → 虚拟机(1).zip → Desktop/Day3/T1~T4
> - 三包02 → Day3 OJ 完整归档（2026-10-05 版）
>
> 目的：区分“算法主体一致”与“提交字节完全一致”，并把 Day3 checker 事故直接连到最终提交版本。

## 1. 四道题全部唯一映射到对应 AC.cpp

逐题比较 OJ record source 与 VM 的所有 .cpp：

| 题 | OJ结果 | OJ时间 | 唯一 VM 主体 |
|---|---|---|---|
| A 报数 | AC 100 | 19:20:20 | T1/AC.cpp |
| B 翻面消除 | WA 65 | 21:55:13 | T2/AC.cpp |
| C 任务领取 | WA 24 | 22:21:43 | T3/AC.cpp |
| D 同类分段 | TLE 15 | 22:45:31 | T4/AC.cpp |

四组都满足：

> 去掉且仅去掉 freopen / 注释 freopen 两行后，其余源码逐字规范化完全一致。

因此这是四个唯一的 BODY/IO 对应，不是模糊相似度猜测。

## 2. 四份差异都只有 traditional IO 开关

A：

    VM: //freopen ("Chant.in", "r", stdin);
        //freopen ("Chant.out", "w", stdout);

    OJ: freopen ("Chant.in", "r", stdin);
        freopen ("Chant.out", "w", stdout);

B：

    VM: //freopen ("Oblivion.in", "r", stdin);
        //freopen ("Oblivion.out", "w", stdout);

    OJ: freopen ("Oblivion.in", "r", stdin);
        freopen ("Oblivion.out", "w", stdout);

C：

    VM: //freopen ("Covenant.in", "r", stdin);
        //freopen ("Covenant.out", "w", stdout);

    OJ: freopen ("Covenant.in", "r", stdin);
        freopen ("Covenant.out", "w", stdout);

D：

    VM: //freopen ("Sunder.in", "r", stdin);
        //freopen ("Sunder.out", "w", stdout);

    OJ: freopen ("Sunder.in", "r", stdin);
        freopen ("Sunder.out", "w", stdout);

结论 [P/source]：

> VM AC.cpp 可以作为“最终提交算法主体”的高强度证据，但不能称作提交字节完全一致；正式提交 source-of-truth 仍是 OJ record source。

## 3. B checker 假安全链直接作用于最终提交主体

VM：

- T2/AC.cpp SHA-256：
  3b8d3e5cdc0b4703b94fe06dba344a8eb654e325ffaab1d15970eca1a555a4ed

此前使用的 checker：
- T2/checker.cpp SHA-256：
  14281b5f2127adce25edc1a980b52d5ff09c8f7520af914b8a0449c871311278

本轮已经重放：
- 原版 T2/AC.cpp；
- 原版 checker；
- 原版 sample1～sample8。

结果：
- checker 对 8 份样例全部返回成功；
- sample7 第4个 case：
  - T2/AC.cpp 输出 NO；
  - 官方输出 YES 62528 125010；
  - checker 因 NO is skipped 把它跳过。

现在又确认：
> OJ B 正式提交源码去掉 freopen 后，与这份 T2/AC.cpp 完全相同。

因此 [P+E]：
> “checker 漏掉 sample7 false-NO”不是中间版事故，而是最终拿 65 分的 submitted algorithm body 本身就带着该反例。

这把因果链闭合成：

    最终 B 算法主体
    → 官方 sample7 已存在 false-NO
    → local checker 不验证 NO
    → checker 全绿
    → 错误主体继续被视为可提交
    → OJ 最终 WA 65

不能再把 Day3 B 归纳成“样例没卡到”；**样例其实已经卡到了，只是验证器把卡点吞了。**

## 4. Day3 与 Day5 的交付模式对照

Day3：
- 四份 OJ source 都与 VM AC.cpp 主体一致；
- 差异统一只有 freopen comment state。

Day5：
- 多份 OJ source 同样只能在忽略 freopen 后映射到 Replay；
- timeline 更进一步证明有些 traditional IO 是在 OJ 网页提交框里最后修改的。

所以跨场稳定规则是：

> “算法主体一致”不等于“上传源码就是最后本地验证字节”。

以后证据报告必须区分：
- EXACT source match；
- BODY/IO match；
- near match；
- no match。

## 5. 对复盘口径的修订

### A/C/D

可以说：
> VM AC.cpp 与正式提交算法主体一致，仅 traditional IO 注释状态不同。

不能说：
> VM AC.cpp 就是 OJ 原样提交文件。

### B

可以进一步说：
> VM T2/AC.cpp 就是正式提交的算法主体；因此 sample7 false-NO 对最终提交版本成立。

这比“checker 不完整”高一个证据等级，因为已经闭合到真正的 scored artifact。

## 6. 后续

1. 继续用 keystream 对齐四次提交前的 copy/paste 与 IO 开关动作；
2. 给 T1/T3/T4 同样恢复“最后一次验证 → 提交”的间隔；
3. 对 B 的 65 分逐子任务/测试点，与 false-NO 类型做分布分析；
4. 把 checker_coverage_probe.py 接入构造题赛前验证流程。
