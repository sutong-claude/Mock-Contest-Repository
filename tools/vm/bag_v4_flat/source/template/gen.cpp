#include <bits/stdc++.h>
#include <chrono>
using namespace std;
#define int long long

mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
inline int Rand(int l, int r) { return rng() % (r - l + 1) + l; }

signed main () {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    // 生成一组完整输入到 stdout
    // 可读取环境变量 SEED / TEST_ID 做可复现随机。
    return 0;
}
