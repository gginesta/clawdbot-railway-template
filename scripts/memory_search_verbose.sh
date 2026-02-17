#!/bin/bash
export PATH="/root/.bun/bin:$PATH"

echo "QMD Collections:"
qmd collection list

echo -e "\nTesting Search in memory-dir:"
qmd search "OpenClaw" -c memory-dir --json

echo -e "\nTesting Vector Search in sessions:"
qmd vsearch "TMNT" -c sessions --json

echo -e "\nTesting Query Mode:"
qmd query "memory framework" --json