#include <bits/stdc++.h>
using namespace std;
using ll=long long;
using i128=__int128_t;
struct Edge{int a,b,t;};
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
#ifndef LOCAL
freopen("nijika.in","r",stdin);freopen("nijika.out","w",stdout);
#endif

 int n,m,s;cin>>n>>m>>s;
 vector<Edge>e(m);vector<vector<int>>ts(n+1);
 for(auto &x:e){cin>>x.a>>x.b>>x.t;ts[x.a].push_back(x.t);ts[x.b].push_back(x.t);}
 ts[s].push_back(0);
 vector<int>base(n+2);int z=0;
 for(int u=1;u<=n;u++){auto &v=ts[u];sort(v.begin(),v.end());v.erase(unique(v.begin(),v.end()),v.end());base[u]=z;z+=v.size();}base[n+1]=z;
 vector<vector<int>>g(z),rg(z);
 auto add=[&](int a,int b){g[a].push_back(b);rg[b].push_back(a);};
 for(int u=1;u<=n;u++)for(int k=1;k<(int)ts[u].size();k++)add(base[u]+k-1,base[u]+k);
 for(auto x:e){int a=base[x.a]+(lower_bound(ts[x.a].begin(),ts[x.a].end(),x.t)-ts[x.a].begin());int b=base[x.b]+(lower_bound(ts[x.b].begin(),ts[x.b].end(),x.t)-ts[x.b].begin());add(a,b);}
 const int INF=2000000000;
 vector<int>earliest(z,INF),latest(z,-1);
 priority_queue<pair<int,int>,vector<pair<int,int>>,greater<pair<int,int>>>pq;
 for(int k=0;k<(int)ts[s].size();k++){int u=base[s]+k;earliest[u]=ts[s][k];pq.push({earliest[u],u});}
 while(!pq.empty()){auto [d,u]=pq.top();pq.pop();if(d!=earliest[u])continue;for(int v:rg[u])if(d<earliest[v]){earliest[v]=d;pq.push({d,v});}}
 priority_queue<pair<int,int>>mx;
 for(int k=0;k<(int)ts[s].size();k++){int u=base[s]+k;latest[u]=ts[s][k];mx.push({latest[u],u});}
 while(!mx.empty()){auto[d,u]=mx.top();mx.pop();if(d!=latest[u])continue;for(int v:g[u])if(d>latest[v]){latest[v]=d;mx.push({d,v});}}
 int q;cin>>q;while(q--){int u,v;cin>>u>>v;int x=u==s?0:(ts[u].empty()?INF:earliest[base[u]]);
  if(x==INF || ts[v].empty()){cout<<-1<<'\n';continue;}
  auto it=lower_bound(latest.begin()+base[v],latest.begin()+base[v+1],x);
  if(it==latest.begin()+base[v+1])cout<<-1<<'\n';else cout<<ts[v][it-(latest.begin()+base[v])]<<'\n';
 }
}
