// T2 brute｜n<=12 的状态空间 BFS（2^n），与贪心完全独立
#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
  int n,L;string s;if(!(cin>>n>>L))return 0;cin>>s;
  int start=0;for(int i=0;i<n;i++)if(s[i]=='1')start|=1<<i;
  int maskLen=(1<<L)-1;
  vector<int>d(1<<n,-1);queue<int>q;d[start]=0;q.push(start);
  while(!q.empty()){int u=q.front();q.pop();if(u==0)break;
    for(int i=0;i+L<=n;i++){int v=u^(maskLen<<i);if(d[v]==-1){d[v]=d[u]+1;q.push(v);}}}
  cout<<d[0]<<'\n';return 0;}
