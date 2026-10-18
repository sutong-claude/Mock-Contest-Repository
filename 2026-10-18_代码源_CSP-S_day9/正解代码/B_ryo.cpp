#include <bits/stdc++.h>
using namespace std;
using ll=long long;
using i128=__int128_t;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
#ifndef LOCAL
freopen("ryo.in","r",stdin);freopen("ryo.out","w",stdout);
#endif

 int n;cin>>n;vector<int>a(n);for(int &x:a)cin>>x;
 set<int>seen;int start=0,ans=1;
 for(int i=1;i<n;i++){
  bool cut=a[i-1]>a[i];
  auto it=seen.lower_bound(a[i]);
  if(it!=seen.begin() && *--it>a[start])cut=true;
  if(cut){for(int j=start;j<i;j++)seen.insert(a[j]);start=i;ans++;}
 }
 cout<<ans<<'\n';
}
