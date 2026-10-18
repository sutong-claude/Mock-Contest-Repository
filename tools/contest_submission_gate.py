#!/usr/bin/env python3
"""OI file-IO submission gate: compile exact source, independently smoke, freeze by SHA.

No oracle fabrication, no score inference. Never touches the original source.
Usage: python3 tools/contest_submission_gate.py --manifest path.json --workspace DIR --freeze DIR
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(manifest, workspace, freeze_dir=None):
    workspace = Path(workspace).resolve()
    tests = json.loads(Path(manifest).read_text(encoding='utf-8'))['tasks']
    report = {'schema_version': 1, 'success': True, 'tasks': []}
    frozen_candidates = []
    with tempfile.TemporaryDirectory(prefix='oi-gate-') as scratch:
        for task in tests:
            name = task['name']
            src = workspace / task.get('source', name + '.cpp')
            cases = task['cases']
            record = {'task': name, 'source': task.get('source', name + '.cpp'), 'sha256': None,
                      'compiled': False, 'tests_passed': 0, 'tests_total': len(cases), 'failures': []}
            report['tasks'].append(record)
            if not src.is_file():
                record['failures'].append('SOURCE_MISSING')
                report['success'] = False
                continue
            record['sha256'] = sha256(src)
            wd = Path(scratch) / name
            wd.mkdir()
            binary = wd / 'solution'
            cmd = ['g++', '-O2', '-std=c++17', '-static', '-s', str(src), '-o', str(binary)]
            comp = subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=False)
            if comp.returncode:
                record['failures'].append('COMPILE_ERROR: ' + comp.stderr[:600])
                report['success'] = False
                continue
            record['compiled'] = True
            for i, case in enumerate(cases):
                (wd / (name + '.in')).write_text(case['input'], encoding='utf-8')
                outfile = wd / (name + '.out')
                outfile.unlink(missing_ok=True)
                try:
                    p = subprocess.run([str(binary)], cwd=wd, capture_output=True,
                                       text=True, timeout=case.get('timeout', 3))
                    if p.returncode:
                        raise RuntimeError('EXIT_CODE ' + str(p.returncode))
                    if not outfile.exists():
                        raise RuntimeError('OUTPUT_MISSING')
                    actual = outfile.read_text(encoding='utf-8').split()
                    expected = case['expected'].split()
                    if actual != expected:
                        raise RuntimeError('WRONG_ANSWER expected=' + str(expected[:15]) +
                                           ' actual=' + str(actual[:15]))
                    record['tests_passed'] += 1
                except (RuntimeError, subprocess.TimeoutExpired, UnicodeDecodeError) as e:
                    record['failures'].append({'case': case.get('label', i), 'error': str(e)[:280]})
                    report['success'] = False
            if not record['failures']:
                frozen_candidates.append((name, src, record['sha256']))
    # Transactional: if any task fails, freeze NONE. No passing-claim from partial suite.
    if freeze_dir and report['success']:
        target = Path(freeze_dir)
        target.mkdir(parents=True, exist_ok=True)
        for name, src, digest in frozen_candidates:
            if sha256(src) != digest:
                report['success'] = False
                report['error'] = 'SOURCE_CHANGED_DURING_VALIDATION'
                break
        if report['success']:
            for name, src, digest in frozen_candidates:
                tmp = target / (name + '.cpp.tmp')
                shutil.copyfile(src, tmp)
                tmp.replace(target / (name + '.cpp'))
            (target / 'freeze_manifest.json').write_text(json.dumps({
                'status': 'VERIFIED_NOT_OJ_SCORED',
                'source_hashes': {n: h for n, _, h in frozen_candidates},
                'tests_passed': {v['task']: v['tests_passed'] for v in report['tasks']},
            }, ensure_ascii=False, indent=2), encoding='utf-8')
            report['frozen'] = True
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--workspace', required=True)
    ap.add_argument('--freeze', help='freeze verified sources only if ALL tasks pass')
    ap.add_argument('--report', help='write JSON results')
    args = ap.parse_args()
    result = run(args.manifest, args.workspace, args.freeze)
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(output+'\n', encoding='utf-8')
    print(output)
    raise SystemExit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
