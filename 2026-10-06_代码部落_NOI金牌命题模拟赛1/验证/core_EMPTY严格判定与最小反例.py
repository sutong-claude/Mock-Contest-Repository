#!/usr/bin/env python3
"""core 最终 EMPTY fallback 的严格成立条件与最小反例。

结论：
存在一个大小为 k、核心串长度 L=0 的选择
iff
原 n 个非空字符串中至少有 k 种不同首字符。

原因：两串 LCP=0 iff 首字符不同；L 是所选集合任意两串 LCP 的最大值，
故 L=0 iff 所选 k 串两两首字符不同。
"""

from itertools import combinations, combinations_with_replacement


def lcp(a,b):
    i=0
    while i<min(len(a),len(b)) and a[i]==b[i]:
        i+=1
    return i


def subset_core(ss):
    L=max(lcp(a,b) for a,b in combinations(ss,2))
    if L==0:
        return ""
    cand=[]
    for a,b in combinations(ss,2):
        if lcp(a,b)>=L:
            cand.append(a[:L])
    return min(cand)


def brute_global(strings,k):
    return min(subset_core(list(sel)) for sel in combinations(strings,k))


def empty_exact(strings,k):
    return len({s[0] for s in strings})>=k


def exhaustive_self_test():
    universe=["a","b","c","aa","ab","ba","bb","ca"]
    checked=0
    for n in range(2,6):
        for tup in combinations_with_replacement(universe,n):
            for k in range(2,n+1):
                b=(brute_global(list(tup),k)=="")
                e=empty_exact(tup,k)
                assert b==e,(tup,k,b,e)
                checked+=1
    return checked


def main():
    checked=exhaustive_self_test()
    print("EMPTY theorem brute-verified instances:",checked)

    # 最小反例：唯一选择 {a,aa} 的最大两两LCP=1，核心串=a。
    strings=["a","aa"]; k=2
    print("minimal wrong-final case:",strings,"k=",k,
          "truth=",repr(brute_global(strings,k)),
          "final=",repr(""))
    assert brute_global(strings,k)=="a"
    assert not empty_exact(strings,k)

    # 官方正文两样例的 EMPTY 分支。
    sample=["abc","bc","abc","ac"]
    assert brute_global(sample,3)=="a"
    assert brute_global(sample,2)==""
    print("official sample1 truth='a'; sample2 truth=EMPTY")
    print("PASS")


if __name__=="__main__":
    main()
