#!/usr/bin/env bash
# Тест команд этапа 4 на deep VFS
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/deep.json --script startups/stage4_commands.txt
