// 原始“投票制”的赛后清晰对照版；仅供小数据 oracle，不适用于满数据。
#include <bits/stdc++.h>
using namespace std;
int main(){
    ios::sync_with_stdio(false);cin.tie(nullptr);
    freopen("lamps.in","r",stdin);freopen("lamps.out","w",stdout);
    int n,B;cin>>n>>B;set<string> uniq;
    for(int i=0;i<n;i++){string s;cin>>s;uniq.insert(s);}
    map<string,int> votes;
    for(const string& s:uniq){
        string t=s;votes[t]++;
        for(int l=0;l<B;l++){
            for(int r=l;r<B;r++){
                t[r]=(t[r]=='0'?'1':'0');
                votes[t]++;
            }
            for(int r=l;r<B;r++)t[r]=s[r];
        }
    }
    int ans=0;for(const auto &x:votes)if(x.second==(int)uniq.size())ans++;
    cout<<ans<<'\n';
}
