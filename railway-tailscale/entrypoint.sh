#!/bin/bash
set -e

# Start Tailscale if auth key is provided
if [ -n "$TAILSCALE_AUTHKEY" ]; then
    echo "🔐 Starting Tailscale daemon..."
    tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
    
    # Wait for daemon to be ready
    sleep 3
    
    echo "🔗 Connecting to Tailscale network..."
    tailscale up \
        --authkey="$TAILSCALE_AUTHKEY" \
        --hostname="${TAILSCALE_HOSTNAME:-openclaw-railway}" \
        --accept-routes \
        --accept-dns=false
    
    echo "✅ Tailscale connected!"
    echo "📍 Tailscale IP: $(tailscale ip -4 2>/dev/null || echo 'pending')"
else
    echo "⚠️  TAILSCALE_AUTHKEY not set - Tailscale disabled"
    echo "   Set it in Railway variables if you want private network access"
fi

# Start OpenClaw server
echo "🚀 Starting OpenClaw..."
exec node src/server.js
