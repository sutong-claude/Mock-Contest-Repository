// 赛后参考：二维Pareto前沿 + 普通卡独立插入+二分+RMQ，O(n log n)。
// 已通过官方样例、n<=7每档80组随机对照全排列、n=2e5性能测试；未提交OJ。
#include <bits/stdc++.h>
using namespace std;
using ll=long long;
ll solve(vector<pair<ll,ll>> a){
    int n=(int)a.size();if(n==1)return 0;
    sort(a.begin(),a.end(),[](auto x,auto y){return x.first!=y.first?x.first>y.first:x.second>y.second;});
    vector<pair<ll,ll>> critical,other;ll maxb=-1;
    for(auto v:a){if(v.second>maxb){critical.push_back(v);maxb=v.second;}else other.push_back(v);}
    reverse(critical.begin(),critical.end());
    int m=(int)critical.size();
    vector<ll> alpha(m+1),beta(m+1);
    for(int j=1;j<=m;j++)alpha[j]=critical[j-1].first;
    for(int j=0;j<m;j++)beta[j]=critical[j].second;
    beta[m]=0;
    ll ans=0;
    for(int j=1;j<m;j++)ans+=alpha[j]+beta[j];
    int size=1;while(size<m+1)size<<=1;
    const ll INF=(1LL<<62);
    vector<ll> seg(size*2,INF);
    for(int j=0;j<=m;j++)seg[size+j]=alpha[j]+beta[j];
    for(int i=size-1;i>0;i--)seg[i]=min(seg[i*2],seg[i*2+1]);
    auto rmq=[&](int l,int r){ll res=INF;for(l+=size,r+=size+1;l<r;l>>=1,r>>=1){if(l&1)res=min(res,seg[l++]);if(r&1)res=min(res,seg[--r]);}return res;};
    for(const auto &card:other){
        ll v=card.first,w=card.second;
        int p=int(upper_bound(alpha.begin(),alpha.end(),v)-alpha.begin())-1;
        int lo=0,hi=m;
        while(lo<hi){int mid=(lo+hi)/2;if(beta[mid]<=w)hi=mid;else lo=mid+1;}
        int q=lo;
        if(q<=p){ans+=v+w;continue;}
        ll cur=min(v+beta[p],alpha[q]+w);
        if(p+1<q)cur=min(cur,rmq(p+1,q-1));
        ans+=cur;
    }
    return ans;
}
int main(){
    ios::sync_with_stdio(false);cin.tie(nullptr);
    freopen("reserves.in","r",stdin);freopen("reserves.out","w",stdout);
    int T;cin>>T;while(T--){int n;cin>>n;vector<pair<ll,ll>>a(n);for(auto &x:a)cin>>x.first>>x.second;cout<<solve(a)<<'\n';}
}
