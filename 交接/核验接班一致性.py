#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate cross-document CSP-S handoff invariants without network access.

Usage from repository root: python3 交接/核验接班一致性.py
No user accounts, raw replay or private files are read.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
folder = ROOT / "交接"
manifest = json.loads((folder / "2026-10-11_机器可读接管状态.json").read_text("utf-8"))
issues = []
def need(cond, message):
    if not cond:
        issues.append(message)

events = manifest["competition"]["contests"]
need(len(events) == 8, "Expected eight CodeSource contests")
need([e["day"] for e in events] == list(range(1, 9)), "Contest days unordered or duplicated")
need(all(sum(e["points"]) == e["score"] for e in events), "Contest subtask sum mismatch")
need(sum(e["score"] for e in events) == 669, "Eight-contest aggregate must be 669")
need(manifest["competition"]["points_possible"] == 3200, "Possible points mismatch")
need(events[-1]["score"] == 15 and events[-1]["points"] == [15, 0, 0, 0],
     "Day8 contest-time snapshot changed")
need(manifest["day8_postgame"]["A"]["reported_score"] == 70, "A postgame source lost")
need(manifest["day8_postgame"]["C"]["reported_score"] == 23, "C postgame source lost")
need(not manifest["day8_postgame"]["A"]["independent_record_retrieved"], "A verification claim changed")
need(not manifest["day8_postgame"]["C"]["independent_record_retrieved"], "C verification claim changed")
sources = manifest["original_sources"]
need(len(sources["library_paths"]) == 3, "Three-package source list mismatch")
need(sources["recursive_container_instances"] == 235, "Container count mismatch")
need(sources["recursive_unique_containers"] == 97, "Unique-container count mismatch")
need(sources["replay_saved_versions"]["day7"] + sources["replay_saved_versions"]["day8"] == 113,
     "Replay count mismatch")
need(not sources["semantic_full_completion"], "Integrity scan should not mean semantic closure")
need(sources["chat_export"]["messages"] == 282, "Chat source count mismatch")
need(manifest["privacy"]["github_public_at_last_check"], "Re-check current privacy before posting files")

for rel in ["README.md", "AI_HANDOFF.md", "AI_MASTER_INDEX.md",
            "证据阅读台账.md", "全题总表_2026-10-11.md",
            "交接/2026-10-11_主力模拟赛分析_万字接班报告.md",
            "交接/2026-10-11_下一阶段任务与验收.md"]:
    need((ROOT / rel).is_file(), f"Required file missing: {rel}")

report = ROOT / "交接/2026-10-11_主力模拟赛分析_万字接班报告.md"
if report.is_file():
    content = report.read_text("utf-8")
    need(len(re.findall(r"[\u3400-\u9fff]", content)) >= 10000,
         "Main handoff report does not contain at least 10,000 Hanzi")
    for phrase in ["Day8", "Replay", "OJ", "赛时", "赛后", "Library", "Day7"]:
        need(phrase in content, f"Required report concept missing: {phrase}")

if issues:
    print("HANDOFF_CHECK_FAIL", len(issues))
    for issue in issues:
        print("-", issue)
    sys.exit(1)
print("HANDOFF_CHECK_PASS: 8 scores, 669/3200, source tiers, replay counts, privacy and full report.")
