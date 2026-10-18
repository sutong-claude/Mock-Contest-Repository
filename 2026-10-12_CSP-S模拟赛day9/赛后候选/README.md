# Day9 四题赛后算法候选（不改赛时四份 final）

> 本目录始于 2026-10-15 的 Gemini 39 页 PDF 转录与独立复核。**不要将“通过本地独立 oracle”升级成“官方 OJ 100 分”。** 完整官方输入/输出、测试范围和四题正式提交 source/score 仍需在 CodeLands OJ 阅读后证据闭合。

| 题 | 真正的赛时切入点 | 新增候选 | 独立验证 |
|---|---|---|---|
| A zerofree | 开场出现前缀和余数 DP，因复杂度误判提前放弃 | [zerofree_onnr.cpp](zerofree_onnr.cpp) | 600组小 r/负数枚举 |
| B count | 正确考虑字典序 Dijkstra，但把有向边建成双向 | [count_directed.cpp](count_directed.cpp) | 650组按步数 DP |
| C color | 赛时想到暴力选子集，未掌握折半查相反向量 | [color_mitm.cpp](color_mitm.cpp) | 550组完全子集枚举 |
| D silent | 赛时观察小 k，正式 final 只有输出0 | [silent_cycle_windows.cpp](silent_cycle_windows.cpp) | 4000组随机函数图+2592组环长组合+4定向 |

**D 是本轮的重要新增工程资产**：以 PDF p20–22 的尾链/周期/gcd 方案为基础，修复自然遍历 x 环并不能使 y 窗口每次平移1位的问题，采用**按同余类/模逆窗口起点分组排序**。参见 [数学证明与最小反例](silent_cycle_windows_数学证明与反例.md) 和 [本地/CI验证记录](silent_本地编译与对拍验收_2026-10-15.md)。

## 真实可重复的测试

```bash
g++ -std=c++17 -O2 -Wall -Wextra -Wshadow zerofree_onnr.cpp -o zerofree_onnr
g++ -std=c++17 -O2 -Wall -Wextra -Wshadow count_directed.cpp -o count_directed
g++ -std=c++17 -O2 -Wall -Wextra -Wshadow color_mitm.cpp -o color_mitm
g++ -std=c++17 -O2 -Wall -Wextra -Wshadow silent_cycle_windows.cpp -o silent
python3 test_candidates.py
python3 test_silent_cycle_windows.py
```

- **GitHub 官方 runner** [第一次成功运行 #38841253085](https://github.com/sutong-claude/Mock-Contest-Repository/actions/runs/38841253085)：四份编译+两套独立oracle测试均为 success。自动化定义 [.github/workflows/day9-candidates-oracle.yml](../../.github/workflows/day9-candidates-oracle.yml)。
- D 源码当前 blob `da645e5c4e0b451c42390c4b117b861d9deae555`，与本地测试完成后的版本严格一致。
- C++传统文件输入输出是基于 PDF 的当前假设：`silent.in/out`，依次读取 `n m k`、起点 `x0 y0`、`P[1..n]`、`Q[1..m]`；**官方数据字段顺序仍需核对**，这属于可交付性断点，不是数学反例。

## 不可混淆的证据

- `../赛时代码/*_final.cpp` 是赛时虚拟机最后保存，保留原状；
- 本目录是赛后 full-model candidate；
- `LOCAL-VERIFIED` 说明在独立模型 oracle 上测试成功，不等价于全部约束/正式 OJ AC；
- PDF p35 的 61 分来自 Gemini 二级截图整理，不是本次独立服务器提取。见 [赛时证据差异](../2026-10-15_Gemini增量_赛时考古与分数争议.md)。
