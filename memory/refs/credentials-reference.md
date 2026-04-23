# Credentials Reference

<!-- Last updated: molty | 2026-04-22 | Key rotation post-leak + auth docs -->

## Auth Architecture

**All secrets live in Railway environment variables ONLY.** Never in files, never in git.
- TOOLS.md documents WHERE to find secrets (variable names), not the values
- `/data/shared/credentials/secrets.json` stores auth profile tokens (read by OpenClaw at runtime)
- This file is on the persistent Railway volume — NOT in git

## Anthropic
- **Auth mode:** `token` (NOT oauth)
- **Env var:** `ANTHROPIC_API_KEY` (Railway)
- **Token type:** `sk-ant-oat01-...` (Anthropic API token, rotated 2026-04-22)
- **Secrets file:** `/data/shared/credentials/secrets.json` → `profiles.anthropic:default.token`
- **Config:** `auth.profiles.anthropic:default.mode = "token"`
- **⚠️ Do NOT change to oauth mode** — causes "OAuth + SecretRef is not supported" error and gateway won't start

## Discord
- **Env var:** `DISCORD_BOT_TOKEN` (Railway, rotated 2026-04-22)
- Bot: Molty | ID: 1468162520958107783

## Discord
- Molty ID: `1468162520958107783` | Raphael: `1468164929285783644` | Leonardo: `1470919061763522570` | April: `1481167770191401021`
- **Bot token:** `DISCORD_BOT_TOKEN` (Railway, rotated 2026-04-22)

## Webhook Tokens (Change Ticket #001 → rotated 2026-04-22)
| Agent | Inbound Token (prefix) | Status |
|-------|----------------------|--------|
| Molty | `ab0100...` | Active |
| Raphael | `ed691...` | Active |
| Leonardo | `08d50...` | Active |
| April | `71591...` | Active |

- Leonardo webhook: `https://leonardo-production.up.railway.app/hooks/agent`
- April webhook: `https://april-agent-production.up.railway.app/hooks/agent`

## Paperclip
- Fleet creds file: `/data/.openclaw/paperclip-fleet-credentials.json`
- Molty CEO keys in TMNT Squad, Brinc, Cerebro (full tokens in fleet creds file)

## Calendar
- SA file: `/data/workspace/credentials/google-service-account.json`
- Cal config: `/data/workspace/credentials/calendar-config.json`
- Calendars: Personal, Brinc, Shenanigans (IDs in TOOLS.md)

## Namecheap
- Full domain list: australvc.com, australventures.com, digitalfingerprint.io, findinggiants.blog, ginesta.io, helmcl.com, helmconsulting.io, helmconsultingltd.com, manacapital.io, manacapital.xyz, manainnovation.com, meetcerebro.com, seltzersake.com

## Vercel Projects (all)
ginesta-site, ginesta-io, buzzrounds, stephrosecounselling, helmcl, tmnt-mission-control, mc-deploy
