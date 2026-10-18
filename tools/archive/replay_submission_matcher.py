#!/usr/bin/env python3
"""
Match official/OJ submitted source files back to Replay v3 file_changes snapshots.

Strongest mode:
    exact normalized source content

Optional weaker bridge:
    exact body after removing only freopen(...) lines

The weaker mode is useful when the development copy keeps freopen commented or
uses placeholder file names, while the uploaded OJ source differs only in the
traditional-I/O lines. It is deliberately opt-in and is reported as
"body_without_freopen", never as an exact source match.

Usage:
  python replay_submission_matcher.py \
      --file-changes file_changes.jsonl \
      --source "A=record_A.cpp" \
      --source "B=record_B.cpp"

Optional:
  --path-hint "A=T1/main.cpp"
  --start-iso 2026-10-05T10:11:01
  --allow-freopen-delta
  --json

Exit codes:
  0  every source has at least one match
  2  one or more sources have no match
  4  only weaker freopen-insensitive matches exist and at least one source is
     ambiguous (multiple candidate snapshots)

This tool identifies source-state correspondence. It does NOT prove that a
specific matching snapshot is the upload moment when identical code appears
multiple times; combine it with OJ submitTime / timeline / screen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional


FREOPEN_RE = re.compile(r"^\s*(?://\s*)?freopen\s*\(")


def normalize_source(text: str) -> str:
    """Normalize only newline representation and terminal newlines."""
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def source_without_freopen(text: str) -> str:
    """Remove only lines whose statement is freopen(...) or //freopen(...).

    We intentionally preserve every other line, comment and whitespace. A match
    here means "same program body except traditional-I/O lines", not exact
    source identity.
    """
    kept = []
    for line in normalize_source(text).splitlines():
        if FREOPEN_RE.match(line):
            continue
        kept.append(line)
    return "\n".join(kept).rstrip("\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalized_sha256(text: str) -> str:
    return sha256_text(normalize_source(text))


def body_sha256(text: str) -> str:
    return sha256_text(source_without_freopen(text))


@dataclass
class Snapshot:
    seq: int
    t: float
    path: str
    size: int
    event_sha256: str
    normalized_sha256: str
    body_without_freopen_sha256: str
    content: str


@dataclass
class Match:
    label: str
    source_path: str
    match_type: str
    replay_seq: int
    replay_path: str
    t: float
    wall_clock: Optional[str]
    size: int
    event_sha256: str
    normalized_sha256: str
    body_without_freopen_sha256: str


def load_snapshots(path: Path) -> List[Snapshot]:
    out: List[Snapshot] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            if not raw.strip():
                continue
            obj = json.loads(raw)
            content = obj.get("content")
            if not isinstance(content, str):
                continue
            out.append(
                Snapshot(
                    seq=len(out) + 1,
                    t=float(obj.get("t", 0.0)),
                    path=str(obj.get("path", "")),
                    size=int(obj.get("bytes", len(content.encode("utf-8")))),
                    event_sha256=str(obj.get("sha256", "")),
                    normalized_sha256=normalized_sha256(content),
                    body_without_freopen_sha256=body_sha256(content),
                    content=content,
                )
            )
    return out


def parse_kv(items: Iterable[str], flag: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"{flag} expects LABEL=VALUE, got: {item!r}")
        k, v = item.split("=", 1)
        k, v = k.strip(), v.strip()
        if not k or not v:
            raise SystemExit(f"{flag} expects non-empty LABEL=VALUE: {item!r}")
        result[k] = v
    return result


def wall_clock(start_iso: Optional[str], t: float) -> Optional[str]:
    if not start_iso:
        return None
    start = datetime.fromisoformat(start_iso)
    return (start + timedelta(seconds=t)).isoformat(timespec="seconds")


def make_match(
    label: str,
    source_path: Path,
    match_type: str,
    s: Snapshot,
    start_iso: Optional[str],
) -> Match:
    return Match(
        label=label,
        source_path=str(source_path),
        match_type=match_type,
        replay_seq=s.seq,
        replay_path=s.path,
        t=s.t,
        wall_clock=wall_clock(start_iso, s.t),
        size=s.size,
        event_sha256=s.event_sha256,
        normalized_sha256=s.normalized_sha256,
        body_without_freopen_sha256=s.body_without_freopen_sha256,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file-changes", required=True, type=Path)
    ap.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="LABEL=FILE",
        help="Official/OJ source to locate. Repeatable.",
    )
    ap.add_argument(
        "--path-hint",
        action="append",
        default=[],
        metavar="LABEL=REPLAY_PATH",
        help="Optional exact file_changes path filter for a label.",
    )
    ap.add_argument(
        "--start-iso",
        help="Capture start ISO datetime; only used to print derived wall clock.",
    )
    ap.add_argument(
        "--allow-freopen-delta",
        action="store_true",
        help=(
            "If exact source is absent, allow same-body matches after removing "
            "only freopen/commented-freopen lines. Reported as weaker evidence."
        ),
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sources = parse_kv(args.source, "--source")
    hints = parse_kv(args.path_hint, "--path-hint")
    if not sources:
        ap.error("at least one --source LABEL=FILE is required")

    snapshots = load_snapshots(args.file_changes)
    all_results = []
    any_unmatched = False
    any_ambiguous_weak = False

    for label, source_file in sources.items():
        source_path = Path(source_file)
        source_text = source_path.read_text(encoding="utf-8")
        exact_target = normalized_sha256(source_text)
        body_target = body_sha256(source_text)
        hint = hints.get(label)

        pool = [
            s for s in snapshots
            if hint is None or s.path == hint
        ]

        exact = [s for s in pool if s.normalized_sha256 == exact_target]
        match_type = "exact"
        candidates = exact

        if not candidates and args.allow_freopen_delta:
            candidates = [
                s for s in pool
                if s.body_without_freopen_sha256 == body_target
            ]
            if candidates:
                match_type = "body_without_freopen"

        if not candidates:
            any_unmatched = True
        if match_type == "body_without_freopen" and len(candidates) > 1:
            any_ambiguous_weak = True

        matches = [
            make_match(label, source_path, match_type, s, args.start_iso)
            for s in candidates
        ]

        all_results.append(
            {
                "label": label,
                "source": str(source_path),
                "source_normalized_sha256": exact_target,
                "source_body_without_freopen_sha256": body_target,
                "path_hint": hint,
                "match_type": match_type if candidates else None,
                "match_count": len(matches),
                "ambiguous": len(matches) > 1,
                "matches": [asdict(m) for m in matches],
            }
        )

    if args.json:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))
    else:
        for item in all_results:
            print(
                f"[{item['label']}] {item['source']} "
                f"type={item['match_type'] or 'none'} "
                f"matches={item['match_count']}"
            )
            if not item["matches"]:
                print("  NO MATCH")
                continue
            if item["match_type"] == "body_without_freopen":
                print(
                    "  WEAKER EVIDENCE: program body matches only after "
                    "removing freopen lines"
                )
            if item["ambiguous"]:
                print(
                    "  AMBIGUOUS: multiple snapshots share this source state; "
                    "use submitTime/timeline/screen/path hints"
                )
            for m in item["matches"]:
                clock = f" wall={m['wall_clock']}" if m["wall_clock"] else ""
                print(
                    f"  seq={m['replay_seq']} t={m['t']:.3f}{clock} "
                    f"path={m['replay_path']} bytes={m['size']} "
                    f"sha={m['event_sha256'][:12]}"
                )

    if any_unmatched:
        return 2
    if any_ambiguous_weak:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
