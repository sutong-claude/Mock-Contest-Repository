#!/usr/bin/env python3
"""Day5 D independent verification, compiling the repository's C++ candidate.

Small exhaustive domain: n=1..3, a_i in {0,1,2},
q=0..2, and each operation [l,r], x in {1,2,3}.
Plus 650 reproducible random cases over full 7-bit input values (n<=8,q<=9).
The brute oracle enumerates every subset and every contiguous interval;
it does NOT use the moment/covariance identity from the solution.
"""
from __future__ import annotations
import argparse
import itertools
from pathlib import Path
import random
import subprocess
import tempfile

MOD = 1000000007


def exact_oracle(initial, operations):
    n = len(initial)
    total = 0
    for mask in range(1 << len(operations)):
        a = list(initial)
        for j, (l, r, x) in enumerate(operations):
            if mask >> j & 1:
                for k in range(l-1, r):
                    a[k] ^= x
        for l in range(n):
            s = 0
            for r in range(l, n):
                s += a[r]
                total += s*s
    return total % MOD


def submitted(exe, initial, operations):
    data = f"{len(initial)}\n" + " ".join(map(str, initial)) + "\n"
    data += str(len(operations)) + "\n"
    data += "".join(f"{l} {r} {x}\n" for l, r, x in operations)
    r = subprocess.run([str(exe)], input=data, text=True,
                       capture_output=True, timeout=12, check=True)
    return int(r.stdout.strip())


def verify(exe):
    samples = [
        ([1, 3], [(1, 2, 2)], 52),
        ([1, 2, 3, 4, 5], [], 1001),
    ]
    for a, operations, expected in samples:
        got = submitted(exe, a, operations)
        if got != expected:
            raise AssertionError(("official sample", a, operations, got, expected))
    print("official samples: 2/2 PASS")

    total = 0
    for n in range(1, 4):
        all_ops = [(l, r, x)
                   for l in range(1, n+1)
                   for r in range(l, n+1)
                   for x in (1,2,3)]
        for a in itertools.product((0,1,2), repeat=n):
            for q in range(3):
                for ops in itertools.product(all_ops, repeat=q):
                    want = exact_oracle(a, ops)
                    got = submitted(exe, a, ops)
                    assert got == want, (a,ops,got,want)
                    total += 1
    print(f"exhaustive: {total} cases, mismatches=0")

    rng = random.Random(190087)
    for run in range(650):
        n = rng.randint(1,8)
        q = rng.randint(0,9)
        a = [rng.randint(0,127) for _ in range(n)]
        ops = []
        for _ in range(q):
            l = rng.randint(1,n)
            r = rng.randint(l,n)
            ops.append((l,r,rng.randint(0,127)))
        got = submitted(exe,a,ops)
        want = exact_oracle(a,ops)
        assert got == want, (run,a,ops,got,want)
    print("random 7-bit: 650 cases, mismatches=0")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "正解代码/D_灯光预案_二阶矩_确定性位集.cpp")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="day5d_test_") as tmp:
        exe = Path(tmp) / "day5d"
        subprocess.run(["g++", "-std=c++17", "-O2",
                        str(args.source), "-o", str(exe)], check=True)
        verify(exe)


if __name__ == "__main__":
    main()
