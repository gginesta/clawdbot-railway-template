# Disaster Recovery Guide

## If Railway instance is lost

### 1. Redeploy from template
```bash
# Use the same Railway template
# vignesh07/clawdbot-railway-template
```

### 2. Restore from GitHub (if pushed)
```bash
cd /data
git clone git@github.com:YOUR_USER/molty-workspace.git workspace
```

### 3. Restore config
Copy `config-export.json` to `/data/.openclaw/openclaw.json` and add back:
- `channels.telegram.botToken` — Get from @BotFather
- `gateway.auth.token` — Generate new: `openssl rand -hex 32`

### 4. Restore from tarball (if available)
```bash
cd /data
tar -xzf molty-backup-XXXXXXXX-XXXXXX.tar.gz
```

### 5. Re-pair Telegram
Send `/pair` to your bot — you may need to re-pair since device tokens change.

### 6. Restart gateway
```bash
openclaw gateway restart
```

## Environment Variables (Railway)

Make sure these are set in Railway:
- `ANTHROPIC_API_KEY` — Your Claude API key

## Key setup choices we made

- **Chromium** added to Dockerfile for browser automation
- **Port 8080** exposed for Control UI (VPN-protected)
- **`dangerouslyDisableDeviceAuth: true`** for web access
- **Telegram** connected to @gginesta (id: 1097408992)
