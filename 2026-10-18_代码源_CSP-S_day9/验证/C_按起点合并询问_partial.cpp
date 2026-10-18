#include <bits/stdc++.h>
using namespace std;
int main(){
 ios::sync_with_stdio(false);cin.tie(nullptr);
#ifndef LOCAL
 freopen("nijika.in","r",stdin);freopen("nijika.out","w",stdout);
#endif
 int n,m,s;cin>>n>>m>>s;
 vector<vector<pair<int,int>>>e(n+1);
 for(int i=0,a,b,t;i<m;i++){cin>>a>>b>>t;e[a].push_back({b,t});}
 int q;cin>>q;vector<vector<pair<int,int>>>queries(n+1);vector<int>ans(q,-1);
 for(int i=0,u,v;i<q;i++){cin>>u>>v;queries[u].push_back({v,i});}
 const int INF=2000000000;
 auto dijkstra=[&](int src,int start){
  vector<int>d(n+1,INF);d[src]=start;
  priority_queue<pair<int,int>,vector<pair<int,int>>,greater<pair<int,int>>>p;p.push({start,src});
  while(!p.empty()){
   auto [time,u]=p.top();p.pop();if(time!=d[u])continue;
   for(auto [v,t]:e[u])if(t>=time && t<d[v]){d[v]=t;p.push({t,v});}
  }
  return d;
 };
 for(int u=1;u<=n;u++)if(!queries[u].empty()){
  auto d=dijkstra(u,0);if(d[s]==INF)continue;
  d=dijkstra(s,d[s]);for(auto[v,id]:queries[u])ans[id]=d[v]==INF?-1:d[v];
 }
 for(int x:ans)cout<<x<<'\n';
}
