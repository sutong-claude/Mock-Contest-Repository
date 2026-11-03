// T4 pairs｜容斥 + 线性递推逆元（全程无 qpow）
// 与仓库 alien 候选（一次 qpow(fac[n],P-2) + invfac 倒推）是不同实现：
// 这里用 inv[i] = P - (P/i)*inv[P%i]%P 递推，C(n,k) 用组合数递推，O(N)。
#include <bits/stdc++.h>
using namespace std;
using ll=long long;const ll P=1000000007;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
  int n,m;if(!(cin>>n>>m))return 0;int N=n+m;
  vector<ll>fac(N+1,1),inv(max(2,N+1),1);
  for(int i=1;i<=N;i++)fac[i]=fac[i-1]*i%P;
  for(int i=2;i<=N;i++)inv[i]=(P-(P/i)*inv[P%i]%P)%P;
  ll comb=1,ans=0;
  for(int k=0;k<=n;k++){
    if(k>0)comb=comb*(n-k+1)%P*inv[k]%P;
    ll term=comb*fac[N-k]%P;
    if(k&1)ans=(ans-term+P)%P;else ans=(ans+term)%P;
  }
  cout<<ans%P<<'\n';return 0;}
