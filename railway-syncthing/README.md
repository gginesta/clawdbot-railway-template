# Railway + Syncthing Setup

Real-time file sync between your Windows PC and Molty on Railway.

## Files in This Folder

| File | Purpose |
|------|---------|
| `Dockerfile` | Complete Dockerfile with Syncthing added |
| `supervisord.conf` | Process manager config (runs OpenClaw + Syncthing) |
| `Dockerfile.patch.md` | Detailed explanation of changes |

## Deployment Steps

### 1. Update Your GitHub Fork

Copy these files to your forked repo (`gginesta/clawdbot-railway-template`):

```bash
# On your PC, clone your fork:
git clone https://github.com/gginesta/clawdbot-railway-template.git
cd clawdbot-railway-template

# Copy the new files (or manually paste contents):
# - Replace Dockerfile with the one from this folder
# - Add supervisord.conf to root

git add .
git commit -m "feat: add Syncthing for real-time file sync"
git push
```

### 2. Railway Will Auto-Deploy

Railway watches your repo and will rebuild automatically.

### 3. First-Time Syncthing Setup

After deployment:

1. **Access Syncthing UI:** Go to `https://your-railway-url:8384`
   - ⚠️ Set a GUI password immediately! (Settings → GUI → GUI Authentication)
   
2. **Get Railway's Device ID:**
   - In Syncthing UI: Actions → Show ID
   - Copy the long string (looks like `XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-...`)

3. **Install Syncthing on Windows:**
   - Download from: https://syncthing.net/downloads/
   - Run it (will open web UI at http://localhost:8384)

4. **Pair Your Devices:**
   - In Windows Syncthing: Add Remote Device → paste Railway's Device ID
   - In Railway Syncthing: Accept the incoming connection

5. **Create Shared Folder:**
   - In Railway Syncthing: Add Folder
   - Path: `/data/shared`
   - Share with: Your Windows device
   - In Windows Syncthing: Accept the folder, choose local path (e.g., `C:\Molty-Shared`)

### 4. Test the Sync

1. Create a file on your Windows PC in the shared folder
2. Within seconds, it should appear on Railway at `/data/shared/`
3. I (Molty) can now read/write files there!

## Folder Structure Suggestion

```
/data/shared/
├── inbox/          # Drop files here for me to process
├── outbox/         # Files I create for you
├── projects/       # Active work
└── reference/      # Documents I should know about
```

## Security Notes

- **Set GUI password** immediately after first deployment
- Consider using Tailscale to access Syncthing UI instead of exposing port 8384 publicly
- Syncthing sync traffic (port 22000) is encrypted

## Troubleshooting

**Syncthing UI not loading?**
- Check Railway logs for Syncthing errors
- Ensure port 8384 is exposed in Railway settings

**Devices not connecting?**
- Both devices need to add each other
- Check firewall on Windows isn't blocking Syncthing
- Verify Device IDs are correct

**Sync is slow?**
- Initial sync of many files takes time
- Check Railway container has enough resources
