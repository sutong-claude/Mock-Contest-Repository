#!/usr/bin/env python3
"""从 总览/赛事账本.json 与工作区文件重生成公开仓库的控制层产物。

用法：python3 tools/build_repo_state.py
产物（自动生成，勿手改）：
  - 全赛事账本_2026-11-03.md / .csv
  - 总览/仓库文件索引_2026-11-03.json / .md

设计原则：确定性（不含时间戳/随机数），便于 tools/verify_repo.py 逐字节比对。
"""
import csv
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, '总览', '赛事账本.json')
STAMP = '2026-11-03'
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', '.cache'}
SKIP_FILES = {'.DS_Store'}
# 生成的产物不进入自身索引，避免「索引包含自己的哈希」造成永不收敛的固定点问题
GENERATED = {
    f'全赛事账本_{STAMP}.md', f'全赛事账本_{STAMP}.csv',
    f'总览/仓库文件索引_{STAMP}.json', f'总览/仓库文件索引_{STAMP}.md',
}


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def inventory():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in sorted(fns):
            if fn in SKIP_FILES:
                continue
            p = os.path.join(dp, fn)
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            r = rel(p)
            if r in GENERATED:
                continue
            out.append({'path': r, 'bytes': os.path.getsize(p), 'sha256': sha256(p), 'category': category(r)})
    return sorted(out, key=lambda x: x['path'])


def category(r):
    if r.startswith('2026-') and '/' in r:
        return '比赛归档'
    if r.startswith('交接/2026-11-03_双PDF解析/'):
        return '转写PDF派生解析'
    if r.startswith('交接/'):
        return '交接与一手证据'
    if r.startswith('考古/'):
        return '桌面取证与赛后候选'
    if r.startswith('NOIP2026/'):
        return 'NOIP备考控制层'
    if r.startswith('总览/'):
        return '总览与可视化'
    if r.startswith('tools/'):
        return '工具'
    if r.startswith('.github/'):
        return 'CI'
    if r.startswith('skills/') or r.startswith('专题课程/') or r.startswith('执行包/'):
        return '协议与课程'
    if r.startswith('docs/') or r.startswith('assets/'):
        return '站点镜像与素材'
    if r in {'START_HERE.md', 'AGENTS.md', 'CLAUDE.md', 'README.md', 'CURRENT_STATE.md',
             'AI_HANDOFF.md', 'AI_MASTER_INDEX.md', '维护日志.md'} or r.startswith('全赛事账本_'):
        return '控制层'
    return '其他根目录文档'


def load_ledger():
    with open(LEDGER, encoding='utf-8') as f:
        return json.load(f)


def csv_escape(v):
    if v is None:
        return ''
    return str(v)


def render_ledger_csv(d):
    buf = io.StringIO(newline='')
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['id', 'date', 'series', 'name', 'folder', 'per_problem', 'score', 'max',
                'score_tier', 'record_status', 'in_main_line', 'review', 'next_action', 'source'])
    for c in d['contests']:
        pp = ';'.join(f'{k}={v}' for k, v in (c.get('per_problem') or {}).items())
        w.writerow([csv_escape(c.get(k)) for k in
                    ('id', 'date', 'series', 'name', 'folder')] +
                   [pp, csv_escape(c.get('score')), c.get('max', 400), c.get('score_tier', ''),
                    c.get('record_status', ''), str(c.get('in_main_line', False)).lower(),
                    c.get('review', ''), c.get('next_action', ''), c.get('source', '')])
    return buf.getvalue()


