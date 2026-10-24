#include <bits/stdc++.h>
using namespace std;
#define int long long
int n;
int a[1000010];
int mp[1000010];
int ma[1000010];
int ans[1000010];
int maxa = 0;
const int MOD = 998244353;
unordered_map <int, int> cnt;
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    freopen ("factor.in", "r", stdin);
    freopen ("factor.out", "w", stdout);
    cin >> n;
    for (int i = 1; i <= n; i++) {
        cin >> a[i];
        maxa = max (maxa, a[i]);
    }
    for (int i = 1; i <= n; i++) {
        cnt.clear();
        int t = a[i];
        for (int j = 2; j * j <= t; j++) {
            while (t % j == 0) {
                mp[j]++, t /= j;
                cnt[j]++;
            }
        }
        if (t > 1)
            mp[t]++, cnt[t]++;
        for (auto y : cnt)
            if (ma[y.first] < y.second)
                ma[y.first] = y.second;
    }
    for (int i = 2; i <= maxa; i++) {
        int down = 0, up = mp[i];
        int more = ma[i] * 2 - mp[i];
        down = max (more, 0LL);
        ans[i] = up - down + 1;
    }
    int res = 1;
    for (int i = 2; i <= maxa; i++)
        res = (1LL * res * ans[i]) % MOD;
    cout << res << '\n';
    return 0;
}
