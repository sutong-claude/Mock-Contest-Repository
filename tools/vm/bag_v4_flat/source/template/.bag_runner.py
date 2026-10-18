#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, re, resource, shutil, subprocess, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
BIN=HERE/'.bag_bin'
BIN.mkdir(exist_ok=True)
BASE=['-std=c++17','-O2','-Wall','-Wextra']
SAN=['-std=c++17','-O1','-g','-Wall','-Wextra','-fsanitize=address,undefined','-fno-omit-frame-pointer']
IGNORE_INPUT_PREFIXES=('.bag_',)

def run(cmd,**kw): return subprocess.run(cmd,**kw)

def strip_freopen(src:Path)->Path:
    text=src.read_text(encoding='utf-8',errors='replace').splitlines(True)
    pat=re.compile(r'(?:std::)?freopen\s*\([^;]*\)\s*;')
    out=[]
    for line in text:
        if line.lstrip().startswith('//'): out.append(line)
        else: out.append(pat.sub('/* [bag disabled freopen] */',line))
    p=BIN/(src.stem+'_stdin.cpp')
    p.write_text(''.join(out),encoding='utf-8')
    return p

def compile_src(src:Path,out:Path,flags,disable_freopen=False):
    s=strip_freopen(src) if disable_freopen else src
    out.unlink(missing_ok=True)
    p=run(['g++',str(s),*flags,'-o',str(out)],cwd=HERE)
    if p.returncode:
        print(f'CE: {src.name}')
        return False
    return True

def active_freopen(src:Path):
    ans=[]
    for line in src.read_text(encoding='utf-8',errors='replace').splitlines():
        if line.lstrip().startswith('//'): continue
        for m in re.finditer(r'(?:std::)?freopen\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"',line):
            ans.append((m.group(1),m.group(2)))
    return ans

def expected(inp:Path):
    for ext in ['.out','.ans','.answer','.OUT','.ANS','.ANSWER']:
        p=inp.with_suffix(ext)
        if p.exists(): return p
    return None

def token_iter(p:Path):
    with p.open('r',encoding='utf-8',errors='replace') as f:
        for line in f:
            yield from line.split()

def token_diff(a:Path,b:Path):
    ia,ib=token_iter(a),token_iter(b)
    n=0
    while True:
        try: x=next(ia); ax=True
        except StopIteration: x=None; ax=False
        try: y=next(ib); by=True
        except StopIteration: y=None; by=False
        if not ax and not by: return None
        n+=1
        if ax!=by or x!=y: return n,x,y

def flat_inputs():
    arr=[]
    for p in HERE.glob('*.in'):
        if p.name.startswith(IGNORE_INPUT_PREFIXES): continue
        arr.append(p)
    return sorted(arr,key=lambda p:p.name.lower())

def warn_nested():
    nested=[]
    for p in HERE.rglob('*.in'):
        if p.parent!=HERE and '.bag_bin' not in p.parts:
            nested.append(p)
    if nested:
        print('FLAT RULE: found .in below subfolders. This BAG only tests files placed directly in this T folder.')
        for p in nested[:8]: print('  nested:',p.relative_to(HERE))
        if len(nested)>8: print(f'  ... +{len(nested)-8} more')

def one_run(exe:Path,inp:Path,timeout:float,got:Path,err:Path):
    got.unlink(missing_ok=True)
    err.unlink(missing_ok=True)
    try:
        with inp.open('rb') as fi,got.open('wb') as fo,err.open('wb') as fe:
            p=run([str(exe)],cwd=HERE,stdin=fi,stdout=fo,stderr=fe,timeout=timeout)
        return ('OK' if p.returncode==0 else f'RE({p.returncode})',time.perf_counter())
    except subprocess.TimeoutExpired:
        return ('TLE',time.perf_counter())

