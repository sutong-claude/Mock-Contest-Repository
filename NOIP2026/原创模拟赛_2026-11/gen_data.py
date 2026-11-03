#!/usr/bin/env python3
"""原创模拟赛 2026-11｜正式数据包生成器（确定性、答案来自独立真值）。

答案来源绝不依赖 std（避免 Day4 B 污染链的共模假绿）：
  - 小数据：brute/ 下完全独立模型的暴力程序输出；
  - 大数据：闭式解析公式，或 T4 用 pow 逆元递推的独立 Python 实现；
  - 每个 .in/.ans 记录 SHA256 到 data_manifest.json，judge.py 逐字节校验。

运行：python3 gen_data.py   → 写 data/ 与 data_manifest.json（字节确定，可重复生成）
"""
import hashlib, json, math, pathlib, random, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / 'data'
SEED = 20261103
P = 1000000007
rnd = random.Random(SEED)

# 子任务分值必须与 statement.md 一致；捆绑评分：组内全过才给分
SUBTASKS = {
    'T1': [20, 20, 20, 40], 'T2': [20, 20, 20, 40],
    'T3': [15, 25, 20, 40], 'T4': [15, 25, 20, 40],
}
TIME_LIMIT = {'T1': 2.0, 'T2': 2.0, 'T3': 3.0, 'T4': 2.0}
BRUTE = {}


def compile_brutes():
    for tag in ['T1_window', 'T2_lamps', 'T3_segments', 'T4_pairs']:
        exe = pathlib.Path('/tmp') / f'mock_brute_{tag}'
        subprocess.run(['g++', '-std=c++17', '-O2', '-Wall', '-Wextra',
                        str(HERE / 'brute' / f'{tag}.cpp'), '-o', str(exe)],
                       check=True, capture_output=True, timeout=120)
        BRUTE[tag[:2]] = exe


def brute_out(problem, inp):
    return subprocess.run([str(BRUTE[problem])], input=inp, text=True,
                          capture_output=True, check=True, timeout=120).stdout.strip()


def py_pairs_independent(n, m):
    """第三条独立路径：pow(k,P-2,P) 递推组合数，与 std 的线性 inv[] 完全不同。"""
    N = n + m
    fac = [1] * (N + 1)
    for i in range(1, N + 1):
        fac[i] = fac[i - 1] * i % P
    c, ans = 1, 0
    for k in range(n + 1):
        if k > 0:
            c = c * (n - k + 1) % P * pow(k, P - 2, P) % P
        term = c * fac[N - k] % P
        ans = (ans - term) if k & 1 else (ans + term)
    return ans % P


def t1_small(rng, n, lo, hi, K=None):
    K = K or rng.randint(1, n)
    a = [rng.randint(lo, hi) for _ in range(n)]
    return f'1\n{n} {K}\n' + ' '.join(map(str, a)) + '\n', None


def t1_analytic(n, K, kind):
    if kind == 'pos':
        a = [1] * n
        ans = K * n - K * (K - 1) // 2
    elif kind == 'zero':
        a = [0] * n
        ans = K * n - K * (K - 1) // 2
    elif kind == 'neg':
        a = [-1] * n
        ans = 0
    elif kind == 'extreme_k1':
        # K=1 时只有长度 1 区间合法，答案 = 非负元素个数；用 ±1e9 压测 64 位
        a = [10**9 if i % 2 == 0 else -10**9 for i in range(n)]
        K = 1
        ans = sum(1 for x in a if x >= 0)
    return f'1\n{n} {K}\n' + ' '.join(map(str, a)) + '\n', str(ans)


def t2_small(rng, n, L=None):
    L = L or rng.randint(1, n)
    s = ''.join(rng.choice('01') for _ in range(n))
    return f'{n} {L}\n{s}\n', None


def t2_analytic(n, kind):
    if kind == 'zero':
        return f'{n} 1\n' + '0' * n + '\n', '0'
    if kind == 'impossible':
        return f'{n} 2\n1' + '0' * (n - 1) + '\n', '-1'
    if kind == 'L1_count':
        s = ''.join('1' if i % 3 != 0 else '0' for i in range(n))
        return f'{n} 1\n{s}\n', str(s.count('1'))


