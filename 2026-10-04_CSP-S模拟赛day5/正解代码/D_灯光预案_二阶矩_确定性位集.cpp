#include <bits/stdc++.h>
using namespace std;
using ll = long long;
using i128 = __int128_t;
const ll MOD = 1000000007LL;
const ll INV4 = 250000002LL;

ll power2(int q) {
    ll a = 2, ans = 1;
    while (q) {
        if (q & 1) ans = ans * a % MOD;
        a = a * a % MOD;
        q >>= 1;
    }
    return ans;
}

// Exact equality: hash accelerates lookup, but collided states are compared in full.
struct CanonicalSets {
    int words;
    vector<vector<uint64_t>> states;
    unordered_map<uint64_t, vector<int>> byHash;

    explicit CanonicalSets(int q): words((q+63)/64) {
        vector<uint64_t> empty(words);
        states.push_back(empty); // id=0 represents empty instruction-incidence vector
        byHash[hashState(empty)].push_back(0);
    }
    static uint64_t hashState(const vector<uint64_t>& s) {
        uint64_t h = 1469598103934665603ULL;
        for (uint64_t v : s) {
            h ^= v;
            h *= 1099511628211ULL;
        }
        return h;
    }
    int id(const vector<uint64_t>& state) {
        uint64_t h = hashState(state);
        auto& ids = byHash[h];
        for (int i : ids)
            if (states[i] == state) return i;
        int i = (int)states.size();
        states.push_back(state);
        ids.push_back(i);
        return i;
    }
};

// Sum_{1<=l<=r<=n} (sum_{i=l}^r c[i])^2.
// xs must be sorted by position, with each position appearing once.
i128 segmentSquareSum(const vector<pair<int,ll>>& xs, int n) {
    i128 total = 0;
    ll sumWeighted = 0;
    for (auto [j,c] : xs) {
        total += (i128)j*(n-j+1)*c*c;
        total += (i128)2*(n-j+1)*c*sumWeighted;
        sumWeighted += (ll)j*c;
    }
    return total;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    if (!(cin >> n)) return 0;
    vector<int> a(n+1);
    for (int i=1;i<=n;i++) cin >> a[i];
    int q; cin >> q;

    vector<vector<pair<int,int>>> events(n+2);
    for (int t=0;t<q;t++) {
        int l,r,x; cin >> l >> r >> x;
        if (x) {
            events[l].push_back({t,x});
            events[r+1].push_back({t,x});
        }
    }

    CanonicalSets table(q);
    vector<vector<uint64_t>> active(7, vector<uint64_t>((q+63)/64,0));
    vector<ll> doubledMean(n+1,0);
    vector<vector<pair<int,ll>>> byGroup(1);

    for (int i=1;i<=n;i++) {
        for (auto [id,x] : events[i]) {
            while (x) {
                int b = __builtin_ctz((unsigned)x);
                active[b][id/64] ^= (1ULL << (id%64));
                x &= x-1;
            }
        }
        for (int b=0;b<7;b++) {
            int gid = table.id(active[b]);
            while ((int)byGroup.size() <= gid) byGroup.emplace_back();
            int w = 1<<b;
            int init = (a[i]>>b)&1;
            if (gid == 0) doubledMean[i] += 2LL*w*init;
            else {
                doubledMean[i] += w;
                byGroup[gid].push_back({i, init ? -w : w});
            }
        }
    }

    vector<pair<int,ll>> meanEntries;
    for (int i=1;i<=n;i++) meanEntries.push_back({i,doubledMean[i]});
    i128 total = segmentSquareSum(meanEntries,n);

    for (size_t gid=1; gid<byGroup.size(); gid++) {
        auto& v = byGroup[gid];
        // Identical group IDs may occur for several bits at one index.
        vector<pair<int,ll>> merged;
        for (auto [p,c] : v) {
            if (!merged.empty() && merged.back().first == p)
                merged.back().second += c;
            else
                merged.push_back({p,c});
        }
        total += segmentSquareSum(merged,n);
    }

    ll numerator = (ll)(total % MOD);
    if (numerator < 0) numerator += MOD;
    cout << numerator * INV4 % MOD * power2(q) % MOD << '\n';
    return 0;
}
