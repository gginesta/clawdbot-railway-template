# PLAN-006: Fleet Directive System
**Created:** 2026-02-27 | **Status:** ✅ COMPLETE (core system live — secrets migration deferred)
**Owner:** Molty 🦎

---

## Problem

Molty needs to send automated, version-gated commands to Raphael/Leonardo without
manual Discord messages. Prior ad-hoc approach caused two incidents:

1. Secrets migration script sent before verifying agent version → partial config corruption
2. HTTP 200 health check mistaken for version confirmation → `state.json` stale

---

## Solution: Startup-Based Directive Queue

### Directory structure
```
/data/shared/pending-directives/
  molty/
  raphael/
  leonardo/
  done/
    molty/
    raphael/
    leonardo/
```

### Directive format
```bash
#!/bin/bash
# DIRECTIVE: <slug>
# REQUIRES_VERSION: v2026.2.26
# REQUIRES_VERSION_OP: >=
# IDEMPOTENT: true
# POSTED_BY: molty
# POSTED_AT: 2026-02-27T11:00:00+08:00
```

### Execution model (no cron — startup only)
- **Molty writes a directive** → `write_directive.py` auto-triggers Railway redeploy for target agent
- **Agent boots** → `startup.sh` checks queue → runs pending directives → starts gateway
- **Zero idle credit cost** — only fires when there's actual work
- Original design had 15-min cron; scrapped as wasteful (Guillermo Feb 27)

### Key scripts
- `/data/shared/scripts/check_directives.py` — runner (shared, all agents)
- `/data/workspace/scripts/write_directive.py` — writer (Molty-local, auto-triggers redeploy)
- `startup.sh` (Dockerfile) — hooks into boot, runs directives before supervisord

---

## Stages

### Stage 1 — Infrastructure ✅
- [x] Directory structure at `/data/shared/pending-directives/`

### Stage 2 — Runner script ✅
- [x] `check_directives.py` written and tested on Molty
- [x] Version gating (REQUIRES_VERSION header), idempotency, done/ archive, .result files

### Stage 3 — Writer helper ✅
- [x] `write_directive.py` — Molty-local, auto-triggers Railway redeploy on write

### Stage 4 — Dockerfile startup hook ✅
- [x] Startup hook added to `gginesta/clawdbot-railway-template` (commit `83d3a3b2`)
- [x] Runs `check_directives.py <agent>` at boot if pending directives exist
- [x] No standing cron needed on Raphael/Leonardo

### Stage 5 — Secrets migration via directives ⚠️ DEFERRED
- [ ] Raphael + Leonardo secrets migration NOT done via directives
- **Blocker:** `/data/shared/credentials/secrets.json` on world-readable directory
  (`/data/shared/` = 755) → OpenClaw rejects filemain provider → agents crash on boot
- **Correct approach:** Use `source: "env"` Railway env vars for Anthropic/Google tokens
  (not filemain file provider). No shared volume needed.
- **Current state:** Raphael + Leonardo on plaintext tokens — functionally identical to
  before; no security regression from pre-migration state

---

## Incident Log (Feb 27)

1. Triggered Leonardo redeploy to run secrets migration directive
2. New Dockerfile startup hook ran `apply-secrets.sh` → migrated API keys to filemain refs
3. Gateway failed: "secrets.providers.filemain.path permissions too open" (parent dir 755)
4. Multiple failed rollback attempts — tokenRef in auth-profiles.json broke even v2026.2.25
5. Fixed via start command injection (`fix-leonardo-full.sh`): restored plaintext tokens,
   stripped secrets config from openclaw.json
6. Leonardo stable on v2026.2.26 with plaintext tokens by 13:40 HKT

**Lesson #87:** OpenClaw `filemain` secrets provider checks parent directory permissions,
not just the file. `/data/shared/` (755) fails this check. Use `source: "env"` for secrets
on shared infrastructure. File-based secrets require a path where the entire parent chain
is owner-only (e.g., `/data/.openclaw/` which is 700).

---

## Remaining Work (PLAN-007 candidate)

- [ ] Migrate Raphael + Leonardo Anthropic token to Railway env var (`ANTHROPIC_API_KEY`)
  and use `source: "env"` ref in auth-profiles.json
- [ ] Same for Google token if needed
- [ ] Run `openclaw secrets audit` on all three agents — target: zero actionable findings
- [ ] Audit hardcoded tokens in Python scripts (Todoist, Notion, MC API key, GitHub)