def t3_small(rng, n, lo, hi, equal=False):
    a = [rng.randint(lo, hi) for _ in range(n)]
    b = list(a) if equal else [rng.randint(lo, hi) for _ in range(n)]
    return f'{n}\n' + ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n', None


def t3_analytic(n, kind):
    if kind == 'all_zero':
        row = ' '.join(['0'] * n)
        return f'{n}\n{row}\n{row}\n', str(n)
    if kind == 'all_neg':
        row = ' '.join(['-1'] * n)
        return f'{n}\n{row}\n{row}\n', '0'
    if kind == 'all_big':
        row = ' '.join(['1000000000'] * n)
        return f'{n}\n{row}\n{row}\n', str(n)


def t4_case(n, m, independent):
    inp = f'{n} {m}\n'
    ans = str(py_pairs_independent(n, m)) if independent else None
    return inp, ans


def build():
    compile_brutes()
    DATA.mkdir(exist_ok=True)
    # 清空旧数据（不含目录本身）
    for f in DATA.rglob('*'):
        if f.is_file():
            f.unlink()
    cases = []
    for pi, (prob, points) in enumerate(SUBTASKS.items(), start=1):
        d = DATA / prob
        d.mkdir(exist_ok=True)
        for s in range(1, 5):
            for k in range(1, 4):
                independent = True
                if prob == 'T1':
                    if s == 1:
                        inp, ans = t1_small(rnd, rnd.randint(1, 12), -10, 10); independent = False
                    elif s == 2:
                        inp, ans = t1_small(rnd, rnd.randint(600, 1500), -50, 50); independent = False
                    elif s == 3:
                        inp, ans = t1_analytic(rnd.randint(100, 1000), rnd.randint(1, 20),
                                               ['pos', 'zero'][k % 2]); independent = True
                    else:
                        n_big = 200000 if k <= 2 else 100000   # ±1e9 压测 64 位，10^5 已远超 int
                        inp, ans = t1_analytic(n_big, 7,
                                               ['pos', 'neg', 'extreme_k1'][k - 1]); independent = True
                elif prob == 'T2':
                    if s == 1:
                        inp, ans = t2_small(rnd, rnd.randint(1, 12)); independent = False
                    elif s == 2:
                        # L=1 时解唯一且恒存在：答案闭式 = 1 的个数（brute BFS 仅适用 n<=12）
                        n = rnd.randint(100, 1000)
                        inp, _ = t2_small(rnd, n, L=1)
                        ans = str(inp.splitlines()[1].count('1')); independent = True
                    elif s == 3:
                        # 保证有解：由 L=1 构造，贪心答案 = 1 的个数
                        n = rnd.randint(100, 1000)
                        inp, _ = t2_small(rnd, n, L=1)
                        ans = str(inp.splitlines()[1].count('1')); independent = True
                    else:
                        n_big = 1000000 if k == 1 else 200000   # 保留 1 个满规模用例，其余避免纯重复大文件
                        inp, ans = t2_analytic(n_big, ['zero', 'impossible', 'L1_count'][k - 1]); independent = True
                elif prob == 'T3':
                    if s == 1:
                        inp, ans = t3_small(rnd, rnd.randint(1, 8), -2, 2); independent = False
                    elif s == 2:
                        inp, ans = t3_small(rnd, rnd.randint(600, 1500), -1, 1); independent = False
                    elif s == 3:
                        inp, ans = t3_small(rnd, rnd.randint(600, 1500), -5, 5, equal=True); independent = False
                    else:
                        n_big = 200000 if k <= 2 else 90000   # 保持单文件 < 2 MiB，避免被全量导出器当超尺寸跳过
                        inp, ans = t3_analytic(n_big, ['all_zero', 'all_neg', 'all_big'][k - 1]); independent = True
                else:
                    if s == 1:
                        N = rnd.randint(0, 8); n = rnd.randint(0, N)
                    elif s == 2:
                        N = rnd.randint(9, 20); n = rnd.randint(0, N)
                    elif s == 3:
                        n = rnd.randint(1, 1000); N = n
                    else:
                        n, N = [(1000, 1000), (0, 1000000), (123456, 876544)][k - 1]
                    m = N - n
                    inp, ans = t4_case(n, m, independent=(s == 3 or s == 4))
                    independent = s == 3 or s == 4
                if ans is None:
                    ans = brute_out(prob, inp)
                src = 'brute_oracle' if not independent else (
                    'analytic_closed_form' if prob != 'T4' else 'python_pow_inverse_independent')
                stem = f's{s}_{k}'
                (d / f'{stem}.in').write_text(inp, encoding='utf-8', newline='')
                (d / f'{stem}.ans').write_text(ans + '\n', encoding='utf-8', newline='')
                cases.append({
                    'id': f'{prob}-{stem}', 'problem': prob, 'subtask': s,
                    'points': points[s - 1], 'in': f'data/{prob}/{stem}.in',
                    'ans': f'data/{prob}/{stem}.ans',
                    'in_sha256': hashlib.sha256((d / f'{stem}.in').read_bytes()).hexdigest(),
                    'ans_sha256': hashlib.sha256((d / f'{stem}.ans').read_bytes()).hexdigest(),
                    'answer_source': src,
                })
    # ---- 定向 hack 点：把考古/代码复审里的最小反例固化成正式数据 ----
    # 这些点专门用来杀死「评测器自检」暴露的覆盖缺口；真值来自独立 oracle/手算，
    # 并在 00_代码复审总览.md §1.1 与 solution.md T3 §5 有出处。
    hacks = [
        ('T3', 4, 'h1', '4\n-2 1 1 -1\n0 -1 1 -1\n', '3', 'known_minimal_counterexample'),
        ('T3', 4, 'h2', '1\n0\n0\n', '1', 'known_minimal_counterexample'),
        ('T3', 4, 'h3', '2\n1 -5\n1 -5\n', '1', 'known_minimal_counterexample'),
        ('T3', 4, 'h4', '2\n1 -1\n1 -1\n', '2', 'known_minimal_counterexample'),
        ('T4', 4, 'h1', '0 0\n', '1', 'endpoint_closed_form'),
        ('T4', 4, 'h2', '1 0\n', '0', 'endpoint_closed_form'),
        ('T4', 4, 'h3', '3 3\n', '426', '128bit_exact_permanent_independent'),
        ('T1', 4, 'h1', '1\n3 3\n1 -1 1\n', '5', 'brute_oracle_verified'),
        ('T2', 4, 'h1', '5 3\n10110\n', '-1', 'bfs_oracle_verified'),
    ]
    for prob, s, tag, inp, ans, src in hacks:
        d = DATA / prob
        stem = f's{s}_{tag}'
        (d / f'{stem}.in').write_text(inp, encoding='utf-8', newline='')
        (d / f'{stem}.ans').write_text(ans + '\n', encoding='utf-8', newline='')
        cases.append({
            'id': f'{prob}-{stem}', 'problem': prob, 'subtask': s,
            'points': SUBTASKS[prob][s - 1], 'in': f'data/{prob}/{stem}.in',
            'ans': f'data/{prob}/{stem}.ans',
            'in_sha256': hashlib.sha256((d / f'{stem}.in').read_bytes()).hexdigest(),
            'ans_sha256': hashlib.sha256((d / f'{stem}.ans').read_bytes()).hexdigest(),
            'answer_source': src, 'kind': 'targeted_hack',
        })

    man = {
        'seed': SEED, 'problems': {p: {'subtask_points': SUBTASKS[p], 'time_limit_s': TIME_LIMIT[p]}
                                for p in SUBTASKS},
        'scoring': '捆绑评分：同一子任务所有测试点全过才给该子任务分值；总分 400',
        'answer_independence': '答案来自独立暴力 / 闭式解析 / pow 逆元递推，绝不由 std 生成',
        'cases': cases,
    }
    (HERE / 'data_manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n',
                                              encoding='utf-8')
    print('GEN_DATA_PASS', json.dumps({
        'cases': len(cases), 'files': len(cases) * 2,
        'answer_sources': {s: sum(1 for c in cases if c['answer_source'] == s)
                           for s in sorted({c['answer_source'] for c in cases})},
        'data_bytes': sum((HERE / c['in']).stat().st_size + (HERE / c['ans']).stat().st_size
                          for c in cases)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(build())