def render_ledger_md(d):
    L = []
    L.append(f'# 全赛事账本｜{STAMP}（自动生成）\n')
    L.append('> **本文件由 `python3 tools/build_repo_state.py` 从 `总览/赛事账本.json` 生成，勿手改。**')
    L.append('> 唯一首读入口是 `START_HERE.md`；本表只负责「所有比赛 + 分数 + 证据等级 + 目录状态」。')
    L.append('> 旧表 `全题总表_2026-10-11.md`（36 题）、`总览/全题总表_32题.*`（32 题）、`赛场星图_2026-10-12.json`（8 场）都是各自日期的历史快照，不覆盖、不混算。\n')
    L.append(f"维护目标：{d['current_goal']}　｜　计分口径：{d['scoring_rule']}\n")
    L.append('## 证据等级缩写\n')
    L.append('| 缩写 | 含义 |\n| --- | --- |')
    for k, v in d['score_tier_legend'].items():
        L.append(f'| `{k}` | {v} |')
    L.append('\n## 全赛事总表\n')
    L.append('| # | 日期 | 体系 | 比赛 | A/B/C/D 或逐题 | 分数 | 等级 | 目录 | 复盘 | 下一步 |')
    L.append('| ---: | --- | --- | --- | --- | ---: | --- | --- | --- | --- |')
    for i, c in enumerate(d['contests'], 1):
        pp = '/'.join(str(v) if v is not None else '未交' for v in (c.get('per_problem') or {}).values()) or '—'
        score = 'UNKNOWN' if c.get('score') is None else f"{c['score']}/{c.get('max', 400)}"
        folder = f"`{c['folder']}`" if c.get('folder') else '**无独立目录**'
        L.append(f"| {i} | {c.get('date') or '待定'} | `{c['series']}` | {c['name']} | {pp} | {score} | `{c['score_tier']}` | {folder} | {c.get('review','')} | {c.get('next_action','')} |")
    L.append('\n### 逐条 record 状态（决定能不能升级证据等级）\n')
    for c in d['contests']:
        L.append(f"- **{c['name']}**（`{c['id']}`）：{c['record_status']}　→　来源：`{c['source']}`")
    L.append('\n## 主线求和（不得手写进文档）\n')
    L.append('| 口径 | 值 |')
    L.append('| --- | ---: |')
    for k, v in d['derived_sums'].items():
        if isinstance(v, (int, float)):
            L.append(f'| `{k}` | {v} |')
    L.append(f"\n> {d['derived_sums']['note']}\n")
    L.append('## 身份消歧（三场 Day9 / 三场 CodeLands 等）\n')
    for t in d['identity_traps']:
        L.append(f'- {t}')
    L.append('\n## 使用规则\n')
    L.append('1. 改分数/加比赛：只改 `总览/赛事账本.json`。')
    L.append('2. 重生成：`python3 tools/build_repo_state.py`。')
    L.append('3. 校验：`python3 tools/verify_repo.py`；每次提交报告真实 commit SHA 与回读结果。')
    L.append('4. `[G]` / `ESTIMATE` / `CONFLICT` / `UNKNOWN` 绝不进主线折线；`LOCAL-VERIFIED ≠ OJ-AC`。\n')
    return '\n'.join(L) + '\n'


def render_index_json(inv, d):
    return json.dumps({
        'schema': 'mock-contest-repository.file-index.v1',
        'as_of': STAMP,
        'generated_by': 'tools/build_repo_state.py',
        'note': '确定性快照；文件的 sha256 可用于跨分支回读。原始录屏/按键/聊天/账号页不在本索引中，也不应在仓库中。',
        'file_count': len(inv),
        'total_bytes': sum(x['bytes'] for x in inv),
        'ledger_contest_count': len(d['contests']),
        'categories': {k: sum(1 for x in inv if x['category'] == k)
                       for k in sorted({x['category'] for x in inv})},
        'files': inv,
    }, ensure_ascii=False, indent=2) + '\n'


def render_index_md(inv, d):
    L = [f'# 仓库文件索引｜{STAMP}（自动生成）\n',
         '> 由 `python3 tools/build_repo_state.py` 生成，勿手改。机器可读版：`仓库文件索引_2026-11-03.json`。\n',
         f"共 **{len(inv)}** 个文件、**{sum(x['bytes'] for x in inv):,}** 字节；赛事账本 **{len(d['contests'])}** 条。\n",
         '## 按分类\n', '| 分类 | 文件数 | 字节 |', '| --- | ---: | ---: |']
    for k in sorted({x['category'] for x in inv}):
        rows = [x for x in inv if x['category'] == k]
        L.append(f'| {k} | {len(rows)} | {sum(x["bytes"] for x in rows):,} |')
    L.append('\n## 控制层文件（接手必读）\n')
    for r in inv:
        if r['category'] in {'控制层', 'NOIP备考控制层', '转写PDF派生解析', '工具', 'CI'}:
            L.append(f"- `{r['path']}` — {r['bytes']:,} B — `{r['sha256'][:12]}…`")
    L.append('\n> 完整逐文件 SHA-256 见同名 JSON。索引只说明「仓库里有什么」，不证明任何算法或成绩。\n')
    return '\n'.join(L) + '\n'


def expected_outputs():
    d = load_ledger()
    inv = inventory()
    return {
        f'全赛事账本_{STAMP}.md': render_ledger_md(d),
        f'全赛事账本_{STAMP}.csv': render_ledger_csv(d),
        f'总览/仓库文件索引_{STAMP}.json': render_index_json(inv, d),
        f'总览/仓库文件索引_{STAMP}.md': render_index_md(inv, d),
    }


def main():
    outs = expected_outputs()
    for path, content in outs.items():
        p = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f'WROTE {path} ({len(content.encode("utf-8"))} bytes)')
    print(f'LEDGER contests={len(load_ledger()["contests"])}  FILES={len(inventory())}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
