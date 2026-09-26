#!/usr/bin/env bash
# Минимальная VFS
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/minimal.json --script startups/stage2_empty_exit.txt
