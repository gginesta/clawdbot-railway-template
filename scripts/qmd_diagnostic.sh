#!/bin/bash

echo "🔍 QMD Installation Diagnostic"
echo "-----------------------------"

# Check existing installations
echo "Existing QMD locations:"
which qmd || echo "No QMD found in PATH"
ls /root/.bun/bin/qmd || echo "No QMD in bun bin"
ls /usr/local/bin/qmd || echo "No QMD in usr local bin"
ls /usr/bin/qmd || echo "No QMD in usr bin"

# Try npm installation
echo -e "\n📦 Attempting NPM Installation:"
npm install -g qmd
which qmd || echo "NPM installation failed"

# Try bun installation
echo -e "\n📦 Attempting Bun Installation:"
bun install -g qmd
which qmd || echo "Bun installation failed"

# Diagnostic information
echo -e "\n🛠️ System Information:"
npm --version
bun --version
node --version