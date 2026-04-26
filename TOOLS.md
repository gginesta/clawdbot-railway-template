# TOOLS.md - Local Notes

## 📧 Email Lanes (STRICT — no cross-contamination)
| Agent | Email | Use for |
|-------|-------|--------|
| **Molty 🦎** | `ggv.molt@gmail.com` | Fleet coordination, personal assistant tasks |
| **Raphael 🔴** | `salesops@brinc.io` | Brinc sales, outreach, CRM |
| **April 🌸** | `april.rose.hk@gmail.com` | Personal/family tasks for Guillermo |
| **Leonardo 🔵** | TBD | Cerebro/venture work |

**Rule:** Never authenticate or send email from another agent's account. Credentials are agent-scoped. gog/gws credentials only restore for Molty on startup (enforced in Dockerfile).
**⚠️ REG-042:** Agent credentials MUST live in `/data/.openclaw/` (private), NEVER `/data/shared/` (synced to all agents). Full isolation rules: `memory/refs/credential-isolation.md`

## 🧾 Summarize CLI
`summarize` v0.11.1 | yt-dlp `/usr/local/bin/yt-dlp` | ffmpeg `/usr/local/bin/ffmpeg`
Config: `~/.summarize/config.json` (Gemini 2.5 Flash). Skill: `/openclaw/skills/summarize/SKILL.md`
Works: web articles, direct audio/video. Blocked: YouTube + podcast RSS (Railway IPs blocked)



## Discord
Channel map + user IDs: `memory/refs/fleet-channels.md`
**Rule:** Don't own a channel → stay silent unless @mentioned or Guillermo asks.

---

## 📅 Calendar Booking Rules — STANDING RULE (confirmed Guillermo 2026-03-03)

### Calendar IDs
| Calendar | ID | Access | Write rule |
|----------|-----|--------|------------|
| Brinc | `guillermo.ginesta@brinc.io` | ✅ | Brinc work events — visible to colleagues |
| Personal | `guillermo.ginesta@gmail.com` | ✅ | Personal / Mana / Molty infra |
| **Shenanigans** | `vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com` | ✅ | Family events |

**Service account:** `molty-assistant@molty-assistant-487823.iam.gserviceaccount.com`
**Full config:** `/data/workspace/credentials/calendar-config.json`

### Booking Rules
1. Check ALL 3 calendars for conflicts before booking
2. Family → Shenanigans | Personal/work → Personal | Brinc → Brinc calendar
3. Every non-Brinc booking → also add "Busy [private]" block on Brinc calendar

### Protected Slots
| Slot | Days | Type |
|------|------|------|
| 08:00–08:30 | Mo/We/Fr | School drop-off (LOCKED) |
| 10:30–11:00 | Mo/We/Fr | School pick-up |
| 08:30–10:30 | We/Fr | Focus time — no calls |

---

## 📧 Google Workspace — gws CLI (primary)

| What | Value |
|------|-------|
| CLI | `gws` v0.4.4 (@googleworkspace/cli) |
| Account | `ggv.molt@gmail.com` |
| Scopes | gmail, calendar, drive, docs, sheets, slides, tasks, people, presentations (9 total) |
| Config | `~/.config/gws/` |
| Backup | `/data/workspace/credentials/gws-config-backup/` |
| Skills | gws-calendar, gws-gmail, gws-drive, gws-docs, gws-sheets + shared |

### Legacy: gog CLI (deprecated)
`gog` v0.11.0 — superseded by gws. Keyring: `GOG_KEYRING_PASSWORD="molty2026"`

---

## Notion

| What | Value |
|------|-------|
| API Key | `$NOTION_API_KEY` (Railway env var) |
| Space ID | `375629bd-cc72-4ad8-a3be-84139fa2fb3b` |
| Standup DB | `2fe39dd69afd81f189f7e58925dad602` |
| token_v2 | `/data/workspace/credentials/notion-token-v2.txt` (session cookie — expires) |
| Internal API | `https://www.notion.so/api/v3/` + `Cookie: token_v2=...` |

---

## Railway

**Auth:** Workspace API token (scope: gginesta's Projects)
**Token:** `$RAILWAY_API_TOKEN` (Railway env var)
**API:** `https://backboard.railway.app/graphql/v2` (Bearer auth)
**Projects:** Molty, Raphael, Leonardo, webclaw, cerebro, wonderful-harmony

---

## Google / Gemini

| What | Value |
|------|-------|
| API Key (Molty) | `$GEMINI_API_KEY` (Railway env var) |
| Project | gen-lang-client-0128730112 (project 226575193033) |
| Creds file | `/data/workspace/credentials/gemini.env` |
| Status | Free tier |

---

## Vercel

| What | Value |
|------|-------|
| Token | `$VERCEL_TOKEN` (Railway env var) |
| Project | tmnt-mission-control |
| URL | https://tmnt-mission-control.vercel.app |

**Vercel Projects:** ginesta-site (ginesta.io), helmcl (helmcl.com)

---

## Namecheap

**Account:** gginesta
**API Key:** `$NAMECHEAP_API_KEY` (Railway env var)
**Whitelisted IP:** `54.241.162.49` (Railway outbound)

**Active domains:** ginesta.io + helmcl.com → Vercel. Full portfolio in `memory/refs/infrastructure.md`

---

## Convex / Mission Control

| What | Value |
|------|-------|
| HTTP API | https://resilient-chinchilla-241.convex.site |
| MC API Key | `$MC_API_KEY` (Railway env var) |
| MC Heartbeat Cron | `46d1ca32-0bd0-43f4-bfa9-3e9e385271cd` (every 2h, Haiku) |
| MC Skill | `/data/workspace/skills/mission-control/SKILL.md` |

---

## GitHub

**Token:** `$GITHUB_TOKEN` (Railway env var) — rotated 2026-04-26
**Note:** Env var name is `GITHUB_TOKEN`. Redeploy required after rotation to take effect.

---

## Twitter/X — USE x-reader SKILL
**Account:** @Molton_Sanchez | Read-only (bot detection blocks posting)

---

## Overnight Schedule (HKT)
Raphael 00:30 | Leonardo 01:30 | April 02:00 | Molty 03:00

## Paperclip
URL: https://paperclip-production-83f5.up.railway.app | Login: `$PAPERCLIP_LOGIN`/`$PAPERCLIP_PASSWORD`
Fleet creds + agent IDs: `memory/refs/paperclip-creds.md`

## Webhooks
All tokens in Railway env vars (`$WEBHOOK_TOKEN_<AGENT>`). All active.
- Leonardo: `https://leonardo-production.up.railway.app/hooks/agent`
- April: `https://april-agent-production.up.railway.app/hooks/agent`

---

## 🧠 Cerebro — Molty's Account

| What | Value |
|------|-------|
| URL | https://www.meetcerebro.com |
| Email | molty@meetcerebro.com |
| Password | `$CEREBRO_PASSWORD` (Railway env var) |
| Tier | owner |
| is_admin | TRUE |
| Dashboard | https://www.meetcerebro.com/admin/dashboard |
| User ID | afb0dca9-7176-49ab-b5d0-98d61253f7c6 |
