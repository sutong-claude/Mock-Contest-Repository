#!/usr/bin/env python3
"""从 总览/赛事账本.json 与工作区文件重生成公开仓库的全部控制层产物。

用法：python3 tools/build_repo_state.py
产物（全部自动生成，勿手改）：
  - 全赛事账本_2026-11-03.md / .csv
  - 总览/仓库文件索引_2026-11-03.json / .md
  - 总览/仓库全量清单_2026-11-03.csv          （逐文件清点，610+ 行）
  - 总览/AI吞入包/01_逐文件摘要.jsonl        （流式可读，一行一文件）
  - 总览/AI吞入包/MANIFEST.json              （分片偏移、读序、校验和）

设计原则：
  1. 确定性：不含时间戳/随机数，便于 tools/verify_repo.py 逐字节比对。
  2. 单一来源：账本只改 JSON；清单只由工作区文件算出；不手写第二套索引。
  3. 自洽：生成物不进入自身索引，避免「索引包含自己的哈希」永不收敛。
"""
import csv
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, '总览', '赛事账本.json')
STAMP = '2026-11-03'
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', '.cache', '_导出', '.pytest_cache'}
SKIP_FILES = {'.DS_Store'}

# 生成的产物不进入自身索引，避免循环哈希
GENERATED = {
    f'全赛事账本_{STAMP}.md', f'全赛事账本_{STAMP}.csv',
    f'总览/仓库文件索引_{STAMP}.json', f'总览/仓库文件索引_{STAMP}.md',
    f'总览/仓库全量清单_{STAMP}.csv',
    f'总览/AI吞入包/MANIFEST.json',
    f'总览/AI吞入包/01_逐文件摘要.jsonl',
}
DIGEST_PATH = f'总览/AI吞入包/01_逐文件摘要.jsonl'

# 历史「首读 / 接班 / 入口」文档：全部已被 START_HERE.md 降级为历史快照
HISTORICAL_ENTRIES = [
    'AGENTS.md', 'CLAUDE.md', 'README.md', 'CURRENT_STATE.md',
    'AI_HANDOFF.md', 'AI_MASTER_INDEX.md',
    '00_请先阅读_2026-10-11.md',
    '00_2026-10-22_桌面全量取证_新AI首读.md',
    '01_2026-10-22_桌面全量考古_陌生AI首读.md',
    '00_2026-10-22_双GeminiPDF_模拟赛全量压缩接班.md',
    '00_2026-10-22_历史源码发布范围_520与522说明.md',
    '总览/AI直接接手入口.md',
    '交接/2026-10-11_主力模拟赛分析_万字接班报告.md',
    '交接/2026-10-11_接班导航.md',
    '交接/2026-10-15_Gemini39页_维护分支更新导航.md',
    '考古/2026-10-22_桌面全量取证入口.md',
]

# 另一个 AI 的读序：0 = 必须读，数字越大越靠后
READ_ORDER = [
    'START_HERE.md',
    '仓库治理规范.md',
    '总览/AI吞入包/02_全仓库知识骨架.md',
    '总览/用户画像_2026-11-03.md',
    '全赛事账本_2026-11-03.md',
    '总览/赛事账本.json',
    'NOIP2026/README.md',
    'NOIP2026/接手总控.md',
    '备考资料库/成长路线图.md',
    '备考资料库/README.md',
    '总览/仓库细节审阅_2026-11-03.md',
    '总览/仓库全量清单_2026-11-03.csv',
    '总览/AI吞入包/00_使用说明.md',
    '维护日志.md',
]

CONTROL_CORE = {
    'START_HERE.md', '仓库治理规范.md', '总览/AI吞入包/02_全仓库知识骨架.md',
    '总览/用户画像_2026-11-03.md', '总览/仓库细节审阅_2026-11-03.md',
    f'全赛事账本_{STAMP}.md', '总览/赛事账本.json', '维护日志.md',
    'NOIP2026/README.md', 'NOIP2026/接手总控.md', '备考资料库/成长路线图.md',
}


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


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
    if r.startswith('备考资料库/'):
        return 'NOIP备考资料库'
    if r.startswith('总览/AI吞入包/'):
        return 'AI吞入包'
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
             'AI_HANDOFF.md', 'AI_MASTER_INDEX.md', '维护日志.md', '仓库治理规范.md'} \
            or r.startswith('全赛事账本_'):
        return '控制层'
    return '其他根目录文档'


