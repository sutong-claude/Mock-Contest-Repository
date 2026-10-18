#!/usr/bin/env python3
"""
Detect verdict-coverage holes where a local checker returns success even though
candidate YES/NO decisions disagree with an official/truth output.

This is aimed at construction problems whose output is one logical verdict per
non-empty line, for example:

    YES l r
    NO

It does two independent checks:

1. Compare the first YES/NO token of candidate vs official/truth output.
2. Optionally run the local checker on the candidate output.

If a verdict mismatch exists while the checker exits 0, the script prints
MASKED_MISMATCH and exits 3. This is the exact failure mode seen in Day3 B:
the construction checker validated YES witnesses but skipped NO answers.

Usage:
    python checker_coverage_probe.py \
        --candidate candidate.out \
        --official sample.out

    python checker_coverage_probe.py \
        --candidate candidate.out \
        --official sample.out \
        --checker ./checker \
        --input sample.in

Exit codes:
    0  verdict tokens agree
    1  verdict mismatch detected (checker not run, or checker also rejected)
    2  malformed/insufficient verdict stream
    3  MASKED_MISMATCH: checker returned success despite a verdict mismatch

Important:
- This is not a universal semantic oracle.
- An official output is only a truth source when its YES/NO decision is
  authoritative for the case.
- For problems with flexible multi-line witness formats, provide a normalized
  verdict-only truth output or adapt the parser.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VerdictLine:
    line_no: int
    verdict: str
    raw: str


def read_verdicts(path: pathlib.Path) -> List[VerdictLine]:
    result: List[VerdictLine] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        first = stripped.split()[0].upper()
        if first in {"YES", "NO"}:
            result.append(VerdictLine(line_no, first, stripped))
    return result


def run_checker(
    checker: pathlib.Path,
    input_file: pathlib.Path,
    candidate: pathlib.Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(checker), str(input_file), str(candidate)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, type=pathlib.Path)
    ap.add_argument("--official", required=True, type=pathlib.Path)
    ap.add_argument("--checker", type=pathlib.Path)
    ap.add_argument("--input", type=pathlib.Path)
    ap.add_argument(
        "--quiet-checker",
        action="store_true",
        help="Do not echo checker stdout/stderr.",
    )
    args = ap.parse_args()

    if args.checker is not None and args.input is None:
        ap.error("--input is required when --checker is supplied")

    candidate = read_verdicts(args.candidate)
    official = read_verdicts(args.official)

    if not candidate or not official:
        print(
            "ERROR: candidate or official output contains no YES/NO verdicts",
            file=sys.stderr,
        )
        return 2

    mismatch = []
    total = max(len(candidate), len(official))
    for i in range(total):
        cv = candidate[i].verdict if i < len(candidate) else "<missing>"
        ov = official[i].verdict if i < len(official) else "<missing>"
        if cv != ov:
            mismatch.append((i + 1, cv, ov))

    checker_rc: Optional[int] = None
    if args.checker is not None:
        proc = run_checker(args.checker, args.input, args.candidate)
        checker_rc = proc.returncode
        if not args.quiet_checker:
            if proc.stdout:
                print(proc.stdout, end="")
            if proc.stderr:
                print(proc.stderr, file=sys.stderr, end="")

    print(
        f"candidate_cases={len(candidate)} "
        f"official_cases={len(official)} "
        f"mismatches={len(mismatch)}"
    )
    for case_no, cv, ov in mismatch:
        print(
            f"MISMATCH case={case_no} "
            f"candidate={cv} official={ov}"
        )

    if mismatch and checker_rc == 0:
        print(
            "MASKED_MISMATCH: checker returned success despite verdict mismatch"
        )
        return 3

    if mismatch:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
