#include <bits/stdc++.h>
using namespace std;
using ll = long long;
struct Edge {int u,v;ll w;};
int main(){
 ios::sync_with_stdio(false);cin.tie(nullptr);
 // freopen("Cartethyia.in", "r", stdin);
 // freopen("Cartethyia.out", "w", stdout);
 int n,s,t;if(!(cin>>n>>s>>t))return 0;
 vector<Edge> es(n-1);vector<vector<pair<int,int>>> adj(n+1);
 for(int i=0;i<n-1;i++){int u,v;ll w;cin>>u>>v>>w;es[i]={u,v,w};adj[u].push_back({v,i});adj[v].push_back({u,i});}
 if(s==t){for(int k=0;k<=n;k++)cout<<0<<(k==n?'\n':' ');return 0;}
 vector<int> parent(n+1,-1),pe(n+1,-1),order;
 parent[s]=0;order.push_back(s);
 for(int j=0;j<(int)order.size();j++){
  int v=order[j];for(auto [u,id]:adj[v])if(parent[u]==-1){parent[u]=v;pe[u]=id;order.push_back(u);}
 }
 vector<unsigned char> onP(n-1,0);
 vector<int> pathverts;vector<ll> weight;
 for(int v=t;v!=0;v=parent[v]){
  pathverts.push_back(v);
  if(v!=s){onP[pe[v]]=1;weight.push_back(es[pe[v]].w);}
 }
 int d=(int)weight.size();
 sort(weight.begin(),weight.end());vector<ll> pref(d+1);
 for(int i=0;i<d;i++)pref[i+1]=pref[i]+weight[i];
 vector<int> dep(n+1,-1),que;
 for(int v:pathverts){dep[v]=0;que.push_back(v);}
 for(int j=0;j<(int)que.size();j++){
  int v=que[j];for(auto [u,id]:adj[v])if(dep[u]==-1){dep[u]=dep[v]+1;que.push_back(u);}
 }
 const ll INF=(1LL<<62);vector<ll> mi(n+1,INF);
 for(int id=0;id<n-1;id++)if(!onP[id]){
  auto [u,v,w]=es[id];int r=min(dep[u],dep[v])+1;
  mi[r]=min(mi[r],w);
 }
 for(int r=1;r<=n;r++)mi[r]=min(mi[r],mi[r-1]);
 for(int k=0;k<=n;k++){
  ll ans=pref[max(1,d-k)];
  if(k>d)ans=min(ans,mi[min(n,k-d)]);
  cout<<ans<<(k==n?'\n':' ');
 }
}
