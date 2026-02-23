# TOOLS.md - Local Notes

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
| `#brinc-sales` | 1470416628272463976 | **Raphael** 🔴 |

**Forums:** `#squad-decisions` (1470223676845723771), `#project-updates` (1470223696349237445), `#research-findings` (1470223714112245873)

**Rule:** Don't own it → stay silent unless @mentioned or Guillermo asks.

**Guillermo Discord ID:** `779143499655151646`

---

## 📧 Google Workspace — ✅ gog CLI (authed Feb 19)

| What | Value |
|------|-------|
| CLI | `gog` v0.11.0 |
| Account | `ggv.molt@gmail.com` |
| Keyring | `GOG_KEYRING_PASSWORD="molty2026"` |
| Guillermo's email | `guillermo.ginesta@gmail.com` |
| Services | gmail, calendar, drive, docs, sheets, contacts, tasks, chat, forms, slides |
| Calendar access | Service account (R/W all Guillermo's calendars) |
| Legacy script | `/data/workspace/scripts/gmail.sh` (deprecated, replaced by gog) |

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
| **Status** | ⚠️ Free tier — Nano Banana Pro (image gen) needs billing enabled |

Also have keys for Raphael (`...ksug`) and another project (`...8bU4`).

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
| Project | tmnt-mission-control |
| Team | guillermo-ginesta |
| Deployment | dev:resilient-chinchilla-241 |
| URL | https://resilient-chinchilla-241.convex.cloud |
| HTTP API | https://resilient-chinchilla-241.convex.site |
| Dashboard | https://dashboard.convex.dev/t/guillermo-ginesta/tmnt-mission-control |
| MC API Key | `232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc` |
| MC Heartbeat Cron | `46d1ca32-0bd0-43f4-bfa9-3e9e385271cd` (every 2h, Haiku) |
| MC Skill | `/data/workspace/skills/mission-control/SKILL.md` |

---

## GitHub

**Token:** `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`

---

## Twitter/X — USE x-reader SKILL (not bird CLI)

**Account:** @Molton_Sanchez | **Creds:** `/data/workspace/credentials/twitter.env`
**Status:** Read-only (posting blocked by bot detection)

---

## Webhook Tokens (Change Ticket #001 — Feb 24 2026)
| Agent | Inbound Token (they receive) | Status |
|-------|-------------------------------|--------|
| Molty | `ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562` | ✅ Applied |
| Raphael | `a006d3378215cfd0cb6e46e2f67f196e9b8960379370f1e3378a4e1258c07c73` | ⏳ Pending |
| Leonardo | `08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758` | ⏳ Pending |

**Use old shared token for outbound to Raphael/Leonardo until they confirm:**
`ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd`

## Leonardo Webhook
- **URL:** `https://leonardo-production.up.railway.app/hooks/agent`
- **Token (active):** `ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd` *(switch to `08d506d4...` once Leonardo confirms)*
