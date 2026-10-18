#!/usr/bin/env python3
"""Executable integration tests: failed source never freezes; exact tested byte SHA is recorded."""
import json
import tempfile
from pathlib import Path
from contest_submission_gate import run, sha256


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        ws = root / 'workspace'
        ws.mkdir()
        frozen = root / 'frozen'
        src = ws / 'probe.cpp'
        # OI-style file IO (not stdin/stdout). The binary must read probe.in and write probe.out.
        good = ('#include <fstream>\nint main(){std::ifstream in("probe.in");'
                'std::ofstream out("probe.out");int x;in>>x;out<<x+1<<"\\n";}\n')
        bad = good.replace('x+1', 'x')
        man = root / 'case.json'
        man.write_text(json.dumps({'tasks':[{'name':'probe','cases':[
            {'label':'increment','input':'4\n','expected':'5\n'}]}]}))
        src.write_text(bad)
        r = run(man, ws, frozen)
        assert not r['success'] and not frozen.exists(), 'FAIL CLOSED: wrong code froze'
        src.write_text(good)
        r = run(man, ws, frozen)
        assert r['success'] and r['frozen'], r
        data = json.loads((frozen / 'freeze_manifest.json').read_text())
        assert data['source_hashes']['probe'] == sha256(src)
        assert (frozen / 'probe.cpp').read_text() == good
        src.write_text(bad)
        r = run(man, ws, frozen)
        assert not r['success']
        assert (frozen / 'probe.cpp').read_text() == good, 'Previous tested version overwritten'
    print('PASS: rejects wrong; freezes correct SHA; rejects regression; preserves last verified source')


if __name__ == '__main__':
    main()
