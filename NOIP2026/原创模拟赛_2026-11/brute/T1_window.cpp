// T1 brute｜O(n^2) 直接枚举所有 (l,r)，与标程的模型完全独立
#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
  int T;if(!(cin>>T))return 0;
  while(T--){int n;long long K;cin>>n>>K;vector<long long>a(n+1);
    for(int i=1;i<=n;i++)cin>>a[i];
    long long ans=0;
    for(int l=1;l<=n;l++){long long s=0;for(int r=l;r<=n && (long long)(r-l+1)<=K;r++){
      s+=a[r];if(s>=0)ans++;}}
    cout<<ans<<'\n';}
  return 0;}
