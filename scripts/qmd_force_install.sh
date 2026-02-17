#!/bin/bash

# Install Bun if not already installed
if ! command -v bun &> /dev/null; then
    curl -fsSL https://bun.sh/install | bash
    export PATH="$HOME/.bun/bin:$PATH"
fi

# Force install QMD globally with Bun
bun install -g qmd@latest
npm install -g qmd@latest

# Verify installation
which qmd
qmd --version

# Create symlinks to ensure availability
sudo ln -sf "$(which qmd)" /usr/local/bin/qmd