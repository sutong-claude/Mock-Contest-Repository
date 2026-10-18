#include <bits/stdc++.h>
using namespace std;
// POST-CONTEST candidate. Split 20-bit mask into two 10-bit halves.
// Local: five official attachments matched optimum and output legality;
// 120 independent random-small DP matches. NOT formally OJ-AC.
constexpr int HALF=1024, WIDTH=11;
static int best[HALF*HALF*WIDTH];
static unsigned char bits[HALF];
int main(){
 ios::sync_with_stdio(false);cin.tie(nullptr);
 // freopen("Aemeath.in","r",stdin);
 // freopen("Aemeath.out","w",stdout);
 int n;if(!(cin>>n))return 0;
 vector<int>a(n+1),k(n+1),dp(n+1),par(n+1);
 for(int i=1;i<=n;i++)cin>>a[i];
 for(int i=1;i<=n;i++)cin>>k[i];
 for(int x=1;x<HALF;x++)bits[x]=bits[x>>1]+(x&1);
 int answer=0,at=0;
 for(int i=1;i<=n;i++){
  int hi=a[i]>>10,lo=a[i]&1023,prev=0;
  int base=lo*HALF*WIDTH;
  for(int x=0;x<HALF;x++){
   int need=k[i]-bits[x&hi];
   if((unsigned)need<=10){
    int j=best[base+x*WIDTH+need];
    if(dp[j]>dp[prev])prev=j;
   }
  }
  dp[i]=dp[prev]+1;par[i]=prev;
  if(dp[i]>answer){answer=dp[i];at=i;}
  int vhi=a[i]>>10,vlo=a[i]&1023;
  int ofs=vhi*WIDTH;
  for(int mask=0;mask<HALF;mask++){
   int idx=mask*HALF*WIDTH+ofs+bits[mask&vlo];
   if(dp[i]>dp[best[idx]])best[idx]=i;
  }
 }
 vector<int>path;for(int v=at;v;v=par[v])path.push_back(v);
 reverse(path.begin(),path.end());
 cout<<answer<<'\n';
 for(size_t i=0;i<path.size();i++)cout<<path[i]<<(i+1==path.size()?'\n':' ');
}
