#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ -d .venv ]; then
  source .venv/bin/activate
fi

PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -u "$ROOT/src/main.py" "$@"
