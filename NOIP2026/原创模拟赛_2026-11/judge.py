#!/usr/bin/env python3
"""原创模拟赛 2026-11｜正式评测器（捆绑评分 + 数据完整性 + 反假绿自检）。

用法：
  python3 judge.py --grade solution.cpp --problem T1   # 评一题，输出 JSON 报告
  python3 judge.py --self-test                          # 标程应 400 分；故意写错的提交必须掉分
  python3 judge.py --verify-data                        # 只校验 48 组数据 SHA

设计要点（承接 Day4 B 污染链）：
  1. 每次评测前校验 data_manifest.json 里 96 个 .in/.ans 的 SHA256，数据被篡改直接拒绝；
  2. 比较**完整 stdout**（strip 后逐字节），不只读第一行，避免「只验一半」假绿；
  3. 子任务捆绑：组内任一 WA/TLE/RE 则该组 0 分（对应 错因总表 #17）；
  4. --self-test 用 std 与 7 个「一行改动」的错误提交双向检验评测器本身，
     即「先证明评测器，再评测选手」。
"""
import argparse, hashlib, json, pathlib, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent
MAN = json.loads((HERE / 'data_manifest.json').read_text(encoding='utf-8'))

# 故意写错的提交：只改一行，映射到历史病因编号
MUTANTS = [
    ('T1_strict_inequality', 'T1', 'T1_window',
     [('upper_bound(v.begin(),v.end(),x)', 'lower_bound(v.begin(),v.end(),x)')], '#1 非严格不等号'),
    ('T1_ignore_K', 'T1', 'T1_window',
     [('if(drop>=0) bit.add(le(S[(int)drop]),-1);', ';')], '#1 漏看长度上限'),
    ('T2_no_impossible', 'T2', 'T2_lamps',
     [('if(i+L>n){cout<<-1<<\'\\n\';return 0;}', 'if(false){cout<<-1<<\'\\n\';return 0;}')],
     '#15 语义契约（可解性）未证明'),
    ('T2_extra_output', 'T2', 'T2_lamps',
     [("cout<<ans<<'\\n';return 0;}", "cout<<ans<<'\\n'<<\"debug\"<<'\\n';return 0;}")],
     '#10 验证链只比第一行（评测器反假绿）'),
    ('T3_missing_inheritance', 'T3', 'T3_segments',
     [('dp[i]=dp[i-1];', 'dp[i]=0;')], '#10 漏继承项'),
    ('T3_strict_dominance', 'T3', 'T3_segments',
     [('upper_bound(xs[k].begin(),xs[k].end(),valA)', 'lower_bound(xs[k].begin(),xs[k].end(),valA)')],
     '#1 非严格支配'),
    ('T4_wrong_combination', 'T4', 'T4_pairs',
     [('comb=comb*(n-k+1)%P*inv[k]%P;', 'comb=comb*(N-k+1)%P*inv[k]%P;')], '#15 容斥对象选错'),
]


def verify_data():
    bad = []
    for c in MAN['cases']:
        for key, hashkey in [('in', 'in_sha256'), ('ans', 'ans_sha256')]:
            f = HERE / c[key]
            if not f.is_file():
                bad.append(c[key]); continue
            if hashlib.sha256(f.read_bytes()).hexdigest() != c[hashkey]:
                bad.append(c[key])
    return bad


def compile_cpp(src_text, exe):
    with tempfile.NamedTemporaryFile('w', suffix='.cpp', delete=False, encoding='utf-8') as tf:
        tf.write(src_text); cpp = tf.name
    r = subprocess.run(['g++', '-std=c++17', '-O2', cpp, '-o', str(exe)],
                       capture_output=True, text=True, timeout=120)
    pathlib.Path(cpp).unlink(missing_ok=True)
    if r.returncode != 0:
        raise RuntimeError('COMPILE_ERROR: ' + r.stderr[-400:])


