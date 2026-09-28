#!/usr/bin/env bash
# uniq на multi VFS (файл с повторами)
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/multi.json --script startups/stage4_uniq.txt