def sample_mode(args,sanitize=False,only=None,final=False):
    flags=SAN if sanitize else BASE
    exact=BIN/('main_exact_san' if sanitize else 'main_exact')
    if not compile_src(HERE/'main.cpp',exact,flags,False): return 2
    af=active_freopen(HERE/'main.cpp')
    test=exact
    if af:
        test=BIN/('main_stdin_san' if sanitize else 'main_stdin')
        if not compile_src(HERE/'main.cpp',test,flags,True): return 2
    warn_nested()
    ins=flat_inputs()
    if only:
        p=HERE/only
        if not p.exists():
            print('NO SUCH INPUT:',only)
            return 2
        ins=[p]
    if not ins:
        print('NO TESTS: unzip/copy *.in + matching *.out/.ans DIRECTLY into this T folder.')
        return 2
    fail=0
    passed=0
    run_only=0
    first_pair=None
    for i,inp in enumerate(ins,1):
        exp=expected(inp)
        got=BIN/'last.out'
        err=BIN/'last.err'
        t0=time.perf_counter()
        status,_=one_run(test,inp,args.timeout,got,err)
        dt=time.perf_counter()-t0
        if status!='OK':
            print(f'[{i:03d}] {status:8} {inp.name} {dt:.3f}s')
            fail+=1
            continue
        if exp is None or args.mode=='none':
            print(f'[{i:03d}] RUN      {inp.name} {dt:.3f}s' + (' (no answer file)' if exp is None else ' (compare off)'))
            run_only+=1
        else:
            d=token_diff(got,exp)
            if d:
                n,x,y=d
                print(f'[{i:03d}] WA       {inp.name} token#{n}: got={x!r} expected={y!r} {dt:.3f}s')
                fail+=1
            else:
                print(f'[{i:03d}] OK       {inp.name} {dt:.3f}s')
                passed+=1
                if first_pair is None: first_pair=(inp,exp)
    print(f'SUMMARY: pass={passed} fail={fail} run_only={run_only} tests={len(ins)}' + (' SANITIZE' if sanitize else ''))
    if final and af and first_pair:
        inspec=[x for x in af if 'r' in x[1]]
        outspec=[x for x in af if any(c in x[1] for c in 'wa')]
        if not inspec or not outspec:
            print('FILEIO: BAD_FREOPEN')
            return 1
        import tempfile
        with tempfile.TemporaryDirectory(prefix='bag_fileio_') as td0:
            td=Path(td0)
            inname=inspec[0][0]
            outname=outspec[0][0]
            (td/inname).parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(first_pair[0],td/inname)
            (td/outname).parent.mkdir(parents=True,exist_ok=True)
            try:
                p=run([str(exact)],cwd=td,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=args.timeout)
            except subprocess.TimeoutExpired:
                print('FILEIO: TLE')
                return 1
            gp=td/outname
            if p.returncode!=0:
                print('FILEIO: RE',p.returncode)
                return 1
            if not gp.exists():
                print('FILEIO: NO_OUTPUT_FILE')
                return 1
            if args.mode!='none' and token_diff(gp,first_pair[1]):
                print('FILEIO: WA')
                return 1
            print('FILEIO: OK')
    return 0 if fail==0 else 1

def preexec_memory(mb):
    if mb<=0:return None
    lim=mb*1024*1024
    def f(): resource.setrlimit(resource.RLIMIT_AS,(lim,lim))
    return f

def proc_bytes(exe,inp,timeout,env=None,memory_mb=0):
    try:
        return run([str(exe)],cwd=HERE,input=inp,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,env=env,preexec_fn=preexec_memory(memory_mb))
    except subprocess.TimeoutExpired:
        return None

def next_debug_name():
    for i in range(1,10000):
        stem=f'debug_{i:03d}'
        if not (HERE/(stem+'.in')).exists(): return stem
    return 'debug_'+str(int(time.time()))

def save_counterexample(inp,exp,got,me,ae,kind,seed):
    stem=next_debug_name()
    (HERE/(stem+'.in')).write_bytes(inp)
    (HERE/(stem+'.out')).write_bytes(exp or b'')
    (HERE/(stem+'.got')).write_bytes(got or b'')
    if me: (HERE/(stem+'.main.err')).write_bytes(me)
    if ae: (HERE/(stem+'.WA.err')).write_bytes(ae)
    (HERE/(stem+'.txt')).write_text(f'kind={kind}\nseed={seed}\n',encoding='utf-8')
    print(f'COUNTEREXAMPLE -> {stem}.in / {stem}.out (now it is automatically a normal sample too)')
    return stem

