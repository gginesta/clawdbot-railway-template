# PLAN-021 Research Notes — Agent-Link Security

*Compiled: 2026-03-25 | Author: Molty*

---

## What I Read

1. **OpenClaw docs: `/automation/hooks.md`** — Internal event hooks (command:new, session events, etc). NOT what we need for webhook verification.
2. **OpenClaw docs: `/automation/webhook.md`** — HTTP webhook endpoints. This is the system we use. Key findings below.
3. **LumaDock tutorial: "OpenClaw webhooks explained"** — Practical guide. Confirms transforms are the right approach.
4. **Fieldy-AI-Webhook skill** — Real-world example of `transformsDir` + `transform.module` in production.
5. **clawctl skill** — Official OpenClaw fleet coordination skill. Exists but has only 2 installs. Worth investigating as a potential replacement for our custom agent-link.

---

## Key Findings

### Transform Module System

From the docs:
- `hooks.transformsDir` sets where transform JS/TS modules live
- `transform.module` on a mapping loads a module from that directory
- Docs say: "must stay within the transforms root under your OpenClaw config directory (typically `~/.openclaw/hooks/transforms`)"
- **BUT:** The fieldy-ai-webhook skill sets `transformsDir` to `/root/clawd/skills/fieldy/scripts` — outside `~/.openclaw/`. So the constraint may not be enforced, or was relaxed.

### What Likely Caused My Crash

Looking at the actual config after the crash, `transformsDir` was set to `/data/.openclaw/hooks/transforms` (the default) instead of `/data/workspace/hooks` (what I tried to set). The `transform` block on the mapping was also stripped.

Possible causes:
1. **Config patch merge behavior** — my patch may have been partially applied, setting `transformsDir` default while the transform block was rejected
2. **Compaction/restart timing** — a compaction happened right after my config patch, which triggered a restart. The config may not have been fully written before the restart.
3. **Path validation rejection** — OpenClaw may have silently rejected my `transformsDir` because it was outside the config directory

**Next step:** Put the transform file where OpenClaw expects it (`/data/.openclaw/hooks/transforms/`) instead of fighting the path system.

### Webhook Endpoint Behavior

- `POST /hooks/agent` — the endpoint our worker calls. Takes `message`, `sessionKey`, etc.
- Currently: worker sends tmnt-v1 JSON as the `message` field. Agent receives it as text.
- With a mapping: can intercept `/hooks/agent` path, run transform, then forward

### Alternative: No Transform Needed

Re-reading the docs, I realize there might be a simpler approach:

**Option A: Transform at gateway (what I tried, crashed)**
- Pros: Verification before agent sees the message. Clean separation.
- Cons: Requires gateway config change. One mistake = offline.

**Option B: Transform in the sender (worker side)**
- Instead of sending raw tmnt-v1 JSON, the worker could:
  1. Verify its own signature (sanity check)
  2. Format the message as plain text with `[SIGNED:hmac-sha256:abc123]` prefix
  3. Send via standard `/hooks/agent` endpoint with the message field
  4. Receiving agent checks the prefix, runs verification via exec
- Pros: No gateway config changes. Zero crash risk.
- Cons: Relies on agent following AGENTS.md instructions to verify. Session amnesia risk.

**Option C: Use clawctl (existing fleet skill)**
- OpenClaw already has an official fleet coordination skill: `clawctl`
- Provides: inter-agent messaging, task orchestration, activity feeds
- Only 2 installs, so it's new/untested in the wild
- Worth investigating before building our own

### Community Patterns

- **builderz-labs/mission-control** — Has HMAC-SHA256 webhook verification built in. Their model: outbound webhooks with delivery history, retry, circuit breaker, and HMAC.
- **clawctl** — Official OpenClaw fleet skill. Inter-agent messaging built in.
- **fis-architecture** — Multi-agent workflow using JSON tickets and file-based coordination.
- The community is converging on webhook-based coordination but no dominant pattern yet.

---

## Revised Plan

### Phase 1: Fix the Transform (Properly This Time)

1. Copy `verify-tmnt.cjs` to `/data/.openclaw/hooks/transforms/verify-tmnt.cjs` (where the gateway expects it)
2. Verify the file is loadable: `node -e "require('/data/.openclaw/hooks/transforms/verify-tmnt.cjs')"`
3. Apply config patch with `transformsDir` pointing to the default location
4. **TEST ON MOLTY ONLY** — verify gateway restarts cleanly
5. If it fails, the revert is simple: remove the mapping (no transform loading = no crash)

### Phase 2: Fleet Rollout

1. Copy transform file to each agent via Syncthing (`/data/shared/hooks/transforms/`)
2. Each agent copies to their local `/data/.openclaw/hooks/transforms/` via startup script
3. Config patch on each agent (one at a time, verify between each)

### Phase 3: Package as Shareable Skill

Structure:
```
agent-link-secure/
├── SKILL.md              # Instructions for the agent
├── scripts/
│   ├── agent-link-worker.py    # Sending (with HMAC signing)
│   ├── agent_link_signing.py   # Signing module
│   └── verify-tmnt.cjs         # Gateway transform
├── setup/
│   └── configure.sh            # Sets up transformsDir, copies files, patches config
└── references/
    └── ARCHITECTURE.md         # How it all fits together
```

### Decision: Transform vs. No-Transform

I recommend **Option A (gateway transform)** because:
- Code enforcement > documentation (SOUL.md principle)
- Agents can't forget to verify — invalid messages never reach them
- Clean separation of concerns
- One-time setup, zero ongoing maintenance

But I'll do it properly:
- Put files where the gateway expects them
- Test locally before patching config
- Have a rollback plan ready
- One agent at a time

---

## Open Questions

1. Should we evaluate `clawctl` before building more custom infrastructure?
2. Is the `transformsDir` constraint real or just documentation? (The fieldy skill violates it)
3. Should the transform also handle non-fleet webhooks gracefully, or should fleet messages use a dedicated endpoint (e.g., `/hooks/fleet` instead of `/hooks/agent`)?
