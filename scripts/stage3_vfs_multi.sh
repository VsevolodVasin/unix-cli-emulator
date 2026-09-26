#!/usr/bin/env bash
# VFS с несколькими файлами
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/multi.json --script startups/stage2_empty_exit.txt
