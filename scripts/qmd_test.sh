#!/bin/bash
set -e

echo "QMD Installation Check"
echo "--------------------"
which qmd || echo "QMD not in PATH"
/root/.bun/bin/qmd --version || echo "QMD version check failed"

echo -e "\nIndexing Test"
echo "-------------"
/root/.bun/bin/qmd index /data/workspace/memory || echo "Indexing failed"

echo -e "\nSearch Test"
echo "------------"
/root/.bun/bin/qmd search "OpenClaw configuration" || echo "Search test failed"