def run_case(exe, c):
    inp = (HERE / c['in']).read_bytes()
    want = (HERE / c['ans']).read_text(encoding='utf-8').strip()
    tl = MAN['problems'][c['problem']]['time_limit_s']
    t0 = time.perf_counter()
    try:
        r = subprocess.run([str(exe)], input=inp, capture_output=True, timeout=tl)
        dt = time.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return {'id': c['id'], 'verdict': 'TLE', 'detail': f'>{tl}s'}
    if r.returncode != 0:
        return {'id': c['id'], 'verdict': 'RE', 'detail': f'rc={r.returncode}'}
    got = r.stdout.decode('utf-8', errors='replace').strip()
    if got != want:
        return {'id': c['id'], 'verdict': 'WA',
                'detail': f'got={got[:40]!r} want={want[:40]!r}'}
    return {'id': c['id'], 'verdict': 'AC', 'detail': f'{dt:.3f}s'}


def grade(src_text, problem):
    bad = verify_data()
    if bad:
        raise RuntimeError('DATA_INTEGRITY_FAIL ' + str(bad[:3]))
    with tempfile.TemporaryDirectory() as td:
        exe = pathlib.Path(td) / 'sol'
        compile_cpp(src_text, exe)
        rows = [c for c in MAN['cases'] if c['problem'] == problem]
        results = [run_case(exe, c) for c in rows]
    by_sub = {}
    for c, r in zip(rows, results):
        by_sub.setdefault(c['subtask'], []).append((c, r))
    detail, score = [], 0
    for s, items in sorted(by_sub.items()):
        pts = MAN['problems'][problem]['subtask_points'][s - 1]
        ok = all(r['verdict'] == 'AC' for _, r in items)
        if ok:
            score += pts
        detail.append({'subtask': s, 'points': pts, 'awarded': pts if ok else 0,
                       'tests': [{'id': c['id'], 'verdict': r['verdict']} for c, r in items]})
    return {'problem': problem, 'score': score, 'max': 100,
            'verdicts': {r['verdict']: sum(1 for x in results if x['verdict'] == r['verdict'])
                         for r in results if r['verdict']}, 'subtasks': detail}


def std_text(tag):
    return (HERE / 'std' / f'{tag}.cpp').read_text(encoding='utf-8')


def mutant_text(m):
    _, _, tag, subs, _ = m
    t = std_text(tag)
    for old, new in subs:
        assert old in t, f'mutant pattern not found: {old[:60]}'
        t = t.replace(old, new)
    return t


def self_test():
    bad = verify_data()
    assert not bad, f'DATA_INTEGRITY_FAIL {bad[:3]}'
    report = {'data_cases': len(MAN['cases']), 'std': {}, 'mutants': {}}
    total = 0
    for prob, tag in [('T1', 'T1_window'), ('T2', 'T2_lamps'),
                      ('T3', 'T3_segments'), ('T4', 'T4_pairs')]:
        r = grade(std_text(tag), prob)
        report['std'][prob] = r['score']
        total += r['score']
        assert r['score'] == 100, f'std {prob} got {r["score"]}'
    report['std_total'] = total
    assert total == 400
    for name, prob, tag, subs, cause in MUTANTS:
        r = grade(mutant_text((name, prob, tag, subs, cause)), prob)
        lost = 100 - r['score']
        report['mutants'][name] = {'score': r['score'], 'lost': lost, 'cause': cause,
                                   'failing_subtasks': [d['subtask'] for d in r['subtasks']
                                                        if d['awarded'] == 0]}
        assert lost > 0, f'mutant {name} was NOT detected (false green!)'
    # 评测器反假绿：多输出一行必须被判 WA
    assert report['mutants']['T2_extra_output']['lost'] > 0
    print('JUDGE_SELFTEST_PASS ' + json.dumps(report, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--grade')
    ap.add_argument('--problem', choices=['T1', 'T2', 'T3', 'T4'])
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--verify-data', action='store_true')
    a = ap.parse_args()
    if a.verify_data:
        bad = verify_data()
        print('DATA_SHA_' + ('PASS' if not bad else 'FAIL') + f' cases={len(MAN["cases"])} bad={len(bad)}')
        return 0 if not bad else 1
    if a.self_test:
        return self_test()
    if a.grade:
        assert a.problem, '需要 --problem'
        print(json.dumps(grade(pathlib.Path(a.grade).read_text(encoding='utf-8'), a.problem),
                         ensure_ascii=False, indent=2))
        return 0
    ap.print_help(); return 1


if __name__ == '__main__':
    sys.exit(main())
