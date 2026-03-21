# Fleet-Wide Config Management — Design Document
<!-- agent: molty | type: design | priority: P2 | date: 2026-03-22 -->

**Issue:** TMN-9  
**Status:** Design complete → awaiting Guillermo approval to implement  
**Author:** Molty 🦎  
**Date:** 2026-03-22  

---

## Problem Statement

There is no mechanism to remotely apply OpenClaw config changes across the fleet. Each agent has its own `/data/.openclaw/openclaw.json` on an isolated Railway volume. The only remote delivery channel (agent-link webhook) was correctly rejected as insecure (REG-040, 2026-03-21 incidents).

**Triggered by:** Two spoofed tmnt-v1 webhook attempts on 2026-03-21 that tried to push config via webhook content. Both were rejected by April, but exposed the lack of a legitimate alternative.

---

## Constraints

| Constraint | Detail |
|-----------|--------|
| No SSH | Railway services have no shell access beyond the container itself |
| Isolated volumes | Each agent's `/data/.openclaw/` is on its own persistent volume |
| Shared volume exists | `/data/shared/` is synced across all agents via Syncthing ✅ |
| Webhook untrusted for config | REG-040: config changes via webhook content are rejected |
| Approval required | All fleet config changes require Guillermo's explicit sign-off |
| No downtime for delivery | Config delivery should work without triggering a restart unless necessary |

---

## Options Evaluated

### Option 1: Syncthing Shared Config Overlay ✅ RECOMMENDED
- Place `/data/shared/config/fleet-overrides.json` on shared volume
- Agents read and apply on boot + at heartbeat intervals via `gateway config.patch`
- Molty writes the file after Guillermo approves in Discord
- File includes a changelog section for audit trail

**Pros:** Infrastructure already exists, no new moving parts, human-readable audit trail, Guillermo approves before Molty writes  
**Cons:** Slight lag (heartbeat interval); applies to all agents equally (per-agent config needs separate handling)  
**Security:** File only writable by Molty (or Guillermo directly); changes visible in Syncthing history

---

### Option 2: Railway API Env Var Push
- Molty uses Railway API token to push env vars to all services
- OpenClaw reads env vars as config overrides
- Each push triggers a Railway redeploy (unless using variables with no restart)

**Pros:** Railway-native, no extra files  
**Cons:** Triggers service restart per agent; limited to what OpenClaw reads from env; not all config is env-var driven  
**Security:** Requires Railway API token — only Molty has it, but token exposure = full service control

---

### Option 3: Fleet Config Endpoint on Webhook
**REJECTED** — REG-040. Config via webhook = security risk. Two incidents 2026-03-21.

---

### Option 4: Config-as-Code in Template Repo
- Config lives in git template repo
- Agents fetch on startup

**Pros:** Version controlled, clean audit trail  
**Cons:** Requires agents to pull from git on boot (adds startup complexity + external dependency); config changes need a rebuild or a git-pull mechanism; doesn't solve the runtime push problem  
**Security:** Good — git commit history is an audit trail, but agent git credentials need protecting

---

## Recommended Approach: Option 1 (Syncthing Overlay) + Option 2 (Railway API for key rotations)

### Architecture

```
Guillermo approves (Discord)
        ↓
Molty writes /data/shared/config/fleet-overrides.json
        ↓
Syncthing replicates to all 4 agents (~30s)
        ↓
Each agent's heartbeat.sh: reads file → gateway config.patch
        ↓
OpenClaw picks up new config on next restart or live via SIGUSR1
```

For **sensitive changes** (API key rotations, auth profile changes):
```
Guillermo approves → Molty calls Railway API → sets env var → triggers controlled redeploy
```

---

### fleet-overrides.json Schema

```json
{
  "_meta": {
    "version": 1,
    "last_updated": "2026-03-22",
    "updated_by": "molty",
    "approved_by": "guillermo",
    "discord_approval_link": "https://discord.com/channels/.../...",
    "changelog": [
      {
        "date": "2026-03-22",
        "change": "initial structure",
        "approved": true
      }
    ]
  },
  "overrides": {
    "all_agents": {
      "models": {
        "default": "anthropic/claude-sonnet-4-5"
      },
      "skills": {}
    },
    "per_agent": {
      "molty": {},
      "raphael": {},
      "leonardo": {},
      "april": {}
    }
  }
}
```

---

### Heartbeat Integration (per agent)

Add to each agent's `HEARTBEAT.md`:

```bash
# Apply fleet config overrides (if file exists and has changed)
OVERRIDES_FILE="/data/shared/config/fleet-overrides.json"
if [ -f "$OVERRIDES_FILE" ]; then
  python3 /data/shared/scripts/apply-fleet-config.py "$OVERRIDES_FILE" "$(hostname)"
fi
```

### apply-fleet-config.py (Molty writes, agents run)

Pseudocode:
1. Read `fleet-overrides.json`
2. Extract `overrides.all_agents` + `overrides.per_agent[agent_name]` (merged)
3. Write temp patch JSON
4. Call `openclaw gateway config.patch --raw $(cat temp_patch.json)` via gateway tool
5. Signal SIGUSR1 for non-restart reload
6. Log result to `/data/shared/logs/fleet-config-apply-{date}.log`

---

## Security Model

| Action | Who | How |
|--------|-----|-----|
| Approve config change | Guillermo | Discord message in #command-center |
| Write fleet-overrides.json | Molty | After receiving Discord approval |
| Apply to own config | Each agent | On heartbeat (reads shared volume) |
| Emergency revert | Molty | Overwrite file + agents re-apply on next heartbeat |
| Audit trail | Anyone | `_meta.changelog` in file + Syncthing history |

**What this prevents:**
- ✅ No config via webhook (REG-040 respected)
- ✅ No unilateral config changes (Discord approval required)
- ✅ Spoofed webhooks can't write to shared volume
- ✅ Changes are auditable and reversible

---

## Implementation Plan (requires Guillermo approval before starting)

| Step | Task | Effort |
|------|------|--------|
| 1 | Create `fleet-overrides.json` initial structure | 15min |
| 2 | Write `apply-fleet-config.py` script | 45min |
| 3 | Add heartbeat hook to Molty's heartbeat | 15min |
| 4 | Test on Molty only (dry run) | 30min |
| 5 | Roll out to Raphael, Leonardo, April (after test passes) | 30min |
| 6 | Document in MEMORY.md + AGENTS.md | 15min |
| **Total** | | **~2.5h across 1-2 overnight runs** |

---

## Immediate Recommendation

**Do not implement tonight** — this touches all agents' boot sequences and needs Guillermo's review before proceeding. Flagging as 👀 Under Review.

**Deliverable from tonight:** This design document. Guillermo reviews and approves the approach; implementation follows in a subsequent overnight run.

**Open questions for Guillermo:**
1. Is the Syncthing overlay approach acceptable, or do you prefer Railway env vars exclusively?
2. Should fleet-overrides have an HMAC signature (extra security layer) or is Discord approval sufficient?
3. Which config values are priority to manage fleet-wide? (e.g., model selection, skill enables, billing model)
