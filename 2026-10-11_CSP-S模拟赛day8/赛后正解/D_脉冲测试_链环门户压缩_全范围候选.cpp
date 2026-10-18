#include <bits/stdc++.h>
using namespace std;
using ll=long long;
const ll INF=(1LL<<62);
struct Edge {int to;ll w;};
struct Component {bool cycle=false; vector<int> verts; vector<ll> pref, coord; ll perimeter=0;};
struct Solver {
 int n; vector<ll> x,y; vector<vector<Edge>> old;
 unordered_map<ll,vector<int>> bx,by;
 vector<Component> comps;
 vector<int> compId,at,stamp;
 int now=0;
 void init(int N,vector<pair<ll,ll>> xy){
  n=N;x.resize(n);y.resize(n);old.assign(n,{});
  bx.clear();by.clear();bx.reserve(n*2+1);by.reserve(n*2+1);
  for(int i=0;i<n;i++){x[i]=xy[i].first;y[i]=xy[i].second; bx[x[i]].push_back(i);by[y[i]].push_back(i);}
  auto link=[&](int u,int v){ll w=llabs(x[u]-x[v])+llabs(y[u]-y[v]);old[u].push_back({v,w});old[v].push_back({u,w});};
  for(auto &p:bx) if(p.second.size()==2)link(p.second[0],p.second[1]);
  for(auto &p:by) if(p.second.size()==2)link(p.second[0],p.second[1]);
  compId.assign(n,-1);at.assign(n,-1);comps.clear();stamp.assign(n,0);
  for(int i=0;i<n;i++)if(compId[i]<0){
   // Find its component and choose a deg 0/1 endpoint, if present.
   vector<int> nodes;queue<int>q;q.push(i);compId[i]=-2;
   int start=-1;
   while(!q.empty()){int u=q.front();q.pop();nodes.push_back(u);if(old[u].size()<2)start=u;
    for(auto e:old[u])if(compId[e.to]==-1){compId[e.to]=-2;q.push(e.to);}}
   Component C;C.cycle=(start==-1); if(start<0)start=i;
   int u=start,pr=-1;
   do{
    at[u]=(int)C.verts.size();compId[u]=(int)comps.size();C.verts.push_back(u);
    int nxt=-1;ll w=0;
    for(auto e:old[u])if(e.to!=pr){nxt=e.to;w=e.w;break;}
    if(nxt<0||nxt==start){if(nxt==start) C.perimeter+=w; break;}
    C.pref.push_back(w);pr=u;u=nxt;
   }while(true);
   vector<ll> pref2(C.verts.size(),0);
   for(int j=1;j<(int)pref2.size();j++)pref2[j]=pref2[j-1]+C.pref[j-1];
   C.pref=move(pref2);
   if(C.cycle)C.perimeter+=C.pref.back();
   else C.perimeter=C.pref.back();
   C.coord=C.pref;
   if(C.cycle)for(auto z:C.pref)C.coord.push_back(C.perimeter+z);
   comps.push_back(move(C));
  }
 }
 vector<ll> solveQuery(vector<pair<ll,ll>> added){
  int k=added.size(); ++now;
  vector<int> touched;
  for(auto [xx,yy]:added){
   auto it=bx.find(xx);if(it!=bx.end())for(int j:it->second)if(stamp[j]!=now){stamp[j]=now;touched.push_back(j);}
   it=by.find(yy);if(it!=by.end())for(int j:it->second)if(stamp[j]!=now){stamp[j]=now;touched.push_back(j);}
  }
  int r=touched.size(),V=r+k;
  unordered_map<int,int> lookup;lookup.reserve(r*2+1);
  for(int i=0;i<r;i++)lookup[touched[i]]=i;
  vector<vector<Edge>> adj(V);
  auto link=[&](int u,int v,ll w){if(u==v)return;adj[u].push_back({v,w});adj[v].push_back({u,w});};
  for(int j=0;j<k;j++){
   auto [xx,yy]=added[j];
   auto it=bx.find(xx); if(it!=bx.end()) for(int oldId:it->second)link(r+j,lookup[oldId],llabs(yy-y[oldId]));
   it=by.find(yy); if(it!=by.end()) for(int oldId:it->second)link(r+j,lookup[oldId],llabs(xx-x[oldId]));
   for(int t=0;t<j;t++)if(added[t].first==xx||added[t].second==yy){
     ll w=llabs(xx-added[t].first)+llabs(yy-added[t].second);link(r+j,r+t,w);
   }
  }
  // Collect portal positions on each base chain/cycle.
  map<int,vector<pair<int,int>>> portal;
  for(int j=0;j<r;j++)portal[compId[touched[j]]].push_back({at[touched[j]],j});
  for(auto &[ci,ps]:portal){
   sort(ps.begin(),ps.end());auto &c=comps[ci];
   for(int t=1;t<(int)ps.size();t++)link(ps[t-1].second,ps[t].second,c.pref[ps[t].first]-c.pref[ps[t-1].first]);
   if(c.cycle&&ps.size()>1)link(ps.back().second,ps.front().second,c.perimeter-c.pref[ps.back().first]+c.pref[ps.front().first]);
  }
  vector<ll> ans(k,0);
  for(int source=0;source<k;source++){
   vector<ll>d(V,INF);d[r+source]=0;
   priority_queue<pair<ll,int>,vector<pair<ll,int>>,greater<pair<ll,int>>>pq;pq.push({0,r+source});
   while(!pq.empty()){
    auto [dist,u]=pq.top();pq.pop();if(dist!=d[u])continue;
    for(auto e:adj[u])if(d[e.to]>dist+e.w){d[e.to]=dist+e.w;pq.push({d[e.to],e.to});}
   }
   ll maxTime=0;
   for(ll value:d)if(value<INF)maxTime=max(maxTime,value);
   for(auto &[ci,ps]:portal){auto &c=comps[ci];int r0=ps.size(),sz=c.verts.size();
    if(d[ps[0].second]==INF)continue;
    // An arc from coord L to R. All its vertices activate from the two portals.
    auto eval=[&](int vl,int vr,ll xl,ll xr,int lidx,int ridx){
     ll dl=d[vl],dr=d[vr];
     // maximum of min(dl+x-xl, dr+xr-x) lies near their intersection.
     ll target=(dl+dr + 0);(void)target;
     ll numerator=dr+xr+xl-dl;
     ll xGoal=numerator/2;
     auto beg=c.coord.begin()+lidx, end=c.coord.begin()+ridx+1;
     auto it=lower_bound(beg,end,xGoal);
     auto check=[&](vector<ll>::iterator p){if(p<beg||p>=end)return;ll x0=*p;ll t=min(dl+x0-xl,dr+xr-x0);maxTime=max(maxTime,t);};
     if(it!=end)check(it); if(it!=beg)check(prev(it));
     // Also check endpoints explicitly.
     check(beg);check(end-1);
    };
    if(!c.cycle){
     int first=ps[0].first,last=ps.back().first;
     maxTime=max(maxTime,d[ps[0].second]+c.pref[first]);
     maxTime=max(maxTime,d[ps.back().second]+c.pref.back()-c.pref[last]);
     for(int t=1;t<r0;t++){
      int left=ps[t-1].first,right=ps[t].first;
      eval(ps[t-1].second,ps[t].second,c.pref[left],c.pref[right],left,right);
     }
    }else{
     for(int t=0;t<r0;t++){
      int next=(t+1)%r0,left=ps[t].first,right=ps[next].first;
      ll xl=c.pref[left],xr=c.pref[right];
      int rightInd=right;
      if(next==0){xr+=c.perimeter;rightInd+=sz;}
      eval(ps[t].second,ps[next].second,xl,xr,left,rightInd);
     }
    }
   }
   ans[source]=maxTime;
  }
  return ans;
 }
};
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
 int T;if(!(cin>>T))return 0;
 while(T--){int n,q;cin>>n>>q;vector<pair<ll,ll>>points(n);for(auto &p:points)cin>>p.first>>p.second;
  Solver S;S.init(n,points);
  while(q--){int k;cin>>k;vector<pair<ll,ll>>additional(k);for(auto &p:additional)cin>>p.first>>p.second;
   auto ans=S.solveQuery(additional);for(int j=0;j<k;j++)cout<<ans[j]<<(j+1==k?'\n':' ');
  }
 }
}