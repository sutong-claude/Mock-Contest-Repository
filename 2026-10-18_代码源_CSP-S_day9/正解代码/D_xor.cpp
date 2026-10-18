#include <bits/stdc++.h>
using namespace std;
using ll=long long;
using i128=__int128_t;
const ll MOD=998244353;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
#ifndef LOCAL
freopen("xor.in","r",stdin);freopen("xor.out","w",stdout);
#endif

 int n;cin>>n;vector<ll>a(n+1);ll ma=0;for(int i=1;i<=n;i++){cin>>a[i];ma=max(ma,a[i]);}
 // lim[r]: largest left endpoint for which F(a[l..r]) >= 2^k.
 vector<int>lim(n+1),nxt(n+1),dq(n+1);iota(lim.begin(),lim.end(),0);
 vector<ll>pre(n+1),pp(n+1);
 ll ans=(ll)n*(n+1)/2%MOD;
 for(ll low=1;low<=ma;low*=2){
  ll high=low*2;
  pre[0]=pp[0]=0;
  for(int r=1;r<=n;r++){
   pre[r]=(pre[r-1]+(a[r]>=low && a[r]<high?a[r]%MOD:0))%MOD;
   pp[r]=(pp[r-1]+pre[r])%MOD;
  }
  int l=1,head=0,tail=0; i128 sum=0;
  for(int r=1;r<=n;r++){
   if(a[r]<low)sum+=a[r];
   if(a[r]>=low && a[r]<high){while(tail>head && a[dq[tail-1]]>=a[r])tail--;dq[tail++]=r;}
   while(l<=lim[r] && (sum>=high-1 || (head<tail && a[dq[head]]<=sum+1))){
    if(a[l]<low)sum-=a[l];
    if(head<tail && dq[head]==l)head++;
    l++;
   }
   nxt[r]=l-1;
   ll L=nxt[r];ans=(ans+L*pre[r]-(L?pp[L-1]:0))%MOD;
  }
  lim.swap(nxt);
 }
 cout<<(ans+MOD)%MOD<<'\n';
}
