# Day3 keystream｜四题最后验证 → 正式提交链

> 原始证据：
> - `虚拟机(1).zip!Desktop/Day3/keystream/keys_20261001_184442.txt`
> - 同 VM 的 `T1~T4/AC.cpp`、可执行文件和 ZIP central-directory 时间
> - Day3 四份 OJ record source / submitTime
>
> 目的：不再笼统写“赛时测过/没测过”，而是回答：
> **最后被本地编译/运行的算法主体，与正式 OJ 字节到底差什么；每题提交前最后一次验证有多强。**

# 1. 时间基准

keystream：
- Start = 2026-10-01 18:44:42
- End = 22:47:32

OJ：
- A：19:20:20，AC100
- B：21:55:13，WA65
- C：22:21:43，WA24
- D：22:45:31，TLE15

同 VM ZIP central-directory 时间与北京时间通过 OJ/按键事件交叉后稳定约 **+12h**：

| 文件 | ZIP时间 | 对齐北京约时刻 | OJ提交 |
|---|---|---|---|
| T1/AC.cpp | 07:20:08 | 19:20:08 | 19:20:20 |
| T2/AC.cpp | 09:54:56 | 21:54:56 | 21:55:13 |
| T3/AC.cpp | 10:21:12 | 22:21:12 | 22:21:43 |
| T4/AC.cpp | 10:44:10 | 22:44:10 | 22:45:31 |
| T4/AC executable | 10:45:08 | 22:45:08 | 22:45:31 |

所以这条链不是“凭录音猜大概”，而是源码保存时间、编译产物时间、keystream 和 OJ 四源对齐。

# 2. 四份 OJ source 与 VM AC.cpp 的差异只有 freopen

机械逐行 diff：

## A

VM：
```cpp
//freopen ("Chant.in", "r", stdin);
//freopen ("Chant.out", "w", stdout);
```

OJ：
```cpp
freopen ("Chant.in", "r", stdin);
freopen ("Chant.out", "w", stdout);
```

算法主体其余逐行一致。

## B

唯一差异：
```diff
-//freopen ("Oblivion.in", "r", stdin);
-//freopen ("Oblivion.out", "w", stdout);
+freopen ("Oblivion.in", "r", stdin);
+freopen ("Oblivion.out", "w", stdout);
```

## C

唯一差异：
```diff
-//freopen ("Covenant.in", "r", stdin);
-//freopen ("Covenant.out", "w", stdout);
+freopen ("Covenant.in", "r", stdin);
+freopen ("Covenant.out", "w", stdout);
```

## D

唯一差异：
```diff
-//freopen ("Sunder.in", "r", stdin);
-//freopen ("Sunder.out", "w", stdout);
+freopen ("Sunder.in", "r", stdin);
+freopen ("Sunder.out", "w", stdout);
```

因此四题都满足：

```
submitted algorithm body
=
VM final AC.cpp algorithm body
```

但四题都**不满足**：

```
submitted bytes
=
local final compiled bytes
```

因为正式 OJ 字节把 traditional IO 打开了。

# 3. A100｜算法验证强，交付字节仍有最后变异

## 本地验证

keystream：

- 33:05：`g++ AC.cpp -o Ac -O2`
- 33:26～33:36：再次编译
- 33:42：运行 `ex_A1`
- 34:18～34:31：运行 `ex_A2`
- 34:33～34:43：`diff ex_A2.out ans.out`

ZIP：
- `T1/Ac` 时间 19:18:18

说明 AC 主体在提交前约2分钟经过：
- 编译；
- 两份附件；
- diff。

## 最后保存/复制

- 35:18～35:22：键盘可见出现 `Chant`
- 35:24：Ctrl+A
- 35:25：Ctrl+C
- 35:26：Ctrl+S
- ZIP `T1/AC.cpp` = 19:20:08，正好对应这次保存
- 35:32：Ctrl+V
- 35:35～35:36：4次 Backspace
- OJ 19:20:20 提交

最终 OJ 与本地只差 `//freopen → freopen`。

因此最谨慎、也最强的结论：

> A 的**算法主体**已被正式附件充分本地验证；提交前最后可见源码变动没有改变算法主体，正式 OJ 只在 IO 行上与本地版本分叉。

这是一条健康链，但仍存在：
> **最终 submitted bytes 本身没有被本地编译。**

A 能 AC 不能证明这种 browser-side/final-step mutation 是安全流程。

# 4. B65｜验证量最大，但 checker 覆盖缺口让“全绿”失真

## 最后 candidate 编译

keystream：
- 3:03:03：第一次敲 `g++ AC.cpp -o AC ...`
- 3:03:18：正确执行 `g++ AC.cpp -o AC -O2`

ZIP：
- `T2/AC` = 21:48:08

与按键时间完全吻合。

## sample/checker 链

之后明确连续运行：

- sample1 + checker
- sample2
- sample3
- sample4/5
- sample6
- sample7
- sample8 + checker

最后：
- 3:09:06：运行 sample8 candidate
- 3:09:13～3:09:24：`./checker sample8.in ans.out`

也就是说：
> B 不是“没认真验证”。它把附件几乎完整扫了一遍。

## 最后 IO 命名与提交

