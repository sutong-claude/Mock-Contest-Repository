#!/usr/bin/env python3
"""Reproduce the 2026-10-22 CodeLands3 source/fixture archaeology.

Example:
  python verify_codelands3_contest.py \
    --source-root '/path/to/Desktop/ZJ-XXXXXX' \
    --samples-root '/path/to/Desktop/20261019 CSP-S复赛 模拟赛（NOI金牌命题）'

Runs the exact source files in *isolated temp directories*, never editing originals.
A clean historical baseline is NOT equivalent to OJ AC; this baseline expects C failures.
"""
import argparse
import json
import subprocess
import tempfile
import time
from pathlib import Path

EXPECTED_BASELINE = {
    'step': {i: True for i in range(1,7)},
    'alien': {i: True for i in range(1,8)},
    'maxcover': {i: i not in (5, 8) for i in range(1,9)},
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--samples-root', type=Path, required=True)
    parser.add_argument('--timeout',type=int,default=15)
    parser.add_argument('--save-json',type=Path)
    args=parser.parse_args()
    results=[]
    with tempfile.TemporaryDirectory(prefix='codelands3-verify-') as tmp:
        root=Path(tmp)
        for name,expected_cases in EXPECTED_BASELINE.items():
            source=args.source_root/name/(name+'.cpp')
            exe=root/(name+'.exe')
            subprocess.run(['g++','-O2','-std=c++17',str(source),'-o',str(exe)],check=True,timeout=60)
            for index,expected_pass in expected_cases.items():
                case_name=f'{name}{index}'
                fixture=args.samples_root/name/(case_name+'.in')
                answer=args.samples_root/name/(case_name+'.ans')
                if not fixture.is_file() or not answer.is_file():
                    raise FileNotFoundError(f'Missing fixture: {fixture} or {answer}')
                run_dir=root/(case_name+'-run')
                run_dir.mkdir()
                (run_dir/(name+'.in')).symlink_to(fixture.resolve())
                start=time.perf_counter()
                try:
                    proc=subprocess.run([str(exe)],cwd=run_dir,capture_output=True,timeout=args.timeout)
                    out_file=run_dir/(name+'.out')
                    actual=out_file.read_text(encoding='utf-8').strip() if out_file.is_file() else '<NO_OUTPUT>'
                    expect=answer.read_text(encoding='utf-8').strip()
                    passed=(proc.returncode==0 and actual==expect)
                    detail={'test':case_name,'passed':passed,'expected_baseline':expected_pass,'actual':actual[:160],
                            'expected':expect[:160],'elapsed_seconds':round(time.perf_counter()-start,3),
                            'exit_code':proc.returncode}
                except subprocess.TimeoutExpired:
                    detail={'test':case_name,'passed':False,'expected_baseline':expected_pass,
                            'actual':'<TIMEOUT>','expected':answer.read_text().strip()[:160],
                            'elapsed_seconds':args.timeout,'exit_code':None}
                results.append(detail)
                print(case_name,'PASS' if detail['passed'] else 'FAIL',detail['elapsed_seconds'],'s')
        name='maxcover'
        exe=root/(name+'.exe')
        hacks={
            'maxcover-special-n21': ([0]*21,[-1,1]+[0]*19,21),
            'maxcover-gap-n21': ([0]*5+[-1]*5+[0]*11,[0]*5+[-1]*5+[0]*11,16),
        }
        for case_name,(a,b,expected) in hacks.items():
            tdir=root/case_name
            tdir.mkdir()
            (tdir/'maxcover.in').write_text('21\n'+' '.join(map(str,a))+'\n'+' '.join(map(str,b))+'\n')
            proc=subprocess.run([str(exe)],cwd=tdir,timeout=args.timeout,check=True)
            actual=int((tdir/'maxcover.out').read_text().strip())
            results.append({'test':case_name,'passed':actual==expected,'expected_baseline':False,
                            'actual':actual,'expected':expected,'exit_code':proc.returncode})
            print(case_name,'PASS' if actual==expected else 'FAIL',f'{actual} vs {expected}')
    ok=sum(r['passed'] for r in results if r['test'].split('-')[0] not in ('maxcover',) or '-n21' not in r['test'])
    baseline_match=all(r['passed']==r['expected_baseline'] for r in results)
    report={'baseline_match':baseline_match,'cases':results}
    print(json.dumps({'fixture_tests':21,'fixture_passed':sum(r['passed'] for r in results[:21]),
                      'fixture_failed':sum(not r['passed'] for r in results[:21]),
                      'known_hack_failures':sum(not r['passed'] for r in results[21:]),
                      'baseline_match':baseline_match},ensure_ascii=False))
    if args.save_json:
        args.save_json.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if baseline_match else 1)

if __name__=='__main__':main()
