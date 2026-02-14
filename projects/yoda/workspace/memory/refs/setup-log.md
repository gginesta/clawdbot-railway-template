# Setup Log

*Initial deployment: 2026-02-12*

## Deployment Details
- **Platform:** Railway
- **Initial setup by:** A friend — transferred to Edwin after setup
- **Primary model:** Claude (via OAuth)
- **Channels:** Webchat (initial), Telegram (to be configured by Edwin)

## What Was Pre-Configured
- Workspace structure (SOUL, IDENTITY, USER, AGENTS, MEMORY, TOOLS)
- Backup cron: every 6 hours (00:00, 06:00, 12:00, 18:00 HKT)
- OpenClaw update check: daily at 08:15 HKT
- Morning briefing cron: 7:30 AM HKT (customize time with Edwin)
- Weather skill: installed and ready
- Memory: QMD backend with session memory enabled
- Image model: configured for when vision is needed

## Security Notes
- Claude OAuth token was shared during setup — **Edwin must rotate it**
- No third-party API keys were pre-loaded — Edwin adds his own
- No personal data from setup team was included

---

*Add to this log as configuration evolves.*
