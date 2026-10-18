#include <bits/stdc++.h>
using namespace std;
#define int long long
int n, m;
vector <pair <int, int>> e[1000010];
pair <int, int> d[1000010];
int cnt[1000010];
bool vis[1000010];
const int P = 1e9 + 7;
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    freopen ("count.in", "r", stdin);
    freopen ("count.out", "w", stdout);
    cin >> n >> m;
    for (int i = 1; i <= m; i++) {
        int u, v, w;
        cin >> u >> v >> w;
        e[u].push_back ({v, w});
        e[v].push_back ({u, w});
    }
    for (int i = 1; i <= n; i++)
        d[i].first = d[i].second = 1e18 + 27;
    priority_queue <pair <int, pair <int, int>>, vector <pair <int, pair <int, int>>>, greater <pair <int, pair <int, int>>>> p;
    p.push ({0, {0, 1}});
    d[1] = {0, 0};
    cnt[1] = 1;
    while (!p.empty ()) {
        pair <int, pair <int, int>> cur = p.top();
        p.pop();
        if (vis[cur.second.second] == true)
            continue;
        vis[cur.second.second] = true;
        for (auto y : e[cur.second.second]) {
            int d1 = cur.first + y.second;
            int k1 = cur.second.first + 1;
            if ((d[y.first].first > d1 || (d[y.first].first == d1 && d[y.first].second > k1)) && vis[y.first] == false) {
                cnt[y.first] = cnt[cur.second.second];
                d[y.first].first = d1;
                d[y.first].second = k1;
                p.push ({d1, {k1, y.first}});
            }
            else if (d[y.first].first == d1 && d[y.first].second == k1)
                cnt[y.first] = (cnt[y.first] + cnt[cur.second.second]) % P;
        }
    }
    if (cnt[n] == 0)
        cout << -1 << '\n';
    else
        cout << cnt[n] % P << '\n';
    return 0;
}
