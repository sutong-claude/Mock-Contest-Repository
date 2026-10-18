# Day4 B｜T2 对拍污染链：非法 generator × 错 oracle × 真实假绿/假红

> 本文件只使用三包原始文件与本轮独立程序验证。
>
> 目标：把旧结论“oracle 漏了端点条件”升级成可复现的完整因果链。

## 1. 题面契约

B《蜗蜗的频谱窗》要求对窗口 [l,r] 选择一个全局出现过的频率 v，并同时满足：

1. `v != a[l]`
2. `v != a[r]`
3. 删除窗口内所有等于 v 的元素后，剩余序列严格递增。

同时数据保证：

```
1 <= a_i <= n
```

## 2. 赛时 generator 本身大量生成非法输入

原件：
`Day4/T2/gen.cpp`

核心：

```cpp
int n = Rand(1, 10);
cout << 1 << '\n';
cout << n << '\n';
for (int i = 1; i <= n; i++)
    cout << Rand(1, 13) << ' ';
```

问题：
- n 只有 1..10；
- a_i 却固定取 1..13；
- 当 n<13 时会大量出现 a_i>n，违反题面。

在 generator 自己的均匀分布下，单个 case 合法的精确概率为：

```
(1/10) * sum_{n=1..10} (n/13)^n
≈ 0.0282690368
```

即约 **2.83% 合法 / 97.17% 非法**。

所以即使跑上万轮，大部分“反例”也不属于原题定义域。

## 3. 现场残留证明：对拍真的停在非法输入上

原始 `T2` 目录残留：

`1.txt`：

```
1
7
1 3 10 7 4 8 10
```

`2.txt`（AC.cpp）：

```
4
```

`3.txt`（WA.cpp）：

```
5
```

而 n=7 时题面要求每个 a_i<=7；该 case 中有 10、8、10。

因此 [P/source]：

> **这一次让 duipai.sh 真正停止的 diff 来自非法输入。**

现场 `notes.txt` 的末尾也保留了完全相同的 case：

```
1
7
1 3 10 7 4 8 10
```

这不是“generator 理论上可能错”，而是已经进入实际 Debug 流程的污染证据。

## 4. 错 oracle：AC.cpp 忘了端点不能被删

原件：
`Day4/T2/AC.cpp`

它枚举：
- 窗口 i..j；
- 全局某个 a[k] 作为 v；
- 删除窗口内所有等于 a[k] 的值；
- 判断剩余序列是否严格递增。

但源码完全没有：

```cpp
a[k] != a[i]
a[k] != a[j]
```

所以它允许：
- v 等于左端点；
- v 等于右端点；
- 甚至把端点删掉后再判“合法”。

这与题面条件直接冲突。

### 最小反例

n=1, a=[1]

真题：
- 全局只有 v=1；
- 但 v=a_l=a_r；
- 不允许选；
- 答案 0。

错 oracle：
- 选 v=1；
- 把唯一元素删掉；
- 空 vector 没触发“不递增”；
- 返回 1。

所以：
```
flawed AC = 1
truth = 0
```

## 5. 不靠手挑：合法输入全穷举三方对照

本轮直接编译三包里的**原版**：
- `T2/AC.cpp`
- `T2/WA.cpp`

另写独立真 oracle，严格实现题面：
- v 必须全局出现；
- v!=a_l；
- v!=a_r；
- 删除 v 后严格递增。

穷举所有：

```
n = 1..6
a_i in [1,n]
```

总计 **50,069 个完全合法输入**。

结果：

| n | 合法输入数 | 错 oracle != truth | candidate != truth | false green | false red |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 1 | 0 |
| 2 | 4 | 4 | 4 | 4 | 0 |
| 3 | 27 | 24 | 24 | 18 | 0 |
| 4 | 256 | 214 | 210 | 162 | 12 |
| 5 | 3,125 | 2,341 | 2,238 | 1,601 | 380 |
| 6 | 46,656 | 31,834 | 32,312 | 20,289 | 5,795 |
| **合计** | **50,069** | **34,418** | **34,789** | **22,075** | **6,187** |

比例：
- 错 oracle 自己错误：**68.74%**
- candidate 自己错误：**69.48%**
- **false green：44.09%**
- **false red：12.36%**

定义：
- false green：`candidate == flawed_oracle != truth`
- false red：`candidate == truth != flawed_oracle`

所以这不是“oracle 偶尔漏一个边界”。

在 n<=6 的合法全空间里，它能同时制造大量：

```
错误 candidate + 错 oracle
→ diff 相等
→ 假绿
```

和：

```
正确 candidate + 错 oracle
→ diff 不等
→ 假红
```

## 6. 可复现最小假绿 / 假红

### 假绿

```
n=1
a=[1]

flawed oracle = 1
candidate      = 1
truth          = 0
```

duipai 会显示 right，但 candidate 实际错。

### 假红

第一个 n=4 例：

```
a=[1,3,2,2]

flawed oracle = 4
candidate      = 3
truth          = 3
```

candidate 实际正确，却会被 diff 打成 wrong。

因此“对拍报错 → candidate 必然有 Bug”在这套工具上同样不成立。

## 7. duipai.sh 为什么会直接传播污染

原件：

```bash
./gen > 1.txt
./AC < 1.txt > 2.txt
./WA < 1.txt > 3.txt
diff -w 2.txt 3.txt || { echo "wrong on test $i"; break; }
```

它没有任何：
- 输入合法性验证；
- oracle sanity test；
- 多 oracle 交叉；
- 特殊边界固定样例。

所以一旦 gen 或 AC 任一层出错，错误会被直接包装成“WA 的反例”。

## 8. Day4 B 的赛时诊断升级

旧诊断：
> 有对拍，但 oracle 漏端点条件。

现在应升级为：

```
generator 约97.17%概率生成题面外数据
+
实际停止 case 就是非法输入
+
AC oracle 漏掉 v != endpoints
+
合法 n<=6 全穷举显示大量 false green / false red
↓
diff 信号失去真值语义
↓
Debug 可能修 candidate，也可能在追 oracle/gen 制造的幻觉
↓
后半段信息增益坍塌
```

这比泛泛说“checker/oracle 也可能错”更重要：

> **真对拍不是四个文件凑齐；真对拍必须闭合 generator domain + oracle contract + candidate contract。**

## 9. 下一场固定 sanity protocol

对拍启动前先做：

### Generator
- assert 每个随机字段满足题面范围；
- 至少固定 5 个边界 case；
- 打印/保留 seed。

### Oracle
- 手工最小样例；
- n=1 / n=2；
- 题面每个“且/或/端点/存在性”条件至少一例；
- 能小空间穷举时，先用第二种独立实现对 oracle 自测。

### Stress
每次 diff 前，概念上应满足：

```
valid(input)
&& oracle_verified(input)
```

不能只写：

```
AC != WA
=> WA wrong
```

## 10. 证据等级

- generator 超范围：[P/source]
- 现场停止 case 非法：[P/source]
- AC 漏端点：[P/source]
- 50,069 合法输入三方穷举：[E]
- false green / false red 最小例：[E/X]
- “这导致某一分钟具体改错了哪一行”：仍需与 recovered keyboard / timeline 继续对齐，不在本文件凭空断言。
