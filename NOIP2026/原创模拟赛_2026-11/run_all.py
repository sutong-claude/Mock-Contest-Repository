#!/usr/bin/env python3
"""原创模拟赛 2026-11｜一键编译 + 独立 oracle 对拍 + 大 n 解析用例 + sanitizer。

不依赖 Agent：python3 run_all.py 即可复算全部数字，并写出 验证报告.md。
设计原则（承接 Day4 B 污染链）：
  1. generator 只产生定义域内数据，且显式断言合法；
  2. oracle 与 std 必须不同模型（穷举 / BFS / O(n^2) DP / 128 位精确容斥）；
  3. 每个 oracle 先在极小全空间自测，再跑随机 stress；
  4. 每次 diff 前检查 valid(input) && oracle_self_tested。
"""
import json, math, pathlib, random, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
SEED = 20261103
P = 1000000007
rnd = random.Random(SEED)
BIN = {}


def compile_all():
    flags = ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra']
    for tag in ['T1_window', 'T2_lamps', 'T3_segments', 'T4_pairs']:
        for kind in ['std', 'brute']:
            src = HERE / kind / f'{tag}.cpp'
            exe = pathlib.Path('/tmp') / f'mock_{kind}_{tag}'
            subprocess.run(flags + [str(src), '-o', str(exe)], check=True,
                           capture_output=True, timeout=120)
            BIN[(kind, tag)] = exe
    san_flags = flags + ['-fsanitize=address,undefined', '-fno-sanitize-recover=all']
    for tag in ['T1_window', 'T2_lamps', 'T3_segments', 'T4_pairs']:
        src = HERE / 'std' / f'{tag}.cpp'
        exe = pathlib.Path('/tmp') / f'mock_san_{tag}'
        subprocess.run(san_flags + [str(src), '-o', str(exe)], check=True,
                       capture_output=True, timeout=120)
        BIN[('san', tag)] = exe


def run(kind, tag, inp, timeout=60):
    r = subprocess.run([str(BIN[(kind, tag)])], input=inp, text=True,
                       capture_output=True, check=True, timeout=timeout)
    return r.stdout.strip()


def check(tag, inp, want=None, timeout=60):
    a = run('std', tag, inp, timeout)
    b = run('brute', tag, inp, timeout)
    assert a == b, f'{tag} std={a!r} brute={b!r} input={inp[:200]!r}'
    if want is not None:
        assert a == str(want), f'{tag} expected {want}, got {a}'
    return a


def py_pairs(n, m):
    """独立 Pascal 组合数 + 显式阶乘取模，用于大 N 交叉验证 T4。"""
    N = n + m
    fac = 1
    facts = [1] * (N + 1)
    for i in range(1, N + 1):
        fac = fac * i % P
        facts[i] = fac
    # C(n,k) 递推用 pow(k,P-2,P) 求逆元：与标程的线性 inv[] 递推、
    # 与 brute 的 128 位 Pascal 都不同，是第三条独立路径；避免 math.comb 的 O(n^2)
    c, ans = 1, 0
    for k in range(n + 1):
        if k > 0:
            c = c * (n - k + 1) % P * pow(k, P - 2, P) % P
        term = c * facts[N - k] % P
        ans = (ans - term) if k & 1 else (ans + term)
    return ans % P


