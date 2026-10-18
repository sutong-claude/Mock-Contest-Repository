#!/usr/bin/env bash
set -u
cd "$(dirname "$0")" || exit 1
N="${1:-0}"
exec bash run.sh p "$N"
