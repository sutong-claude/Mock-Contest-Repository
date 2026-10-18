#include <bits/stdc++.h>
using namespace std;
#define int long long
int n, m, s;
vector <pair <int, int>> e[1000010];
int d[1000010];
int q;
priority_queue <pair <int, int>, vector <pair <int, int>>, greater <pair <int, int>>> p;
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
    cin >> q;
    while (q--) {
        int u, v;
        cin >> u >> v;
        for (int i = 1; i <= n; i++)
            d[i] = 1e18;
        d[u] = 0;
        p.push ({0, u});
        while (!p.empty()) {
            pair <int, int> cur = p.top();
            p.pop();
            if (cur.first != d[cur.second])
                continue;
            for (auto y : e[cur.second]) {
                if (y.second >= cur.first && d[y.first] > y.second) {
                    d[y.first] = y.second;
                    p.push ({y.first, y.second});
                }
            }
        }
        int time1 = d[s];
        for (int i = 1; i <= n; i++)
            d[i] = 1e18;
        d[s] = time1;
        p.push ({time1, s});
        while (!p.empty()) {
            pair <int, int> cur = p.top();
            p.pop();
            if (cur.first != d[cur.second])
                continue;
            for (auto y : e[cur.second]) {
                if (y.second >= cur.first && d[y.first] > y.second) {
                    d[y.first] = y.second;
                    p.push ({y.first, y.second});
                }
            }
        }
        int time2 = d[v];
        int tot = time2;
        if (time2 > 1e17)
            cout << -1 << '\n';
        else
            cout << tot << '\n';
    }
    return 0;
}
