// T2 lamps｜差分 + 左到右贪心，O(n)
#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
  int n,L;string s;if(!(cin>>n>>L))return 0;cin>>s;
  vector<int> diff(n+L+2,0);long long cur=0,ans=0;
  for(int i=0;i<n;i++){
    cur+=diff[i];
    int bit=(s[i]-'0')^(int)(cur&1);
    if(bit){
      if(i+L>n){cout<<-1<<'\n';return 0;}
      ++ans;diff[i]+=1;diff[i+L]-=1;cur+=1;   // 本位立即受这次翻转影响
    }
  }
  cout<<ans<<'\n';return 0;}
