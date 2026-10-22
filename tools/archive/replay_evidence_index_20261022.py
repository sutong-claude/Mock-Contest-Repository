#!/usr/bin/env python3
"""Index a user's own *extracted* desktop contest Replay without reading keystrokes/clipboard/video.
Usage: python replay_evidence_index.py /path/to/Desktop /path/to/output
By default outputs only event metadata, file hashes and session summaries.
--private-code outputs source snapshots; NEVER publish those without a privacy review.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,collections
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('desktop',type=Path)
    ap.add_argument('output',type=Path)
    ap.add_argument('--private-code',action='store_true',help='Write private source snapshots; do not publish')
    a=ap.parse_args()
    base=a.desktop.resolve();dest=a.output.resolve()
    if not base.is_dir():ap.error('desktop is not a directory')
    if dest==base or base in dest.parents:ap.error('output must not be nested inside desktop to prevent re-indexing')
    dest.mkdir(parents=True,exist_ok=True)
    events=[];summaries=[];sources=[];issues=[]
    for first in sorted(base.rglob('AI_READ_FIRST.txt')):
        if first.parent.parent.name!='contest_capture':continue
        session=first.parent; rel=session.relative_to(base).as_posix()
        mf=session/'manifest.json'
        try: m=json.loads(mf.read_text(encoding='utf-8'))
        except (FileNotFoundError,ValueError) as ex:issues.append((rel,'manifest',str(ex)));m={}
        changes=session/'file_changes.jsonl'
        counter=collections.Counter();count=0
        if changes.exists():
            for lineno,line in enumerate(changes.read_text(encoding='utf-8').splitlines(),1):
                if not line.strip():continue
                try: d=json.loads(line)
                except ValueError as ex:issues.append((rel,f'line {lineno}',str(ex)));continue
                count+=1
                code=d.get('path','').lower().endswith(('.cpp','.cc','.c','.h','.hpp','.py'))
                raw=d.get('content')
                real=hashlib.sha256(raw.encode('utf8')).hexdigest() if isinstance(raw,str) else ''
                stored=d.get('sha256') or ''
                if raw is not None and stored and stored!=real:issues.append((rel,f'line {lineno}','source_sha256_mismatch'))
                counter[d.get('path','')]+=1
                events.append([rel,lineno,d.get('t',''),d.get('kind',''),d.get('path',''),d.get('bytes',''),stored,real,bool(code),bool(raw)])
                if a.private_code and code and raw:
                    sources.append({'session':rel,'line':lineno,'t':d.get('t'),'path':d.get('path'),'sha256':stored,'content':raw})
        summaries.append({'session':rel,'start':m.get('start'),'end':m.get('end'),
                          'manifest_status':m.get('status'),'file_events':count,
                          'screen_files':len(list(session.glob('screen_*.mkv'))),
                          'top_paths':counter.most_common(25),
                          'note':'saved file does not prove OJ submission or validated algorithm'})
    with (dest/'event_metadata.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['session','line','relative_seconds','kind','path','bytes','reported_sha256','recomputed_sha256','is_source','has_nonempty_content']);w.writerows(events)
    with (dest/'session_summary.json').open('w',encoding='utf8') as f:json.dump(summaries,f,ensure_ascii=False,indent=2)
    if a.private_code:
        with (dest/'PRIVATE_code_history.jsonl').open('w',encoding='utf8') as f:
            for row in sources:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    with (dest/'integrity_issues.json').open('w',encoding='utf8') as f:json.dump(issues,f,ensure_ascii=False,indent=2)
    print('sessions',len(summaries),'events',len(events),'private source snapshots',len(sources),'issues',len(issues))
    if issues: print('First issues:',issues[:5])

if __name__=='__main__':main()
