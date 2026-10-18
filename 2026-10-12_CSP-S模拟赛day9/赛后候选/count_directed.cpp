// POST-CONTEST CANDIDATE: directed lexicographic Dijkstra, not OJ-verified.
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const ll INF = (1LL<<62);
const int MOD = 1000000007;
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    freopen("count.in", "r", stdin);
    freopen("count.out", "w", stdout);
    int n, m;
    if (!(cin >> n >> m)) return 0;
    vector<vector<pair<int,ll>>> g(n+1);
    for (int i=0;i<m;++i) {
        int u,v; ll w; cin>>u>>v>>w;
        g[u].push_back({v,w}); // directed: NO reverse edge
    }
    using Dist = pair<ll,int>; // (weight, edge count)
    vector<Dist> dist(n+1, {INF,INT_MAX});
    vector<int> ways(n+1,0);
    using State = tuple<ll,int,int>;
    priority_queue<State,vector<State>,greater<State>> pq;
    dist[1]={0,0}; ways[1]=1; pq.push({0,0,1});
    while(!pq.empty()) {
        auto [d,k,u]=pq.top(); pq.pop();
        if (dist[u]!=Dist(d,k)) continue;
        for (auto [v,w]:g[u]) {
            Dist nd={d+w,k+1};
            if (nd<dist[v]) {
                dist[v]=nd; ways[v]=ways[u];
                pq.push({nd.first,nd.second,v});
            } else if (nd==dist[v]) {
                ways[v]+=ways[u];
                if (ways[v]>=MOD) ways[v]-=MOD;
            }
        }
    }
    cout << (dist[n].first==INF ? -1 : ways[n]) << '\n';
}
