// POST-CONTEST MODEL CANDIDATE from Gemini PDF pp20-22, not official-OJ verified.
// Assumed input: n m k; x0 y0; P[1..n]; Q[1..m].
// k distinct time indices t=0..k-1; cell is (x_t,y_t), x(t+1)=P[x_t], y(t+1)=Q[y_t].
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
constexpr ll MOD=998244353LL, INV12=582309206LL; // 12^{-1} mod MOD

ll F(ll x) {
    if (x<=0) return 0;
    ll a=x%MOD, b=(x+1)%MOD, c=(x+2)%MOD;
    return a*b%MOD*b%MOD*c%MOD*INV12%MOD;
}
ll addmod(ll x,ll y){ x+=y; if(x>=MOD)x-=MOD; return x; }
ll submod(ll x,ll y){ x-=y; if(x<0)x+=MOD; return x; }
struct Gaps {
    int len;
    set<int> positions;
    vector<int> count;
    ll energy;
    Gaps(int n):len(n),positions({0,n+1}),count(n+2,0),energy(F(n)){}
    void insert(int y){
        assert(1<=y && y<=len);
        if(count[y]++ > 0) return;
        auto [it,ok]=positions.insert(y); assert(ok);
        int nxt=*next(it),prv=*prev(it);
        energy=submod(energy,F(nxt-prv-1));
        energy=addmod(energy,F(y-prv-1));
        energy=addmod(energy,F(nxt-y-1));
    }
    void erase(int y){
        assert(count[y]>0);
        if(--count[y] > 0) return;
        auto it=positions.find(y); assert(it!=positions.end());
        int nxt=*next(it),prv=*prev(it);
        energy=submod(energy,F(y-prv-1));
        energy=submod(energy,F(nxt-y-1));
        energy=addmod(energy,F(nxt-prv-1));
        positions.erase(it);
    }
};
struct Orbit {
    vector<int> walk;
    int mu,lambda;
};
Orbit orbit(const vector<int>& nxt, int start){
    vector<int> where(nxt.size(),-1);
    Orbit o;
    int v=start;
    while(where[v]<0){
        where[v]=(int)o.walk.size();
        o.walk.push_back(v);
        v=nxt[v];
    }
    o.mu=where[v]; o.lambda=(int)o.walk.size()-o.mu;
    return o;
}
int valueAt(const Orbit &o,ll t){
    if(t<(ll)o.walk.size())return o.walk[(size_t)t];
    return o.walk[o.mu+(t-o.mu)%o.lambda];
}
ll extended_gcd(ll a,ll b,ll &x,ll &y){
    if(!b){x=1;y=0;return a;}
    ll x1,y1,g=extended_gcd(b,a%b,x1,y1);
    x=y1; y=x1-(a/b)*y1; return g;
}
ll inverse(ll a,ll m){
    if(m==1) return 0;
    ll x,y; ll g=extended_gcd(a,m,x,y); assert(g==1);
    return (x%m+m)%m;
}

// Computes sum over rows, where row label is first orbit, column label is second.
// Initial prefix noise points are grouped in per-row vectors, including duplicates.
ll directedEnergy(int rowN,int colN, const Orbit& ox, const Orbit& oy,
                  ll mu,ll K, const vector<vector<int>>& prefixByRow){
    // Before any cyclic segment, baseline is energy with prefix noise only.
    vector<ll> baseline(rowN+1);
    ll total=0;
    for(int row=1;row<=rowN;++row){
        vector<int> v=prefixByRow[row];
        sort(v.begin(),v.end());
        v.erase(unique(v.begin(),v.end()),v.end());
        int prev=0;
        ll val=0;
        for(int y:v){
            val=addmod(val,F(y-prev-1));
            prev=y;
        }
        val=addmod(val,F(colN-prev));
        baseline[row]=val;
        total=addmod(total,val);
    }
    if(K<=mu) return total;
    ll remaining=K-mu;
    int A=ox.lambda,B=oy.lambda;
    vector<int> xc(A),yc(B);
    for(int i=0;i<A;++i)xc[i]=valueAt(ox,mu+i);
    for(int i=0;i<B;++i)yc[i]=valueAt(oy,mu+i);
    int g=std::gcd(A,B), h=B/g;
    ll inv=inverse(A/g,h);
    // For residue r mod A, visited time indices r+j*A, j=0..q_r-1.
    // In y cycle these are a consecutive window under the permutation stride A mod B.
    // Sort the row queries by their start index *in that permutation*.
    vector<vector<pair<int,int>>> requests(g); // (start position, x-residue r)
    for(int r=0;r<A;++r){
        int residue=r%g;
        int p=(int)(((ll)((r-residue)/g)*inv)%h);
        requests[residue].push_back({p,r});
    }
    Gaps gaps(colN);
    ll base=remaining/A,extra=remaining%A;
    for(int residue=0;residue<g;++residue){
        auto &v=requests[residue];
        sort(v.begin(),v.end());
        vector<int> permutation(h);
        for(int j=0;j<h;++j)
            permutation[j]=yc[((ll)residue+(ll)j*A)%B];
        int L=0,R=0;
        for(auto [p,r]:v){
            ll q=min((ll)h,base+(r<extra));
            int wantRight=p+(int)q;
            // Start positions may repeat when A>B; q may then decrease by one. Roll back R if needed.
            assert(L<=p);
            while(R<wantRight){gaps.insert(permutation[R%h]);++R;}
            while(R>wantRight){--R;gaps.erase(permutation[R%h]);}
            while(L<p){gaps.erase(permutation[L%h]);++L;}
            int row=xc[r];
            for(int y:prefixByRow[row])gaps.insert(y);
            total=submod(total,baseline[row]);
            total=addmod(total,gaps.energy);
            for(int y:prefixByRow[row])gaps.erase(y);
        }
        while(L<R){gaps.erase(permutation[L%h]);++L;}
        assert(gaps.energy==F(colN) && gaps.positions.size()==2);
    }
    return total;
}
int main(){
    ios::sync_with_stdio(false);cin.tie(nullptr);
    freopen("silent.in","r",stdin);
    freopen("silent.out","w",stdout);
    int n,m;ll k; if(!(cin>>n>>m>>k))return 0;
    int x0,y0;cin>>x0>>y0;
    vector<int>P(n+1),Q(m+1);
    for(int i=1;i<=n;++i)cin>>P[i];
    for(int i=1;i<=m;++i)cin>>Q[i];
    Orbit ox=orbit(P,x0),oy=orbit(Q,y0);
    ll mu=max(ox.mu,oy.mu);
    vector<vector<int>> rowTail(n+1),colTail(m+1);
    for(ll t=0;t<min(k,mu);++t){
        int x=valueAt(ox,t),y=valueAt(oy,t);
        rowTail[x].push_back(y);
        colTail[y].push_back(x);
    }
    ll rows=directedEnergy(n,m,ox,oy,mu,k,rowTail);
    ll cols=directedEnergy(m,n,oy,ox,mu,k,colTail);
    cout<<addmod(rows,cols)<<'\n';
}
