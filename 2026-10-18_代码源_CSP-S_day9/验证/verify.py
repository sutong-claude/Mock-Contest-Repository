#!/usr/bin/env python3
"""Independent small oracles; compile and test actual candidate source files.
Run: python3 verify.py --rounds 1200 --output results.json
"""
import argparse,subprocess,tempfile,itertools,random,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=argparse.ArgumentParser();P.add_argument('--rounds',type=int,default=1200);P.add_argument('--output',default='results.json');args=P.parse_args()
rng=random.Random(20261018);tmp=tempfile.TemporaryDirectory();bin=Path(tmp.name);result={}
def run(code,s):
 r=subprocess.run([str(bin/code)],input=s.encode(),capture_output=True,timeout=5,check=True)
 return list(map(int,r.stdout.split()))
for name in ['A_hitori','B_ryo','C_nijika','D_xor']:
 f=ROOT/'正解代码'/(name+'.cpp');subprocess.run(['g++','-std=c++17','-O2','-DLOCAL',str(f),'-o',str(bin/name)],check=True)
 result[name]={'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'cases':0}
# A: enumerate actual operation-count vectors, no greedy feasibility predicate.
# For odd n, the final fixed value bounds every earlier final element.
# For even n, include all count vectors up to max(a) (sufficient by the all-prefix construction).
def bruteA(a):
 n=len(a);best=None;bounds=[]
 for k in range(2,n+1,2):bounds.append(max(a) if n%2==0 else max(0,(a[-1]-a[k-1])//k))
 for cnt in itertools.product(*(range(x+1) for x in bounds)):
  total=sum(cnt)
  if best is not None and total>=best:continue
  b=a[:]
  for k,c in zip(range(2,n+1,2),cnt):
   for i in range(k):b[i]+=(i+1)*c
  if b==sorted(b):best=total
 return -1 if best is None else best
cases=[list(a) for n in range(1,7) for a in itertools.product(range(1,4),repeat=n)]
cases += [[rng.randint(1,7) for _ in range(rng.randint(1,7))] for _ in range(args.rounds)]
s=str(len(cases))+'\n'+''.join(str(len(a))+'\n'+' '.join(map(str,a))+'\n' for a in cases)
actual=run('A_hitori',s)
for a,v in zip(cases,actual):assert v==bruteA(a),(a,v,bruteA(a))
assert len(actual)==len(cases);result['A_hitori']['cases']=len(cases);print('A',len(cases),flush=True)
# B: DP over every segment, explicitly try every insertion position into the sorted previous prefix.
def bruteB(a):
 n=len(a);dp=[n+1]*(n+1);dp[0]=0
 for l in range(n):
  before=sorted(a[:l])
  for r in range(l+1,n+1):
   seg=a[l:r]
   for slot in range(l+1):
    b=before[:slot]+seg+before[slot:]
    if b==sorted(b):dp[r]=min(dp[r],dp[l]+1);break
 return dp[n]
cases=[list(x) for n in range(1,6) for x in itertools.product(range(1,4),repeat=n)]
cases += [[rng.randint(1,6) for _ in range(rng.randint(1,9))] for _ in range(args.rounds)]
for a in cases:
 v=run('B_ryo',str(len(a))+'\n'+' '.join(map(str,a))+'\n')[0];assert v==bruteB(a),(a,v,bruteB(a))
result['B_ryo']['cases']=len(cases);print('B',len(cases),flush=True)
# C: chronological two-layer reachability, repeated closure for all same-time edges.
def bruteC(n,e,s,u):
 seen={(u,u==s)};ans=[-1]*n
 if u==s:ans[u]=0
 for t in sorted({x[2] for x in e}):
  changed=True
  while changed:
   changed=False
   for a,b,w in e:
    if w!=t:continue
    for flag in (False,True):
     v=(b,flag or b==s)
     if (a,flag) in seen and v not in seen:seen.add(v);changed=True
  for v in range(n):
   if (v,True) in seen and ans[v]<0:ans[v]=t
 return ans
for z in range(args.rounds):
 n=rng.randint(1,8);m=rng.randint(1,35);s=rng.randrange(n);e=[(rng.randrange(n),rng.randrange(n),rng.randint(0,7)) for _ in range(m)]
 q=[(u,v) for u in range(n) for v in range(n)]
 inp=f'{n} {m} {s+1}\n'+''.join(f'{a+1} {b+1} {t}\n' for a,b,t in e)+str(len(q))+'\n'+''.join(f'{u+1} {v+1}\n' for u,v in q)
 truth=[x for u in range(n) for x in bruteC(n,e,s,u)];actual=run('C_nijika',inp);assert actual==truth,(inp,actual,truth)
result['C_nijika']['cases']=args.rounds;print('C',args.rounds,flush=True)
# D: enumerate reachable subset sums for every interval (not the sorted-coin lemma).
def bruteD(a):
 ans=0
 for l in range(len(a)):
  sums={0}
  for r in range(l,len(a)):
   sums|={x+a[r] for x in sums};v=1
   while v in sums:v+=1
   ans+=v
 return ans%998244353
cases=[list(x) for n in range(1,6) for x in itertools.product(range(1,4),repeat=n)]
cases += [[rng.choice([1,1,2,3,4,7,8,9,15,16,17,10**18]) for _ in range(rng.randint(1,12))] for _ in range(args.rounds)]
for a in cases:
 v=run('D_xor',str(len(a))+'\n'+' '.join(map(str,a))+'\n')[0];assert v==bruteD(a),(a,v,bruteD(a))
result['D_xor']['cases']=len(cases);print('D',len(cases),flush=True)
result['seed']=20261018;result['status']='PASS';Path(args.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
