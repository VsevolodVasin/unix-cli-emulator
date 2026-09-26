#!/usr/bin/env bash
# VFS с глубиной >= 3
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/deep.json --script startups/stage2_empty_exit.txt
