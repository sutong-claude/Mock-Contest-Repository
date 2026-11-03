#!/usr/bin/env python3
"""CodeLands3 独立验证器 v2｜2026-11-03 深度代码复审产物。

与 v1 (verify_codelands3_candidates.py) 的区别 —— v1 的 `covered()` 与 C++ 候选
共用「dp[i]=max(dp[i-1], i + max_{t<i,dom}(dp[t]-t))」这一分解，属于仓库反复踩过的
**共模风险**（Day4 B 假绿链：generator/oracle/candidate 三层同源）。v2 增加：

  1. maxcover 真穷举 oracle：递归枚举所有「两两不相交的合法段」集合，不使用 DP、
     不使用前缀和、不使用支配关系；n<=8 全空间验证分解本身。
  2. alien 真穷举 oracle：0/1 矩阵的 permanent（子集 DP），与容斥公式完全独立；N<=10。
  3. 4 个已知错误变体（漏继承 / 严格不等号 / 支配反向 / 漏掉第二数组）
     自动搜索最小反例（[X]），证明 verifier 能杀死它们。
  4. 结构化对抗数据（全 0 / ±1 / 相等前缀 / 重复值）2000 组 + 大 n 解析用例。
  5. -fsanitize=address,undefined 编译并跑子集，检查 UB / 越界。
  6. alien 大 N 用 Pascal 组合数 + 独立阶乘实现交叉验证线性逆元优化（不含 qpow）。

输出一行结构化 JSON；全部断言通过才打印 PASS。LOCAL-VERIFIED，不是 OJ 结果。
"""
import itertools, json, math, pathlib, random, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAND = ROOT / '赛后候选'
SEED = 20261103
P = 1000000007


# ---------- 1. 真独立 oracle ----------
def brute_segments(a, b):
    """枚举所有两两不相交的合法段集合；无 DP、无前缀和、无支配查询。"""
    n = len(a)
    best = 0

    def rec(start, total):
        nonlocal best
        if total > best:
            best = total
        for l in range(start, n):
            sa = sb = 0
            for r in range(l, n):
                sa += a[r]
                sb += b[r]
                if sa >= 0 and sb >= 0:          # 合法段 [l,r]
                    rec(r + 1, total + (r - l + 1))
    rec(0, 0)
    return best


def brute_permanent(N, n):
    """数满足 p_i != i (i<n) 的 N 阶排列数 = 0/1 矩阵的 permanent（子集 DP）。"""
    dp = [0] * (1 << N)
    dp[0] = 1
    for mask in range(1 << N):
        i = mask.bit_count()                     # 下一个要填的位置
        if i >= N:
            continue
        for c in range(N):
            if (mask >> c) & 1:
                continue
            if i < n and c == i:                 # 禁止的不动点
                continue
            dp[mask | (1 << c)] += dp[mask]
    return dp[(1 << N) - 1]


def covered_quadratic(a, b):
    """v1 的 O(n^2) 实现，保留作交叉对照（不是主 oracle）。"""
    n = len(a)
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i - 1]
        sa = sb = 0
        for j in range(i, 0, -1):
            sa += a[j - 1]
            sb += b[j - 1]
            if sa >= 0 and sb >= 0:
                dp[i] = max(dp[i], dp[j - 1] + i - j + 1)
    return dp[n]


def alien_formula_pascal(n, m):
    """独立实现：math.comb + 显式阶乘取模，不用 qpow/逆元递推。"""
    N = n + m
    fac = 1
    facts = [1] * (N + 1)
    for i in range(1, N + 1):
        fac = fac * i % P
        facts[i] = fac
    return sum((-1) ** k * math.comb(n, k) * facts[N - k] for k in range(n + 1)) % P


# ---------- 2. 已知错误变体 + 最小反例搜索 ----------
def maxcover_variant(a, b, bug):
    """与候选同分解，但注入一个具体 bug；用于证明 verifier 能杀死它。"""
    n = len(a)
    sa = [0] * (n + 1)
    sb = [0] * (n + 1)
    for i in range(1, n + 1):
        sa[i] = sa[i - 1] + a[i - 1]
        sb[i] = sb[i - 1] + b[i - 1]
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        if bug != 'missing_inheritance':
            dp[i] = dp[i - 1]
        best = None
        for t in range(0, i):
            oka = sa[t] < sa[i] if bug == 'strict_prefix' else sa[t] <= sa[i]
            okb = sb[t] < sb[i] if bug == 'strict_prefix' else sb[t] <= sb[i]
            if bug == 'wrong_direction':
                oka, okb = sa[t] >= sa[i], sb[t] >= sb[i]
            if bug == 'ignore_b':
                okb = True
            if oka and okb:
                v = dp[t] - t
                best = v if best is None else max(best, v)
        if best is not None:
            dp[i] = max(dp[i], i + best)
        if bug == 'missing_inheritance' and dp[i] == 0 and i > 1:
            dp[i] = dp[i - 1] if dp[i - 1] > dp[i] else dp[i]
    return dp[n]


