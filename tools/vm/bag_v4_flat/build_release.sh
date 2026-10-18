#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/source"
OUT="${1:-$ROOT/dist}"

rm -rf "$OUT"
mkdir -p "$OUT/bag/.flat_template"

cp "$SRC/README.txt" "$OUT/bag/README.txt"
cp "$SRC/doctor.sh" "$OUT/bag/doctor.sh"
cp "$SRC/reset.sh" "$OUT/bag/reset.sh"
cp -a "$SRC/template/." "$OUT/bag/.flat_template/"

chmod +x "$OUT/bag/doctor.sh" "$OUT/bag/reset.sh"
chmod +x "$OUT/bag/.flat_template/run.sh" "$OUT/bag/.flat_template/duipai.sh" "$OUT/bag/.flat_template/.bag_runner.py"

for t in T1 T2 T3 T4; do
  cp -a "$OUT/bag/.flat_template" "$OUT/bag/$t"
done

(cd "$OUT" && zip -qr bag_v4_flat_integrated.zip bag)
sha256sum "$OUT/bag_v4_flat_integrated.zip"
echo "release: $OUT/bag_v4_flat_integrated.zip"
