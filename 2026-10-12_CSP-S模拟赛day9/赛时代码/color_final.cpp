#include <bits/stdc++.h>
using namespace std;
#define int long long
int T;
int b[10];
int a[50][10];
int temp[10];
inline void solve () {
    int n, m, k;
    cin >> n >> m >> k;
    for (int i = 1; i <= m; i++)
        cin >> b[i];
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= m; j++)
            cin >> a[i][j];
    if (n <= 5) {
        for (int i = 0; i < (1 << n); i++) {
            for (int j = 1; j <= m; j++)
                temp[j] = 0;
            int t = i;
            int cnt = 1;
            int tot = 0;
            while (cnt != n) {
                if (t % 2 == 1) {
                    for (int j = 1; j <= m; j++)
                        temp[j] += a[cnt][j];
                    tot++;
                }
                cnt++;
                t /= 2;
            }
            if (tot < k)
                continue;
            bool ok = true;
            for (int j = 1; j <= m; j++) {
                if (b[j] * tot != temp[j])
                    ok = false;
            }
            if (ok) {
                cout << "Yes" << '\n';
                return;
            }
        }
    }
    cout << "No" << '\n';
}
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    freopen ("color.in", "r", stdin);
    freopen ("color.out", "w", stdout);
    cin >> T;
    while (T--)
        solve ();
    return 0;
}
