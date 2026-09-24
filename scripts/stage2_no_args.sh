#!/usr/bin/env bash
# Запуск без параметров командной строки
set -e
cd "$(dirname "$0")/.."
printf 'ls\nexit\n' | ./run.sh
