// Day1 A《记录带》复杂度改写版｜2026-11-03 深度代码复审产物
// 改写目标：保留赛时 O(n^2) 枚举语义，把每步 O(n) 的
//   distance(multiset::upper_bound(x), multiset::end())
// 换成 O(log n) 的「坐标压缩 + Fenwick 前缀计数」，即 O(n^3) -> O(n^2 log n)。
// 同时修掉旧码三个工程隐患：
//   1. 删除 `#define int long long`（避免 long long main()/scanf %d 的 UB 与 2 倍内存）；
//   2. 坐标压缩，不再假设 a_i ∈ [1,n]，且允许重复值；
//   3. 显式 long long 累加，避免 n=2e5 时答案溢出 32 位。
// 这是 LOCAL-VERIFIED 的改写候选，不是官方 OJ 提交源码；等价性由
//   交接/2026-11-03_深度代码复审/基准与等价性.py 穷举 + 随机验证。
#include <bits/stdc++.h>
using namespace std;

struct BIT {
    int n;
    vector<int> t;
    explicit BIT(int n_) : n(n_), t(n_ + 1, 0) {}
    void reset() { fill(t.begin(), t.end(), 0); }
    void add(int x, int v) { for (; x <= n; x += x & -x) t[x] += v; }
    int ask(int x) const { int s = 0; for (; x > 0; x -= x & -x) s += t[x]; return s; }
};

long long solve_one(const vector<long long>& a) {
    int n = (int)a.size() - 1;               // 1-indexed
    vector<long long> vals(a.begin() + 1, a.end());
    sort(vals.begin(), vals.end());
    vals.erase(unique(vals.begin(), vals.end()), vals.end());
    auto idx_leq = [&](long long x) {         // 1-based：<= x 的最大压缩下标
        return (int)(upper_bound(vals.begin(), vals.end(), x) - vals.begin());
    };
    BIT bit((int)vals.size());
    // 全局逆序对：k<l 且 a[k]>a[l]
    long long ans = 0;
    for (int i = 1; i <= n; ++i) {
        int pos = idx_leq(a[i]);
        ans += (long long)(i - 1) - bit.ask(pos);   // 已插入 i-1 个，<= a[i] 的个数
        bit.add(pos, 1);
    }
    long long tot = ans;
    // 枚举子段 [i,j]：now = ans - x + y
    //   x = 子段内逆序对数；y = 子段内非逆序对数（含相等）
    // 恒等式 x + y = C(len,2)，故 now = ans + C(len,2) - 2*inv(i,j)
    for (int i = 1; i <= n; ++i) {
        bit.reset();
        long long x = 0, y = 0;
        bit.add(idx_leq(a[i]), 1);
        for (int j = i + 1; j <= n; ++j) {
            int inserted = j - i;
            int pos = idx_leq(a[j]);
            long long numGreater = inserted - bit.ask(pos); // 严格大于 a[j] 的个数
            x += numGreater;
            y += inserted - numGreater;                    // <= a[j] 的个数
            long long now = ans - x + y;
            if (now > tot) tot = now;
            bit.add(pos, 1);
        }
    }
    return tot;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    if (!(cin >> T)) return 0;
    while (T--) {
        int n; cin >> n;
        vector<long long> a(n + 1);
        for (int i = 1; i <= n; ++i) cin >> a[i];
        cout << solve_one(a) << '\n';
    }
    return 0;
}
