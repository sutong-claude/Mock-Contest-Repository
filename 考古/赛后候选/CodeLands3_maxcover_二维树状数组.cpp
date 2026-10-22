// CodeLands III: maxcover. Post-contest candidate, NOT the user's submitted source.
// dp[i] = max(dp[i-1], i + max_{j<i, A[j]<=A[i], B[j]<=B[i]} (dp[j]-j))
// Offline-coordinate 2D Fenwick. O(n log^2 n), O(n log n).
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int NEG = -1000000000;
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; if (!(cin >> n)) return 0;
    vector<ll> a(n+1), b(n+1), sa(n+1), sb(n+1);
    for (int i=1; i<=n; ++i) cin >> a[i];
    for (int i=1; i<=n; ++i) cin >> b[i];
    for (int i=1; i<=n; ++i) { sa[i]=sa[i-1]+a[i]; sb[i]=sb[i-1]+b[i]; }
    vector<ll> allA=sa;
    sort(allA.begin(),allA.end());
    allA.erase(unique(allA.begin(),allA.end()),allA.end());
    int K=(int)allA.size();
    vector<int> ix(n+1);
    vector<vector<ll>> ys(K+1);
    for (int i=0; i<=n; ++i) {
        ix[i]=(int)(lower_bound(allA.begin(),allA.end(),sa[i])-allA.begin())+1;
        for (int k=ix[i]; k<=K; k+=k&-k) ys[k].push_back(sb[i]);
    }
    vector<vector<int>> bit(K+1);
    for (int k=1; k<=K; ++k) {
        sort(ys[k].begin(),ys[k].end());
        ys[k].erase(unique(ys[k].begin(),ys[k].end()),ys[k].end());
        bit[k].assign(ys[k].size()+1,NEG);
    }
    auto add = [&](int idx,ll y,int v) {
        for (int k=idx; k<=K; k+=k&-k) {
            int j=(int)(lower_bound(ys[k].begin(),ys[k].end(),y)-ys[k].begin())+1;
            for (;j<(int)bit[k].size();j+=j&-j) bit[k][j]=max(bit[k][j],v);
        }
    };
    auto ask = [&](int idx,ll y) {
        int best=NEG;
        for (int k=idx;k>0;k-=k&-k) {
            int j=(int)(upper_bound(ys[k].begin(),ys[k].end(),y)-ys[k].begin());
            for (;j>0;j-=j&-j) best=max(best,bit[k][j]);
        }
        return best;
    };
    vector<int> dp(n+1);
    add(ix[0],sb[0],0);
    for (int i=1;i<=n;++i) {
        dp[i]=dp[i-1];
        int v=ask(ix[i],sb[i]);
        if (v!=NEG) dp[i]=max(dp[i],i+v);
        add(ix[i],sb[i],dp[i]-i);
    }
    cout << dp[n] << '\n';
}
