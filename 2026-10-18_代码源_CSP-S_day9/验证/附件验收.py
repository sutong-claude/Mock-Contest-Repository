#!/usr/bin/env python3
"""Run actual final C++ against private Desktop/T1..T4 input/output attachments.
Usage: python3 附件验收.py /private/Desktop [--ubsan]
"""
from pathlib import Path
import argparse,subprocess,tempfile,hashlib,time,json
p=argparse.ArgumentParser();p.add_argument('desktop',type=Path);p.add_argument('--ubsan',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parents[1];rows=[]
with tempfile.TemporaryDirectory() as d:
 for i,name in enumerate(['A_hitori','B_ryo','C_nijika','D_xor'],1):
  source=root/'正解代码'/(name+'.cpp');exe=Path(d)/name
  flags=['-O1','-g','-fsanitize=undefined','-fno-sanitize-recover=all'] if a.ubsan else ['-O2']
  subprocess.run(['g++','-std=c++17','-DLOCAL',*flags,str(source),'-o',str(exe)],check=True)
  inputs=sorted((a.desktop/f'T{i}').glob('*.in'));assert inputs,f'No inputs for T{i}'
  for inp in inputs:
   start=time.perf_counter();r=subprocess.run([str(exe)],input=inp.read_bytes(),capture_output=True,timeout=40,check=True)
   ok=r.stdout.split()==inp.with_suffix('.out').read_bytes().split() and not r.stderr
   row=dict(code=name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),input=inp.name,input_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),ok=ok,seconds=round(time.perf_counter()-start,4));rows.append(row);assert ok,row
Path('附件重验.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('PASS',len(rows))
