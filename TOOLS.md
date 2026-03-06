# TOOLS.md - Local Notes

## 🧾 Summarize CLI (`@steipete/summarize`)

| What | Value |
|------|-------|
| Binary | `summarize` v0.11.1 — globally installed |
| yt-dlp | v2026.02.21 — `/usr/local/bin/yt-dlp` |
| ffmpeg | v7.0.2 static — `/usr/local/bin/ffmpeg` |
| Config | `~/.summarize/config.json` — Gemini 2.5 Flash default |
| Skill | `/openclaw/skills/summarize/SKILL.md` (auto-discovered) |
| Works | Web articles, direct audio/video URLs |
| Blocked | YouTube + podcast RSS — Railway IPs blocked by Google |



## Discord Channel Ownership

| Channel | ID | Owner |
|---------|-----|-------|
| `#command-center` | 1468164160398557216 | **Molty** 🦎 |
| `#squad-updates` | 1468164181155909743 | **Molty** 🦎 |
| `#brinc-general` | 1468164121420628081 | **Raphael** 🔴 |
| `#brinc-private` | 1468164139674238976 | **Raphael** 🔴 |
| `#brinc-marketing` | 1469590792900186245 | **Raphael** 🔴 |
| `#brinc-sales` | 1470416628272463976 | **Raphael** 🔴 |
| `#launchpad-general` | 1470919420791619758 | **Leonardo** 🔵 |
| `#launchpad-private` | 1470919437975814226 | **Leonardo** 🔵 |
| `#launchpad-cerebro` | 1472224798158618735 | **Leonardo** 🔵 |

**Rule:** Don't own it → stay silent unless @mentioned or Guillermo asks.

**Guillermo Discord ID:** `779143499655151646`

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
| What | Value |
|------|-------|
| CLI | `gog` v0.11.0 |
| Keyring | `GOG_KEYRING_PASSWORD="molty2026"` |
| Status | Superseded by gws — keep as fallback |

---

## Notion

| What | Value |
|------|-------|
| API Key | `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` |
| Space ID | `375629bd-cc72-4ad8-a3be-84139fa2fb3b` |
| Standup DB | `2fe39dd69afd81f189f7e58925dad602` |
| token_v2 | `/data/workspace/credentials/notion-token-v2.txt` (session cookie — expires) |
| Internal API | `https://www.notion.so/api/v3/` + `Cookie: token_v2=...` |

---

## Railway

**Auth:** Workspace API token (scope: gginesta's Projects)
**Token:** `1d318b62-a713-4fd6-80cf-c54c0934f5d8`
**API:** `https://backboard.railway.app/graphql/v2` (Bearer auth)
**Projects:** Molty, Raphael, Leonardo, webclaw, cerebro, wonderful-harmony

---

## Google / Gemini

| What | Value |
|------|-------|
| API Key (Molty) | `AIzaSyApzvaLAGWebLU2kRdx8qxC00uBbfYC_bY` |
| Project | gen-lang-client-0128730112 (project 226575193033) |
| Creds file | `/data/workspace/credentials/gemini.env` |
| Status | Free tier |

---

## Vercel

| What | Value |
|------|-------|
| Token | `vcp_7dd90Ihydd6STMuelqNXRCb7eOTfe4oX2HvTDmyLw4PnNpQ4FF1A1Jcg` |
| Project | tmnt-mission-control |
| URL | https://tmnt-mission-control.vercel.app |

---

## Convex / Mission Control

| What | Value |
|------|-------|
| HTTP API | https://resilient-chinchilla-241.convex.site |
| MC API Key | `232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc` |
| MC Heartbeat Cron | `46d1ca32-0bd0-43f4-bfa9-3e9e385271cd` (every 2h, Haiku) |
| MC Skill | `/data/workspace/skills/mission-control/SKILL.md` |

---

## GitHub

**Token:** `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` (classic PAT, expires May 28 2026 — active)

---

## Twitter/X — USE x-reader SKILL
**Account:** @Molton_Sanchez | Read-only (bot detection blocks posting)

---

## Webhook Tokens (Change Ticket #001 — Feb 24 2026)
| Agent | Inbound Token | Status |
|-------|---------------|--------|
| Molty | `ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562` | ✅ Active |
| Raphael | `ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd` | ✅ Active (old shared) |
| Leonardo | `08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758` | ✅ Active (new) |

## Leonardo Webhook
- **URL:** `https://leonardo-production.up.railway.app/hooks/agent`
- **Token (active):** `08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758`

---

## 🧠 Cerebro — Molty's Account

| What | Value |
|------|-------|
| URL | https://www.meetcerebro.com |
| Email | molty@meetcerebro.com |
| Password | Molty2026!Cerebro |
| Tier | owner |
| is_admin | TRUE |
| Dashboard | https://www.meetcerebro.com/admin/dashboard |
| User ID | afb0dca9-7176-49ab-b5d0-98d61253f7c6 |