def read_priority(r, cat):
    if r in CONTROL_CORE:
        return 0
    if cat in {'NOIP备考控制层', 'NOIP备考资料库', 'AI吞入包', '控制层', 'CI'}:
        return 1
    if cat in {'转写PDF派生解析', '交接与一手证据', '总览与可视化', '协议与课程'}:
        return 1
    if cat == '比赛归档':
        return 2
    if cat in {'工具', '桌面取证与赛后候选', '其他根目录文档'}:
        return 3
    return 4


def probe(path, r):
    """只读地探测文件；大二进制只取类型，不把内容读进内存两次。"""
    size = os.path.getsize(path)
    ext = os.path.splitext(r)[1].lower().lstrip('.') or '(none)'
    info = dict(ext=ext, encoding='binary', lines=0, headings=[], title='', summary='',
                flags=[])
    if size == 0:
        info['flags'].append('EMPTY')
        info['encoding'] = 'utf8'  # 空文件是合法空文本，不是二进制
        return info
    if size > 2_000_000 and ext not in {'md', 'csv', 'json', 'jsonl', 'txt', 'py', 'cpp', 'sh', 'yml'}:
        info['flags'].append('LARGE')
        info['flags'].append('BINARY')
        return info
    try:
        text = open(path, encoding='utf-8').read()
    except (UnicodeDecodeError, OSError):
        info['flags'].append('BINARY')
        if size > 1_000_000:
            info['flags'].append('LARGE')
        return info
    info['encoding'] = 'utf8'
    lines = text.splitlines()
    info['lines'] = len(lines)
    info['headings'] = [h.strip()[:120] for h in re.findall(r'^#{1,3} +(.{1,120})$', text, re.M)][:14]
    info['title'] = info['headings'][0] if info['headings'] else ''
    for l in lines[:40]:
        s = l.strip()
        if s and not s.startswith(('#', '>', '|', '---', '```', '<!--')):
            info['summary'] = re.sub(r'\s+', ' ', s)[:170]
            break
    if size > 1_000_000:
        info['flags'].append('LARGE')
    if len(re.findall(r'TODO|待办|待补|待验证|未完成|FIXME', text)) >= 5:
        info['flags'].append('TODO_MANY')
    if re.search(r'ZJ-\d{6}', text):
        info['flags'].append('LEGACY_ID')
    if r in HISTORICAL_ENTRIES:
        info['flags'].append('ENTRY')
    if r in CONTROL_CORE:
        info['flags'].append('CONTROL')
    if r in GENERATED:
        info['flags'].append('GENERATED')
    return info


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
            cat = category(r)
            info = probe(p, r)
            out.append({
                'path': r, 'bytes': os.path.getsize(p), 'sha256': sha256(p),
                'category': cat, 'ext': info['ext'], 'encoding': info['encoding'],
                'read_priority': read_priority(r, cat), 'lines': info['lines'],
                'headings': info['headings'], 'title': info['title'],
                'summary': info['summary'], 'flags': info['flags'],
            })
    out.sort(key=lambda x: x['path'])
    # DUP：内容完全相同的文件（多为历史占位/镜像，属事实而非错误）
    by_sha = {}
    for x in out:
        by_sha.setdefault(x['sha256'], []).append(x['path'])
    for x in out:
        if len(by_sha[x['sha256']]) > 1:
            x['flags'].append('DUP')
        x['flags'] = sorted(set(x['flags']))
    return out


def load_ledger():
    with open(LEDGER, encoding='utf-8') as f:
        return json.load(f)


def csv_escape(v):
    return '' if v is None else str(v)


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
        'schema': 'mock-contest-repository.file-index.v2',
        'as_of': STAMP,
        'generated_by': 'tools/build_repo_state.py',
        'note': '确定性快照；sha256 可跨分支回读。逐文件元信息见 仓库全量清单_2026-11-03.csv 与 AI吞入包/01_逐文件摘要.jsonl。',
        'file_count': len(inv),
        'total_bytes': sum(x['bytes'] for x in inv),
        'ledger_contest_count': len(d['contests']),
        'categories': {k: sum(1 for x in inv if x['category'] == k)
                       for k in sorted({x['category'] for x in inv})},
        'files': [{'path': x['path'], 'bytes': x['bytes'], 'sha256': x['sha256'],
                   'category': x['category'], 'read_priority': x['read_priority'],
                   'flags': x['flags']} for x in inv],
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
        if r['read_priority'] == 0 or r['category'] in {'NOIP备考控制层', '转写PDF派生解析', 'AI吞入包'}:
            L.append(f"- `{r['path']}` — {r['bytes']:,} B — `{r['sha256'][:12]}…`")
    L.append('\n> 完整逐文件 SHA-256 见同名 JSON；逐文件摘要见 `总览/AI吞入包/01_逐文件摘要.jsonl`。索引只说明「仓库里有什么」，不证明任何算法或成绩。\n')
    return '\n'.join(L) + '\n'


