#include <bits/stdc++.h>
using namespace std;

// Exact persistent-string lex order via an AVL tree.
// Nodes represent a character followed by a canonical existing tail.
// No string copying or probabilistic hash equality.
// Dynamic 64-bit labels speed up comparison; relabeling preserves order.
// Complexity: O(L log L + R), R = total relabel work; worst-case R not
// proven O(L log L) for this practical local-window labeling heuristic.
struct OrderedStrings {
    struct Node {
        int left=0,right=0,parent=0,height=1,size=1,next=0;
        int prevLex=0,nextLex=0;
        uint64_t label=0;
        unsigned char ch=0;
    };
    vector<Node> t;
    int root;
    explicit OrderedStrings(size_t reserve_nodes=0) {
        t.reserve(reserve_nodes+2);
        t.emplace_back(); // 0: null link
        t.emplace_back(); // 1: empty string, unique lexicographic minimum
        root=1;
        t[1].label=0;
    }
    int ht(int x) const {return x?t[x].height:0;}
    int sz(int x) const {return x?t[x].size:0;}
    void pull(int x) {
        t[x].height=1+max(ht(t[x].left),ht(t[x].right));
        t[x].size=1+sz(t[x].left)+sz(t[x].right);
    }
    int compare(unsigned char c,int tail,int y) const {
        if(c!=t[y].ch) return c<t[y].ch?-1:1;
        uint64_t a=t[tail].label,b=t[t[y].next].label;
        return (a>b)-(a<b);
    }
    void replace_parent_link(int x,int y) {
        int p=t[x].parent;
        t[y].parent=p;
        if(!p) root=y;
        else if(t[p].left==x) t[p].left=y;
        else t[p].right=y;
    }
    int rotate_left(int x) {
        int y=t[x].right;
        replace_parent_link(x,y);
        t[x].right=t[y].left;
        if(t[x].right) t[t[x].right].parent=x;
        t[y].left=x;t[x].parent=y;
        pull(x);pull(y);
        return y;
    }
    int rotate_right(int x) {
        int y=t[x].left;
        replace_parent_link(x,y);
        t[x].left=t[y].right;
        if(t[x].left) t[t[x].left].parent=x;
        t[y].right=x;t[x].parent=y;
        pull(x);pull(y);
        return y;
    }
    void rebalance(int x) {
        while(x) {
            pull(x);
            int b=ht(t[x].left)-ht(t[x].right);
            if(b>1) {
                int l=t[x].left;
                if(ht(t[l].left)<ht(t[l].right)) rotate_left(l);
                x=rotate_right(x);
            } else if(b<-1) {
                int r=t[x].right;
                if(ht(t[r].right)<ht(t[r].left)) rotate_right(r);
                x=rotate_left(x);
            }
            x=t[x].parent;
        }
    }
    void assign_label(int id) {
        int p=t[id].prevLex,q=t[id].nextLex;
        uint64_t lo=p?t[p].label:0;
        uint64_t hi=q?t[q].label:UINT64_MAX;
        if(hi-lo>1) {t[id].label=lo+(hi-lo)/2;return;}
        int window=32;
        while(true) {
            int l=id,r=id,count=1;
            while(count<window) {
                bool progressed=false;
                if(t[l].prevLex && t[l].prevLex!=1) {
                    l=t[l].prevLex;++count;progressed=true;
                }
                if(count>=window) break;
                if(t[r].nextLex) {
                    r=t[r].nextLex;++count;progressed=true;
                }
                if(!progressed) break;
            }
            uint64_t low=t[l].prevLex?t[t[l].prevLex].label:0;
            uint64_t high=t[r].nextLex?t[t[r].nextLex].label:UINT64_MAX;
            uint64_t step=(high-low)/(uint64_t(count)+1);
            if(step>=4) {
                uint64_t label=low;
                for(int x=l;;x=t[x].nextLex) {
                    label+=step;t[x].label=label;
                    if(x==r) break;
                }
                return;
            }
            window*=2;
        }
    }
    int prepend(unsigned char c,int tail) {
        int x=root,parent=0,direction=0,pred=0,succ=0;
        while(x) {
            int cmp=compare(c,tail,x);
            if(cmp==0) return x; // canonical reuse
            parent=x;direction=cmp;
            if(cmp<0) succ=x;
            else pred=x;
            x=cmp<0?t[x].left:t[x].right;
        }
        int id=(int)t.size();
        t.emplace_back();
        t[id].ch=c;t[id].next=tail;t[id].parent=parent;
        if(direction<0) t[parent].left=id;
        else t[parent].right=id;
        t[id].prevLex=pred;t[id].nextLex=succ;
        if(pred) t[pred].nextLex=id;
        if(succ) t[succ].prevLex=id;
        assign_label(id);
        rebalance(parent);
        return id;
    }
    int best_suffix(const string& s,int rest) {
        int tail=rest,best=0;
        for(int i=(int)s.size()-1;i>=0;i--) {
            tail=prepend((unsigned char)s[i],tail);
            if(!best || t[tail].label<t[best].label) best=tail;
        }
        return best;
    }
    string materialize(int node) const {
        string s;
        while(node!=1) {
            s.push_back(char(t[node].ch));
            node=t[node].next;
        }
        return s;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
#ifndef LOCAL
    freopen("Hina.in","r",stdin);
    freopen("Hina.out","w",stdout);
#endif
    int T;if(!(cin>>T))return 0;
    while(T--) {
        int n;cin>>n;
        vector<string> s(n);
        size_t L=0;
        for(auto& v:s){cin>>v;L+=v.size();}
        OrderedStrings os(L);
        int rest=1;
        for(int i=n-1;i>=0;i--) rest=os.best_suffix(s[i],rest);
        cout<<os.materialize(rest)<<'\n';
    }
}