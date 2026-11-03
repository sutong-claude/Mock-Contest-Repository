// T1 window｜坐标压缩 + Fenwick 滑窗计数，O(n log n)/case
#include <bits/stdc++.h>
using namespace std;
struct BIT { int n; vector<int> t; explicit BIT(int n_):n(n_),t(n_+1,0){}
  void add(int x,int v){for(;x<=n;x+=x&-x)t[x]+=v;}
  int ask(int x){int s=0;for(;x>0;x-=x&-x)s+=t[x];return s;} };
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
  int T;if(!(cin>>T))return 0;
  while(T--){int n;long long K;cin>>n>>K;
    vector<long long>S(n+1,0),a(n+1);
    for(int i=1;i<=n;i++){cin>>a[i];S[i]=S[i-1]+a[i];}
    vector<long long>v(S.begin(),S.end());sort(v.begin(),v.end());v.erase(unique(v.begin(),v.end()),v.end());
    auto le=[&](long long x){return (int)(upper_bound(v.begin(),v.end(),x)-v.begin());}; // 1-based 上限下标
    BIT bit((int)v.size());long long ans=0;
    for(int r=1;r<=n;r++){
      bit.add(le(S[r-1]),1);                       // 加入 t=r-1
      long long drop=(long long)r-K-1;
      if(drop>=0) bit.add(le(S[(int)drop]),-1);    // 移出 t=r-K-1
      ans+=bit.ask(le(S[r]));                      // 统计 S[t]<=S[r]
    }
    cout<<ans<<'\n';}
  return 0;}
