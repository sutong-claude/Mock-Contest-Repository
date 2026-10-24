#include <bits/stdc++.h>
using namespace std;
#define int long long
int n, b;
set <string> s;
string input;
map <string, int> vote;
inline string re (string t) {
    reverse (t.begin(), t.end());
    return t;
}
int tot = 0;
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    //freopen ("lamps.in", "r", stdin);
    //freopen ("lamps.out", "w", stdout);
    cin >> n >> b;
    for (int i = 1; i <= n; i++) {
        cin >> input;
        s.insert (input);
    }
    n = s.size();
    for (auto y : s) {
        string left = "";
        string right = re (y);
        for (int i = 0; i < b; i++) {
            string mid = "";
            string r = right;
            for (int j = i; j < b; j++) {
                r.pop_back();
                if (y[j] == '0')
                    mid += '1';
                else
                    mid += '0';
                string res = left + mid + re (r);
                vote[res]++;
            }
            left += y[i];
            right.pop_back();
        }
        vote[y]++;
    }
    for (auto y : vote) {
        if (y.second == n)
            tot++;
    }
    cout << tot << '\n';
    return 0;
}
