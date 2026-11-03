#!/usr/bin/env python3
"""超大规模批量写入：把新材料按类别导入 备考资料库/，幂等、脱敏、可复算。

用法：
  python3 tools/ingest_materials.py --src <目录> --dry-run     # 只看计划，不写文件
  python3 tools/ingest_materials.py --src <目录>               # 正式导入（默认重建索引）
  python3 tools/ingest_materials.py --self-test                # 200+ 文件自检，不碰仓库

设计目标（对应「支持超大规模写入」）：
  - 流式遍历，按 SHA-256 去重，重复运行是幂等的；
  - 文件名规范化、按内容/名称路由到 8 个类别；
  - 隐私与原始附件硬拦截，只报文件名与命中类型，不打印内容；
  - 每次导入写 append-only 的 INGEST_LOG.jsonl；
  - 全部决定可复算：--dry-run 输出与正式导入一致。
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))

DEFAULT_DEST = os.path.join(ROOT, '备考资料库')
CATEGORIES = [
    ('01_大纲与路线', ('大纲', '路线', '知识点', 'syllabus', 'roadmap')),
    ('02_模板与代码', ('模板', '板子', 'template', 'board', 'snippet')),
    ('03_题单与题解', ('题解', '题单', 'solution', 'editorial', 'problem')),
    ('04_模拟赛与成绩', ('模拟赛', '成绩', 'score', 'contest', 'vp', '得分矩阵')),
    ('05_课程与讲义', ('课程', '讲义', 'lecture', 'lesson', '动画', '讲义')),
    ('06_复盘与错因', ('复盘', '错因', '状态机', '病因', 'review', 'postmortem')),
    ('07_考场SOP', ('执行卡', 'sop', '试机', '赛前', '封盘', 'checklist')),
    ('08_证据与来源', ('证据', '原始材料', '一手', 'evidence', 'manifest', 'index')),
]

# 真正会泄露的片段（中文描述词不算命中，见 verify_repo.py 的教训）
FORBIDDEN = re.compile(
    r'苏潼|@gmail\.com|bce-auth|pplines-online|MX0INOIP|E:\\[^\s]{4,}|'
    r'(?:token|access_key|Authorization|密码|邀请码)\s*[:：=]\s*\S{6,}', re.I)
# 文件名黑名单（原始附件、按键、剪贴板、账号页、OCR 原文）
BAD_NAME = re.compile(
    r'(\.7z$|\.mkv$|raw_keys|clipboard|账号页|未脱敏|private|'
    r'pdf_by_PaddleOCR|OCR原文|聊天全文|screen_\d+\.(png|jpg)$)', re.I)
TEXT_EXT = {'.md', '.txt', '.csv', '.json', '.jsonl', '.tsv', '.py', '.cpp', '.h',
            '.hpp', '.sh', '.mjs', '.js', '.yml', '.yaml', '.svg', '.html', '.in', '.out'}
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', '_导出', '.cache'}
MAX_FILE_BYTES = 5 * 1024 * 1024


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def slug(name):
    stem = os.path.splitext(os.path.basename(name))[0]
    stem = re.sub(r'[\s()（）\[\]{}#&+（）,，。;；:：/\\]+', '_', stem)
    stem = re.sub(r'_+', '_', stem).strip('_')
    return (stem or 'material')[:60]


def classify(fname, text):
    low = fname.lower()
    for cat, kws in CATEGORIES:
        if any(k in low for k in kws):
            return cat
    head = text[:2000]
    for cat, kws in CATEGORIES:
        if any(k in head for k in kws):
            return cat
    ext = os.path.splitext(fname)[1].lower()
    if ext in {'.cpp', '.h', '.hpp', '.py', '.sh', '.mjs', '.js'}:
        return '02_模板与代码'
    if ext in {'.csv', '.json', '.jsonl', '.tsv'}:
        return '08_证据与来源'
    return '08_证据与来源'  # 兜底：证据/来源，绝不丢进收件箱造成混乱


def existing_shas(dest):
    out = set()
    for dp, dns, fns in os.walk(dest):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                with open(p, 'rb') as f:
                    out.add(sha256_bytes(f.read()))
            except OSError:
                pass
    return out


def plan(src, dest, limit, date):
    """返回 (actions, stats)，不写任何文件。"""
    actions, stats = [], {'scanned': 0, 'import': 0, 'duplicate': 0,
                          'reject_privacy': 0, 'reject_name': 0,
                          'reject_size': 0, 'reject_binary': 0}
    seen = existing_shas(dest)
    for dp, dns, fns in os.walk(src):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in sorted(fns):
            if fn in {'README.md', 'INGEST_LOG.jsonl', '.DS_Store'}:
                continue
            p = os.path.join(dp, fn)
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            stats['scanned'] += 1
            if limit and stats['import'] >= limit:
                break
            if BAD_NAME.search(fn):
                stats['reject_name'] += 1
                actions.append(('REJECT_NAME', fn, '原始附件/未脱敏命名'))
                continue
            size = os.path.getsize(p)
            if size > MAX_FILE_BYTES:
                stats['reject_size'] += 1
                actions.append(('REJECT_SIZE', fn, f'{size} B > 5 MB'))
                continue
            with open(p, 'rb') as f:
                raw = f.read()
            h = sha256_bytes(raw)
            if h in seen:
                stats['duplicate'] += 1
                actions.append(('DUPLICATE', fn, h[:12]))
                continue
            ext = os.path.splitext(fn)[1].lower()
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                if ext in TEXT_EXT or size > 200_000:
                    stats['reject_binary'] += 1
                    actions.append(('REJECT_BINARY', fn, '非 UTF-8 且非允许的小素材'))
                    continue
                text = ''
            m = FORBIDDEN.search(text) or FORBIDDEN.search(fn)
            if m:
                stats['reject_privacy'] += 1
                actions.append(('REJECT_PRIVACY', fn, '敏感片段（内容不打印）'))
                continue
            cat = classify(fn, text)
            target_name = f'{date}_{slug(fn)}{ext or ".txt"}'
            seen.add(h)
            stats['import'] += 1
            actions.append(('IMPORT', fn, f'{cat}/{target_name}', p, h, size, cat))
        if limit and stats['import'] >= limit:
            break
    return actions, stats


def execute(actions, dest, date, rebuild):
    os.makedirs(dest, exist_ok=True)
    log_path = os.path.join(dest, 'INGEST_LOG.jsonl')
    written = 0
    with open(log_path, 'a', encoding='utf-8') as log:
        for a in actions:
            if a[0] != 'IMPORT':
                continue
            _, src_name, rel_target, src_path, h, size, cat = a
            target = os.path.join(dest, rel_target)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            n = 2
            while os.path.exists(target):
                stem, ext = os.path.splitext(rel_target)
                target = os.path.join(dest, f'{stem}-{n}{ext}')
                n += 1
            shutil.copyfile(src_path, target)
            written += 1
            log.write(json.dumps({
                'date': date, 'src_name': src_name,
                'dest': os.path.relpath(target, dest).replace(os.sep, '/'),
                'sha256': h, 'bytes': size, 'category': cat,
            }, ensure_ascii=False) + '\n')
    if rebuild and os.path.commonpath([os.path.abspath(dest), ROOT]) == ROOT:
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_repo_state.py')],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        print('REBUILT 索引（build_repo_state.py）')
    return written


def self_test():
    tmp = tempfile.mkdtemp(prefix='ingest-selftest-')
    src, dest = os.path.join(tmp, 'src'), os.path.join(tmp, 'dest')
    os.makedirs(src)
    try:
        for i in range(200):
            ext = ['.md', '.cpp', '.txt', '.json'][i % 4]
            body = f'# 材料 {i}\n\n> 日期：2026-11-03｜等级：[G]\n\n内容 {i} 用于自检。\n'
            with open(os.path.join(src, f'material_{i:03d}{ext}'), 'w', encoding='utf-8') as f:
                f.write(body)
        with open(os.path.join(src, 'dup_copy.md'), 'w', encoding='utf-8') as f:
            f.write('# 材料 0\n\n> 日期：2026-11-03｜等级：[G]\n\n内容 0 用于自检。\n')
        with open(os.path.join(src, 'secret_note.md'), 'w', encoding='utf-8') as f:
            f.write('# 私密\n\n密码：abcdef123456\n')
        with open(os.path.join(src, 'raw_capture.mkv'), 'wb') as f:
            f.write(b'\x00\x01')
        with open(os.path.join(src, 'huge.bin'), 'wb') as f:
            f.write(b'x' * (MAX_FILE_BYTES + 1))
        a1, s1 = plan(src, dest, 0, '2026-11-03')
        assert s1['import'] == 200, s1
        assert s1['duplicate'] == 1, s1
        assert s1['reject_privacy'] == 1, s1
        assert s1['reject_name'] == 1, s1
        assert s1['reject_size'] == 1, s1
        dry_actions, dry_stats = plan(src, dest, 0, '2026-11-03')
        assert [x[:3] for x in dry_actions] == [x[:3] for x in a1], 'dry-run 与正式计划不一致'
        w = execute(a1, dest, '2026-11-03', rebuild=False)
        assert w == 200, w
        files = [os.path.join(dp, f) for dp, _, fs in os.walk(dest) for f in fs
                 if f != 'INGEST_LOG.jsonl']
        assert len(files) == 200, len(files)
        a2, s2 = plan(src, dest, 0, '2026-11-03')
        assert s2['import'] == 0 and s2['duplicate'] == 201, s2
        with open(os.path.join(dest, 'INGEST_LOG.jsonl'), encoding='utf-8') as f:
            assert sum(1 for l in f if l.strip()) == 200
        print(f'INGEST_SELFTEST_PASS  scanned={s1["scanned"]} imported=200 '
              f'dup={s1["duplicate"]} privacy_reject={s1["reject_privacy"]} '
              f'name_reject={s1["reject_name"]} size_reject={s1["reject_size"]} '
              f'rerun_import={s2["import"]} idempotent=True')
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description='批量导入备考资料（幂等 / 脱敏 / 可复算）')
    ap.add_argument('--src', help='新材料目录')
    ap.add_argument('--dest', default=DEFAULT_DEST, help='导入目标（默认 备考资料库/）')
    ap.add_argument('--date', default=datetime.date.today().isoformat(), help='命名用日期 YYYY-MM-DD')
    ap.add_argument('--limit', type=int, default=0, help='最多导入 N 个（0=不限）')
    ap.add_argument('--dry-run', action='store_true', help='只打印计划，不写文件')
    ap.add_argument('--no-rebuild', action='store_true', help='导入后不重建索引')
    ap.add_argument('--self-test', action='store_true', help='自检，不写仓库')
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.src or not os.path.isdir(args.src):
        ap.error('--src 必须是存在的目录（或使用 --self-test）')
    os.makedirs(args.dest, exist_ok=True)
    actions, stats = plan(args.src, args.dest, args.limit, args.date)
    for a in actions[:25]:
        print('  ' + ' | '.join(str(x) for x in a[:3]))
    if len(actions) > 25:
        print(f'  … 其余 {len(actions) - 25} 条省略（完整决定可复算）')
    print('PLAN ' + json.dumps(stats, ensure_ascii=False))
    if args.dry_run:
        print('DRY_RUN：未写入任何文件')
        return 0
    written = execute(actions, args.dest, args.date, rebuild=not args.no_rebuild)
    print(f'IMPORTED {written} 个文件 → {args.dest}')
    print('NEXT: python3 tools/verify_repo.py → 维护日志.md 追加一行 → 提交真实 SHA')
    return 0


if __name__ == '__main__':
    sys.exit(main())
