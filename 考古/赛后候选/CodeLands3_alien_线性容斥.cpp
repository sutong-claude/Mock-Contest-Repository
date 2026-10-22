// CodeLands III: alien. Independent post-contest optimization, NOT the submitted source.
// Forbidding N disjoint man/woman pairs yields inclusion-exclusion:
// Sum_{k=0}^N (-1)^k * C(N,k) * (N+M-k)! modulo 1e9+7.
// O(N+M) time / memory: one modular inverse, rather than one per term.
#include <bits/stdc++.h>
using namespace std;
const int P=1000000007;
int qpow(int a,int b) {
    long long x=a,r=1;
    while(b) {if(b&1) r=r*x%P; x=x*x%P; b>>=1;}
    return (int)r;
}
int main() {
    ios::sync_with_stdio(false);cin.tie(nullptr);
    int n,m; if(!(cin>>n>>m)) return 0;
    vector<int> fac(n+m+1), invfac(n+1);
    fac[0]=1;
    for(int i=1;i<=n+m;++i)fac[i]=(long long)fac[i-1]*i%P;
    invfac[n]=qpow(fac[n],P-2);
    for(int i=n;i>=1;--i)invfac[i-1]=(long long)invfac[i]*i%P;
    long long ans=0;
    for(int k=0;k<=n;++k) {
        long long choose=(long long)fac[n]*invfac[k]%P*invfac[n-k]%P;
        int term=(long long)choose*fac[n+m-k]%P;
        if(k&1)ans-=term;else ans+=term;
        if(ans<0)ans+=P;
        if(ans>=P)ans-=P;
    }
    cout<<ans<<'\n';
}
