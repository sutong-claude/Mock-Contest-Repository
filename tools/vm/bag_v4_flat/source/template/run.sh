#!/usr/bin/env bash
set -u
cd "$(dirname "$0")" || exit 1
exec python3 .bag_runner.py "$@"
