#!/usr/bin/env bash
# Только --vfs (без --script)
set -e
cd "$(dirname "$0")/.."
printf 'ls\nexit\n' | ./run.sh --vfs vfs/placeholder
