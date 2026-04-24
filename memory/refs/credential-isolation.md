# Credential Isolation — Agent Volume Rules
<!-- Last updated: molty | 2026-04-24 | REG-042 credential isolation failure -->

## The Rule
**Agent-scoped credentials MUST live in `/data/.openclaw/` (private volume), NEVER in `/data/shared/`.**

`/data/shared/` is Syncthing-synced across ALL agents. Anything stored there is readable by every agent in the fleet.

## Why This Exists
On 2026-04-24, Raphael's `gog` CLI defaulted to `/data/shared/credentials/gog/` and picked up April's OAuth token (`april.rose.hk@gmail.com`) instead of his own credentials. This is a credential cross-contamination failure. Logged as REG-042.

## Per-Agent Credential Paths

| Agent | Private Volume | gog config path | gws config path |
|-------|---------------|-----------------|-----------------|
| Molty 🦎 | `/data/.openclaw/` | `~/.config/gog/` (default, local) | `~/.config/gws/` |
| Raphael 🔴 | `/data/.openclaw/` | `/data/.openclaw/gog-raphael/` (empty — no gog) | N/A |
| Leonardo 🔵 | `/data/.openclaw/` | `/data/.openclaw/gog-leonardo/` (empty — no gog) | N/A |
| April 🌸 | `/data/.openclaw/` | `/data/.openclaw/gog/` ← **MUST set on redeploy** | `/data/.openclaw/gws/` |

## What Lives Where

### ✅ `/data/.openclaw/` (private — agent-only)
- Google OAuth tokens (`gog`, `gws`)
- Anthropic tokens
- Discord bot tokens
- Telegram bot tokens
- Any credential that is agent-specific

### ✅ `/data/shared/` (shared — fleet coordination only)
- Health status files (`health/<agent>.json`)
- Agent-link scripts
- Memory vault contributions
- Shared scripts
- **NO credentials, NO tokens, NO OAuth material**

## April Redeploy Checklist (credential isolation)
Before bringing April back online, set these Railway env vars:

```
GOG_CONFIG_DIR=/data/.openclaw/gog
GWS_CONFIG_DIR=/data/.openclaw/gws
```

Then migrate her credentials:
1. Copy `/data/shared/credentials/gog/` → April's private volume at `/data/.openclaw/gog/`
2. Remove or empty `/data/shared/credentials/gog/` after migration
3. Verify `gog whoami` returns `april.rose.hk@gmail.com` on April only

## Enforcement
- REGRESSIONS.md: REG-042
- Before any agent redeploy: verify credential paths point to `/data/.openclaw/` not `/data/shared/`
- Railway env var `GOG_CONFIG_DIR` is the override — always set explicitly on non-Molty agents
