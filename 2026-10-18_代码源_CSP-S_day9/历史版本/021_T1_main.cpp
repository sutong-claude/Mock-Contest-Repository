#include <bits/stdc++.h>
using namespace std;
#define int long long
int T;
int n;
int a[2000010];
inline void solve () {
    cin >> n;
    for (int i = 1; i <= n; i++)
        cin >> a[i];
    if (n == 1) {
        cout << 0 << '\n';
        return;
    }
    if (n % 2 == 0) {
        int ma = 0;
        for (int i = 2; i <= n; i++) {
            int cha = a[i - 1] - a[i];
            ma = max (ma, cha);
        }
        cout << ma << '\n';
        return;
    }
    else {
        int ma = 0;
        for (int i = 2; i <= n - 1; i++) {
            int cha = a[i - 1] - a[i];
            ma = max (ma, cha);
        }
        int last = (a[n - 1] + 1LL * ma * (n - 1));
        if (last <= a[n])
            cout << ma << '\n';
        else
            cout << -1 << '\n';
    }
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
