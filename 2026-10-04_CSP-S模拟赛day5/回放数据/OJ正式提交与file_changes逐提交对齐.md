# Day5 六次正式提交 ↔ Replay file_changes 对齐

> 原始证据：
> - capture `20261004_090304/file_changes.jsonl`
> - Day5 OJ 两版完整归档中的六份 record source
>
> 方法：统一 CRLF/LF、忽略文件末尾空白；先 exact full source，再做最近版本 diff。

## 1. 六次提交结果

| OJ record | 题 | 结果 | 与 Replay |
|---|---|---|---|
| 6ac1d8c2… | A | WA0 | 最近 T2/WA.cpp，**只差 freopen 两行** |
| 6ac1d937… | B | WA15 | 最近 T2/main.cpp，**只差 freopen 两行** |
| 6ac1d987… | C | RE0 | **EXACT** T3/main.cpp |
| 6ac1dd29… | C | RE0 | **EXACT** T3/WA.cpp |
| 6ac1dd8a… | C | WA0 | 最近 T3/WA.cpp，**只差 Hina freopen 两行** |
| 6ac1de0d… | A | WA0 | 最近 T4(now T1)/main.cpp，**只差 Uika freopen 两行** |

## 2. 四次非 exact 并不是算法主体漂移

四份 OJ source 与最近 Replay snapshot 的 unified diff 都只落在：

```cpp
//freopen ("...", "r", stdin);
//freopen ("...", "w", stdout);
```

变成正式提交中的：

```cpp
freopen ("真实题目.in", "r", stdin);
freopen ("真实题目.out", "w", stdout);
```

算法主体其余内容相同。

这给 FileTracker 的 2 秒 polling 边界提供了一个真实比赛级证据：

> **file_changes 能恢复主体版本链，但不保证捕捉到网页提交前/极短间隔最后一次 traditional IO 修改。**

因此以后：
- exact = 最强；
- body_without_freopen = 主体对应，但 delivery bytes 未完整捕捉；
- 不能把 body_without_freopen 冒充 exact。

## 3. 这也修正了“提交后到底改了什么”

Day5 并不是六次都从完整本地 final 直接提交。

至少四次：
- Replay 最近可见落盘版仍是注释 freopen；
- OJ source 已打开正确/错误的正式 IO。

所以“最后一分钟网页/编辑器里改 traditional IO”本身就是独立版本事件。

若这个版本没有重新 F9/样例验证：
```
VERIFIED/FROZEN
→ 修改 IO
→ MODIFIED_UNVERIFIED
```

这也是仓库《得分资产状态机》里“冻结只对具体字节成立”的原始证据。

## 4. 与 Day6 / Day7 的对照

同样方法实测：

### Day6
A/B/C/D 四份 OJ source **全部 exact** 命中 file_changes：
- A → T1 2978.079s；
- B → T2 9290.971s；
- D → T4 10296.119s；
- C → T3 12512.606s。

### Day7
- A100 → T1 2175.586s **EXACT**；
- B45 → T2 14006.987s **EXACT**。

所以 Day5 的“只差 freopen”不是 matcher 本身太松，而是 Day5 提交流程真实存在最后字节漂移。
