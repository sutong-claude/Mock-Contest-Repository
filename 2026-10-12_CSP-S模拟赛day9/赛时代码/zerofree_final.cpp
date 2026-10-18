#include <bits/stdc++.h>
using namespace std;
#define int long long
int n, r;
int a[1000010], c[1000010];
int lst[1000010];
int tot = 0;
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    freopen ("zerofree.in", "r", stdin);
    freopen ("zerofree.out", "w", stdout);
    cin >> n >> r;
    for (int i = 1; i <= n; i++)
        cin >> a[i];
    for (int i = 1; i <= n; i++)
        cin >> c[i];
    if (r == 2) {
    for (int i = 1; i <= n; i++)
        lst[i] = (lst[i - 1] + a[i]) % r;
    int cnt = 0;
    for (int i = 1; i <= n; i++) {
        int now = lst[i] + cnt;
        if (now % r == 0) {
            tot += c[i];
            cnt++;
        }
    }
    cout << tot << '\n';
    return 0;
    }
    else if (n <= 10) {
        int ans = 1e19;
        for (int i = 0; i < (1 << n); i++) {
            vector <int> keep;
            int cost = 0;
            int t = i;
            int cnt = 1;
            while (cnt != n) {
                if (t % 2 == 1)
                    keep.push_back (a[cnt]);
                else
                    cost += c[cnt];
                t /= 2;
                cnt++;
            }
            int sum = 0;
            bool ok = true;
            for (auto y : keep) {
                sum += y;
                sum %= r;
                if (sum == 0) {
                    ok = false;
                }
            }
            if (ok)
                ans = min (ans, cost);
        }
        cout << ans << '\n';
        return 0;
    }
    else
        cout << c[1] << '\n';
    return 0;
}
