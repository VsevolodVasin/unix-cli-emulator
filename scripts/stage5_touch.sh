#!/usr/bin/env bash
# Тест touch и связанных сценариев (этап 5)
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/deep.json --script startups/stage5_touch.txt
