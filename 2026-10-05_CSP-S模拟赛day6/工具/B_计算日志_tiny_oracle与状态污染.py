#!/usr/bin/env python3
"""Day6 B 计算日志：tiny exact oracle + submitted predicate reproducer."""

from fractions import Fraction
from itertools import combinations


def F(x, borders, speed):
    """从进度0到x，按各阶段最大速率工作的最短时间。"""
    ans = Fraction(0)
    for i, v in enumerate(speed):
        L, R = borders[i], borders[i + 1]
        if x <= L:
            break
        take = min(x, R) - L
        if take > 0:
            ans += Fraction(take, v)
        if x <= R:
            break
    return ans


def compatible(p, q, borders, speed):
    x1, t1 = p
    x2, t2 = q
    return Fraction(t2 - t1) >= F(x2, borders, speed) - F(x1, borders, speed)


def exact_answer(l, tend, borders, speed, logs):
    pts = [(0, 0)] + logs + [(l, tend)]
    if not compatible(pts[0], pts[-1], borders, speed):
        return -1

    m = len(logs)
    best_keep = 0
    for mask in range(1 << m):
        kept = [pts[0]]
        for i in range(m):
            if mask >> i & 1:
                kept.append(logs[i])
        kept.append(pts[-1])
        ok = True
        for i in range(len(kept)):
            for j in range(i + 1, len(kept)):
                if not compatible(kept[i], kept[j], borders, speed):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            best_keep = max(best_keep, mask.bit_count())
    return m - best_keep


def submitted_single(n, m, l, tend, borders, speed, logs):
    # 单 case、未读槽按全局零初始化。
    xs = [0] * (max(n, m) + 2)
    ts = [0] * (max(n, m) + 2)
    for i, (x, t) in enumerate(logs, 1):
        xs[i], ts[i] = x, t

    if Fraction(tend) < F(l, borders, speed):
        return -1

    fail = 0
    avg = Fraction(l, tend)
    for i in range(1, n + 1):  # 正式源码的 bug：n 而不是 m
        if Fraction(xs[i]) != avg * ts[i]:
            fail += 1
    return fail


# 1) 合法但不在平均线：submitted false negative
case1 = dict(
    n=1, m=1, l=10, tend=3,
    borders=[0, 10], speed=[10], logs=[(5, 2)]
)
assert exact_answer(case1["l"], case1["tend"], case1["borders"], case1["speed"], case1["logs"]) == 0
assert submitted_single(**case1) == 1

# 2) 在平均线，但局部阶段已经超速：submitted false positive
case2 = dict(
    n=2, m=1, l=120, tend=15,
    borders=[0, 60, 120], speed=[5, 120], logs=[(40, 5)]
)
assert exact_answer(case2["l"], case2["tend"], case2["borders"], case2["speed"], case2["logs"]) == 1
assert submitted_single(**case2) == 0

# 3) n/m + 全局数组残留：同一第二 case 因 prefix 不同而变答案。
# 这里直接复现数组残留语义。
x = [0] * 10
t = [0] * 10

# prefix case 写入两条日志
x[1], t[1] = 5, 1
x[2], t[2] = 15, 2

# second case 只覆盖第一条，但源码会 loop i=1..n=2
x[1], t[1] = 5, 1
avg = Fraction(20, 4)
contaminated = sum(Fraction(x[i]) != avg * t[i] for i in range(1, 3))
assert contaminated == 1

# fresh process 中 x[2]=t[2]=0
fresh = [(0, 0), (5, 1), (0, 0)]
fresh_fail = sum(Fraction(fresh[i][0]) != avg * fresh[i][1] for i in range(1, 3))
assert fresh_fail == 0

print("PASS")
print("legal off-average: true=0, submitted=1")
print("invalid on-average: true=1, submitted=0")
print("same second testcase: fresh=0, contaminated-prefix=1")
