#!/usr/bin/env python3
"""Day7 D 提纳里的巡林路线：03:48 版 5000 候选的 exact oracle / 最小反例。

- true oracle: 枚举所有叶子对，计算路径长度与全树到路径最大距离 H。
- candidate: 逐行复现赛时 D_5000候选_03-48.cpp 的逻辑。
- 自动搜索 Prüfer 小树，区分：
  1) H=0 边界错误；
  2) 计数错误；
  3) 真正的正值模型错误。
"""

from itertools import product, combinations
from collections import deque


def trees_prufer(n):
    if n == 2:
        yield [(1, 2)]
        return
    import heapq
    for seq in product(range(1, n + 1), repeat=n - 2):
        deg = [0] + [1] * n
        for x in seq:
            deg[x] += 1
        leaves = [i for i in range(1, n + 1) if deg[i] == 1]
        heapq.heapify(leaves)
        edges = []
        for x in seq:
            u = heapq.heappop(leaves)
            edges.append((u, x))
            deg[u] -= 1
            deg[x] -= 1
            if deg[x] == 1:
                heapq.heappush(leaves, x)
        u = heapq.heappop(leaves)
        v = heapq.heappop(leaves)
        edges.append((u, v))
        yield edges


def build(n, edges):
    e = [[] for _ in range(n + 1)]
    for u, v in edges:
        e[u].append(v)
        e[v].append(u)
    return e


def all_dist(n, e):
    dist = [[10**9] * (n + 1) for _ in range(n + 1)]
    for s in range(1, n + 1):
        q = deque([s])
        dist[s][s] = 0
        while q:
            x = q.popleft()
            for y in e[x]:
                if dist[s][y] > dist[s][x] + 1:
                    dist[s][y] = dist[s][x] + 1
                    q.append(y)
    return dist


def exact(n, edges):
    e = build(n, edges)
    dist = all_dist(n, e)
    leaves = [i for i in range(1, n + 1) if len(e[i]) == 1]
    best = -1
    cnt = 0
    witnesses = []
    for a, b in combinations(leaves, 2):
        path = [
            v for v in range(1, n + 1)
            if dist[a][v] + dist[v][b] == dist[a][b]
        ]
        H = max(
            min(dist[x][v] for v in path)
            for x in range(1, n + 1)
        )
        val = H * dist[a][b]
        if val > best:
            best = val
            cnt = 1
            witnesses = [(a, b, H, dist[a][b])]
        elif val == best:
            cnt += 1
            witnesses.append((a, b, H, dist[a][b]))
    return best, cnt, witnesses


def candidate(n, edges):
    e = build(n, edges)
    fa = [0] * (n + 1)

    def calc(root, parent):
        fa[root] = parent
        for y in e[root]:
            if y != parent:
                calc(y, root)

    calc(1, 0)
    ans = 0
    cnt = 0
    details = []

    for i in range(1, n + 1):
        d = [0] * (n + 1)
        d[fa[i]] = 1

        def dfs(root, parent):
            if root == 0:
                return 0
            ma = 0
            for y in e[root]:
                if y == parent:
                    continue
                d[y] = d[root] + 1
                ma = max(ma, d[y])
                ma = max(ma, dfs(y, root))
            return ma

        dfs(fa[i], i)

        # 原代码强行至少为 1。
        ma = 1
        for j in range(1, n + 1):
            ma = max(ma, d[j])

        ma1 = ma2 = 0
        for y in e[i]:
            if y == fa[i]:
                continue
            c = dfs(y, i) + 1
            if c >= ma1:
                ma2, ma1 = ma1, c
            elif c > ma2:
                ma2 = c

        tot = max(ma1 + ma2, 1)
        res = ma * tot
        details.append((i, ma, ma1, ma2, tot, res))

        if res > ans:
            ans = res
            cnt = 1
        elif res == ans:
            cnt += 1

    return ans, cnt, details


def search():
    first_positive_value = None
    first_count_only = None

    for n in range(2, 8):
        for edges in trees_prufer(n):
            t = exact(n, edges)
            c = candidate(n, edges)

            if t[0] > 0 and t[0] != c[0] and first_positive_value is None:
                first_positive_value = (n, edges, t, c)

            if (
                t[0] > 0
                and t[0] == c[0]
                and t[1] != c[1]
                and first_count_only is None
            ):
                first_count_only = (n, edges, t, c)

        if first_positive_value and first_count_only:
            break

    return first_positive_value, first_count_only


if __name__ == "__main__":
    # 最小 H=0 边界错：唯一叶子对覆盖全树。
    e2 = [(1, 2)]
    print("n=2 boundary:", "true=", exact(2, e2), "candidate=", candidate(2, e2))
    assert exact(2, e2)[:2] == (0, 1)
    assert candidate(2, e2)[:2] == (1, 2)

    # 正值核心模型反例。
    core = [(3, 1), (4, 1), (1, 2), (2, 5)]
    print("core n=5:", "true=", exact(5, core), "candidate=", candidate(5, core))
    assert exact(5, core)[:2] == (4, 1)
    assert candidate(5, core)[:2] == (3, 4)

    value_cex, count_cex = search()
    print("first positive-value mismatch:", value_cex)
    print("first positive count-only mismatch:", count_cex)

    print("PASS")
