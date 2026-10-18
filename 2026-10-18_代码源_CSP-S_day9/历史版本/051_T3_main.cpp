#include <bits/stdc++.h>
using namespace std;
#define int long long
int n, m, s;
vector <pair <int, int>> e[1000010];
int d1[1000010];
int d2[1000010];
int q;
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    //freopen (".in", "r", stdin);
    //freopen (".out", "w", stdout);
    cin >> n >> m >> s;
    for (int i = 1; i <= m; i++) {
        int a, b, t;
        cin >> a >> b >> t;
        e[a].push_back ({b, t});
    }
    priority_queue <pair <int, int>> p;
    p.push ({1e18, s});
    d[s] = 0;
    while (!p.empty()) {
        pair <int, int> cur = p.top();
        p.pop();
        for (auto y : e[cur.second]) {
            if (y.second > cur.first)
                continue;
            if (d[y.first] > cur.first)
                continue;
            d1[y.first] = y.second;
            p.push (y.second, y.first);
        }
    }

    return 0;
}
