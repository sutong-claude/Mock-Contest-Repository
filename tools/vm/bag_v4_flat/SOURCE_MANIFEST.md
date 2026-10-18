# BAG V4 Flat — 源码同步说明

2026-10-07 从 ChatGPT Library 的正式包重新 materialize：

`/CSP-S比赛工具/BAG V4 Flat/bag_v4_flat_integrated.zip`

原 ZIP SHA-256：

`326bc566a3a1ba039354af86d6e91ba57b2feb8d10bb1e5cc2d2d06c0e5bca55`

仓库现在不再只有 README / TEST_REPORT，而保存**可维护的 source mirror**：

```text
source/
  README.txt
  doctor.sh
  reset.sh
  template/
    .bag_runner.py
    AC.cbp
    AC.layout
    WA.cpp
    duipai.sh
    gen.cpp
    main.cpp
    notes.txt
    run.sh
build_release.sh
```

`build_release.sh` 会从模板生成 T1～T4 并打出 ZIP。正式 Library ZIP 仍是字节级权威版本；Git 中的 source mirror 面向维护和重建，不承诺重打 ZIP 后字节哈希与历史 ZIP 完全相同（ZIP 时间戳等也会影响哈希）。

## 本轮重新冒烟

实际重新执行：
- doctor：PASS；
- 平铺 sample：PASS；
- 独立 main.cpp / WA.cpp / gen.cpp stress 300 组：PASS。

## 仍需真实 NOI Linux VM 验收

- Code::Blocks GUI；
- 实际比赛桌面的人机手感；
- 宿主机/VM 共享剪贴板；
- recorder 与 BAG 同时开启时的磁盘水位。

另外，BAG 无法自动证明：
- SPJ/checker 语义；
- oracle 自身正确性。
