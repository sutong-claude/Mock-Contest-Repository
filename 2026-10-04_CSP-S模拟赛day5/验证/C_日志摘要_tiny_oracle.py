#!/usr/bin/env python3
"""Day5 C tiny exhaustive suffix oracle for the OJ-submitted source.

Usage:
  python3 C_日志摘要_tiny_oracle.py --source record_6ac1dd8a4a5cd1a28f06ca55.cpp

Source path must be supplied from the private source archive or a verified
copy. Never infer general correctness from these deliberately small domains.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
from pathlib import Path
import subprocess
import tempfile

SUBMITTED_SHA256 = "1fe58756e48eb807daab13a1fd3ba6a65a905e2a4d10f1249f4ae106324c9bb2"


def brute(words: tuple[str, ...]) -> str:
    choices = [tuple(s[k:] for k in range(len(s))) for s in words]
    return min(map("".join, itertools.product(*choices)))


def feasible(words: tuple[str, ...], result: str) -> bool:
    choices = [tuple(s[k:] for k in range(len(s))) for s in words]
    return result in {"".join(t) for t in itertools.product(*choices)}


def domains():
    small = ["".join(t) for length in (1, 2, 3)
             for t in itertools.product("ab", repeat=length)]
    length2 = ["".join(t) for t in itertools.product("ab", repeat=2)]
    yield "ab/len1..3/n1..3", [c for n in range(1, 4)
                               for c in itertools.product(small, repeat=n)]
    yield "ab/len2/n2..5", [c for n in range(2, 6)
                            for c in itertools.product(length2, repeat=n)]


def run_source(source: Path, cases: list[tuple[str, ...]]) -> list[str]:
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != SUBMITTED_SHA256:
        raise ValueError(f"Source hash mismatch: {digest}")
    with tempfile.TemporaryDirectory(prefix="day5c_") as tmp:
        wd = Path(tmp)
        exe = wd / "submitted"
        subprocess.run(["g++", "-std=gnu++17", "-O2", str(source),
                        "-o", str(exe)], check=True)
        data = str(len(cases)) + "\n"
        data += "".join(str(len(c)) + "\n" + "\n".join(c) + "\n"
                        for c in cases)
        (wd / "Hina.in").write_text(data, encoding="utf-8")
        subprocess.run([str(exe)], cwd=wd, check=True,
                       capture_output=True, timeout=30)
        return (wd / "Hina.out").read_bytes().decode("utf-8").splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    source = parser.parse_args().source.resolve()
    for label, cases in domains():
        got = run_source(source, cases)
        assert len(got) == len(cases), (label, len(got), len(cases))
        bad = [(c, brute(c), s) for c, s in zip(cases, got) if brute(c) != s]
        illegal = sum(not feasible(c, actual) for c, _, actual in bad)
        print(f"{label}: cases={len(cases)} mismatches={len(bad)} infeasible_outputs={illegal}")
        for c, expected, actual in bad[:8]:
            print(f"  {c!r}: expected={expected!r} submitted={actual!r}")
        if label == "ab/len2/n2..5":
            for n in range(2, 6):
                total = sum(len(c) == n for c in cases)
                errors = sum(len(c) == n for c, _, _ in bad)
                print(f"  n={n}: errors={errors}/{total}")
    print("SOURCE_SHA256_CHECK=PASS")


if __name__ == "__main__":
    main()
