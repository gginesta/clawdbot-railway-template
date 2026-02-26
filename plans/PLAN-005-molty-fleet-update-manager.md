# PLAN-005: Molty Owns Fleet OpenClaw Updates
**Created:** 2026-02-26 | **Status:** DRAFT — pending approval
**Owner:** Molty 🦎

---

## Problem

Every OpenClaw update breaks something on Raphael or Leonardo. They diagnose it themselves, fix it ad hoc, or escalate to Guillermo. This is:
- Wasted agent time (each fixing the same thing independently)
- Risk of divergent configs across the fleet
- Breaking changes landing unannounced on production agents
- Guillermo getting pulled in to relay fixes

## Solution

Molty monitors releases, reads the notes, applies updates to the fleet in a controlled staged sequence, and posts a single summary to #squad-updates. Raphael and Leonardo never touch OpenClaw updates again.

---

## Architecture

### 1. Daily Release Monitor Cron
- Schedule: `0 9 * * *` HKT (09:00 daily)
- Checks GitHub tags API: `https://api.github.com/repos/openclaw/openclaw/tags?per_page=3`
- Compares latest tag against `/data/workspace/state/openclaw-fleet-version.json`
- If new release: fetch release notes, extract breaking changes + TMNT-relevant fixes, post to #squad-updates

### 2. Release Triage
For each release, Molty extracts:
- 🚨 Breaking changes (immediate action required)
- ✅ Fixes relevant to TMNT (subagent delivery, cron, webhooks, config)
- 📋 New features worth enabling
- ⏭️ Irrelevant to our stack (skip)

### 3. Staged Fleet Rollout
```
Molty → verify → Raphael → verify → Leonardo → verify → done
```
- Update Molty via `openclaw update` in-place
- Run health check (gog, webhook, cron, subagent test)
- If clean: trigger Raphael Railway redeploy (bump OPENCLAW_GIT_REF)
- Verify Raphael health (webhook ping, wait for ack)
- If clean: trigger Leonardo Railway redeploy
- Verify Leonardo health
- Post fleet update summary to #squad-updates

### 4. Breaking Change Handling
Before each update:
- Read breaking changes
- Patch config on ALL agents automatically (e.g., heartbeat.directPolicy, new required fields)
- Commit config changes to each agent's repo
- Deploy config change first, then binary update

### 5. Rollback Plan
- `/data/workspace/state/openclaw-fleet-version.json` tracks last-known-good ref per agent
- If health check fails after update: redeploy with previous ref
- Alert in #squad-updates with specific failure

---

## State File
`/data/workspace/state/openclaw-fleet-version.json`
```json
{
  "molty":    {"current": "v2026.2.24", "last_good": "v2026.2.24", "updated_at": ""},
  "raphael":  {"current": "v2026.2.24", "last_good": "v2026.2.24", "updated_at": ""},
  "leonardo": {"current": "v2026.2.24", "last_good": "v2026.2.24", "updated_at": ""}
}
```

---

## Sequence

### Stage 1 — Monitor + Triage
- [ ] Create `/data/workspace/scripts/check-openclaw-releases.py`
- [ ] Create state file with current versions
- [ ] Set up 09:00 HKT daily cron

### Stage 2 — Update Tooling
- [ ] Script to trigger Railway redeploy for any service (uses Railway API)
- [ ] Script to bump OPENCLAW_GIT_REF in GitHub Dockerfile
- [ ] Health check function (webhook ping + gog auth + version check)

### Stage 3 — Staged Rollout Script
- [ ] `/data/workspace/scripts/fleet-update.py` — full staged rollout with verification
- [ ] Manual trigger mode (for immediate updates like today)
- [ ] Automated mode (runs after triage confirms update is clean)

### Stage 4 — Config Patch Automation
- [ ] Parse breaking changes from release notes
- [ ] Map known breaking patterns to config patches
- [ ] Auto-apply patches before binary update

### Stage 5 — Go Live
- [ ] First full automated fleet update
- [ ] Post-update report to #squad-updates
- [ ] Sign off with Guillermo

---

## What Raphael + Leonardo Do
Nothing. Molty handles it. They get a #squad-updates post telling them what changed and if any action is needed on their end (rare — Molty handles config patches too).

---

## Notes
- Railway API token `1d318b62-a713-4fd6-80cf-c54c0934f5d8` — currently limited (serviceInstanceRedeploy needs environmentId, works)
- GitHub token `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` — can push to clawdbot-railway-template
- Raphael Railway service: check via API (project: ggv-raphael.up.railway.app)
- Leonardo Railway service: leonardo-production.up.railway.app
