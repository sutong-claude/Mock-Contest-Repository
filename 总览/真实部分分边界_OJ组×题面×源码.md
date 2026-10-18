# Day1–Day7｜真实部分分边界：OJ group × 题面子任务 × submitted source

证据链：27 个正式 OJ record 的测试表格 + OJ 原始题面 HTML + submitted source。

## Day1 A 记录带：20 分 = 小规模通用算法
- #1 20分：Σn≤100，AC。
- #2 10分：p_i=i，TLE。
- #3 20分：Σn≤2000，TLE。
- #4 20分：Σn≤5000；#5 30分无限制。
结论：不是 special 命中，而是通用算法数学能算，小规模能跑，规模上去超时。

## Day1 B 联动面板：25 分 = 两个 special 完整命中
- #1 15分 Σn≤8：WA。
- #2 10分 a_i=i：AC。
- #3 15分 a_i=1：AC。
结论：SPECIAL_EXACT_25，不是 general partial。最后 n≤2/3 patch 使 all-ones 组由 11/14 变14/14，真实换来15分。

## Day2 C：30 分 = O(n²) 标准复杂度台阶
- n≤10：10 AC；n≤5000：20 AC；n≤2×10^5：30 TLE；full n≤2×10^6。
结论：稳定可冻结 SIZE_BRUTE_30。

## Day3 B 翻面消除：65 分不是稳定 partial
20个独立5分测试点，AC为6,7,8,9,10,11,12,13,15,16,17,19,20；WA为1,2,3,4,5,14,18。

特别重要：
- #13/#14 声明限制相同（R≤100一档）却一过一挂；
- #16–#20 都是 full-general，18挂而16/17/19/20过。

失败反馈同时有：
- “interval does not erase the string”：YES构造错；
- “a solution exists”：false NO。

结论：DISTRIBUTION_HIT_65，是错模型覆盖了大量官方数据分布，不应当成可靠 score floor。

## Day3 C 任务领取：24 分高度结构化
- #1–#4：n≤8，共16分，submitted source 真正穷举所有 (n−1)! 发布顺序。
- #12：星形树，4分；大 n 分支输出 (n−1)!。星形树任意发布顺序都不会让一条新边两端都已占用，因此所有排列成功。
- #17：k=1，4分；同一 factorial 分支由官方整组确认。

结论：16分 brute + 4分 star special + 4分 k=1 special。

## Day3 D 同类分段：15 分 = n≤40
#1 n≤8、#2/#3 n≤40 均AC；#4/#5 n≤2000开始TLE。submitted source 在 n≤2000 分支做多层枚举+unordered_map重算，近 O(n³) 量级。

结论：稳定 SIZE_BRUTE_15。

## Day5 B 巡检路线：15 分 = A_i≥B_i special 的完整正解
题面 #4 独立15分，保证所有 i 有 A_i≥B_i。submitted source 直接输出 A_N。

证明：
A、B 都严格递增，B_i≤A_i 意味到第 i 个检测点前至少经过 i 个补给点。机器人从0一路单调向右到 A_N 即可完成全部检测，路程 A_N；任何方案又必须到达 A_N，所以 OPT=A_N。

结论：SPECIAL_EXACT_15，不是碰巧。

## Day6 D 频段配对：15 分 = n,q≤100
题面 #1/#2 各15分（HTML score rowspan）：
- #1 n,q≤100 AC；
- #2 n,q≤1000 TLE；
- #3 n,q≤1e5；
- #4 随机排列20；
- #5 full40。

结论：官方把 brute 承受边界钉在100级，1000级已经不可用。

## Day7 B 委托分组：45 分 = Σn≤2000 的稳定 brute
题面：
- #1 20分 Σn≤10；
- #2/#3 各25分，分别Σn≤2000、≤1e4；
- #4 30 full。

OJ：
- #1 AC20；
- #2 AC25；
- #3 RE0。

#3 细节：
- #3-1 AC：62.3MiB；
- #3-2 RE：227.2MiB；
- #3-3 AC：33.1MiB；
- #3-4 RE：227.1MiB。

本题内存限制256MiB。

submitted source 每个组件扫描都会创建 unordered_set 并插入整组件，但集合之后完全不读取。它是纯额外内存/哈希开销；两个RE点峰值逼近内存上限，资源型崩溃强相关，但因OJ verdict为RE而非MLE，不能写成唯一死因。删掉它仍保留重复 calc 扫组件的 O(n²) 根复杂度。

结论：数学语义正确的稳定 brute，官方可靠到Σn≤2000。

## 统一分类
- SIZE_BRUTE：通用真值，小规模受复杂度限制。Day1 A20、Day2 C30、Day3 D15、Day6 D15、Day7 B45。
- SPECIAL_EXACT：题面特殊性质的完整正解。Day1 B #2/#3、Day5 B #4。
- MIXED_SPECIAL：brute + 若干真实 special。Day3 C24。
- DISTRIBUTION_HIT：错模型离散撞中，不稳定。Day3 B65。
- DELIVERY_LOSS：数学资产存在但提交/编译/IO导致0。Day2 D final、Day4 A。
- PROVED_UNCODED：赛时已推对但未物化。Day7 C10、D19。

以后“合理保分线”只累计可复现的 SIZE_BRUTE / SPECIAL_EXACT / MIXED_SPECIAL；DISTRIBUTION_HIT 不算可靠 score floor。
