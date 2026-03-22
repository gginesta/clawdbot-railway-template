# TMN-9: Fleet-Wide Config Management — Design Analysis
<!-- agent: molty | type: decision | priority: P2 | date: 2026-03-23 -->

**Issue:** TMN-9 | **Status:** Blocked → Under Review  
**Written by:** Molty 🦎 | **Date:** 2026-03-23 03:00 HKT  
**Goal:** Enable Molty (or Guillermo) to push OpenClaw config changes to all 4 agents without manual relay.

---

## Context

Each Railway agent has its own non-shared volume at `/data/.openclaw/openclaw.json`. There is no SSH access, no shared filesystem for `/data/.openclaw/`, and Syncthing only syncs `/data/shared/`.

**Key discovery from this analysis:** OpenClaw already supports reading values from external sources via its `secrets.providers` mechanism:
- `secrets.providers.filemain` → reads from `/data/shared/credentials/secrets.json` (shared across all agents via Syncthing)
- Individual config values can reference this: `{"source": "file", "provider": "filemain", "id": "/path"}`

This means a partial solution already exists — it just hasn't been fully exploited.

**Security constraints in force:**
- REG-040: Fleet config changes require Discord approval (not webhooks)
- REG-033: No version bumps without explicit same-session approval
- 2026-03-21: Webhook spoofing incident — two suspicious tmnt-v1 webhooks claimed to be Molty. Trust in webhook-sourced config changes is LOW.

---

## Option Analysis

### Option 1: Shared config template in Syncthing `/data/shared/`

**Mechanism:** Store a fleet config overrides file in `/data/shared/config/fleet-overrides.json`. Each agent's heartbeat script checks for changes and applies them via `gateway config.patch`.

**Pros:**
- Syncthing infrastructure already exists and works
- `/data/shared/config/` directory already exists
- `filemain` secret provider already reads from `/data/shared/credentials/` — proven pattern
- Instant propagation (Syncthing runs continuously)
- Changes don't require Railway redeployment
- Molty acts as the write gate — changes go through Discord approval, then Molty writes the file

**Cons:**
- Requires code change to heartbeat scripts on each agent to check + apply overrides
- Agent must be alive to pick up changes (no boot-time mechanism without additional change)
- Syncthing hub-and-spoke: if Molty is down, fleet-overrides.json won't propagate (REG-028)
- Must carefully limit what keys can be overridden (block security-critical keys)
- Risk: file could grow stale or conflict if multiple agents write to it

**Verdict:** ✅ Best operational option for non-secret behavior changes. Proven pattern.

---

### Option 2: Railway API env var overrides

**Mechanism:** Use Railway GraphQL API to set env vars that OpenClaw reads as config. Requires Railway redeploy per agent.

**Pros:**
- Railway API already available (token in TOOLS.md)
- Full audit trail in Railway dashboard
- Approval gate: Railway restart = visible operational event

**Cons:**
- Railway CLI not available inside containers — must call GraphQL API directly
- Config changes require service restart (brief downtime, cold boot)
- Not all OpenClaw config is settable via env vars — only `env.vars` section
- Must know exact env var → config mapping (no documentation found)
- Restarting 4 agents sequentially = operational risk
- Slow: 4 separate API calls + 4 restart waits

**Verdict:** ⚠️ Viable for env-var-backed settings only. Not suitable for structural config changes. High operational overhead.

---

### Option 3: Fleet config endpoint on each agent's webhook

**Mechanism:** Add a `/fleet/config` endpoint to each agent that accepts authenticated config patches from Molty.

**Pros:**
- Clean API design
- Real-time application
- Agent-link v2 HMAC signing could provide authentication

**Cons:**
- **Security: 2026-03-21 webhook spoofing incident makes this HIGH RISK**
- REG-040: Config changes must go through Discord approval — a webhook endpoint bypasses this
- Requires code change to OpenClaw (upstream fork needed)
- Even with HMAC auth, this creates a code-execution pathway from network to config
- If agent-link token is compromised, all 4 agents could be misconfigured simultaneously

**Verdict:** ❌ Not recommended. Security risk outweighs convenience. Rejected.

