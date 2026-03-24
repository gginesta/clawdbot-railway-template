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

## Discord User IDs (for @mentions)
| User | ID | Mention Format |
|------|-----|----------------|
| Guillermo | `779143499655151646` | `<@779143499655151646>` |
| Molty | `1468162520958107783` | `<@1468162520958107783>` |
| Raphael | `1468164929285783644` | `<@1468164929285783644>` |
| Leonardo | `1470919061763522570` | `<@1470919061763522570>` |
| April | `1481167770191401021` | `<@1481167770191401021>` |

**Note:** Plain `@Name` doesn't ping. Must use `<@USER_ID>` format.

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

**Vercel Projects (Domain/Hosting):**
| Project | URL | Purpose |
|---------|-----|---------|
| ginesta-site | https://ginesta.io | Guillermo family landing page |
| helmcl | https://helmcl.com | Helm Consulting placeholder |

---

## Namecheap

**Account:** gginesta
**API Key:** `fd3a6f8b61794e23aef787c6ac4a1233`
**Whitelisted IP:** `54.241.162.49` (Railway outbound)

**Domain Portfolio:**
australvc.com, australventures.com, digitalfingerprint.io, findinggiants.blog, ginesta.io, helmcl.com, helmconsulting.io, helmconsultingltd.com, manacapital.io, manacapital.xyz, manainnovation.com, meetcerebro.com, seltzersake.com

**Domains in Use (2026-03-24):**
| Domain | Points To | Status |
|--------|-----------|--------|
| ginesta.io | Vercel (76.76.21.21) | ✅ Live |
| helmcl.com | Vercel (76.76.21.21) | ✅ Live |
| helmconsulting.io | → helmcl.com redirect | ✅ Live |
| helmconsultingltd.com | → helmcl.com redirect | ✅ Live |

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

## Overnight Schedule (HKT)
| Time | Agent | Focus |
|------|-------|-------|
| 00:30 | Raphael 🔴 | Brinc proposals, sales |
| 01:30 | Leonardo 🔵 | Cerebro, ventures |
| 02:00 | April 🌸 | Family, Steph tasks, research |
| 03:00 | Molty 🦎 | Consolidation, fleet |

## Paperclip

| What | Value |
|------|-------|
| URL | https://paperclip-production-83f5.up.railway.app |
| Railway Project | `03da4228-5b2e-4b15-be2e-44f81352224f` |
| Login | guillermo.ginesta@gmail.com / TmntPaperclip2026! |
| Fleet Creds | `/data/.openclaw/paperclip-fleet-credentials.json` |
| Skill | `/data/shared/skills/paperclip/SKILL.md` |

**Molty's Keys (CEO in all 3):**
| Company | Agent ID | Token Prefix |
|---------|----------|-------------|
| TMNT Squad | `0e4e3ca3-...` | `pcp_5c669...` |
| Brinc | `d46b6609-...` | `pcp_04dac...` |
| Cerebro | `ff8f1f31-...` | `pcp_a1c05...` |

**Other Agents:**
| Agent | Company | Agent ID | Token Prefix |
|-------|---------|----------|-------------|
| April | TMNT Squad | `0fb8e023-...` | `pcp_869b9...` |
| Raphael | Brinc | `93db3fa0-...` | `pcp_2f841...` |
| Leonardo | Cerebro | `0c2e90aa-...` | `pcp_2eceb...` |

---

## Webhook Tokens (Change Ticket #001 — Feb 24 2026)
| Agent | Inbound Token | Status |
|-------|---------------|--------|
| Molty | `ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562` | ✅ Active |
| Raphael | `ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd` | ✅ Active (old shared) |
| Leonardo | `08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758` | ✅ Active (new) |
| April | `7159178afb1c2c24b1e98bbbac0f0f02dc759aa038cd49ae7fac7873d8acf3ee` | ✅ Active |

## Leonardo Webhook
- **URL:** `https://leonardo-production.up.railway.app/hooks/agent`
- **Token (active):** `08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758`

## April Webhook
- **URL:** `https://april-agent-production.up.railway.app/hooks/agent`
- **Token (active):** `7159178afb1c2c24b1e98bbbac0f0f02dc759aa038cd49ae7fac7873d8acf3ee`

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
