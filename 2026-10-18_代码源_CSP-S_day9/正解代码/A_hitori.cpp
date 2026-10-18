#include <bits/stdc++.h>
using namespace std;
using ll=long long;
using i128=__int128_t;
ll solve(vector<ll> a){
 int n=(int)a.size()-1; ll need=0;
 for(int i=1;i<n;i++)need=max(need,a[i]-a[i+1]);
 ll next=0; // number of operations covering i+1
 for(int i=n;i>=1;i--){
  ll cur=next;
  if(i%2==0){
   if(i==n)cur=need;
   else {
    i128 cap=(i128)a[i+1]-a[i]+(i128)(i+1)*next;
    if(cap<0)return -1;
    cur=min<i128>(need,cap/i);
   }
  }
  if(cur<next)return -1;
  if(i<n && (i128)a[i]+(i128)i*cur>(i128)a[i+1]+(i128)(i+1)*next)return -1;
  next=cur;
 }
 return next==need?need:-1;
}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
#ifndef LOCAL
freopen("hitori.in","r",stdin);freopen("hitori.out","w",stdout);
#endif

 int T;cin>>T;while(T--){int n;cin>>n;vector<ll>a(n+1);for(int i=1;i<=n;i++)cin>>a[i];cout<<solve(a)<<'\n';}
}
