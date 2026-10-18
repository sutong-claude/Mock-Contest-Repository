#!/usr/bin/env python3
# Day4 B 频谱窗：独立定义暴力 + 正式 solve1 的 Python 等价实现
# 目标：固定复现 n=21 的最小分支边界反例。

def brute(a):
    n=len(a)
    vals=set(a)
    best=0
    for l in range(n):
        for r in range(l,n):
            for v in vals:
                if v==a[l] or v==a[r]:
                    continue
                b=[a[i] for i in range(l,r+1) if a[i]!=v]
                if all(b[i]<b[i+1] for i in range(len(b)-1)):
                    best=max(best,r-l+1)
                    break
    return best

def solve1(a0):
    n=len(a0)
    a=[-1]+a0+[0]
    r=0
    c=-1
    mp={}
    ans=0
    last=0
    least=0
    for l in range(1,n+1):
        while r!=n:
            r+=1
            if r-l+1==1:
                least=last
                last=r
            else:
                if c==a[r]:
                    pass
                elif a[last]<a[r]:
                    least=last
                    last=r
                elif c==-1:
                    if a[r]>a[least]:
                        c=a[last]
                        last=r
                    else:
                        c=a[r]
                else:
                    r-=1
                    break
            mp[a[r]]=mp.get(a[r],0)+1
            ans=max(ans,r-l+1)
        if a[l]==c and mp.get(c,0)==1:
            c=-1
        if a[l+1]==c and mp.get(c,0)==1:
            c=-1
        if mp.get(a[l],0)==1:
            mp.pop(a[l],None)
        else:
            mp[a[l]]=mp.get(a[l],0)-1
        if least<=l:
            least=0
        if last<=l:
            last=0
    return ans

a=list(range(2,22))+[1]
got=solve1(a)
truth=brute(a)
print("a =",a)
print("submitted solve1 =",got)
print("definition brute =",truth)
assert got==21
assert truth==20
print("PASS: explicit correctness counterexample reproduced")
