#!/bin/bash
set -x

# Use explicit path to QMD
QMD="/root/.bun/bin/qmd"

# Check QMD status
"$QMD" status

# List collections
"$QMD" collection list

# Simple search test
"$QMD" search "OpenClaw" -c memory-dir