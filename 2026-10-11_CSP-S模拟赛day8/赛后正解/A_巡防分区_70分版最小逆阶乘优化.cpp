#include <bits/stdc++.h>
using namespace std;
#define int long long
int T;
const int INF = 2e6 + 18;
int loop = 2e6 + 12;
int P = 998244353;
int f[INF], g[INF];
inline int fac (int x) {
    return f[x];
}
inline int qpow (int a, int b) {
    int res = 1;
    int base = a;
    while (b != 0) {
        if (b % 2 == 1)
            res = (res * base) % P;
        base = (base * base) % P;
        b /= 2;
    }
    return res;
}
inline int devide (int a, int b) {
    return (1LL * a * qpow (b, P - 2)) % P;
}
inline int calc (int xn, int yn, int xm, int ym) {
    int dis1 = xm - xn, dis2 = ym - yn;
    if (dis1 < 0 || dis2 < 0)
        return 0;
    if (dis1 == 0 || dis2 == 0)
        return 1;
    int ans = fac (dis1 + dis2) * g[dis1] % P * g[dis2] % P;
    return ans;
}
inline void solve () {
    int n, m, a, b, c, d;
    cin >> n >> m >> a >> b >> c >> d;
    int cnt = calc (0, 0, n, m);
    int sum = 0;
    for (int i = 0; i <= a - 1; i++) {
        int res1 = calc (0, 0, i, d);
        int res2 = calc (i, d + 1, n, m);
        int tot = res1 * res2 % P;
        sum = (sum + tot) % P;
    }
    for (int i = a; i <= a; i++) {
        int res1 = calc (0, 0, d, i);
        int res2 = calc (i, d, n, m);
        int tot = res1 * res2 % P;
        sum = (sum + tot) % P;
    }
    for (int i = c; i <= n; i++) {
        int res1 = calc (0, 0, i, b);
        int res2 = calc (i, b + 1, n, m);
        int tot = res1 * res2 % P;
        sum = (sum + tot) % P;
    }
    int final_ans = devide (sum, cnt) % P;
    cout << final_ans << '\n';
}
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    freopen ("Jinhsi.in", "r", stdin);
    freopen ("Jinhsi.out", "w", stdout);
    f[1] = 1;
    for (int i = 2; i <= loop; i++)
        f[i] = (1LL * f[i - 1] * i) % P;
    g[loop] = qpow (f[loop], P - 2);
    for (int i = loop; i >= 1; i--)
        g[i - 1] = g[i] * i % P;
    cin >> T;
    while (T--)
        solve ();
    return 0;
}