import random,subprocess,heapq
from pathlib import Path
R=random.Random(20261011)
scenarios=[]; expected=[]
for zz in range(1800):
 n=R.randint(1,13); q=R.randint(1,5)
 old=[]
 for _ in range(n):
  for attempt in range(10000):
   p=(R.randint(1,9),R.randint(1,9))
   if p not in old and sum(x==p[0] for x,y in old)<2 and sum(y==p[1] for x,y in old)<2:
    old.append(p);break
  else:break
 n=len(old);queries=[]
 for i in range(q):
  k=R.randint(1,6);extra=[]
  for j in range(k):
   for t in range(100):
    p=R.choice(old) if R.random()<.18 else (R.randint(1,9),R.randint(1,9))
    if p not in extra:extra.append(p);break
  queries.append(extra)
  allpts=old+extra
  answers=[]
  for s in range(k):
   INF=10**15;ds=[INF]*len(allpts);ds[len(old)+s]=0;pq=[(0,len(old)+s)]
   while pq:
    dd,u=heapq.heappop(pq)
    if dd!=ds[u]:continue
    x,y=allpts[u]
    for v,(xx,yy) in enumerate(allpts):
     if x==xx or y==yy:
      cost=abs(x-xx)+abs(y-yy)
      if ds[v]>dd+cost:
       ds[v]=dd+cost;heapq.heappush(pq,(ds[v],v))
   answers.append(max(d for d in ds if d<INF))
  expected.append(' '.join(map(str,answers)))
 scenarios.append((old,queries))
lines=[str(len(scenarios))]
for old,qs in scenarios:
 lines.append(f'{len(old)} {len(qs)}')
 for x,y in old:lines.append(f'{x} {y}')
 for ps in qs:
  lines.append(str(len(ps)))
  for x,y in ps:lines.append(f'{x} {y}')
data='\n'.join(lines)+'\n'
p=subprocess.run([str(Path(__file__).resolve().parent / 'D_full_candidate')],input=data,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
actual=p.stdout.splitlines()
if len(actual)!=len(expected):print('ROW MISMATCH',len(actual),len(expected),p.stderr);exit(1)
for i,(a,b) in enumerate(zip(actual,expected)):
 if a.strip()!=b.strip():
  print('MISMATCH',i,a,b,scenarios);exit(1)
print('D OK',len(scenarios),'scenarios,',len(expected),'queries,',sum(len(qs) for _,s in scenarios),'queries')