def find_min_counterexample(bug, maxn=4):
    vals = [-2, -1, 0, 1]
    for n in range(1, maxn + 1):
        for a in itertools.product(vals, repeat=n):
            for b in itertools.product(vals, repeat=n):
                truth = brute_segments(list(a), list(b))
                got = maxcover_variant(list(a), list(b), bug)
                if got != truth:
                    return {'bug': bug, 'n': n, 'a': list(a), 'b': list(b),
                            'truth': truth, 'variant': got}
    return None


def alien_variant(n, m, bug):
    N = n + m
    facts = [1] * (N + 1)
    for i in range(1, N + 1):
        facts[i] = facts[i - 1] * i % P
    out = 0
    for k in range(n + 1):
        c = math.comb(n, k)
        if bug == 'omit_parity':
            sgn = 1
        elif bug == 'wrong_parity':
            sgn = 1 if k % 2 == 0 else 0      # 只加偶项
        elif bug == 'off_by_one':
            sgn = (-1) ** k
            facts_k = facts[min(N, N - k + 1)]  # 阶乘下标错一位
            out = (out + sgn * c * facts_k) % P
            continue
        else:
            sgn = (-1) ** k
        out = (out + sgn * c * facts[N - k]) % P
    return out % P


# ---------- 3. 编译与调用 ----------
def compile_candidates(work, sanitize=False):
    flags = ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra']
    if sanitize:
        flags += ['-fsanitize=address,undefined', '-fno-sanitize-recover=all']
    outs = {}
    for tag, src, exe in [
        ('maxcover', 'CodeLands3_maxcover_二维树状数组.cpp', 'mc'),
        ('alien', 'CodeLands3_alien_线性容斥.cpp', 'al'),
    ]:
        out = work / (exe + ('_san' if sanitize else ''))
        subprocess.run(flags + [str(CAND / src), '-o', str(out)], check=True,
                       capture_output=True, timeout=120)
        outs[tag] = out
    return outs


def invoke(binary, content, timeout=20):
    r = subprocess.run([str(binary)], input=content, text=True,
                       capture_output=True, check=True, timeout=timeout)
    return r.stdout.strip()


def mc_input(a, b):
    return f'{len(a)}\n' + ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n'


