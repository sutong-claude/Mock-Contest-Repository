// T4 brute｜N<=20 用 128 位精确整数 + Pascal 组合数做容斥，完全独立：
// 不用模逆元、不用模运算（最后才取模）
#include <bits/stdc++.h>
using namespace std;
using i128=__int128_t;
i128 C[25][25];
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
  for(int i=0;i<=20;i++){C[i][0]=C[i][i]=1;for(int j=1;j<i;j++)C[i][j]=C[i-1][j-1]+C[i-1][j];}
  int n,m;if(!(cin>>n>>m))return 0;int N=n+m;
  i128 fac[25];fac[0]=1;for(int i=1;i<=N;i++)fac[i]=fac[i-1]*i;
  i128 ans=0;
  for(int k=0;k<=n;k++){i128 t=C[n][k]*fac[N-k];if(k&1)ans-=t;else ans+=t;}
  long long out=(long long)(ans%(i128)1000000007);if(out<0)out+=1000000007;
  cout<<out<<'\n';return 0;}