def render_catalog_csv(inv):
    buf = io.StringIO(newline='')
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['path', 'bytes', 'sha256', 'category', 'ext', 'encoding',
                'read_priority', 'lines', 'heading_count', 'title', 'summary', 'flags'])
    for x in inv:
        w.writerow([x['path'], x['bytes'], x['sha256'], x['category'], x['ext'],
                    x['encoding'], x['read_priority'], x['lines'], len(x['headings']),
                    x['title'], x['summary'], ';'.join(x['flags'])])
    return buf.getvalue()


def render_digest_jsonl(inv):
    lines = []
    for x in inv:
        lines.append(json.dumps({
            'path': x['path'], 'bytes': x['bytes'], 'sha256': x['sha256'],
            'category': x['category'], 'read_priority': x['read_priority'],
            'encoding': x['encoding'], 'title': x['title'], 'summary': x['summary'],
            'headings': x['headings'], 'flags': x['flags'],
        }, ensure_ascii=False))
    return '\n'.join(lines) + '\n'


def render_manifest(inv, d, digest):
    digest_bytes = digest.encode('utf-8')
    prios = {}
    for x in inv:
        prios[str(x['read_priority'])] = prios.get(str(x['read_priority']), 0) + 1
    return json.dumps({
        'schema': 'mock-contest-repository.ai-corpus.v1',
        'as_of': STAMP,
        'generated_by': 'tools/build_repo_state.py',
        'purpose': '让不具备 Agent 能力的 AI 一次读入全仓库：先读 02_全仓库知识骨架.md，再按 read_order 逐层展开。',
        'entry': 'START_HERE.md',
        'read_order': READ_ORDER,
        'file_count': len(inv),
        'total_bytes': sum(x['bytes'] for x in inv),
        'text_file_count': sum(1 for x in inv if x['encoding'] == 'utf8'),
        'binary_file_count': sum(1 for x in inv if x['encoding'] == 'binary'),
        'ledger_contest_count': len(d['contests']),
        'categories': {k: sum(1 for x in inv if x['category'] == k)
                       for k in sorted({x['category'] for x in inv})},
        'read_priority_distribution': dict(sorted(prios.items())),
        'shards': [{
            'name': '01_逐文件摘要.jsonl', 'records': len(inv),
            'bytes': len(digest_bytes), 'sha256': hashlib.sha256(digest_bytes).hexdigest(),
            'format': 'jsonl; 一行一文件；可流式读入，支持按 category / read_priority 过滤',
        }, {
            'name': '02_全仓库知识骨架.md', 'records': 1,
            'format': 'markdown; 人工编纂的全仓库事实骨架，非自动生成',
        }],
        'catalog': f'总览/仓库全量清单_{STAMP}.csv',
        'full_body_export': '按需运行 python3 tools/export_ai_corpus.py --out <路径>；输出目录 _导出/ 已 gitignore，不进版本库',
        'bulk_import': '批量写入用 python3 tools/ingest_materials.py --src <目录>；先落 99_收件箱_待归档/ 再分类',
        'verification': ['python3 tools/build_repo_state.py', 'python3 tools/verify_repo.py'],
        'boundary': '索引只描述仓库内容，不证明算法正确性、不把 [G]/ESTIMATE 升级成 OJ 成绩；LOCAL-VERIFIED ≠ OJ-AC。',
    }, ensure_ascii=False, indent=2) + '\n'


def expected_outputs():
    d = load_ledger()
    inv = inventory()
    digest = render_digest_jsonl(inv)
    return {
        f'全赛事账本_{STAMP}.md': render_ledger_md(d),
        f'全赛事账本_{STAMP}.csv': render_ledger_csv(d),
        f'总览/仓库文件索引_{STAMP}.json': render_index_json(inv, d),
        f'总览/仓库文件索引_{STAMP}.md': render_index_md(inv, d),
        f'总览/仓库全量清单_{STAMP}.csv': render_catalog_csv(inv),
        DIGEST_PATH: digest,
        '总览/AI吞入包/MANIFEST.json': render_manifest(inv, d, digest),
    }


def main():
    outs = expected_outputs()
    for path, content in outs.items():
        p = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f'WROTE {path} ({len(content.encode("utf-8"))} bytes)')
    print(f'LEDGER contests={len(load_ledger()["contests"])}  FILES={len(inventory())}  PRODUCTS={len(outs)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
