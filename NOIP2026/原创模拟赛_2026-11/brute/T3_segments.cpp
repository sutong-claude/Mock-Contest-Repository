// T3 brute｜两个独立 oracle：
//  (1) n<=8 递归枚举所有两两不相交合法段集合（无 DP / 无前缀和 / 无支配查询）
//  (2) O(n^2) 逐段 DP，与标程的二维支配结构完全不同
#include <bits/stdc++.h>
using namespace std;
using ll=long long;
int n;vector<ll>a,b;ll bestEx;
void rec(int start,ll total){if(total>bestEx)bestEx=total;
  for(int l=start;l<n;l++){ll sa=0,sb=0;for(int r=l;r<n;r++){sa+=a[r];sb+=b[r];
    if(sa>=0&&sb>=0)rec(r+1,total+(r-l+1));}}}
ll quad(){vector<ll>dp(n+1,0);
  for(int i=1;i<=n;i++){dp[i]=dp[i-1];ll sa=0,sb=0;
    for(int j=i;j>=1;j--){sa+=a[j-1];sb+=b[j-1];if(sa>=0&&sb>=0)dp[i]=max(dp[i],dp[j-1]+i-j+1);}}
  return dp[n];}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
  if(!(cin>>n)) return 0;
  a.resize(n); b.resize(n);
  for(auto &x : a) cin >> x;
  for(auto &x : b) cin >> x;
  ll q=quad();
  if(n<=8){bestEx=0;rec(0,0);if(bestEx!=q){cerr<<"EXHAUSTIVE_MISMATCH "<<bestEx<<" "<<q<<'\n';return 2;}}
  cout<<q<<'\n';return 0;}