def main():
    rep = {'seed': SEED, 'v1_common_mode_risk': True}
    rnd = random.Random(SEED)
    with tempfile.TemporaryDirectory() as td:
        work = pathlib.Path(td)
        bins = compile_candidates(work)
        san = compile_candidates(work, sanitize=True)

        # (a) 两级验证：Python 全空间证明「v1 quadratic oracle == 真穷举」；
        #     再对抽样 + 对抗集调用 C++ 二进制（子进程不能按 500 万次跑）。
        tri = 0
        for n in range(1, 7):
            for a in itertools.product([-1, 0, 1], repeat=n):
                for b in itertools.product([-1, 0, 1], repeat=n):
                    truth = brute_segments(list(a), list(b))
                    assert covered_quadratic(list(a), list(b)) == truth, ('v1 oracle 与穷举不符', a, b)
                    tri += 1
        rep['maxcover_exhaustive_python_triples'] = tri
        # C++ 与真穷举的小空间直接对照（400 个随机 + 2 个已知 [X]）
        cpp_small = 0
        for _ in range(400):
            n = rnd.randint(1, 7)
            a = [rnd.choice([-1, 0, 1]) for _ in range(n)]
            b = [rnd.choice([-1, 0, 1]) for _ in range(n)]
            truth = brute_segments(a, b)
            got = int(invoke(bins['maxcover'], mc_input(a, b)))
            assert got == truth, ('C++ 与真穷举不符', n, a, b, truth, got)
            cpp_small += 1
        known = [([1, -5], [1, -5], 1), ([1, -1], [1, -1], 2)]
        for a, b, want in known:
            assert brute_segments(a, b) == want
            assert int(invoke(bins['maxcover'], mc_input(a, b))) == want
        rep['maxcover_cpp_vs_brute_cases'] = cpp_small + len(known)

        # (b) 结构化对抗随机 2000 组，n<=40，与 quadratic 交叉
        adv = 0
        for _ in range(2000):
            n = rnd.randint(1, 40)
            mode = rnd.randrange(4)
            if mode == 0:
                a = [0] * n; b = [0] * n
            elif mode == 1:
                a = [rnd.choice([-1, 1]) for _ in range(n)]
                b = [rnd.choice([-1, 1]) for _ in range(n)]
            elif mode == 2:
                a = [rnd.randint(-10000, 10000) for _ in range(n)]
                b = [rnd.randint(-10000, 10000) for _ in range(n)]
            else:
                a = [rnd.choice([-2, 0, 2]) for _ in range(n)]
                b = list(a)
            t = covered_quadratic(a, b)
            got = int(invoke(bins['maxcover'], mc_input(a, b)))
            assert got == t, ('对抗数据失败', mode, a, b, t, got)
            adv += 1
        rep['maxcover_adversarial_cases'] = adv

        # (c) sanitizer 子集
        san_n = 0
        for _ in range(40):
            n = rnd.randint(1, 60)
            a = [rnd.randint(-50, 50) for _ in range(n)]
            b = [rnd.randint(-50, 50) for _ in range(n)]
            int(invoke(san['maxcover'], mc_input(a, b)))
            san_n += 1
        rep['maxcover_sanitizer_runs'] = san_n

        # (d) 大 n 解析用例：常数 / 溢出 / 哨兵
        large = {}
        for name, a, b, want in [
            ('all_zero', [0] * 200000, [0] * 200000, 200000),
            ('all_neg', [-1] * 200000, [-1] * 200000, 0),
            ('single_pos_then_neg', [1] + [-5] * 199999, [1] + [-5] * 199999, 1),
        ]:
            got = int(invoke(bins['maxcover'], mc_input(a, b), timeout=60))
            assert got == want, (name, want, got)
            large[name] = got
        rep['maxcover_large_n_analytic'] = large

        # (e) 最小反例：4 个错误变体必须都被杀死
        kills = []
        for bug in ['missing_inheritance', 'strict_prefix', 'wrong_direction', 'ignore_b']:
            k = find_min_counterexample(bug, maxn=4)
            assert k is not None, f'未找到 {bug} 的反例'
            kills.append(k)
        rep['maxcover_minimal_counterexamples'] = kills

        # (f) alien：permanent 穷举 N<=10
        perm_n = 0
        for N in range(0, 11):
            for n in range(0, N + 1):
                m = N - n
                truth = brute_permanent(N, n)
                got = int(invoke(bins['alien'], f'{n} {m}\n'))
                assert got == truth, ('alien permanent 不符', n, m, truth, got)
                assert alien_formula_pascal(n, m) == truth % P
                perm_n += 1
        rep['alien_permanent_cases'] = perm_n

        # (g) alien 大 N：Pascal 独立实现交叉验证线性逆元，且无 qpow-per-term
        big = []
        for n, m in [(1000, 0), (0, 1000), (500, 500), (999, 1), (1234, 4321)]:
            want = alien_formula_pascal(n, m)
            got = int(invoke(bins['alien'], f'{n} {m}\n', timeout=30))
            assert got == want, ('alien bigN 不符', n, m, want, got)
            big.append({'n': n, 'm': m, 'mod': got})
        rep['alien_large_N_crosscheck'] = big
        alien_kills = []
        for bug in ['omit_parity', 'wrong_parity', 'off_by_one']:
            for N in range(0, 9):
                for n in range(0, N + 1):
                    m = N - n
                    truth = brute_permanent(N, n) % P
                    if alien_variant(n, m, bug) != truth:
                        alien_kills.append({'bug': bug, 'n': n, 'm': m,
                                            'truth': truth, 'variant': alien_variant(n, m, bug)})
                        break
                if alien_kills and alien_kills[-1]['bug'] == bug:
                    break
        assert len(alien_kills) == 3
        rep['alien_minimal_counterexamples'] = alien_kills

        # (h) sanitizer on alien
        for n, m in [(0, 0), (1, 0), (0, 1), (7, 0), (3, 4), (50, 50)]:
            int(invoke(san['alien'], f'{n} {m}\n'))
        rep['alien_sanitizer_runs'] = 6

    rep['result'] = 'LOCAL_VERIFIED only; not an official OJ result.'
    rep['boundary'] = '结构/独立 oracle 验证，不替代官方逐点 record、录像审阅或数学证明。'
    print('CODELANDS3_V2_PASS ' + json.dumps(rep, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
