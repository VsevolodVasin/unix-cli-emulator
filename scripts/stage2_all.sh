#!/usr/bin/env bash
# Оба параметра: --vfs и --script
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/placeholder --script startups/stage2_demo.txt
