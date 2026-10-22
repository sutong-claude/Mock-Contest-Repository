#!/usr/bin/env python3
"""Independent contest-candidate validation. Stdlib only; no editorial/oracle imports."""
import itertools
import pathlib
import random
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1] / "赛后候选"
SEED = 20261025

def covered(a, b):
    """Quadratic *independent* interval DP; no 2D Fenwick structure."""
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

def matchings(n, m):
    """Count permutations satisfying individual forbidden pair edges."""
    return sum(all(p[i] != i for i in range(n))
               for p in itertools.permutations(range(n + m)))

def invoke(binary, content):
    result = subprocess.run([str(binary)], input=content, text=True,
                            capture_output=True, check=True, timeout=5)
    return result.stdout.strip()

def main():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        bin_c = d / "maxcover"
        bin_b = d / "alien"
        subprocess.run(["g++", "-std=c++17", "-O2",
                        str(ROOT / "CodeLands3_maxcover_二维树状数组.cpp"),
                        "-o", str(bin_c)], check=True)
        subprocess.run(["g++", "-std=c++17", "-O2",
                        str(ROOT / "CodeLands3_alien_线性容斥.cpp"),
                        "-o", str(bin_b)], check=True)
        rnd = random.Random(SEED)
        count_c = count_b = 0
        for z in range(600):
            n = rnd.randint(1, 40)
            a = [rnd.randint(-10000, 10000) for _ in range(n)]
            b = [rnd.randint(-10000, 10000) for _ in range(n)]
            inp = f"{n}\n" + " ".join(map(str, a)) + "\n" + " ".join(map(str, b)) + "\n"
            expected = covered(a, b)
            actual = invoke(bin_c, inp)
            assert actual == str(expected), ("C", z, expected, actual, inp)
            count_c += 1
        for label, a, b in [
            ("special_negative_prefix", [0]*21, [-1, 2]+[0]*19),
            ("general_skip_disjoint", [1]+[-100]*19+[1],
             [1]+[-100]*19+[1]),
        ]:
            n = len(a)
            inp = f"{n}\n" + " ".join(map(str, a)) + "\n" + " ".join(map(str, b)) + "\n"
            assert invoke(bin_c, inp) == str(covered(a, b)), label
            count_c += 1
        for z in range(300):
            n = rnd.randint(0, 7)
            m = rnd.randint(0, 7-n)
            expected = matchings(n, m)
            actual = invoke(bin_b, f"{n} {m}\n")
            assert actual == str(expected), ("B", z, n, m, expected, actual)
            count_b += 1
        print(f"SEED={SEED}; maxcover {count_c} pass; alien {count_b} pass")
        print("LOCAL_VERIFIED only; not an official OJ result.")

if __name__ == "__main__":
    main()