- 3:09:39：Ctrl+A/C
- 3:09:51～3:10:08：输入 `Oblivion`
- 3:10:13：Ctrl+A
- 3:10:14：Ctrl+C
- 3:10:15：Ctrl+S
- ZIP `T2/AC.cpp` = 21:54:56，对应这次保存
- 3:10:23：Ctrl+V
- 3:10:26～28：Backspace
- OJ 21:55:13

最终 OJ 仍只比本地多“取消注释 freopen”。

### 真正的问题

E-D3-007 已证明：
- 官方 sample7 case4 本身就是 false-NO 反例；
- checker 对 NO 直接 skipped；
- 所以 candidate 真错，但整份 checker 仍 green。

因此 B 的提交链不是：
> “没测 → 错”。

而是更危险的：

```
candidate 编译
→ sample1~8 大量验证
→ checker contract 不完整
→ false-NO 被吞
→ 主观置信度升级成“AC”
→ 正式提交同一算法主体
→ WA65
```

这是“验证很多但 oracle 命题不完整”的标准反例。

# 5. C24｜确实重新编译并手测，但只做了很窄的单例

C 的 keystream 在 3:35～3:36 仍有大量算法代码编辑：
- `MOD=998244353`
- factorial / answer 计算
- 输出逻辑

随后：
- ZIP `T3/AC.cpp` = 22:21:12
- `T3/AC.o` = 22:21:12
- `T3/AC` = 22:21:14

这说明：
> 即使 keystream 没记录 F9 键，VM 文件时间仍证明这里发生了一次**新编译**；可能通过鼠标/IDE GUI 触发。

紧接着 keystream 3:36:34～3:36:45 手输：

```text
5
1 2 3 4 5
1 2
1 3
1 4
1 5
```

即：
- n=5
- priority 1..5
- 以1为中心的星形树

然后：
- 3:36:48 Ctrl+A
- 3:36:49 Ctrl+C
- 3:36:54 Ctrl+V
- 3:36:57～59 Backspace
- OJ 22:21:43

所以旧式说法：
> “C 最后临时写完，没编译就交”

不准确。

应改成：

> **C 最后主体确实重新编译，并至少手测过一棵 n=5 星形树；问题是验证域极窄，无法覆盖 n>8 后 factorial 猜法。**

最终24分与这种结构也一致：
- tiny brute 有效；
- 大数据猜法没有独立 oracle。

# 6. D15｜四题中最后交付闭环最强

最后源码编辑：
- 3:57:39～3:58:44：仍在补 special / 判断
- 3:59:20～3:59:25：输入 `Sunder`
- 3:59:27：Ctrl+S
- ZIP `T4/AC.cpp` = 22:44:10

随后先复制提交：
- 3:59:28 Ctrl+A
- 3:59:29 Ctrl+C
- 3:59:32 Ctrl+V
- 3:59:38～39 Backspace

但没有立刻交。

接下来又做手测：
- 3:59:55 起输入小数据
- 4:00:17：**F9**
- 再输 n=5 / 1 2 3 4 5
- 4:00:24：**第二次 F9**
- 再输 n=5 / 1 1 1 2 2
- ZIP `T4/AC` / `AC.o` = 22:45:08

OJ：
- 22:45:31 提交

所以 D 的算法主体在正式提交前约23秒**确实刚重新编译并跑过**。

这与它最终：
- TLE15；
- 小数据模型正确、复杂度不足

高度一致。

### 仍然存在的交付缝隙

OJ source 与本地 compiled source 唯一差异仍是：
```
//freopen → freopen
```

所以最终 traditional IO 字节没有被上述 F9 覆盖。

但四题相比：
> **D 是最接近“最终主体 → 编译 → 手测 → 提交”的健康 delivery chain。**

# 7. 四题验证强度对照

| 题 | 最后算法主体编译 | 最后验证 | OJ body一致 | submitted bytes exact local compiled? |
|---|---|---|---|---|
| A | 是 | 两附件 + diff | 是 | 否，仅 freopen 分叉 |
| B | 是 | sample1~8 + checker | 是 | 否，仅 freopen 分叉 |
| C | 是 | 至少1个 n=5 星形手测 | 是 | 否，仅 freopen 分叉 |
| D | 是 | 提交前两次 F9 + 两组手测 | 是 | 否，仅 freopen 分叉 |

## 最值得学的反差

### B
验证**数量**最高，却因为 checker 命题不完整而错。

### D
验证数量不多，但验证对象是当前最新主体，且最终拿到正确 brute partial 15。

所以：
> **验证质量 = oracle覆盖 × 字节身份 × 时效性，不能用“跑了多少样例”衡量。**

# 8. Day3 新的交付结论

Day3 比 Day1/Day2 已经明显进步：
- 四题算法主体都能映射到正式 OJ source；
- 没出现“提交了另一份旧算法文件”的严重 identity failure；
- C/D 甚至在最后几十秒仍有新编译证据。

但仍统一存在：

```
本地 AC.cpp（freopen 注释）
→ 编译/测试
→ 复制
→ 提交链中取消注释 freopen
→ OJ source
```

因此“测试字节 = 提交字节”仍未闭合。

这个问题后来在 Day5 再次发生，并最终推动出更强规则：

> **OJ source 必须 exact match 一个本地 VERIFIED/FROZEN 文件。**
>
> 任何 browser-only / submission-only mutation 都让状态从 VERIFIED 降级为 MODIFIED_UNVERIFIED。