def stress_mode(args,count):
    for src in ['main.cpp','WA.cpp','gen.cpp']:
        if not (HERE/src).exists():
            print('MISSING:',src)
            return 2
    if not compile_src(HERE/'main.cpp',BIN/'stress_main',BASE,True): return 2
    if not compile_src(HERE/'WA.cpp',BIN/'stress_WA',BASE,True): return 2
    if not compile_src(HERE/'gen.cpp',BIN/'stress_gen',BASE,True): return 2
    if (HERE/'main.cpp').read_bytes()==(HERE/'WA.cpp').read_bytes():
        print('WARN: main.cpp and WA.cpp are byte-identical; oracle is not independent.')
    t0=time.perf_counter()
    i=1
    while count<=0 or i<=count:
        seed=args.seed+i
        env=os.environ.copy()
        env['SEED']=str(seed)
        env['TEST_ID']=str(i)
        g=proc_bytes(BIN/'stress_gen',b'',args.timeout,env,args.memory)
        if g is None:
            print('GEN TLE',i)
            return 2
        if g.returncode!=0:
            print('GEN RE',i,g.stderr.decode(errors='replace')[:1000])
            return 2
        inp=g.stdout
        if not inp.strip():
            print('GEN EMPTY: write gen.cpp first; refusing fake green.')
            return 2
        a=proc_bytes(BIN/'stress_WA',inp,args.timeout,memory_mb=args.memory)
        if a is None:
            save_counterexample(inp,b'',b'',b'',b'','WA_TLE',seed)
            print('WA/oracle TLE',i)
            return 3
        if a.returncode!=0:
            save_counterexample(inp,a.stdout,b'',b'',a.stderr,'WA_RE',seed)
            print('WA/oracle RE',i)
            return 3
        m=proc_bytes(BIN/'stress_main',inp,args.timeout,memory_mb=args.memory)
        if m is None:
            save_counterexample(inp,a.stdout,b'',b'',b'','MAIN_TLE',seed)
            print('MAIN TLE',i)
            return 4
        if m.returncode!=0:
            save_counterexample(inp,a.stdout,m.stdout,m.stderr,a.stderr,'MAIN_RE',seed)
            print('MAIN RE',i)
            return 4
        if i==1 and not args.allow_empty and not a.stdout.strip() and not m.stdout.strip():
            print('BOTH OUTPUTS EMPTY: refusing fake green.')
            return 2
        if a.stdout.split()!=m.stdout.split():
            save_counterexample(inp,a.stdout,m.stdout,m.stderr,a.stderr,'WA',seed)
            print(f'WA on stress #{i}, seed={seed}')
            return 1
        if args.progress and i%args.progress==0:
            dt=time.perf_counter()-t0
            print(f'OK {i} ({i/dt:.1f} tests/s)',flush=True)
        i+=1
    dt=time.perf_counter()-t0
    print(f'PASS: {count} tests in {dt:.2f}s ({count/dt:.1f} tests/s)')
    return 0

def clean():
    shutil.rmtree(BIN,ignore_errors=True)
    for pat in ['debug_*.got','debug_*.main.err','debug_*.WA.err']:
        for p in HERE.glob(pat): p.unlink(missing_ok=True)
    print('CLEAN: temporary binaries/outputs removed; .in/.out regression cases kept.')
    return 0

def main():
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('action',nargs='?',default='sample')
    ap.add_argument('arg',nargs='?')
    ap.add_argument('--timeout',type=float,default=float(os.getenv('TIMEOUT','3')))
    ap.add_argument('--mode',choices=['tokens','none'],default=os.getenv('COMPARE','tokens'))
    ap.add_argument('--seed',type=int,default=int(os.getenv('SEED','123456789')))
    ap.add_argument('--memory',type=int,default=0)
    ap.add_argument('--progress',type=int,default=200)
    ap.add_argument('--allow-empty',action='store_true')
    args,_=ap.parse_known_args()
    a=args.action.lower()
    if a in ('sample','r','run'): return sample_mode(args)
    if a in ('s','san','sanitize'): return sample_mode(args,sanitize=True)
    if a in ('one','o'):
        if not args.arg:
            print('usage: bash run.sh one FILE.in')
            return 2
        return sample_mode(args,only=args.arg)
    if a in ('p','stress','duipai'):
        try: n=int(args.arg) if args.arg else 0
        except ValueError:
            print('stress count must be integer')
            return 2
        return stress_mode(args,n)
    if a in ('c','check','submit'): return sample_mode(args,final=True)
    if a=='clean': return clean()
    print('Usage:')
    print('  bash run.sh                 # all flat tests')
    print('  bash run.sh s               # sanitizer')
    print('  bash run.sh one X.in        # one input')
    print('  bash run.sh p 10000         # stress')
    print('  bash run.sh c               # pre-submit check')
    print('  bash run.sh --mode none     # SPJ/run-only')
    return 2

if __name__=='__main__':
    raise SystemExit(main())