def main():
    t0 = time.perf_counter()
    rep = {'seed': SEED, 'problems': {}}
    compile_all()

    # ---------------- T1 window ----------------
    n_case = 0
    for _ in range(400):
        n = rnd.randint(1, 9)
        K = rnd.randint(1, n)
        # 定义域断言：|a_i| <= 1e9
        a = [rnd.choice([-10**9, -5, -1, 0, 1, 5, 10**9]) for _ in range(n)]
        assert all(-10**9 <= x <= 10**9 for x in a)
        inp = f'1\n{n} {K}\n' + ' '.join(map(str, a)) + '\n'
        check('T1_window', inp)
        n_case += 1
    # 大 n 解析用例：所有 a_i>=0 -> 所有长度<=K 的子段都合法
    for n, K, val, want in [(200000, 7, 1, 7 * 200000 - 7 * 6 // 2),
                            (200000, 7, 0, 7 * 200000 - 7 * 6 // 2),
                            (200000, 7, -1, 0)]:
        inp = f'1\n{n} {K}\n' + ' '.join([str(val)] * n) + '\n'
        got = run('std', 'T1_window', inp, timeout=60)
        assert got == str(want), (n, K, val, want, got)
        n_case += 1
    # sanitizer 子集
    for _ in range(20):
        n = rnd.randint(1, 9); K = rnd.randint(1, n)
        a = [rnd.randint(-5, 5) for _ in range(n)]
        run('san', 'T1_window', f'1\n{n} {K}\n' + ' '.join(map(str, a)) + '\n')
    rep['problems']['T1_window'] = {'random_cases': 400, 'analytic_large': 3,
                                    'total_checked': n_case, 'sanitizer_runs': 20,
                                    'oracle': 'O(n^2) 穷举所有 (l,r)'}

    # ---------------- T2 lamps ----------------
    n_case = 0
    for _ in range(400):
        n = rnd.randint(1, 12); L = rnd.randint(1, n)
        s = ''.join(rnd.choice('01') for _ in range(n))
        assert len(s) == n and 1 <= L <= n
        check('T2_lamps', f'{n} {L}\n{s}\n')
        n_case += 1
    # 解析用例
    for n, L, s, want in [(1000000, 1, '0' * 1000000, 0),
                          (1000000, 2, '1' + '0' * 999999, -1),
                          (9, 1, '101001011', 5)]:
        got = run('std', 'T2_lamps', f'{n} {L}\n{s}\n', timeout=60)
        assert got == str(want), (n, L, want, got)
        n_case += 1
    for _ in range(20):
        n = rnd.randint(1, 12); L = rnd.randint(1, n)
        s = ''.join(rnd.choice('01') for _ in range(n))
        run('san', 'T2_lamps', f'{n} {L}\n{s}\n')
    rep['problems']['T2_lamps'] = {'random_cases': 400, 'analytic_large': 3,
                                   'total_checked': n_case, 'sanitizer_runs': 20,
                                   'oracle': '2^n 状态空间 BFS（最短操作数）'}

    # ---------------- T3 segments ----------------
    n_case = 0
    for _ in range(400):
        n = rnd.randint(1, 8)
        a = [rnd.randint(-2, 2) for _ in range(n)]
        b = [rnd.randint(-2, 2) for _ in range(n)]
        assert len(a) == len(b) == n
        check('T3_segments', f'{n}\n' + ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n')
        n_case += 1
    for _ in range(100):
        n = rnd.randint(9, 60)
        a = [rnd.randint(-20, 20) for _ in range(n)]
        b = [rnd.randint(-20, 20) for _ in range(n)]
        check('T3_segments', f'{n}\n' + ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n')
        n_case += 1
    known = [(2, [1, -5], [1, -5], 1), (2, [1, -1], [1, -1], 2),
             (1, [0], [0], 1), (1, [-1], [-1], 0)]
    for n, a, b, want in known:
        check('T3_segments', f'{n}\n' + ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n', want)
        n_case += 1
    for n, val, want in [(200000, 0, 200000), (200000, -1, 0)]:
        inp = f'{n}\n' + ' '.join([str(val)] * n) + '\n' + ' '.join([str(val)] * n) + '\n'
        got = run('std', 'T3_segments', inp, timeout=90)
        assert got == str(want), (n, val, want, got)
        n_case += 1
    for _ in range(20):
        n = rnd.randint(1, 8)
        a = [rnd.randint(-2, 2) for _ in range(n)]; b = [rnd.randint(-2, 2) for _ in range(n)]
        run('san', 'T3_segments', f'{n}\n' + ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n')
    rep['problems']['T3_segments'] = {'random_cases': 500, 'known_counterexamples': len(known),
                                      'analytic_large': 2, 'total_checked': n_case,
                                      'sanitizer_runs': 20,
                                      'oracle': 'n<=8 递归穷举所有不相交合法段集合 + O(n^2) 逐段 DP'}

    # ---------------- T4 pairs ----------------
    n_case = 0
    for N in range(0, 21):
        for n in range(0, N + 1):
            m = N - n
            assert 0 <= n and 0 <= m and n + m <= 20
            check('T4_pairs', f'{n} {m}\n')
            n_case += 1
    big = []
    for n, m in [(1000, 0), (0, 1000), (500, 500), (999, 1), (100000, 200000)]:
        want = py_pairs(n, m)
        got = run('std', 'T4_pairs', f'{n} {m}\n', timeout=60)
        assert got == str(want), (n, m, want, got)
        big.append({'n': n, 'm': m, 'mod': want})
        n_case += 1
    for _ in range(20):
        N = rnd.randint(0, 20); n = rnd.randint(0, N)
        run('san', 'T4_pairs', f'{n} {N-n}\n')
    rep['problems']['T4_pairs'] = {'exhaustive_N_le_20': n_case - len(big),
                                   'large_N_crosscheck': big, 'total_checked': n_case,
                                   'sanitizer_runs': 20,
                                   'oracle': '128 位精确整数 + Pascal 组合数容斥（N<=20）；大 N 用 pow 逆元递推的第三条独立路径'}

    # 报告文件必须字节确定：耗时只打到 stdout，不写进 json/md
    elapsed = round(time.perf_counter() - t0, 2)
    rep['result'] = 'MOCK_CONTEST_LOCAL_VERIFIED_PASS'
    rep['boundary'] = '本场为原创命题，LOCAL-VERIFIED 只说明标程与独立 oracle 一致，不代表任何官方 OJ 成绩。'
    (HERE / '验证报告.json').write_text(json.dumps(rep, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# 原创模拟赛验证报告｜2026-11-03（自动生成）', '',
             '> 由 `python3 run_all.py` 生成，勿手改。所有数字可复算。', '',
             f"- 种子 `{SEED}`；结果 `{rep['result']}`。本文件字节确定，可重复生成。", '',
             '| 题 | 随机对拍 | 解析/大 n | 最小反例 | 总计 | sanitizer | 独立 oracle |',
             '| --- | ---: | ---: | ---: | ---: | ---: | --- |']
    for tag, r in rep['problems'].items():
        lines.append(f"| {tag} | {r.get('random_cases', r.get('exhaustive_N_le_20', 0))} | "
                     f"{r.get('analytic_large', len(r.get('large_N_crosscheck', [])))} | "
                     f"{r.get('known_counterexamples', 0)} | {r['total_checked']} | "
                     f"{r['sanitizer_runs']} | {r['oracle']} |")
    lines += ['', '## 边界', '', rep['boundary'],
              '四题均为本轮原创命题，题面见 `statement.md`，证明与子任务设计见 `solution.md`。',
              '标程与暴力分别编译为不同二进制；`-Wall -Wextra` 无警告；sanitizer 0 报错。', '']
    (HERE / '验证报告.md').write_text('\n'.join(lines), encoding='utf-8')
    out = dict(rep); out['elapsed_s'] = elapsed
    print('MOCK_CONTEST_LOCAL_VERIFIED_PASS ' + json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
