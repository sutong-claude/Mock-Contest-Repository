#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TARGET="${1:-all}"
STAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p .history

make_one(){
  local k="$1"
  if [ -d "$k" ]; then mv "$k" ".history/${k}_${STAMP}"; fi
  mkdir "$k"
  python3 - "$k" <<'PY2'
from pathlib import Path
import shutil,sys
root=Path.cwd()
k=sys.argv[1]
src=root/'.flat_template'
dst=root/k
for p in src.iterdir():
    if p.is_file():
        shutil.copy2(p,dst/p.name)
PY2
  chmod +x "$k/run.sh" "$k/duipai.sh" "$k/.bag_runner.py"
  echo "$k reset; old folder -> .history/${k}_${STAMP}"
}

case "$TARGET" in
  purge)
    echo "This will DELETE .history (old problem folders)."
    read -r -p "confirm purge? (y/N) " a
    [ "$a" = "y" ] || [ "$a" = "Y" ] || exit 0
    rm -rf .history
    echo ".history purged"
    ;;
  all)
    for k in T1 T2 T3 T4; do make_one "$k"; done
    ;;
  T1|T2|T3|T4)
    make_one "$TARGET"
    ;;
  *)
    echo "usage: bash reset.sh [T1|T2|T3|T4|all|purge]"
    exit 2
    ;;
esac
