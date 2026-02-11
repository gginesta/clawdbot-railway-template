# MEMORY.md - Long-Term Memory

*Created: 2026-02-11*

---

## 🖥️ System Architecture

### Hosting
- **Platform:** Railway (Docker containers)
- **Template:** https://github.com/gginesta/clawdbot-railway-template
- **Volume:** `/data` (persistent storage)
- **URL:** https://leonardo-production.up.railway.app

### Fleet
| Agent | Role | Emoji | Status |
|-------|------|-------|--------|
| Molty | Coordinator | 🦎 | ✅ Active |
| Raphael | Brinc (Corporate) | 🔴 | ✅ Active |
| Leonardo | The Launchpad (Venture Building) | 🔵 | 🆕 Deploying |
| Donatello | Tinker Labs (Research) | 🟣 | ⏳ Planned |

### Communication
- **Discord:** TMNT Squad server
- **Webhooks:** For urgent cross-agent comms
- **Coordinator:** Molty 🦎 handles fleet ops

---

## 🚀 The Launchpad

### Mission
Take validated ideas from Donatello's lab and build them into real ventures.

### Sub-Projects
| Project | Status | Description |
|---------|--------|-------------|
| **Cerebro** | 🆕 Starting | AI-powered venture platform |

---

## 📋 Lessons Learned (Fleet-Wide)

1. **BACKUP BEFORE UPDATE** — Non-negotiable. Run backup.sh before any update.
2. **One config change at a time** — Don't bundle changes. Use gateway config.patch.
3. **Research before config edits** — If config.patch rejects, STOP. Don't brute-force.
4. **Do it yourself first** — Don't give Guillermo instructions when you have access.
5. **Write it down** — Mental notes don't survive. Files do.
6. **Always think in HKT** — System clock is UTC, Guillermo is in Hong Kong.

---

*This file is your curated long-term memory. Daily logs go in `memory/YYYY-MM-DD.md`.*
