#!/usr/bin/env python3
"""Day5 T1: verify the meaning of 'first greater endpoint to the right'.

Scope: checks ONLY the next-greater-position subproblem, not the whole
triangle-area DP, OJ subtask scoring, or the historical C++ program.

Uses two independent algorithms:
  O(n^2) position-scan oracle vs. O(n) monotonic stack.
Also shows why a sorted-by-endpoint selection is a wrong substitute.
"""
from itertools import product


def first_greater_brute(d):
    r = [i + 1 + value for i, value in enumerate(d)]
    return [next((j for j in range(i + 1, len(d)) if r[j] > r[i]), None)
            for i in range(len(d))]


def first_greater_stack(d):
    r = [i + 1 + value for i, value in enumerate(d)]
    ans = [None] * len(d)
    stack = []
    for i in range(len(d) - 1, -1, -1):
        while stack and r[stack[-1]] <= r[i]:
            stack.pop()
        ans[i] = stack[-1] if stack else None
        stack.append(i)
    return ans


def WRONG_minimum_endpoint(d):
    """Intentional bug: smallest r_j, not first position j; for contrast."""
    r = [i + 1 + value for i, value in enumerate(d)]
    ans = []
    for i in range(len(d)):
        possible = [j for j in range(i + 1, len(d)) if r[j] > r[i]]
        ans.append(min(possible, key=lambda j: (r[j], j)) if possible else None)
    return ans


def display_positions(ans):
    return [None if j is None else j + 1 for j in ans]


def verify():
    checked = 0
    flawed_cases = 0
    for n in range(1, 8):
        for d in product(range(1, 5), repeat=n):
            expected = first_greater_brute(d)
            got = first_greater_stack(d)
            assert expected == got, (d, expected, got)
            if WRONG_minimum_endpoint(d) != expected:
                flawed_cases += 1
            checked += 1

    # Archived case: r = [3,5,4]. Position 2 is the first greater to
    # the right of position 1; endpoint-minimum incorrectly picks pos 3.
    d = (2, 3, 1)
    assert display_positions(first_greater_brute(d)) == [2, None, None]
    assert display_positions(WRONG_minimum_endpoint(d)) == [3, None, None]

    # With r = [3,4,5], processing from right to left appends [5,4],
    # which violates std::upper_bound's partition/sorted precondition.
    d2 = (2, 2, 2)
    insertion_order = [i + 1 + d2[i] for i in range(2, 0, -1)]
    assert insertion_order == [5, 4]
    assert insertion_order != sorted(insertion_order)

    print(f"PASS: {checked} arrays checked; monotonic stack == position-scan oracle")
    print(f"PASS: {flawed_cases} arrays distinguish position-first from endpoint-value-first")
    print("PASS: (2,3,1) yields correct next positions [2,None,None], not [3,None,None]")
    print("PASS: (2,2,2) yields descending candidate sequence [5,4], unsafe for upper_bound")
    print("LIMITATION: DP/area and historical C++ submissions were not executed by this test")


if __name__ == '__main__':
    verify()
