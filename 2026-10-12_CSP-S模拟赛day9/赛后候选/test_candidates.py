# Model-conditioned offline regression, not an official OJ test.
# Compile before running:
#   g++ -std=c++17 -O2 zerofree_onnr.cpp -o zerofree_onnr
#   g++ -std=c++17 -O2 count_directed.cpp -o count_directed
#   g++ -std=c++17 -O2 color_mitm.cpp -o color_mitm
import random, subprocess, pathlib, math, time
P=pathlib.Path(__file__).parent
rng=random.Random(20261015)
def run(which, data):
    (P/(which+'.in')).write_text(data)
    proc=subprocess.run([str(P/({'zerofree':'zerofree_onnr','count':'count_directed','color':'color_mitm'}[which]))],cwd=P,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=3)
    assert proc.returncode==0,(which,proc.stderr)
    return (P/(which+'.out')).read_text().strip()
# true brute: all possible new value residues each step, sum costs if same residue can choose unchanged
for z in range(600):
    n=rng.randint(1,6);r=rng.randint(2,5)
    a=[rng.randint(-9,9) for i in range(n)]
    c=[rng.randint(0,15) for i in range(n)]
    b={(0,0):0}  # key = (old sum (mod r), new sum (mod r))
    for i in range(n):
        nb={}
        for (old,new),v in b.items():
            old2=(old+a[i])%r
            for residue in range(r):
                new2=(new+residue)%r
                if new2==0:continue
                nv=v+(0 if residue==a[i]%r else c[i])
                key=(old2,new2)
                nb[key]=min(nb.get(key,10**30),nv)
        b=nb
    ans=min(b.values(),default=-1)
    data=f'{n} {r}\n'+ ' '.join(map(str,a))+'\n'+' '.join(map(str,c))+'\n'
    actual=int(run('zerofree',data))
    assert actual==ans,('A',z,n,r,a,c,ans,actual)
print('A: 600 randomized cases vs independent residue enumeration oracle passed')

for z in range(650):
    n=rng.randint(1,7);m=rng.randint(0,16)
    e=[(rng.randrange(n),rng.randrange(n),rng.randint(0,5)) for i in range(m)]
    # oracle dynamic across exact k=0..n-1, keep minimum distance and count for exact k
    dp=[None]*n;dp[0]=(0,1)
    best=None
    for depth in range(n):
        if dp[-1] is not None:
            cand=(dp[-1][0],depth)
            if best is None or cand<best[0]:best=(cand,dp[-1][1])
            elif cand==best[0]:best=(cand,(best[1]+dp[-1][1])%1000000007)
        nd=[None]*n
        for u,v,w in e:
            if dp[u] is None:continue
            cost,cnt=dp[u];nv=cost+w
            if nd[v] is None or nv<nd[v][0]:nd[v]=(nv,cnt)
            elif nv==nd[v][0]:nd[v]=(nv,(nd[v][1]+cnt)%1000000007)
        dp=nd
    answer=str(-1 if best is None else best[1]%1000000007)
    data=f'{n} {m}\n'+''.join(f'{u+1} {v+1} {w}\n' for u,v,w in e)
    actual=run('count',data)
    assert actual==answer,('B',z,n,e,answer,actual)
print('B: 650 randomized cases vs by-length dynamic programming oracle passed')

for z in range(550):
    n=rng.randint(1,12);m=rng.randint(1,5);k=rng.randint(1,n)
    b=[rng.randint(-4,4) for j in range(m)]
    a=[[rng.randint(-4,4) for j in range(m)] for i in range(n)]
    yes=False
    for mask in range(1<<n):
        if mask.bit_count()<k:continue
        if all(sum(a[i][j]-b[j] for i in range(n) if (mask>>i)&1)==0 for j in range(m)):
            yes=True;break
    data='1\n'+f'{n} {m} {k}\n'+' '.join(map(str,b))+'\n'+''.join(' '.join(map(str,row))+'\n' for row in a)
    actual=run('color',data)
    assert actual==('Yes' if yes else 'No'),('C',z,n,m,k,'Yes' if yes else 'No',actual)
print('C: 550 randomized cases vs complete subset exhaustive oracle passed')

# targeted structural checks
assert run('count','2 1\n2 1 0\n')=='-1'
assert run('color','1\n1 1 1\n5\n5\n')=='Yes'
assert run('zerofree','1 2\n0\n9\n')=='9'
print('Directed reversal, final singleton, and n=1 targeted cases passed')
