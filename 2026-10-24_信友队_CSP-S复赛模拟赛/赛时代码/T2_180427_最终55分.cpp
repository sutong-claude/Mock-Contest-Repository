#include <bits/stdc++.h>
using namespace std;
#define int long long
int n, b;
set <string> s;
string input;
map <string, int> vote;
int tot = 0;
signed main () {
    ios::sync_with_stdio (false);
    cin.tie (0);
    cout.tie (0);
    freopen ("lamps.in", "r", stdin);
    freopen ("lamps.out", "w", stdout);
    cin >> n >> b;
    for (int i = 1; i <= n; i++) {
        cin >> input;
        s.insert (input);
    }
    n = s.size();
    if (b == 1) {
        cout << 2 << '\n';
        return 0;
    }
    for (auto y : s) {
        string temp = y;
        for (int i = 0; i < b; i++) {
            for (int j = i; j < b; j++) {
                if (y[j] == '0')
                    temp[j] = '1';
                else
                    temp[j] = '0';
                vote[temp]++;
            }
            for (int j = i; j < b; j++)
                temp[j] = y[j];
            temp[i] = y[i];
        }
        vote[y]++;
    }
    for (auto y : vote)
        if (y.second == n)
            tot++;
    cout << tot << '\n';
    return 0;
}
