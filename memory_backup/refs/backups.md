## 💾 Backup System

### Automated Backups
- **Cron:** Every 6 hours
- **Script:** `/data/workspace/backups/backup.sh`
- **Keeps:** Last 5 tarballs locally

### GitHub Backup
- **Repo:** https://github.com/gginesta/moltybackup (private)
- **Remote:** `backup`
- **Push:** `git push backup master`
- **Note:** Tarballs gitignored (too large), sanitized config pushed

### Recovery Guide
- `/data/workspace/backups/RECOVERY.md`

---
