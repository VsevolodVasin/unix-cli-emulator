#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
  echo "venv создан"
else
  echo "venv уже есть"
fi

source .venv/bin/activate
echo "готово: source .venv/bin/activate"
