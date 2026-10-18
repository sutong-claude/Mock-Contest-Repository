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
