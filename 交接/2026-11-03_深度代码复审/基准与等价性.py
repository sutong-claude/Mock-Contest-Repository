#!/usr/bin/env python3
"""Day1 A 三版等价性与复杂度基准（stdlib only，不需要 Agent 能力）。

三版：
  multiset : 2026-09-25.../赛时代码/A_v4_n方multiset_已提交_21-10.cpp   O(n^3)
  bit      : 2026-09-25.../正解代码/A_记录带_赛时代码只换树状数组.cpp    O(n^2 log n)
  rewrite  : 本目录 Day1A_改写_树状数组版.cpp                            O(n^2 log n) + 压缩/显式 64 位
验证：
  1) n<=6 全排列穷举（distinct）；
  2) 含重复值、含 |a_i|>n 的随机小数据（旧 bit 版不支持，故只比 multiset/rewrite）；
  3) 大 n 计时，实测 O(n^3) 与 O(n^2 log n) 的增长倍数。
输出全部为可复算数字，不写「感觉快」。
"""
import itertools, random, subprocess, sys, time, pathlib, json

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
MULTISET = '/tmp/day1a_multiset'
BIT = '/tmp/day1a_bit'
REWRITE = '/tmp/day1a_rewrite'


def compile_sources():
    """自编译：/tmp 不持久化，脚本每次自己从仓库源码编译三份二进制。"""
    sources = {
        MULTISET: ROOT / '2026-09-25_CSP-S模拟赛day1/赛时代码/A_v4_n方multiset_已提交_21-10.cpp',
        BIT: ROOT / '2026-09-25_CSP-S模拟赛day1/正解代码/A_记录带_赛时代码只换树状数组.cpp',
        REWRITE: HERE / 'Day1A_改写_树状数组版.cpp',
    }
    for exe, src in sources.items():
        assert src.is_file(), f'缺少源码 {src}'
        subprocess.run(['g++', '-std=c++17', '-O2', '-Wall', '-Wextra',
                        str(src), '-o', exe], check=True, timeout=180)
    return list(sources)


def run(binary, cases):
    inp = f'{len(cases)}\n'
    for a in cases:
        inp += f'{len(a)}\n' + ' '.join(map(str, a)) + '\n'
    r = subprocess.run([binary], input=inp, text=True, capture_output=True, timeout=180, check=True)
    return r.stdout.split()


def timed(binary, a, repeat=5):
    """一次进程内喂 repeat 组相同数据，用总耗时/repeat 消除 fork+exec 启动噪声。

    三份源码都支持多测 T，故可用同一份输入批量计时；返回值是单组数据的纯计算耗时。
    """
    one = f'{len(a)}\n' + ' '.join(map(str, a)) + '\n'
    inp = f'{repeat}\n' + one * repeat
    best = 1e18
    for _ in range(2):
        t0 = time.perf_counter()
        subprocess.run([binary], input=inp, text=True, capture_output=True, timeout=300, check=True)
        best = min(best, (time.perf_counter() - t0) / repeat)
    return best


def main():
    compile_sources()   # 不依赖任何预先存在的 /tmp 二进制
    report = {}
    # 1) 全排列穷举 n=1..6（720 组一次性喂给三个程序）
    cases = [list(p) for n in range(1, 7) for p in itertools.permutations(range(1, n + 1))]
    outs = {k: run(v, cases) for k, v in
            [('multiset', MULTISET), ('bit', BIT), ('rewrite', REWRITE)]}
    assert outs['multiset'] == outs['bit'] == outs['rewrite'], '全排列等价性失败'
    report['exhaustive_permutations'] = len(cases)
    report['all_three_agree'] = True

    # 2) 含重复值 / 越界值：旧 bit 版假设 a_i∈[1,n]，会越界，故退出对比
    rnd = random.Random(20261103)
    cases2 = [[rnd.randint(-5, 20) for _ in range(rnd.randint(1, 9))] for _ in range(400)]
    o1, o3 = run(MULTISET, cases2), run(REWRITE, cases2)
    assert o1 == o3, '重复/越界值等价性失败'
    report['duplicate_out_of_range_cases'] = len(cases2)
    report['multiset_vs_rewrite_agree'] = True

    # 3) 计时：同一随机排列，n = 100,200,400 对 multiset；加 800,1600 对 rewrite
    timings = {}
    for n in [100, 200, 400, 800, 1600]:
        a = list(range(1, n + 1))
        rnd.shuffle(a)
        row = {}
        row['rewrite_s'] = round(timed(REWRITE, a), 4)
        if n <= 400:
            row['multiset_s'] = round(timed(MULTISET, a), 4)
            row['speedup'] = round(row['multiset_s'] / max(row['rewrite_s'], 1e-4), 1)
            row['bit_s'] = round(timed(BIT, a), 4)
        timings[n] = row
    report['timings_s'] = timings
    report['complexity'] = 'distance(multiset iterator) = O(n) per query -> O(n^3); Fenwick = O(log n) -> O(n^2 log n)'
    report['note'] = 'rewrite 仍为 O(n^2 log n)：目标函数是 2D 最大子段和，本轮不声称已降到 O(n log n)。'
    print('DAY1A_EQUIVALENCE_PASS ' + json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
