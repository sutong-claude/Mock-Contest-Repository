BAG V4 FLAT — 一题 = 一个目录 = 一个实验室

核心不是 samples / debug / duipai 分开。
核心是所有测试都只是 testcase：

- 官方大样例：直接平铺成 *.in + *.out/.ans
- 你手造的 Debug 数据：也是 *.in + *.out
- 对拍打出来的反例：自动保存成 debug_001.in + debug_001.out

所以对拍失败以后，反例自动成为下一次 bash run.sh 会跑的普通回归样例。
没有 samples/，没有 debug/，没有 duipai_T1/。

每题目录只有 main.cpp / WA.cpp / gen.cpp / notes.txt / AC.cbp / run.sh / duipai.sh。

大样例：bash run.sh
对拍：bash duipai.sh 10000
调越界：bash run.sh s
交之前：bash run.sh c

如果对拍找到反例，会直接出现 debug_001.in/out/got。
修完 main.cpp 后只需再 bash run.sh。

快速复原：
  bash reset.sh T1
  bash reset.sh all

旧目录移动到隐藏 .history；归档完成后可 bash reset.sh purge 回收磁盘。
