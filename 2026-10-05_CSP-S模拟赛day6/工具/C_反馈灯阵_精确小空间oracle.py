#!/usr/bin/env python3
"""Day6 C 反馈灯阵：精确 tiny oracle。

逐实例枚举所有灯态，得到真实 S；
同时复现正式提交的错误 predicate：
    |{j: k-1 in I_j}| == k

用来证明：
1) n=2,d=(0,0) 时，真实期望=1，提交逻辑=0；
2) I1=[0,0],I2=[1,1] 时，提交逻辑出现 false positive；
3) d=(1,1) 时，错误 predicate 虽逐实例出错，但期望恰好抵消到 8/9。
"""

from itertools import product
from fractions import Fraction


def interval_choices(d):
    return [(l, r) for l in range(d + 1) for r in range(l, d + 1)]


def true_S(intervals):
    n = len(intervals)
    S = set()
    for mask in range(1 << n):
        k = mask.bit_count()
        ok = True
        for i, (l, r) in enumerate(intervals):
            lit = (mask >> i) & 1
            other_lit = k - lit
            should_lit = l <= other_lit <= r
            if should_lit != bool(lit):
                ok = False
                break
        if ok:
            S.add(k)
    return S


def submitted_S(intervals):
    n = len(intervals)
    S = set()
    for k in range(1, n + 1):
        cnt = sum(l <= k - 1 <= r for l, r in intervals)
        if cnt == k:
            S.add(k)
    return S


def expectation(d):
    pools = [interval_choices(x) for x in d]
    total = 0
    tsum = 0
    csum = 0
    first_instance_mismatch = None

    for intervals in product(*pools):
        total += 1
        t = true_S(intervals)
        c = submitted_S(intervals)
        tsum += len(t)
        csum += len(c)
        if first_instance_mismatch is None and t != c:
            first_instance_mismatch = (intervals, t, c)

    return Fraction(tsum, total), Fraction(csum, total), first_instance_mismatch


# 最小期望级反例
t00, c00, local00 = expectation((0, 0))
print("d=(0,0): true expectation =", t00,
      "submitted expectation =", c00,
      "first local mismatch =", local00)
assert t00 == 1
assert c00 == 0

# 最小局部 false positive
fp = ((0, 0), (1, 1))
print("local false positive:", fp,
      "true S =", true_S(fp),
      "submitted S =", submitted_S(fp))
assert true_S(fp) == set()
assert submitted_S(fp) == {1}

# 错误在期望层恰好抵消
t11, c11, local11 = expectation((1, 1))
print("d=(1,1): true expectation =", t11,
      "submitted expectation =", c11,
      "yet local mismatch =", local11)
assert t11 == c11 == Fraction(8, 9)
assert local11 is not None

print("PASS")
