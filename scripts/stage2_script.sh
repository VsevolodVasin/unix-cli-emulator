#!/usr/bin/env bash
# Только --script
set -e
cd "$(dirname "$0")/.."
./run.sh --script startups/stage2_demo.txt
