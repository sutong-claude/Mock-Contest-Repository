# BAG 演化史与赛场工作流：为什么 V4 Flat 真的变强

> BAG 不是“一个模板文件夹”。
>
> 它是把写代码、测样例、Debug、对拍、保存反例、交前检查、快速复原压成同一套赛场动作的工作系统。

## 1. 最早的问题不是功能少，而是工作流分裂

早期桌面同时存在：
- `problems/T1.cpp`
- `duipai_T1/`
- 独立 `debug/`
- Code::Blocks 工程
- 手敲 `g++ / diff`
- 大样例散落目录

于是同一题出现多个“候选代码身份”。

真实事故包括：
- 屏幕上改 A，F9 编译 B；
- 测过的是一份，最后交另一份；
- 对拍反例留在别的文件夹，修完以后不会自动回归；
- debug/main.cpp 被旧题污染；
- gen.cpp 为空还能假绿；
- CE 后继续跑旧 binary。

所以创建 BAG 的第一原则不是“多加功能”，而是：

> **先设计唯一事实源。**

---

## 2. Day4 暴露了更严重的问题：repo 与真实 VM 漂移

Day4 的真实虚拟机 `Desktop/bag/` 已经和 GitHub 里的 `tools/vm/bag_v2/` 不是同一个结构。

真实 VM 是：

```text
bag/T1/main.cpp
bag/T1/AC.cpp
bag/T1/WA.cpp
bag/T1/gen.cpp
```

而仓库还停在：

```text
problems/T1.cpp
duipai_T1/
...
```

甚至真实 `T1/main.cpp` 已经被旧 Debug 示例污染。

这给出一条长期规则：

> **赛场工具必须有版本号、可重建 release、doctor/selftest；不能靠“桌面上那个 bag 应该就是最新版”。**

---

## 3. V3.1：先消灭“假安全感”

V3.1 的重点不是目录好不好看，而是 runner 不能撒谎。

它补掉了：
- 空 generator 假绿；
- CE 后继续跑 stale binary；
- candidate 死循环无 timeout；
- 大样例不能批量跑；
- active freopen 最终形态没实测；
- stress 失败不留证据；
- reset 丢 samples；
- 恶意 ZIP 路径；
- 中文 / 空格 / 括号文件名；
- SPJ 不能直接 diff；
- ASan / UBSan；
- 大量样例 / 大输入 / 多组 stress 压力测试。

V3.1 的关键词是：

> **可靠 runner。**

---

## 4. V3.2：第一次真正纠正“工作流模型”

V3.1 仍然把：
- samples；
- debug；
- stress；
- candidate；

当成几套不同系统。

V3.2 开始意识到：

> **一题就应该只有一个工作区。**

可见层收缩成：

```text
T1/
  main.cpp
  oracle/brute
  gen.cpp
  notes.txt
  AC.cbp
  run.sh
  *.in / *.out
```

真正收益不是“少几个目录”，而是减少比赛时的心智分叉。

---

## 5. V4 Flat：最关键的统一——所有测试都是 testcase

V4 的核心抽象：

> 官方样例、手工 Hack、对拍反例，本质上完全一样：input + expected output。

### 官方样例
```text
sample1.in
sample1.out
```

### 手造 Debug
```text
corner.in
corner.out
```

### 对拍失败
自动产生：
```text
debug_001.in
debug_001.out
debug_001.got
debug_001.txt
```

对拍反例从这一刻起，直接成为普通回归样例。

修完 `main.cpp` 后，仍然只需要：

```bash
bash run.sh
```

这才是“所有东西融为一体”。

---

## 6. V4 的一个事实源

可见文件角色固定：

- `main.cpp`：唯一 candidate、唯一提交源；
- `WA.cpp`：独立 brute/oracle（保留旧命名）；
- `gen.cpp`：generator；
- `notes.txt`：P/E/H/X 研究笔记；
- `AC.cbp`：Code::Blocks 只构建 main.cpp；
- `run.sh`：统一入口；
- `duipai.sh`：只是兼容旧手感，本质仍走同一 runner。

内部复杂度隐藏到：
- `.bag_runner.py`
- `.bag_bin/`

比赛时不需要管理它们。

---

## 7. 四个命令其实是同一代码资产的四层验证

```bash
bash run.sh
```
普通全部回归。

```bash
bash run.sh s
```
同一批 testcase + ASan/UBSan。

```bash
bash run.sh p 10000
```
同一 `main.cpp` 对拍；失败反例直接进入当前 testcase 池。

```bash
bash run.sh c
```
exact compile + 全回归 + active freopen smoke。

不是四套工具，而是同一对象的不同验证强度。

---

## 8. reset / history 为什么也重要

V4 reset：
- 当前 T1 原子 move 到隐藏 `.history/`；
- 从干净模板重建 T1。

所以：
- 大样例不需要复制一遍；
- 旧源码 / notes / debug cases 全保留；
- 需要时还能恢复；
- 归档完成后再 purge 回收磁盘。

这直接吸收了 Day4 的磁盘/环境事故。

---

## 9. 从零创建一个好 BAG 的正确顺序

### 第一步：定义唯一事实源
candidate 只能有一个；提交源必须就是平时测试那份。

### 第二步：定义最小可见表面
比赛时只看：
- main.cpp
- WA.cpp
- gen.cpp
- notes.txt
- testcase
- run.sh

### 第三步：统一 testcase
任何确认过的反例都必须永久进入回归集合。

### 第四步：runner 先保证“不撒谎”
故障注入至少覆盖：
- CE；
- stale binary；
- TLE；
- RE；
- 空 generator；
- oracle RE/TLE；
- both-empty fake green；
- bad freopen；
- SPJ；
- 中文路径；
- 恶意 ZIP。

### 第五步：用真实比赛材料验收
不能只跑 toy。
至少拿一题真实 AC 源码 + 真实官方附件。

### 第六步：再做压力
- 50MB 输入；
- 数千样例；
- 数千/万组 stress；
- reset 大目录。

### 第七步：doctor + release + hash
每个 release 都应该可重建、可验收。

---

## 10. BAG 仍然不能替你解决

1. SPJ/checker 的语义正确性；
2. brute/oracle 自己写错；
3. Code::Blocks GUI 在真实 NOI Linux VM 的人机问题。

所以 BAG 的使命不是：

> “替你证明算法。”

而是：

> **让正确的验证动作变得极便宜，让错误的工程动作变得很难发生。**

---

## 11. 2026-10-07 再验收

本轮从 ChatGPT Library 重新 materialize 正式包：

`bag_v4_flat_integrated.zip`

SHA-256：

`326bc566a3a1ba039354af86d6e91ba57b2feb8d10bb1e5cc2d2d06c0e5bca55`

重新实际运行：
- `doctor.sh`：PASS；
- 一个平铺 sample：PASS；
- 独立 `main.cpp / WA.cpp / gen.cpp` stress 300 组：PASS，当前容器约 190 tests/s。

因此 V4 不是只存在于说明文档里的构想；当前 release 仍可实际运行。
