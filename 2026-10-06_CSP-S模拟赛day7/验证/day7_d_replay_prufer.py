#!/usr/bin/env python3
"""Day7 D: independent leaf-pair oracle vs a recorded Replay T4/main.cpp version.

Usage:
  python day7_d_replay_prufer.py --day7-zip Day7.zip --version 19 --max-n 6

Inputs come from Day7.zip!Day7/Desktop/contest_capture/20261006_080043/file_changes.jsonl.
The oracle uses only the statement's leaf-pair/path/distance definition.
Requires Python 3, g++; never uploads the raw Replay/keyboard/screen.
"""
import argparse
import collections
import hashlib
import heapq
import itertools
import json
import pathlib
import subprocess
import tempfile
import zipfile

CAPTURE = 'Day7/Desktop/contest_capture/20261006_080043/file_changes.jsonl'


def get_versions(day7_zip):
    with zipfile.ZipFile(day7_zip) as archive:
        rows = [json.loads(line) for line in archive.read(CAPTURE).splitlines() if line]
    versions = [row for row in rows if row.get('path') == 'T4/main.cpp' and row.get('content') is not None]
    assert len(versions) == 20, f'expected 20 saves, got {len(versions)}'
    for row in versions:
        assert hashlib.sha256(row['content'].encode('utf-8')).hexdigest() == row['sha256']
    return versions


def tree_from_prufer(seq):
    n = len(seq) + 2
    degree = [1] * n
    for x in seq:
        degree[x] += 1
    leaves = [x for x in range(n) if degree[x] == 1]
    heapq.heapify(leaves)
    edges = []
    for x in seq:
        y = heapq.heappop(leaves)
        edges.append((x, y))
        degree[x] -= 1
        degree[y] -= 1
        if degree[x] == 1:
            heapq.heappush(leaves, x)
    edges.append((heapq.heappop(leaves), heapq.heappop(leaves)))
    return edges


def oracle(n, edges):
    graph = [[] for _ in range(n)]
    for x, y in edges:
        graph[x].append(y)
        graph[y].append(x)
    leaves = [v for v in range(n) if len(graph[v]) == 1]
    best = -1
    ways = 0
    for a, b in itertools.combinations(leaves, 2):
        parent = {a: -1}
        queue = collections.deque([a])
        while queue and b not in parent:
            x = queue.popleft()
            for y in graph[x]:
                if y not in parent:
                    parent[y] = x
                    queue.append(y)
        path = set()
        x = b
        while x != -1:
            path.add(x)
            x = parent[x]
        dist = {x: 0 for x in path}
        queue = collections.deque(path)
        while queue:
            x = queue.popleft()
            for y in graph[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    queue.append(y)
        score = (len(path) - 1) * max(dist.values())
        if score > best:
            best, ways = score, 1
        elif score == best:
            ways += 1
    return best, ways


def run(binary, n, edges):
    inp = str(n) + '\n' + ''.join(f'{x+1} {y+1}\n' for x, y in edges)
    try:
        result = subprocess.run([str(binary)], input=inp, text=True, capture_output=True, timeout=1)
    except subprocess.TimeoutExpired:
        return ('TIMEOUT',)
    if result.returncode:
        return ('CRASH', result.returncode)
    try:
        return tuple(map(int, result.stdout.strip().split()))
    except ValueError:
        return ('BAD_OUTPUT', result.stdout[:60])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--day7-zip', type=pathlib.Path, required=True)
    ap.add_argument('--version', type=int, default=19, choices=range(1, 21), metavar='1..20')
    ap.add_argument('--max-n', type=int, default=6)
    args = ap.parse_args()
    versions = get_versions(args.day7_zip)
    row = versions[args.version - 1]
    print('source sha256:', row['sha256'], 'capture elapsed:', row['t'])
    with tempfile.TemporaryDirectory() as tmp:
        source, binary = pathlib.Path(tmp)/'candidate.cpp', pathlib.Path(tmp)/'candidate'
        source.write_text(row['content'], encoding='utf-8')
        subprocess.run(['g++', '-std=c++17', '-O2', str(source), '-o', str(binary)], check=True)
        for n in range(2, args.max_n + 1):
            failures = 0
            first_score = first_count = first_any = None
            for seq in itertools.product(range(n), repeat=n - 2):
                edges = tree_from_prufer(seq)
                expected = oracle(n, edges)
                actual = run(binary, n, edges)
                if actual != expected:
                    failures += 1
                    pair = ([(a+1, b+1) for a, b in edges], expected, actual)
                    if first_any is None:
                        first_any = pair
                    if first_score is None and (len(actual) != 2 or actual[0] != expected[0]):
                        first_score = pair
                    if first_count is None and (len(actual) != 2 or actual[1] != expected[1]):
                        first_count = pair
            total = n ** (n - 2)
            print(f'n={n}: {failures}/{total} mismatch; first={first_any}')
            if first_score:
                print('  first score mismatch:', first_score)
            if first_count:
                print('  first count mismatch:', first_count)


if __name__ == '__main__':
    main()
