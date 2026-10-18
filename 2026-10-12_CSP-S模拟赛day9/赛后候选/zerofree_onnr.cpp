// POST-CONTEST CANDIDATE: Gemini PDF pp.16-17, not OJ-verified.
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    freopen("zerofree.in", "r", stdin);
    freopen("zerofree.out", "w", stdout);
    int n, r;
    if (!(cin >> n >> r)) return 0;
    vector<ll> a(n), c(n);
    for (ll &x : a) cin >> x;
    for (ll &x : c) cin >> x;
    const ll INF = (1LL<<62);
    vector<ll> dp(r, INF);
    dp[0] = 0;
    int s = 0;
    for (int i = 0; i < n; ++i) {
        s = (s + ((a[i] % r + r) % r)) % r;
        ll mn = *min_element(dp.begin(), dp.end());
        // no change retains old offset; change allows any offset for cost c[i]
        if (mn < INF) for (int d = 0; d < r; ++d)
            dp[d] = min(dp[d], mn + c[i]);
        dp[(r - s) % r] = INF;
    }
    ll ans = *min_element(dp.begin(), dp.end());
    cout << (ans >= INF ? -1 : ans) << '\n';
}
