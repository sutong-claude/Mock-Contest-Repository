#!/usr/bin/env python3
"""Day4 D 组合题：三代赛时代码判定的最小反例。

exact oracle:
枚举排列；每加一个区间，要求它与当前并集相交/接触，使前缀并集始终为闭区间。

复现三种历史模型：
1) submitted_factorial: 正式提交版实际走到的逻辑——恒输出 n!；
2) old_endpoint_dfs: 正式源码中被注释掉的第一代 DFS predicate；
3) postvm_common_intersection: 赛后 VM 后续版的第二代 DFS predicate。
"""

from itertools import product, permutations
from math import factorial


def good_perm(intervals, perm):
    L = R = None
    for idx in perm:
        l, r = intervals[idx]
        if L is None:
            L, R = l, r
            continue
        # 两个闭区间的并仍为闭区间 iff 新区间和当前并集有交。
        if r < L or l > R:
            return False
        L = min(L, l)
        R = max(R, r)
    return True


def true_count(intervals):
    return sum(good_perm(intervals, p)
               for p in permutations(range(len(intervals))))


def submitted_factorial(intervals):
    return factorial(len(intervals))


def old_endpoint_good(intervals, perm):
    n = len(intervals)
    endpoints = set()
    mi, ma = n, 1
    for idx in perm:
        l, r = intervals[idx]
        endpoints.add(l)
        endpoints.add(r)
        mi = min(mi, l, r)
        ma = max(ma, l, r)
        if any(x not in endpoints for x in range(mi, ma + 1)):
            return False
    return True


def old_endpoint_count(intervals):
    return sum(old_endpoint_good(intervals, p)
               for p in permutations(range(len(intervals))))


def postvm_common_intersection(intervals):
    L = max(l for l, r in intervals)
    R = min(r for l, r in intervals)
    return factorial(len(intervals)) if L <= R else 0


def all_intervals(n):
    return [(l, r) for l in range(1, n + 1)
            for r in range(l, n + 1)]


def search_first(max_n=4):
    names = (
        ("submitted_factorial", submitted_factorial),
        ("old_endpoint_dfs", old_endpoint_count),
        ("postvm_common_intersection", postvm_common_intersection),
    )
    first = {}
    for n in range(1, max_n + 1):
        for intervals in product(all_intervals(n), repeat=n):
            truth = true_count(intervals)
            for name, fn in names:
                if name not in first:
                    got = fn(intervals)
                    if got != truth:
                        first[name] = (n, intervals, truth, got)
        if len(first) == len(names):
            break
    return first


if __name__ == "__main__":
    first = search_first()
    for k, v in first.items():
        print(k, v)

    # 三个可读性更好的固定回归例。
    cases = [
        ("submitted minimal", ((1, 1), (2, 2))),
        ("old endpoint-hole", ((1, 3), (1, 3), (1, 3))),
        ("postvm chain", ((1, 1), (1, 2), (2, 2))),
    ]
    for name, intervals in cases:
        print(
            name,
            "intervals=", intervals,
            "true=", true_count(intervals),
            "submitted=", submitted_factorial(intervals),
            "old=", old_endpoint_count(intervals),
            "postvm=", postvm_common_intersection(intervals),
        )

    assert true_count(((1, 1), (2, 2))) == 0
    assert submitted_factorial(((1, 1), (2, 2))) == 2

    assert true_count(((1, 3), (1, 3), (1, 3))) == 6
    assert old_endpoint_count(((1, 3), (1, 3), (1, 3))) == 0

    assert true_count(((1, 1), (1, 2), (2, 2))) == 4
    assert postvm_common_intersection(((1, 1), (1, 2), (2, 2))) == 0

    print("PASS")
