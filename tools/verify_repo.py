#!/usr/bin/env python3
"""仓库总控自检：结构、链接、总账、逐文件清单、AI 吞入包、一手证据、隐私、治理、CI。

用法：python3 tools/verify_repo.py
输出：每项 PASS/FAIL + 汇总；有 FAIL 时 exit 1。
注意：本脚本检查**结构与自洽性**，不能替代真实 OJ 回读或数学证明。
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_repo_state as brs  # noqa: E402

STAMP = '2026-11-03'
results = []


def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))
    print(f'{"PASS" if ok else "FAIL"}  {name}' + (f'  :: {detail}' if detail else ''))
    return ok


def p(*parts):
    return os.path.join(ROOT, *parts)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def strip_code(text):
    """去掉围栏代码块与行内代码，避免把 `operator[](size())` 当成链接。"""
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    text = re.sub(r'`[^`\n]*`', '', text)
    return text


def md_links(text):
    """返回 [(line_no, target)]，支持目标中含括号的合法路径。"""
    out = []
    for lineno, line in enumerate(strip_code(text).splitlines(), 1):
        i = 0
        while True:
            j = line.find('](', i)
            if j < 0:
                break
            k = j + 2
            depth = 1
            while k < len(line) and depth:
                if line[k] == '(':
                    depth += 1
                elif line[k] == ')':
                    depth -= 1
                k += 1
            if depth == 0:
                target = line[j + 2:k - 1].strip()
                target = re.sub(r'\s+"[^"]*"$', '', target).strip()
                out.append((lineno, target))
                i = k
            else:
                i = j + 2
    return out


def link_audit():
    broken = []
    total = 0
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in brs.SKIP_DIRS]
        for fn in fns:
            if not fn.endswith('.md'):
                continue
            path = os.path.join(dp, fn)
            for lineno, target in md_links(read(path)):
                if not target or target.startswith(('http://', 'https://', 'mailto:', '#')):
                    continue
                t = target.split('#')[0].strip()
                if not t:
                    continue
                total += 1
                from urllib.parse import unquote
                dest = os.path.normpath(os.path.join(dp, unquote(t)))
                if not os.path.exists(dest):
                    broken.append((brs.rel(path), lineno, t))
    return total, broken


def main():
    # 1. 必备文件（控制层 + 治理 + 吞入包 + 资料库 + 工具）
    required = [
        'START_HERE.md', '仓库治理规范.md', 'AGENTS.md', 'CLAUDE.md', 'README.md', '维护日志.md',
        '总览/赛事账本.json', f'全赛事账本_{STAMP}.md', f'全赛事账本_{STAMP}.csv',
        f'总览/仓库文件索引_{STAMP}.json', f'总览/仓库文件索引_{STAMP}.md',
        f'总览/仓库全量清单_{STAMP}.csv', '总览/用户画像_2026-11-03.md',
        '总览/仓库细节审阅_2026-11-03.md', '总览/可视化/README.md',
        '总览/AI吞入包/00_使用说明.md', '总览/AI吞入包/01_逐文件摘要.jsonl',
        '总览/AI吞入包/MANIFEST.json', '总览/AI吞入包/02_全仓库知识骨架.md',
        'NOIP2026/README.md', 'NOIP2026/接手总控.md', 'NOIP2026/四阶段路线图.md',
        'NOIP2026/考场执行卡_NOIP.md', 'NOIP2026/补题队列.md', 'NOIP2026/错因总表.csv',
        '备考资料库/README.md', '备考资料库/成长路线图.md', '备考资料库/知识点掌握度.csv',
        '备考资料库/99_收件箱_待归档/README.md',
        '交接/2026-11-03_双PDF解析/00_总览_方法论与事实分栏.md',
        '交接/2026-11-03_双PDF解析/08_全文主题索引.csv',
        'tools/build_repo_state.py', 'tools/ingest_materials.py', 'tools/export_ai_corpus.py',
        '.github/workflows/repo-integrity.yml', '.github/workflows/atlas-smoke.yml',
        '赛场星图.html', 'docs/index.html',
    ]
    missing = [r for r in required if not os.path.isfile(p(r))]
    check('必备控制层文件齐全', not missing, f'{len(required) - len(missing)}/{len(required)}' + (f' 缺 {missing}' if missing else ''))

    # 2. 7 个生成产物与账本/工作区逐字节一致
    expected = brs.expected_outputs()
    drift = [path for path, content in expected.items()
             if not os.path.isfile(p(path)) or read(p(path)) != content]
    check('7 个生成产物与账本/工作区同步', not drift,
          f'{len(expected)} 个产物逐字节一致' if not drift else f'需重跑 build_repo_state.py：{drift}')

    # 3. 逐文件清单 / 吞入包分片 / MANIFEST 自洽
    inv = brs.inventory()
    with open(p(f'总览/仓库全量清单_{STAMP}.csv'), newline='', encoding='utf-8') as f:
        cat_rows = list(csv.DictReader(f))
    check('逐文件清单覆盖全部非生成文件', len(cat_rows) == len(inv),
          f'{len(cat_rows)} 行 / inventory {len(inv)} 个文件')
    digest_path = p('总览/AI吞入包/01_逐文件摘要.jsonl')
    digest_bytes = open(digest_path, 'rb').read()
    recs = [json.loads(l) for l in digest_bytes.decode('utf-8').splitlines() if l.strip()]
    check('AI 吞入包摘要一行一文件', len(recs) == len(inv) and
          all(r['sha256'] and r['path'] for r in recs), f'{len(recs)} 条记录')
    man = json.loads(read(p('总览/AI吞入包/MANIFEST.json')))
    shard = man['shards'][0]
    check('MANIFEST 分片校验和与记录数正确',
          shard['sha256'] == hashlib.sha256(digest_bytes).hexdigest() and
          shard['records'] == len(inv) and man['file_count'] == len(inv) and
          man['total_bytes'] == sum(x['bytes'] for x in inv),
          f"sha={shard['sha256'][:12]}… records={shard['records']}")
    miss_order = [r for r in man['read_order'] if not os.path.isfile(p(r))]
    check('MANIFEST 读序中的文件都存在', not miss_order, f'{len(man["read_order"])} 个入口' + (f' 缺 {miss_order}' if miss_order else ''))

    # 4. 总账自洽
    d = json.loads(read(p('总览', '赛事账本.json')))
    ids = [c['id'] for c in d['contests']]
    check('赛事 id 唯一', len(ids) == len(set(ids)), f'{len(ids)} 场')
    miss_folder = [c['id'] for c in d['contests'] if c.get('folder') and not os.path.isdir(p(c['folder']))]
    check('账本中标记为存在的比赛目录都存在', not miss_folder, str(miss_folder))
    main_oj = [c for c in d['contests'] if c.get('in_main_line') and c['score_tier'] == 'OJ']
    s9 = sum(c['score'] for c in main_oj)
    s8 = sum(c['score'] for c in main_oj[:8])
    sums = d['derived_sums']
    check('代码源主线求和', s9 == sums['codesource_day1_day9_oj'] == 729 and s8 == sums['codesource_day1_day8_oj'] == 669,
          f'Day1-8={s8}, Day1-9={s9}, 声明={sums["codesource_day1_day8_oj"]}/{sums["codesource_day1_day9_oj"]}')
    day10 = next(c for c in d['contests'] if c['id'] == 'codesource-day10')
    check('Day10 未混入主线', day10['score_tier'] == 'GEMINI_REPORT' and not day10['in_main_line'],
          f"score_tier={day10['score_tier']}, in_main_line={day10['in_main_line']}")
    cl3 = next(c for c in d['contests'] if c['id'] == 'codelands-3')
    check('CodeLands3 保持待回读状态', 'GEMINI_REPORT' in cl3['score_tier'] and cl3['score'] == 160,
          f"160 分仍为 {cl3['score_tier']}，未升级为 OJ")
    official = [c for c in d['contests'] if c['series'] == 'official']
    check('正式考试成绩未被写成已定案', all(c['score'] is None and c['score_tier'] == 'ESTIMATE' for c in official),
          f'{len(official)} 场 ESTIMATE')

    # 5. Markdown 本地链接
    total, broken = link_audit()
    check('Markdown 本地链接全部可解析', not broken,
          f'{total} 条本地链接，{len(broken)} 条断链' + (f'：{broken[:6]}' if broken else ''))

    # 6. 一手证据 CSV / JSONL 数字与哈希
    ev_path = p('交接', '一手证据', '2026-10-22_690保存事件_脱敏可搜索.csv')
    with open(ev_path, newline='', encoding='utf-8') as f:
        ev = list(csv.DictReader(f))
    mismatch = [r for r in ev if r['reported_sha256'] and r['recomputed_sha256']
                and r['reported_sha256'] != r['recomputed_sha256']]
    nonempty = [r for r in ev if r['is_source'].lower() == 'true' and r['has_nonempty_content'].lower() == 'true']
    check('690 事件数与哈希', len(ev) == 690 and not mismatch,
          f'{len(ev)} 行, reported/recomputed mismatch={len(mismatch)}, 非空源码事件={len(nonempty)}')
    with open(p('交接', '一手证据', '2026-10-22_2581桌面文件_SHA256脱敏目录.csv'), newline='', encoding='utf-8') as f:
        nfiles = sum(1 for _ in csv.DictReader(f))
    check('2581 文件 SHA 目录', nfiles == 2581, f'{nfiles} 行')
    for name, want in [('2026-10-22_520份赛时C++非空源码快照.jsonl', 520),
                       ('2026-10-22_96份赛时草稿笔记保存链.jsonl', 96)]:
        recs2 = [json.loads(l) for l in read(p('交接', '一手证据', name)).splitlines() if l.strip()]
        bad = [r for r in recs2 if hashlib.sha256(r.get('content', '').encode()).hexdigest() != r['sha256']]
        check(f'{name[:22]}… 条数与 content 哈希', len(recs2) == want and not bad,
              f'{len(recs2)} 条, mismatch={len(bad)}')
    j = json.loads(read(p('考古', '2026-10-22_机器可读取证状态.json')))
    check('取证状态 JSON 与事件表一致',
          j['file_changes_events'] == len(ev) and
          sum(s['video_segments'] for s in j['sessions']) == 240 and
          sum(s['file_events'] for s in j['sessions']) == len(ev),
          f"events={j['file_changes_events']}, videos={sum(s['video_segments'] for s in j['sessions'])}, sessions={len(j['sessions'])}（其中 1 个 0 事件）")

    # 7. 四份离线 HTML 字节一致（含被误命名的「阶段成长仪表盘」）
    htmls = ['赛场星图.html', 'docs/index.html', '总览/可视化/赛场星图_2026-10-12.html',
             '总览/可视化/阶段成长仪表盘.html']
    hs = {x: hashlib.sha256(open(p(x), 'rb').read()).hexdigest() for x in htmls}
    check('赛场星图四份镜像字节一致', len(set(hs.values())) == 1, f'{len(htmls)} 份 / {next(iter(hs.values()))[:16]}…')

    # 8. 隐私：新控制层不得含 OCR 原文敏感串；全仓不得新增原始敏感附件
    scan_dirs = ['NOIP2026', '交接/2026-11-03_双PDF解析', 'tools', '.github', '总览', '备考资料库']
    scan_files = ['START_HERE.md', '仓库治理规范.md', '维护日志.md',
                  f'全赛事账本_{STAMP}.md', f'全赛事账本_{STAMP}.csv']
    forbidden = re.compile(r'苏潼|bce-auth|pplines-online|MX0INOIP|@gmail\.com|E:\\[^\s]{4,}')
    self_scan_skip = {'tools/verify_repo.py', 'tools/ingest_materials.py'}  # 内含正则字面量
    hits = []
    for base in scan_dirs:
        for dp, dns, fns in os.walk(p(base)):
            dns[:] = [x for x in dns if x not in brs.SKIP_DIRS]
            for fn in fns:
                if not fn.endswith(('.md', '.csv', '.json', '.jsonl', '.yml', '.py', '.txt')):
                    continue
                fp = os.path.join(dp, fn)
                if brs.rel(fp) in self_scan_skip or os.path.getsize(fp) > 3_000_000:
                    continue
                try:
                    if forbidden.search(read(fp)):
                        hits.append(brs.rel(fp))
                except UnicodeDecodeError:
                    pass
    for f in scan_files:
        if os.path.isfile(p(f)) and forbidden.search(read(p(f))):
            hits.append(f)
    check('新增控制层无 OCR 原文敏感串', not hits, str(hits[:5]))
    legacy = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [x for x in dns if x not in brs.SKIP_DIRS]
        for fn in fns:
            if not fn.endswith('.md'):
                continue
            fp = os.path.join(dp, fn)
            try:
                if re.search(r'ZJ-\d{6}', read(fp)):
                    legacy.append(brs.rel(fp))
            except UnicodeDecodeError:
                pass
    print(f'INFO  历史文件中已有 {len(legacy)} 份含自有提交目录名 ZJ-…（2026-10 已公开，本轮不新增、不判失败）')
    sensitive_files = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [x for x in dns if x not in brs.SKIP_DIRS]
        for fn in fns:
            low = fn.lower()
            if low.endswith(('.7z', '.mkv')) or 'raw_keys' in low or 'clipboard' in low:
                sensitive_files.append(brs.rel(os.path.join(dp, fn)))
    check('仓库无原始 7z/录像/按键/剪贴板附件', not sensitive_files, str(sensitive_files[:5]))

    # 9. 治理：16 份历史入口横幅 + 禁止新建平行首读档 + 收件箱为空
    no_nav = [e for e in brs.HISTORICAL_ENTRIES
              if not os.path.isfile(p(e)) or 'START_HERE.md' not in read(p(e))]
    check('16 份历史入口都指向 START_HERE', not no_nav,
          f'{len(brs.HISTORICAL_ENTRIES)} 份' + (f' 缺横幅 {no_nav}' if no_nav else ''))
    bad_new_entry = [f for f in os.listdir(ROOT)
                     if f.endswith('.md') and re.search(r'首读|接班|入口|最新|当前', f)
                     and f not in brs.HISTORICAL_ENTRIES and f != 'START_HERE.md']
    check('根目录没有新的平行首读/入口文档', not bad_new_entry, str(bad_new_entry))
    inbox = p('备考资料库', '99_收件箱_待归档')
    stray = [brs.rel(os.path.join(dp, fn)) for dp, _, fs in os.walk(inbox) for fn in fs
             if fn != 'README.md']
    check('收件箱已清空（未分类混乱为 0）', not stray, str(stray[:5]))
    with open(p('备考资料库', '知识点掌握度.csv'), newline='', encoding='utf-8') as f:
        kn = list(csv.DictReader(f))
    check('知识点掌握度表可用', len(kn) >= 50 and
          all({'topic', 'status', 'evidence', 'tier'} <= set(r) for r in kn),
          f'{len(kn)} 个知识点 / 8 列')

    # 10. CI 触发与自检覆盖
    atlas = read(p('.github', 'workflows', 'atlas-smoke.yml'))
    integ = read(p('.github', 'workflows', 'repo-integrity.yml'))
    check('星图 CI 支持 PR 与全分支 push', 'pull_request:' in atlas and "'**'" in atlas,
          'pull_request + branches **')
    check('总控 CI 覆盖全分支、PR 与新工具自检',
          'pull_request:' in integ and "'**'" in integ and 'verify_repo.py' in integ and
          'ingest_materials.py --self-test' in integ and 'export_ai_corpus.py --self-test' in integ,
          'repo-integrity.yml')

    # 11. 双 PDF 派生解析完整性
    derived = sorted(f for f in os.listdir(p('交接', '2026-11-03_双PDF解析')) if f.endswith(('.md', '.csv')))
    with open(p('交接', '2026-11-03_双PDF解析', '08_全文主题索引.csv'), newline='', encoding='utf-8') as f:
        idx_rows = sum(1 for _ in csv.reader(f)) - 1
    check('双 PDF 派生解析齐全且索引有内容', len(derived) >= 9 and idx_rows > 300,
          f'{len(derived)} 个文件, 主题索引 {idx_rows} 行')

    # 12. 两个新工具的自检（CI 也会单独跑一次）
    self_tests = {}
    for script in ['ingest_materials.py', 'export_ai_corpus.py']:
        try:
            r = subprocess.run([sys.executable, p('tools', script), '--self-test'],
                               cwd=ROOT, capture_output=True, text=True, timeout=180)
            self_tests[script] = (r.returncode, (r.stdout or '').strip().splitlines()[-1:] or [''])
        except subprocess.TimeoutExpired:
            self_tests[script] = (1, ['TIMEOUT'])
    bad_st = [k for k, (rc, _) in self_tests.items() if rc != 0]
    check('批量写入/分片读入工具自检通过', not bad_st,
          '; '.join(f'{k}: {v[1][0][:90]}' for k, v in self_tests.items()))

    failed = [n for n, ok, _ in results if not ok]
    print('\n' + '=' * 72)
    print(f'REPO_INTEGRITY_{"PASS" if not failed else "FAIL"}  checks={len(results)}  failed={len(failed)}')
    if failed:
        print('FAILED:', ', '.join(failed))
    print('边界：结构/自洽性检查，不替代官方 OJ 回读、录像逐帧审阅或数学证明。')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
