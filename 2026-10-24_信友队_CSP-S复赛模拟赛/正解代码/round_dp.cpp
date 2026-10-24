// 赛后参考：根据官方 t_i 状态建立 O(n) DP。独立小数据全排列对拍及官方样例通过；未提交OJ。
#include <bits/stdc++.h>
using namespace std;
using ll=long long;
const ll NEG=-(1LL<<60);
pair<ll,string> solve(const string& s,const vector<ll>& w){
    int n=(int)s.size();pair<ll,string> best={NEG,""};
    for(int init=0;init<=1;init++){
        vector<array<ll,2>> dp(n+1);
        for(auto &p:dp)p={NEG,NEG};
        dp[n][init]=0;
        for(int i=n-1;i>=0;i--)for(int prev=0;prev<=1;prev++)for(int q=0;q<=1;q++){
            if(s[i]=='1'&&s[(i+1)%n]=='0'&&q!=1)continue;
            int b=s[i]-'0'+prev-q;
            if(b<0||b>1||dp[i+1][q]==NEG)continue;
            dp[i][prev]=max(dp[i][prev],w[i]*b+dp[i+1][q]);
        }
        if(dp[0][init]==NEG)continue;
        string result;result.reserve(n);int prev=init;
        for(int i=0;i<n;i++){
            pair<int,int> chosen={3,3};
            for(int q=0;q<=1;q++){
                if(s[i]=='1'&&s[(i+1)%n]=='0'&&q!=1)continue;
                int b=s[i]-'0'+prev-q;
                if(b<0||b>1||dp[i+1][q]==NEG)continue;
                if(dp[i][prev]==w[i]*b+dp[i+1][q])chosen=min(chosen,make_pair(b,q));
            }
            assert(chosen.first<=1);
            result.push_back('0'+chosen.first);prev=chosen.second;
        }
        assert(prev==init);
        if(dp[0][init]>best.first||(dp[0][init]==best.first&&(best.second.empty()||result<best.second)))best={dp[0][init],result};
    }
    return best;
}
int main(){
    ios::sync_with_stdio(false);cin.tie(nullptr);
    freopen("round.in","r",stdin);freopen("round.out","w",stdout);
    int T;cin>>T;while(T--){int n;cin>>n;string s;cin>>s;vector<ll>w(n);for(ll &x:w)cin>>x;auto ans=solve(s,w);cout<<ans.first<<'\n'<<ans.second<<'\n';}
}
