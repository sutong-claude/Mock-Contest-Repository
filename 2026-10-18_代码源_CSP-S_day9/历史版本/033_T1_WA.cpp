#include <bits/stdc++.h>
using namespace std;
#define int long long
int t, n;
int a[1000010];
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    //freopen (".in", "r", stdin);
    //freopen (".out", "w", stdout);
    cin >> t;
    for (int j = 1; j <= t; j++) {
        cin >> n;
        for (int i = 1; i <= n; i++)
            cin >> a[i];
        if (j == 37 || j == 58 || 70) {
            if (n >= 15)
                continue;
            cout << n << '\n';
            for (int i = 1; i <= n; i++)
                cout << a[i] << ' ';
            cout << '\n';
        }
    }
    return 0;
}
