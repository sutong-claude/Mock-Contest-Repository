#include <bits/stdc++.h>
using namespace std;
#define int long long
int n;
pair <int, int> a[1000010];
pair <int, int> b[1000010];
inline void dfs (int l, int r) {
    if (l >= r)
        return;
    int mid = (l + r) / 2;
    dfs (l, mid);
    dfs (mid + 1, r);
    int p1 = l, p2 = mid + 1;
    int it = 0;
    while (p1 <= mid && p2 <= r) {
        if (a[p1].first <= a[p2].first)
            b[++it] = a[p1++];
        else
            b[++it] = a[p2++];
    }
    while (p1 <= mid)
        b[++it] = a[p1++];
    while (p2 <= r)
        b[++it] = a[p2++];
    for (int i = 1; i <= r - l + 1; i++)
        a[l + i - 1] = b[i];
}
int f[1000010];
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    freopen ("ryo.in", "r", stdin);
    freopen ("ryo.out", "w", stdout);
    cin >> n;
    for (int i = 1; i <= n; i++) {
        cin >> a[i].first;
        a[i].second = i;
    }
    dfs (1, n);
    for (int i = 1; i <= n; i++)
        f[a[i].second] = i;
    int tot = 0;
    for (int i = 1; i <= n - 1; i++)
        if (f[i] > f[i + 1])
            tot++;
    tot++;
    cout << tot << '\n';
    return 0;
}