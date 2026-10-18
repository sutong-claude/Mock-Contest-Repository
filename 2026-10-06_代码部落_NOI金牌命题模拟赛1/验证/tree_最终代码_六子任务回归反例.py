#!/usr/bin/env python3
"""代码部落 tree 最终提交：六个子任务的可复现反例集。

可直接：
    python tree_最终代码_六子任务回归反例.py /path/to/tree_executable

若传入 executable，本脚本会在临时目录写 tree.in、运行程序、读取 tree.out。
这些 case 的真值均可由题意直接证明，不依赖赛时代码。

覆盖：
- task1/2: n<=300 / n<=5000 同一小反例；
- task3: l_i=r_i；
- task4: 星形；
- task5: 链；
- task6: 一般树。
"""

from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys


def emit(n, intervals, edges):
    out=[str(n)]
    out += [f"{l} {r}" for l,r in intervals]
    out += [f"{u} {v}" for u,v in edges]
    return "\n".join(out)+"\n"


def cases():
    # task1/2: 程序把起点时间当0。
    yield {
        "name":"task1_task2_start_time",
        "input":emit(
            3,
            [(100,100),(1,1),(50,50)],
            [(1,2),(2,3)],
        ),
        "expected":"2",
        "why":"2->3 可在1,50访问；任何3点有向路径都无法严格递增。"
    }

    # task3: n>5000 才进入性质A分支；该分支最终为空，直接 return。
    n=5001
    yield {
        "name":"task3_A_empty_branch",
        "input":emit(
            n,
            [(i,i) for i in range(1,n+1)],
            [(i,i+1) for i in range(1,n)],
        ),
        "expected":str(n),
        "why":"1->2->...->5001 在日期1..5001逐点访问，整链可行；最终代码性质A分支不输出。"
    }

    # task4: 星形。root=1 [1,2]；一片叶[1,2]，其余叶[1,1]。
    # 任意3点路径 leaf-root-leaf 需要三个严格递增整数；
    # 两端叶的上界都<=2，不可能长度3。leaf(day1)->root(day2) 可行，故真值2。
    # 赛时代码把“能单独 leaf->root”和“能单独 root->leaf”拼成3，忽略两侧要共享同一个root访问日。
    intervals=[(1,2),(1,2)]+[(1,1)]*(n-2)
    yield {
        "name":"task4_star_joint_center_time",
        "input":emit(
            n,
            intervals,
            [(1,i) for i in range(2,n+1)],
        ),
        "expected":"2",
        "why":"最长只能2；左右可行性必须共享同一个中心访问日，不能独立拼接。"
    }

    # task5: 链且A=false。整条链显然可行。
    intervals=[(i,i) for i in range(1,n)]
    intervals.append((n,n+1))
    yield {
        "name":"task5_chain_full_feasible",
        "input":emit(
            n,
            intervals,
            [(i,i+1) for i in range(1,n)],
        ),
        "expected":str(n),
        "why":"取路径1->...->5001，访问日x_i=i，全部合法。"
    }

    # task6: 非星、非链、A=false 的双中心树。
    # 所有窗口[1,2]：任意一条边可访问2点；严格递增整数只有1,2，
    # 所以不可能访问3点，真值恰好2。最终 general fallback 输出1。
    edges=[(1,2)]
    edges += [(1,i) for i in range(3,2502)]
    edges += [(2,i) for i in range(2502,n+1)]
    assert len(edges)==n-1
    yield {
        "name":"task6_general_fallback",
        "input":emit(n,[(1,2)]*n,edges),
        "expected":"2",
        "why":"任意边可用1->2访问两个点；只有两个可用整数日，因此三点不可能。"
    }


def run_one(exe, case):
    with TemporaryDirectory() as td:
        td=Path(td)
        (td/"tree.in").write_text(case["input"],encoding="utf-8")
        p=subprocess.run(
            [str(Path(exe).resolve())],
            cwd=td,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        out=(td/"tree.out").read_text(encoding="utf-8") if (td/"tree.out").exists() else ""
        return p.returncode, out.strip(), p.stderr.decode("utf-8","replace").strip()


def main():
    cs=list(cases())
    exe=sys.argv[1] if len(sys.argv)>=2 else None
    for c in cs:
        print(f"[{c['name']}] expected={c['expected']}")
        print(" proof:",c["why"])
        if exe:
            rc,out,err=run_one(exe,c)
            print(f" final: rc={rc}, tree.out={out!r}")
            if err:
                print(" stderr:",err)
            if out==c["expected"]:
                raise SystemExit(f"unexpectedly passed counterexample: {c['name']}")
    print("COUNTEREXAMPLE SUITE READY")


if __name__=="__main__":
    main()
