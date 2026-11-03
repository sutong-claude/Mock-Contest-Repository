#!/usr/bin/env python3
"""超大规模读入：把全仓库文本正文按文件边界分片导出，供不具备 Agent 能力的 AI 一次吞下。

用法：
  python3 tools/export_ai_corpus.py --out 总览/AI吞入包/_导出/full.txt --max-bytes 8000000
  python3 tools/export_ai_corpus.py --out /tmp/ctrl.jsonl --format jsonl \
      --categories 控制层,NOIP备考控制层,NOIP备考资料库,AI吞入包
  python3 tools/export_ai_corpus.py --self-test

特性：
  - 文件边界分片：绝不把一个文件切成两半；每个分片写 chunks.json 便于随机访问；
  - 全部文本带 path / sha256 / category / read_priority 头，可回查；
  - 默认跳过二进制（9 个 PDF/ZIP/MP4/DOCX）与 >2 MB 的单文件；
  - 输出目录 _导出/ 已 gitignore，不进版本库、不污染索引哈希；
  - 自检不写仓库。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_repo_state as brs  # noqa: E402

DEFAULT_OUT = os.path.join(ROOT, '总览', 'AI吞入包', '_导出', '全仓库正文.txt')
MAX_SINGLE_FILE = 2 * 1024 * 1024


def collect(categories=None):
    """复用 build_repo_state.inventory() 的单一清单，再补上 7 个生成物。"""
    items = [dict(x) for x in brs.inventory()]
    for g in sorted(brs.GENERATED):
        p = os.path.join(ROOT, g)
        if os.path.isfile(p):
            items.append({'path': g, 'bytes': os.path.getsize(p), 'sha256': brs.sha256(p),
                          'category': 'AI吞入包/生成物', 'read_priority': 1,
                          'encoding': 'utf8', 'title': '', 'summary': '',
                          'headings': [], 'flags': ['GENERATED']})
    if categories:
        wanted = set(categories.split(','))
        # 生成物类别用前缀匹配，方便 --categories AI吞入包 一并选中
        items = [x for x in items if x['category'] in wanted
                 or any(x['category'].startswith(w + '/') for w in wanted)]
    items.sort(key=lambda x: (x['read_priority'], x['path']))
    return items


def header(x):
    return (f"\n===== FILE: {x['path']} | bytes={x['bytes']} | sha256={x['sha256']} | "
            f"category={x['category']} | priority={x['read_priority']} =====\n")


def render_txt(items, max_bytes):
    """返回 [(suffix, text, [paths])]；按文件边界分片。"""
    chunks, cur, cur_paths = [], [], []
    cur_bytes = 0
    skipped = []
    for x in items:
        p = os.path.join(ROOT, x['path'])
        if x['encoding'] != 'utf8':
            skipped.append((x['path'], 'binary'))
            continue
        if x['bytes'] > MAX_SINGLE_FILE:
            skipped.append((x['path'], 'too_large'))
            continue
        try:
            body = open(p, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            skipped.append((x['path'], 'decode_error'))
            continue
        block = header(x) + body + f"\n===== END: {x['path']} =====\n"
        b = len(block.encode('utf-8'))
        if cur and cur_bytes + b > max_bytes:
            chunks.append((''.join(cur), cur_paths))
            cur, cur_paths, cur_bytes = [], [], 0
        # 单文件超限时单独成片（仍不切断文件）
        cur.append(block)
        cur_paths.append(x['path'])
        cur_bytes += b
    if cur:
        chunks.append((''.join(cur), cur_paths))
    return chunks, skipped


def render_jsonl(items):
    out, skipped = [], []
    for x in items:
        p = os.path.join(ROOT, x['path'])
        if x['encoding'] != 'utf8' or x['bytes'] > MAX_SINGLE_FILE:
            skipped.append((x['path'], 'binary_or_large'))
            continue
        try:
            text = open(p, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            skipped.append((x['path'], 'decode_error'))
            continue
        out.append(json.dumps({'path': x['path'], 'sha256': x['sha256'],
                               'category': x['category'], 'read_priority': x['read_priority'],
                               'text': text}, ensure_ascii=False))
    return out, skipped


def write_chunks(out_path, payloads, suffix='.txt'):
    base, ext = os.path.splitext(out_path)
    ext = ext or suffix
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    manifest = []
    for i, (text, paths) in enumerate(payloads):
        path = f'{base}_{i:03d}{ext}' if len(payloads) > 1 else f'{base}{ext}'
        data = text.encode('utf-8')
        with open(path, 'wb') as f:
            f.write(data)
        manifest.append({'chunk': os.path.basename(path), 'bytes': len(data),
                         'sha256': hashlib.sha256(data).hexdigest(),
                         'files': len(paths), 'first': paths[0] if paths else '',
                         'last': paths[-1] if paths else ''})
    mpath = os.path.join(os.path.dirname(out_path), 'chunks.json')
    with open(mpath, 'w', encoding='utf-8') as f:
        json.dump({'schema': 'mock-contest-repository.corpus-export.v1',
                   'out': os.path.basename(out_path), 'chunk_count': len(manifest),
                   'chunks': manifest}, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return manifest


def export(out_path, max_bytes, categories, fmt):
    items = collect(categories)
    if fmt == 'jsonl':
        lines, skipped = render_jsonl(items)
        # jsonl 也按字节分片，每行一条记录，不拆行
        payloads, cur, cur_paths, cur_bytes = [], [], [], 0
        for l in lines:
            b = len((l + '\n').encode('utf-8'))
            if cur and cur_bytes + b > max_bytes:
                payloads.append(('\n'.join(cur) + '\n', cur_paths))
                cur, cur_paths, cur_bytes = [], [], 0
            cur.append(l)
            cur_paths.append(json.loads(l)['path'])
            cur_bytes += b
        if cur:
            payloads.append(('\n'.join(cur) + '\n', cur_paths))
    else:
        payloads, skipped = render_txt(items, max_bytes)
    manifest = write_chunks(out_path, payloads, suffix='.jsonl' if fmt == 'jsonl' else '.txt')
    return dict(source_files=len(items), exported_files=sum(c['files'] for c in manifest),
                skipped=len(skipped), chunks=len(manifest),
                max_chunk_bytes=max((c['bytes'] for c in manifest), default=0),
                categories_sorted=sorted({x['category'] for x in items}),
                skipped_detail=skipped[:8])


def self_test():
    tmp = tempfile.mkdtemp(prefix='export-selftest-')
    try:
        out = os.path.join(tmp, 'corpus.txt')
        r = export(out, 40000, '控制层,NOIP备考控制层,NOIP备考资料库,AI吞入包', 'txt')
        assert r['chunks'] >= 2, r
        assert r['max_chunk_bytes'] <= 40000 + MAX_SINGLE_FILE, r
        assert r['exported_files'] == r['source_files'] - r['skipped'], r
        m = json.load(open(os.path.join(tmp, 'chunks.json'), encoding='utf-8'))
        assert m['chunk_count'] == len(m['chunks']) == r['chunks']
        for c in m['chunks']:
            data = open(os.path.join(tmp, c['chunk']), 'rb').read()
            assert len(data) == c['bytes']
            assert hashlib.sha256(data).hexdigest() == c['sha256']
            assert '===== FILE:' in data.decode('utf-8')
        out2 = os.path.join(tmp, 'sub', 'corpus.jsonl')
        r2 = export(out2, 40000, '控制层', 'jsonl')
        assert r2['chunks'] >= 1 and r2['exported_files'] > 0, r2
        m2 = json.load(open(os.path.join(tmp, 'sub', 'chunks.json'), encoding='utf-8'))
        for c in m2['chunks']:
            for line in open(os.path.join(tmp, 'sub', c['chunk']), encoding='utf-8'):
                rec = json.loads(line)
                assert rec['sha256'] and 'text' in rec
        # 确定性：同参数再导一次，分片 SHA 列表完全相同
        before = [c['sha256'] for c in m['chunks']]
        r3 = export(out, 40000, '控制层,NOIP备考控制层,NOIP备考资料库,AI吞入包', 'txt')
        after = [c['sha256'] for c in json.load(open(os.path.join(tmp, 'chunks.json'), encoding='utf-8'))['chunks']]
        assert before == after, '同参数导出不确定'
        assert r3['max_chunk_bytes'] == r['max_chunk_bytes']
        print(f'EXPORT_SELFTEST_PASS  source={r["source_files"]} exported={r["exported_files"]} '
              f'skipped_binary={r["skipped"]} chunks={r["chunks"]} '
              f'max_chunk={r["max_chunk_bytes"]} deterministic=True jsonl_ok=True')
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description='按文件边界分片导出全仓库文本正文')
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--max-bytes', type=int, default=8_000_000, help='每分片上限（不切断文件）')
    ap.add_argument('--categories', default='', help='逗号分隔的分类过滤；空=全部')
    ap.add_argument('--format', choices=['txt', 'jsonl'], default='txt')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.max_bytes < 1000:
        ap.error('--max-bytes 至少 1000')
    r = export(args.out, args.max_bytes, args.categories, args.format)
    print('EXPORT ' + json.dumps({k: v for k, v in r.items() if k != 'categories_sorted'}, ensure_ascii=False))
    print('CATEGORIES ' + ','.join(r['categories_sorted']))
    print(f'MANIFEST {os.path.join(os.path.dirname(args.out), "chunks.json")}')
    print('边界：导出内容只代表仓库里写了什么；[G]/ESTIMATE 不是成绩，LOCAL-VERIFIED ≠ OJ-AC。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
