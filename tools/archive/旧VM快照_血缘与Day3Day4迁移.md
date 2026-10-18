# 旧 VM 快照血缘｜Day3 → Day4 工作区迁移证据

> 原件：`模拟赛资料_03_共03包.zip`
>
> - `虚拟机.zip`：27,570,482 bytes；SHA-256 `666124f73da6d229751f7e6f572cf4f457527cbb23535a17471b089d4b950d2e`
> - `虚拟机(1).zip`：66,019,657 bytes；SHA-256 `55ddfd51e30b6f7c23db6c49e61ecf5185dcc919860641e42d07de2e8c3bfd91`
>
> 目的：把“两个 VM 包”从模糊附件，变成有血缘关系的时间快照；降低重复阅读，并恢复 Day3→Day4 的工作区迁移。

# 1. 两个快照不是独立材料

去掉 ZIP 顶层 `虚拟机/` 后按相对路径 + SHA-256 比较：

| 指标 | 数量 |
|---|---:|
| `虚拟机.zip` 文件 | 410 |
| `虚拟机(1).zip` 文件 | 595 |
| 同路径同时存在 | 338 |
| 同路径且内容完全相同 | **310** |
| 同路径但 SHA 改变 | **28** |
| 仅旧快照 | 72 |
| 仅新快照 | 257 |

所以对 338 个共同路径，**91.7% 内容未变**。

结论：
> 后续不能把这两个 VM 当成两套 100% 新资料重复读；真正高信息量的是“28 个同路径变化 + 257 个新增路径 + 被移动/归档的旧路径”。

# 2. [P] `虚拟机.zip` 的根 T1～T4 被完整归档进新快照的 `Desktop/Day3/`

发现 **60 个文件**满足：

```
旧：Desktop/T?/...
新：Desktop/Day3/T?/...
SHA-256 完全相同
```

按题号：

- T1：14 个；
- T2：28 个；
- T3：9 个；
- T4：9 个。

典型：

```
Desktop/T1/AC.cpp
→ Desktop/Day3/T1/AC.cpp
SHA 132a61d87560...

Desktop/T2/checker.cpp
→ Desktop/Day3/T2/checker.cpp
SHA 14281b5f2127...

Desktop/T3/AC.cpp
→ Desktop/Day3/T3/AC.cpp
SHA e267dd1741...

Desktop/T4/AC.cpp
→ Desktop/Day3/T4/AC.cpp
SHA 59a5775ec8...
```

新快照还新增：

`Desktop/Day3/keystream/events_20261001_184442.jsonl`
`Desktop/Day3/keystream/keys_20261001_184442.txt`

因此 [P/source]：
> `虚拟机.zip` 的根 T1～T4 是 Day3-era 工作区；到 `虚拟机(1).zip` 时，这批内容被保留进 `Desktop/Day3/`，根工作区随后被用于下一场。

这给 Day3 原始材料提供了一个非常干净的 provenance bridge。

# 3. 新快照根工作区已经进入 Day4

与 2026-10-05 抓取的 Day4 OJ record source 交叉匹配：

## B 频谱窗

`虚拟机(1).zip!Desktop/T2/main.cpp`

与正式 OJ B 提交源码**逐字规范化完全一致**。

OJ：
- record：`6abfbca84f6635dea334a605`
- status：TLE
- score：0
- submitTime：2026-10-02 22:16:08

因此新快照根 T2 可明确映射到 Day4 B。

## A 温控舱

正式 OJ A 源码与：

`虚拟机(1).zip!Desktop/A/main.cpp`

相似度极高，唯一关键 diff 是提交版：

```cpp
freopen ("Thermokinesis.in", "r", stdin);
freopen ("Thermokinesis.out, "w", stdout);
```

而 VM 后续版本把两行都注释：

```cpp
//freopen ("Thermokinesis.in", "r", stdin);
//freopen ("Thermokinesis.out, "w", stdout);
```

OJ record：
- status：Compile Error
- score：0
- submitTime：2026-10-02 22:10:48

[P/source] 第二行正式提交少了文件名后的闭引号：
`"Thermokinesis.out, "`

这就是一个可直接由源码解释的 CE。

更重要的是：
> VM 后续版本已经把事故行注释掉，因此只看赛后本地文件，会错过真实提交故障。

## D 组合题

OJ D source 与 `Desktop/D/main.cpp` **不是同一版本**。

提交版把 n≤20 的 DFS 分支整段注释，直接输出 n!；VM 后续版又恢复：
- n≤20 调 DFS；
- 大数据输出 n!；

且 DFS 内部判定逻辑也发生较大变化。

所以 D 再次证明：
> final VM workspace 不等于 submitted source。

# 4. 28 个“同路径变更”是什么

主要集中在：
- `Desktop/T1`；
- `Desktop/T2`；
- `Desktop/T3`；
- `Desktop/T4`；
- `Desktop/sample*`。

这正符合：
> Day3 旧工作区被归档后，根 T1～T4 被下一场复用。

因此这 28 个变化属于**高价值版本分叉**，不能被“同路径文件”去重掉。

相反，310 个同路径同 SHA 文件优先视为快照重复证据，只补 provenance，不重新分析内容。

# 5. 对三包去重算法的升级

原先只做“同 ZIP SHA / 同文件 SHA”还不够。

旧 VM 快照还需要识别：

```
同内容 + 路径发生归档迁移
```

推荐 future inventory 增加：

- snapshot_id
- relative_path
- content_sha256
- canonical_content_id
- moved_from / moved_to
- contest_mapping
- semantic_role

这样像 Day3：

`Desktop/T2/checker.cpp → Desktop/Day3/T2/checker.cpp`

应记成**同一个证据对象的迁移**，而不是两个待分析文件。

# 6. 当前价值排序

高价值，继续挖：
1. `Desktop/Day3/keystream/events_20261001_184442.jsonl`
2. `Desktop/Day3/keystream/keys_20261001_184442.txt`
3. 新旧根 T1/T2 的 28 个 SHA 分叉；
4. Day4 A/B/D OJ submitted source ↔ VM post-submit diff。

低价值/可降权：
- 310 个共同路径同 SHA 副本；
- 二进制 .o / executable 若已有对应源码且不涉及编译器/环境事故；
- 明显重复 sample 副本，除非同名不同 SHA。

# 7. 已落盘后的下一步

- Day4《逐段考古纪要》加入 A CE 的提交源码证据；
- Day3 keystream 做高信息量时间片考古；
- 将“路径迁移检测”补进递归 inventory 工具；
- 对 `虚拟机(1).zip` 里 Day4 D 的 submitted/post-submit 分叉继续对齐键盘回放。