---

### Option 4: Config-as-code in the template repo

**Mechanism:** Store fleet baseline config in `clawdbot-railway-template/` as a versioned `fleet-config.json`. Each Railway deploy applies it.

**Pros:**
- Full git history = audit trail
- PR-based = Guillermo approval built into the workflow
- Clean infrastructure-as-code
- Handles structural changes (channels, model configs, behavior flags) well

**Cons:**
- Requires redeploy for every change (downtime, slow)
- Cannot hold per-agent secrets (would be in git)
- Per-agent customization needs templating logic
- Overnight operational changes (quick behavioral tweak) are impractical via this path

**Verdict:** ✅ Best for baseline structural config. Not for quick operational changes.

---

## Recommended Approach: Two-Phase Hybrid

### Phase A — "Config-as-code baseline" (Option 4, immediately actionable)

For structural config (channels, model settings, feature toggles):
1. Add a `fleet-config.json` to the template repo containing shared baseline settings
2. Deploy script merges this into each agent's `openclaw.json` on boot (using a start script)
3. Changes go through git PR → merge → Railway redeploy (Guillermo approval = PR merge)
4. Per-agent overrides stay in individual `openclaw.json` files (not in fleet-config)

**What goes in fleet-config.json:** channel config, model defaults, feature toggles, behavior flags  
**What stays per-agent:** Discord tokens, API keys, gateway bind address, identity

---

### Phase B — "Shared overrides via Syncthing" (Option 1, quick operational changes)

For quick runtime changes that shouldn't require redeployment:
1. Create `/data/shared/config/fleet-overrides.json` — Syncthing distributes to all agents
2. Add to each agent's heartbeat script: check `fleet-overrides.json` timestamp, apply via `gateway config.patch` if newer than last applied
3. Store `last_applied` hash in `/data/shared/config/.fleet-overrides-applied-{agent}.txt` to avoid re-applying
4. **Hard allowed-list of patchable keys** — only non-security keys (feature flags, model preferences, etc.) — block `gateway.bind`, `auth.*`, `secrets.*`, channel tokens

**Approval gate (mandatory):**
- Guillermo approves change in #command-center Discord
- Molty writes to `/data/shared/config/fleet-overrides.json`
- Syncthing propagates to all agents within ~30s
- Next heartbeat (~2h cycle) or manual `/reload` picks it up

---

## Security Guardrails (Non-Negotiable)

Regardless of which approach is chosen, these constraints apply:
1. **No config changes without Guillermo Discord approval** (REG-040)
2. **Allowed-list only** — explicit whitelist of safe-to-override config keys
3. **No secret values in fleet-overrides.json** — use `filemain` references for secrets
4. **Immutable log** — every fleet config change appended to `/data/shared/logs/fleet-config-changes.log`
5. **Rollback mechanism** — each agent keeps `openclaw.json.bak` before applying any override (already happens via OpenClaw's native backup behavior)

---

## Implementation Estimate

| Phase | Effort | Risk | Value |
|-------|--------|------|-------|
| Phase A (config-as-code baseline) | 2-3h | Low | High |
| Phase B (shared overrides via Syncthing) | 3-4h | Medium | High |
| Combined | ~1 day | Low-Medium | Very High |

---

## Decision Needed from Guillermo

1. **Which phase to start with?** A (structural, git-based) or B (operational, Syncthing-based), or both in sequence?
2. **What config changes are you actually trying to make?** The right mechanism depends on what needs to change fleet-wide. If it's mostly "add a new skill to all agents" → Phase A. If it's "toggle a behavior flag quickly" → Phase B.
3. **Approve the allowed-list of patchable keys** before Phase B is implemented.

---

## Files Referenced
- `/data/.openclaw/openclaw.json` — Molty's config (reviewed 2026-03-23)
- `/data/shared/credentials/secrets.json` — existing shared secrets (providers + profiles keys)
- `/data/shared/config/embedding_standard.json` — existing shared config pattern
- `REGRESSIONS.md` — REG-033, REG-040 constraints

*Molty 🦎 | 2026-03-23 03:00 HKT*
