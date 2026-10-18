// POST-CONTEST CANDIDATE: mean-difference meet-in-the-middle, not OJ-verified.
#include <bits/stdc++.h>
using namespace std;
using ll=long long;
using Vec=array<ll,5>;
struct Node {Vec d; int cnt;};
void solve(){
    int n,m,k; cin>>n>>m>>k;
    Vec b={}; for(int j=0;j<m;++j) cin>>b[j];
    vector<Vec> a(n);
    for(int i=0;i<n;++i)
        for(int j=0;j<m;++j) {cin>>a[i][j]; a[i][j]-=b[j];}
    int n1=n/2,n2=n-n1;
    vector<Node> left(1<<n1);
    for(int s=1;s<(1<<n1);++s){
        int p=s&-s,bit=__builtin_ctz((unsigned)p),old=s^p;
        left[s]=left[old]; ++left[s].cnt;
        for(int j=0;j<m;++j) left[s].d[j]+=a[bit][j];
    }
    sort(left.begin(),left.end(),[](const Node&x,const Node&y){
        if(x.d!=y.d) return x.d<y.d;
        return x.cnt>y.cnt;
    });
    vector<Node> uniq; uniq.reserve(left.size());
    for(const auto&v:left)
        if(uniq.empty()||uniq.back().d!=v.d) uniq.push_back(v);
    Vec right={}; int cnt=0,previous=0; // Gray code: O(m 2^(n/2))
    for(int g=0;g<(1<<n2);++g){
        int s=g^(g>>1);
        if(g){
            int bit=__builtin_ctz((unsigned)(s^previous));
            int sg=(s>>bit&1)?1:-1;
            for(int j=0;j<m;++j) right[j]+=sg*a[n1+bit][j];
            cnt+=sg;
        }
        previous=s;
        Vec need={};for(int j=0;j<m;++j) need[j]=-right[j];
        auto it=lower_bound(uniq.begin(),uniq.end(),need,
           [](const Node&v,const Vec&d){return v.d<d;});
        if(it!=uniq.end()&&it->d==need&&it->cnt+cnt>=k){
            cout<<"Yes\n";return;
        }
    }
    cout<<"No\n";
}
int main(){
    ios::sync_with_stdio(false);cin.tie(nullptr);
    freopen("color.in","r",stdin);
    freopen("color.out","w",stdout);
    int T; if(!(cin>>T))return 0;
    while(T--)solve();
}
