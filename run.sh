#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ -d .venv ]; then
  source .venv/bin/activate
fi

cd src
python3 main.py
