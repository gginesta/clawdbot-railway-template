#!/bin/bash
# Install Chromium to persistent volume (only runs once)
# Add this to your Railway startup or run manually after deploy

CHROMIUM_MARKER="/data/.openclaw/chromium-installed"

if [ -f "$CHROMIUM_MARKER" ]; then
    echo "✅ Chromium already installed (marker exists)"
    exit 0
fi

echo "📦 Installing Chromium..."
apt-get update
apt-get install -y --no-install-recommends chromium

# Create marker file
echo "installed=$(date -Iseconds)" > "$CHROMIUM_MARKER"
echo "✅ Chromium installed successfully"
