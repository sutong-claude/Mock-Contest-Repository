#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for x in g++ python3; do command -v "$x" >/dev/null || { echo "MISSING: $x"; exit 1; }; done
for k in T1 T2 T3 T4; do
  [ -d "$k" ] || { echo "MISSING: $k"; exit 1; }
  for f in main.cpp WA.cpp gen.cpp notes.txt run.sh duipai.sh .bag_runner.py AC.cbp; do
    [ -e "$k/$f" ] || { echo "MISSING: $k/$f"; exit 1; }
  done
done
echo "DOCTOR: OK — flat T1..T4, g++, python3"
if command -v codeblocks >/dev/null 2>&1; then echo "Code::Blocks: $(command -v codeblocks)"; else echo "Code::Blocks: not found here (test on NOI Linux VM)"; fi
FREE_KB=$(df -Pk . | awk 'NR==2 {print $4}')
if [ -n "$FREE_KB" ]; then
  FREE_MB=$((FREE_KB/1024))
  echo "Disk free: ${FREE_MB} MiB"
  if [ "$FREE_MB" -lt 2048 ]; then echo "WARN: less than 2 GiB free."; fi
fi
