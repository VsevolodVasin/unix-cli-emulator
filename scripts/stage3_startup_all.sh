#!/usr/bin/env bash
# Стартовый скрипт: команды прошлых этапов + deep VFS
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/deep.json --script startups/stage3_all.txt
