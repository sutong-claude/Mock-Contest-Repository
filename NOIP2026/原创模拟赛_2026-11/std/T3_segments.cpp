// T3 segments｜离线二维支配最大（外层 Fenwick over sb，内层 Fenwick over sa）
// 与仓库 考古/赛后候选/CodeLands3_maxcover_二维树状数组.cpp 的维度组织相反：
// 候选外层是 sa、内层是 sb；本标程外层 sb、内层 sa。两者都实现
//   dp[i] = max(dp[i-1], i + max_{t<i, sa[t]<=sa[i], sb[t]<=sb[i]} (dp[t]-t))
// 但数据结构索引、压缩数组、插入顺序全部不同，便于交叉验证。O(n log^2 n)
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int NEG = -1000000000;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
  int n;if(!(cin>>n))return 0;
  vector<ll>a(n+1),b(n+1),sa(n+1,0),sb(n+1,0);
  for(int i=1;i<=n;i++)cin>>a[i];
  for(int i=1;i<=n;i++)cin>>b[i];
  for(int i=1;i<=n;i++){sa[i]=sa[i-1]+a[i];sb[i]=sb[i-1]+b[i];}
  vector<ll> yb(sb.begin(),sb.end());sort(yb.begin(),yb.end());yb.erase(unique(yb.begin(),yb.end()),yb.end());
  int K=(int)yb.size();
  auto ib=[&](ll x){return (int)(lower_bound(yb.begin(),yb.end(),x)-yb.begin())+1;};
  vector<int> ix(n+1);for(int t=0;t<=n;t++)ix[t]=ib(sb[t]);
  vector<vector<ll>> xs(K+1);
  for(int t=0;t<=n;t++)for(int k=ix[t];k<=K;k+=k&-k)xs[k].push_back(sa[t]);
  vector<vector<int>> bit(K+1);
  for(int k=1;k<=K;k++){sort(xs[k].begin(),xs[k].end());xs[k].erase(unique(xs[k].begin(),xs[k].end()),xs[k].end());
    bit[k].assign(xs[k].size()+1,NEG);}
  auto add=[&](int idxB,ll valA,int v){
    for(int k=idxB;k<=K;k+=k&-k){
      int p=(int)(lower_bound(xs[k].begin(),xs[k].end(),valA)-xs[k].begin())+1;
      for(int j=p;j<(int)bit[k].size();j+=j&-j)if(v>bit[k][j])bit[k][j]=v;
    }};
  auto ask=[&](int idxB,ll valA){
    int best=NEG;
    for(int k=idxB;k>0;k-=k&-k){
      int p=(int)(upper_bound(xs[k].begin(),xs[k].end(),valA)-xs[k].begin());
      for(int j=p;j>0;j-=j&-j)if(bit[k][j]>best)best=bit[k][j];
    }
    return best;};
  vector<int> dp(n+1,0);
  add(ix[0],sa[0],0);                       // t=0, dp[0]-0 = 0
  for(int i=1;i<=n;i++){
    dp[i]=dp[i-1];                          // 必须继承：位置 i 可以不被任何合法段覆盖
    int v=ask(ix[i],sa[i]);
    if(v!=NEG)dp[i]=max(dp[i],i+v);
    add(ix[i],sa[i],dp[i]-i);
  }
  cout<<dp[n]<<'\n';return 0;}
