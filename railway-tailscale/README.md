# Adding Tailscale to OpenClaw Railway Template

## Quick Steps

### 1. Fork the template repo
- Go to [github.com/vignesh07/clawdbot-railway-template](https://github.com/vignesh07/clawdbot-railway-template)
- Click **Fork** (top right)
- This creates `github.com/YOUR_USERNAME/clawdbot-railway-template`

### 2. Get a Tailscale auth key
- Go to [login.tailscale.com/admin/settings/keys](https://login.tailscale.com/admin/settings/keys)
- Click **"Generate auth key..."**
- Settings:
  - ✅ **Reusable** (so Railway redeploys work)
  - ✅ **Ephemeral** (nodes auto-cleanup when stopped)
  - Expiration: 90 days (or longer)
- Copy the key (starts with `tskey-auth-...`)

### 3. Replace files in your fork
Replace these files with the versions in this folder:
- `Dockerfile` — adds Tailscale installation
- `entrypoint.sh` — starts Tailscale before OpenClaw (NEW FILE)

### 4. Update Railway to use your fork
- Go to Railway dashboard → your project → Settings
- Change the GitHub repo to your fork
- Or: delete the service and create a new one pointing to your fork

### 5. Add environment variables in Railway
Go to Railway → Variables and add:
```
TAILSCALE_AUTHKEY=tskey-auth-xxxxx
TAILSCALE_HOSTNAME=openclaw
```

### 6. Redeploy
Railway will rebuild with Tailscale. Check deployment logs for:
```
🔐 Starting Tailscale daemon...
🔗 Connecting to Tailscale network...
✅ Tailscale connected!
📍 Tailscale IP: 100.x.x.x
```

### 7. Access via Tailscale
Once deployed, your OpenClaw appears in your Tailscale network:
- Tailscale admin: [login.tailscale.com/admin/machines](https://login.tailscale.com/admin/machines)
- Access URL: `http://<tailscale-ip>:8080/`

### 8. (Optional) Disable public URL
Once Tailscale works, you can disable Railway's public networking:
- Railway → Settings → Networking → Disable public domain

Now your OpenClaw is only accessible via Tailscale! 🔒

---

## Files in this folder

- `Dockerfile` — modified to include Tailscale
- `entrypoint.sh` — starts Tailscale then OpenClaw
- `README.md` — this file
