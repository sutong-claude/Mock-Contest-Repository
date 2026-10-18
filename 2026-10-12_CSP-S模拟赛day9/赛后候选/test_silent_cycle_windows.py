# Independent exact small-state oracle for silent_cycle_windows.cpp.
# k can be huge because an ordered pair of functional-graph states repeats after <=n*m steps.
# Run from the candidates directory after compiling silent_cycle_windows.cpp to ./silent.
import random,subprocess,pathlib,time
P=pathlib.Path(__file__).parent
rng=random.Random(20261015)
def calc(n,m,k,x0,y0,p,q):
    points=set(); seen={}; x,y=x0,y0; t=0
    while t<k:
        if (x,y) in seen:break
        seen[(x,y)]=t
        points.add((x,y)); x,y=p[x],q[y];t+=1
    def F(L): return L*(L+1)**2*(L+2)//12
    ret=0
    for i in range(1,n+1):
        ys=sorted([y for x,y in points if x==i]); z=[0,*ys,m+1]
        ret+=sum(F(z[j+1]-z[j]-1) for j in range(len(z)-1))
    for j in range(1,m+1):
        xs=sorted([x for x,y in points if y==j]); z=[0,*xs,n+1]
        ret+=sum(F(z[i+1]-z[i]-1) for i in range(len(z)-1))
    return ret%998244353

def run(exe,n,m,k,x0,y0,p,q):
    data=f'{n} {m} {k}\n{x0} {y0}\n'+ ' '.join(map(str,p[1:]))+'\n'+' '.join(map(str,q[1:]))+'\n'
    (P/'silent.in').write_text(data)
    pr=subprocess.run([str(P/exe)], cwd=P, capture_output=True,timeout=12)
    if pr.returncode!=0:raise RuntimeError((pr.returncode,pr.stderr.decode()[-1400:],data))
    return int((P/'silent.out').read_text()),data

if __name__=='__main__':
    samples=[(1,1,0,1,1,[0,1],[0,1]),(1,1,10**10,1,1,[0,1],[0,1]),(2,2,10**10,1,1,[0,2,1],[0,2,1]),(2,3,10000000000,1,2,[0,2,1],[0,2,3,1])]
    for z in samples:
        a,d=run('silent',*z);b=calc(*z)
        assert a==b,('targeted',a,b,d)
    print('Targeted tests: 4 passed')
    start=time.time()
    for case in range(4000):
        n=rng.randint(1,9);m=rng.randint(1,9)
        p=[0]+[rng.randint(1,n) for _ in range(n)]
        q=[0]+[rng.randint(1,m) for _ in range(m)]
        x0=rng.randint(1,n); y0=rng.randint(1,m)
        k=rng.choice([0,1,2,3,5,7,10,25,50,100,200,1000,10**10])
        a,data=run('silent',n,m,k,x0,y0,p,q);b=calc(n,m,k,x0,y0,p,q)
        assert a==b,('random',case,a,b,data)
    print('Random graph/large-k independent oracle 4000/4000',round(time.time()-start,2),'sec')
    for la in range(1,19):
      for lb in range(1,19):
        n=la;m=lb
        p=[0]+[i+1 if i<n else 1 for i in range(1,n+1)]
        q=[0]+[i+1 if i<m else 1 for i in range(1,m+1)]
        for k in [0,1,2,la,lb,la*lb,la*lb+1,10**12]:
            a,data=run('silent',n,m,k,1,1,p,q); b=calc(n,m,k,1,1,p,q)
            assert a==b,('paircycles',la,lb,k,a,b,data)
    print('All cycle length pairs [1..18] x [1..18] x 8 k scenarios: 2592/2592 passed')
