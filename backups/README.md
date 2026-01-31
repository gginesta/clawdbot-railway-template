# Backups

This folder contains backup scripts and config exports for disaster recovery.

## Quick Recovery

1. **Workspace** → Push to GitHub (see below)
2. **Config** → `config-export.json` (sanitized, no secrets)
3. **Full backup** → Run `backup.sh` to create tarball

## GitHub Backup (Recommended)

```bash
# Create a private repo on GitHub, then:
cd /data/workspace
git remote add origin git@github.com:YOUR_USER/molty-workspace.git
git push -u origin master
```

After that, I'll auto-commit changes and you can push periodically.

## Files in this folder

- `config-export.json` — Sanitized OpenClaw config (no tokens/passwords)
- `backup.sh` — Creates timestamped tarball of /data
- `RECOVERY.md` — Step-by-step restore instructions
