#!/usr/bin/env python3
"""远古/历史数值的精确复算层（不改写任何历史快照）。

设计原则（承接 总览/赛事账本.json 的 maintainer_note）：
  历史文件（全题总表_2026-10-11.md、赛场星图_2026-10-12.json、
  2026-10-02 Day4 污染链文档、错因总表.csv 等）都是各自日期的快照，
  不得覆盖。本脚本只在【新目录】生成一份机器可读的精确复算结果，
  把历史里的近似小数/百分比升级成 exact Fraction，并给出可复算路径。

运行：python3 交接/2026-11-03_远古数据复算/复算.py
输出：同目录 历史数值复算.json
"""
import json, pathlib, statistics
from fractions import Fraction as F

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent / '历史数值复算.json'


def frac(f):
    return {'exact': f'{f.numerator}/{f.denominator}', 'float': float(f)}


def main():
    r = {'as_of': '2026-11-03', 'source_tier': '[E] 本地可复算 / [P] 仓库源码事实',
         'policy': '不改写历史快照；只在新目录给出精确值与复算路径。近似值仍保留在原文。',
         'sections': {}}

    # ---- 1. Day4 污染链：generator 合法率，近似 0.0282690368 -> 精确分数 ----
    p = sum(F(n, 13) ** n for n in range(1, 11)) / 10
    assert p == F(38971267793, 1378584918490)
    r['sections']['day4_generator_legality'] = {
        'old_text': '2026-10-02_CSP-S模拟赛day4/原始材料/T2_对拍污染链_非法generator_错oracle.md:45 "≈ 0.0282690368"',
        'formula': '(1/10) * sum_{n=1..10} (n/13)^n',
        'legal': frac(p), 'illegal': frac(1 - p),
        'old_approx_legal': 0.0282690368, 'old_approx_illegal': 0.9717,
        'delta_abs': abs(float(p) - 0.0282690368),
    }

    # ---- 2. Day4 全空间穷举表：逐行求和校验 + 4 个百分比精确化 ----
    tbl = [  # n, 合法, 错oracle!=truth, candidate!=truth, false_green, false_red
        (1, 1, 1, 1, 1, 0), (2, 4, 4, 4, 4, 0), (3, 27, 24, 24, 18, 0),
        (4, 256, 214, 210, 162, 12), (5, 3125, 2341, 2238, 1601, 380),
        (6, 46656, 31834, 32312, 20289, 5795)]
    sums = [sum(row[i] for row in tbl) for i in range(1, 6)]
    declared = [50069, 34418, 34789, 22075, 6187]
    assert sums[:5] == declared, (sums, declared)
    r['sections']['day4_exhaustive_table'] = {
        'old_text': '同文件:168-176 的合计行与 4 个百分比',
        'row_sums_verified': sums[:5], 'declared_totals': declared, 'assert_equal': True,
        'flawed_oracle_error_rate': frac(F(sums[1], sums[0])),
        'candidate_error_rate': frac(F(sums[2], sums[0])),
        'false_green': frac(F(sums[3], sums[0])),
        'false_red': frac(F(sums[4], sums[0])),
        'old_percentages': [68.74, 69.48, 44.09, 12.36],
    }

    # ---- 3. 赛事总账：从 contests 重新求和，核对 derived_sums ----
    ledger = json.loads((ROOT / '总览/赛事账本.json').read_text(encoding='utf-8'))
    main = [c for c in ledger['contests'] if c.get('in_main_line') and c.get('score_tier') == 'OJ']
    tot, mx = sum(c['score'] for c in main), sum(c['max'] for c in main)
    assert (tot, mx) == (729, 3600) == (ledger['derived_sums']['codesource_day1_day9_oj'],
                                       ledger['derived_sums']['codesource_day1_day9_max'])
    per = {}
    for p_ in 'ABCD':
        v = [c['per_problem'].get(p_) for c in main]
        v = [x for x in v if isinstance(x, int)]
        per[p_] = {'sum': sum(v), 'mean': float(F(sum(v), len(v))),
                   'zero_count': sum(1 for x in v if x == 0), 'n': len(v),
                   'full_100_count': sum(1 for x in v if x == 100)}
    scores = [c['score'] for c in main]
    day10 = next(c for c in ledger['contests'] if c['id'] == 'codesource-day10')
    r['sections']['contest_ledger'] = {
        'old_text': '总览/赛事账本.json derived_sums；错因档案.md 的各场分数',
        'contest_count': len(ledger['contests']), 'main_line_oj_count': len(main),
        'total': tot, 'max': mx, 'ratio': frac(F(tot, mx)),
        'per_problem': per,
        'A_plus_B_share': frac(F(per['A']['sum'] + per['B']['sum'], tot)),
        'C_plus_D_share': frac(F(per['C']['sum'] + per['D']['sum'], tot)),
        'score_list': scores, 'median': statistics.median(scores),
        'mean': float(F(tot, len(scores))),
        'population_stdev': round(statistics.pstdev(scores), 4),
        'coefficient_of_variation': round(statistics.pstdev(scores) / (tot / len(scores)), 4),
        'low_le_15_count': sum(1 for s in scores if s <= 15),
        'high_ge_130_count': sum(1 for s in scores if s >= 130),
        'day10_conditional': {'score': day10['score'], 'tier': day10['score_tier'],
                              'sum_if_confirmed': tot + day10['score'],
                              'note': '仅在官方 record 复核后才可写入主线折线，当前 [G]。'},
        'derived_sums_match': True,
    }

    # ---- 4. 病因聚类：只用有计数的历史条目（#21~#28 计数为 0，属 [G] 新增） ----
    import csv
    with (ROOT / 'NOIP2026/错因总表.csv').open(encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    cnt = {x['id']: int(x['仓库口径次数'] or 0) for x in rows}
    clusters = {
        '决策/流程': ['3', '4', '5', '6', '12', '13'],
        '知识/建模': ['1', '2', '7', '14', '15', '16'],
        '验证链': ['10', '17', '18', '19'],
        '环境/工具': ['8'],
        '版本/证据分层/其他': ['9', '11', '20'],
    }
    total = sum(cnt.values())
    assert total == 40
    out = {}
    for k, ids in clusters.items():
        s = sum(cnt[i] for i in ids)
        out[k] = {'ids': ids, 'count': s, 'share': frac(F(s, total))}
    assert sum(v['count'] for v in out.values()) == total
    r['sections']['error_clusters'] = {
        'old_text': 'NOIP2026/错因总表.csv 28 条病因 / 40 次归档复发',
        'total_recurrences': total, 'clusters': out,
        'stop_loss_and_time': frac(F(cnt['3'] + cnt['5'], total)),
        'top5_share': frac(F(sum(sorted(cnt.values(), reverse=True)[:5]), total)),
        'new_pdf_ids_with_zero_count': [i for i in cnt if int(i) >= 21 and cnt[i] == 0],
        'warning': '#21~#28 是 2026-11-03 转写 PDF 新增 [G] 条目，计数为 0，不可并入 40 次分母。',
    }

    # ---- 5. 目标分解：180~220 的逐项倍数 ----
    a, b, cd = F(per['A']['sum'], len(scores)), F(per['B']['sum'], len(scores)), \
               F(per['C']['sum'] + per['D']['sum'], len(scores))
    r['sections']['goal_decomposition'] = {
        'old_text': 'NOIP2026/四阶段路线图.md 目标 T1 100 + T2 60~100 + T3/T4 30~40 = 180~220',
        'historical_mean': {'T1': float(a), 'T2': float(b), 'T3T4': float(cd), 'total': float(F(tot, len(scores)))},
        'required_multiplier': {'T1': float(F(100, 1) / a),
                                'T2_low': float(F(60, 1) / b), 'T2_high': float(F(100, 1) / b),
                                'T3T4_low': float(F(30, 1) / cd), 'T3T4_high': float(F(40, 1) / cd),
                                'total_low': float(F(180, 1) / F(tot, len(scores))),
                                'total_high': float(F(220, 1) / F(tot, len(scores)))},
        't2_ge60_historical_rate': frac(F(sum(1 for c in main if (c['per_problem'].get('B') or 0) >= 60), len(scores))),
        't1_full_historical_rate': frac(F(sum(1 for c in main if c['per_problem'].get('A') == 100), len(scores))),
        'hypothetical_only_decision_fix': {
            'T1_all_100': f'{900 + (tot - per["A"]["sum"])}/{mx} = {float(F(900 + tot - per["A"]["sum"], len(scores)))}/400',
            'T1_100_T2_60': f'{900 + 540 + (tot - per["A"]["sum"] - per["B"]["sum"])}/{mx} = {float(F(900 + 540 + tot - per["A"]["sum"] - per["B"]["sum"], len(scores)))}/400',
        },
    }

    OUT.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('ANCIENT_DATA_RECOMPUTE_PASS', json.dumps({
        'day4_legal': frac(p)['exact'], 'ledger': f'{tot}/{mx}',
        'A_plus_B_share': frac(F(per['A']['sum'] + per['B']['sum'], tot))['exact'],
        'decision_share': out['决策/流程']['share']['exact'],
        't2_low_multiplier': r['sections']['goal_decomposition']['required_multiplier']['T2_low']},
        ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
