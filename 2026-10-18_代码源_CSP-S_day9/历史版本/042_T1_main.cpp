#include <bits/stdc++.h>
using namespace std;
#define int long long
int T;
int n;
int a[2000010];
bool rst[1000010];
inline void solve () {
    cin >> n;
    for (int i = 1; i <= n; i++)
        cin >> a[i];
    if (n == 1) {
        cout << 0 << '\n';
        return;
    }
    rst[n] = true;
    rst[n + 1] = true;
    for (int i = n - 1; i >= 1; i--) {
        if (a[i] <= a[i + 1] && rst[i + 1] == true)
            rst[i] = true;
        else
            rst[i] = false;
    }
    int ma = 0, pos = 0;
    if (rst[1] == true) {
        cout << 0 << '\n';
        return;
    }
    a[n + 1] = LONG_LONG_MAX;
    a[0] = 0;
    int left = 0;
    for (int i = 1; i <= n; i++) {
        int cha = a[i - 1] - a[i];
        if (cha > ma) {
            ma = cha;
            left = cha;
        }
        if (left > 0) {
            int v = a[i + 1] - a[i];
            int go = v / i;
            go = max (go, 0LL);
            left -= go;
            left = max (left, 0LL);
            a[i] = a[i] + go * i;
        }
        if (i % 2 == 0 && a[i] <= a[i + 1] && rst[i + 1] && left == 0) {
            cout << ma << '\n';
            return;
        }
    }
    cout << -1 << '\n';
}
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    //freopen (".in", "r", stdin);
    //freopen (".out", "w", stdout);
    cin >> T;
    while (T--)
        solve ();
    return 0;
}
