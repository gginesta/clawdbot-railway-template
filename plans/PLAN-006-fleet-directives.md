# PLAN-006: Fleet Directive System
**Created:** 2026-02-27 | **Status:** IN PROGRESS
**Owner:** Molty 🦎

---

## Problem

Molty sends directives to Raphael/Leonardo via Discord messages or webhooks.
Agents read them and act — but there's no guarantee of timing, ordering, or
confirmation. Two incidents this session:

1. Secrets migration script sent before verifying Raphael was on v2026.2.26 —
   partially corrupted his config (Raphael caught and rolled back).
2. Fleet update health check (HTTP 200) doesn't confirm actual running version —
   `state.json` showed `v2026.2.26` for Raphael before he'd actually updated.

---

## Root Causes

1. **Health check was too shallow** — `/health` returns 200 even on old version.
   Fixed in fleet-update.py: webhook-updated agents now marked `pending_update`,
   not confirmed, until they self-report.

2. **No version gate before sending version-dependent scripts** — secrets
   migration used `openclaw secrets` which only exists in v2026.2.26. Script
   ran on v2026.2.25 and partially mutated config before failing.

3. **No structured directive system** — everything is ad-hoc Discord messages.
   No ordering, no preconditions, no confirmation loop.

---

## Solution: Shared Directive Queue

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

### Directive file format
```
/data/shared/pending-directives/<agent>/<YYYYMMDD>-<seq>-<slug>.sh
```

Example: `20260227-001-secrets-migration.sh`

Each directive is a shell script with a header:
```bash
#!/bin/bash
# DIRECTIVE: secrets-migration
# REQUIRES_VERSION: v2026.2.26        ← gate: skip if agent is older
# REQUIRES_VERSION_OP: >=             ← gte check
# IDEMPOTENT: true                    ← safe to re-run
# POSTED_BY: molty
# POSTED_AT: 2026-02-27T11:00:00+08:00
```

### Directive runner (`check_directives.py`)
Each agent runs this every 15 min via cron:

1. Scan `/data/shared/pending-directives/<agent>/` for `.sh` files
2. For each (sorted by filename = chronological):
   - Parse header to check `REQUIRES_VERSION` — skip if agent is older
   - Run: `bash <file>`, capture stdout/stderr + exit code
   - On success: move to `done/<agent>/` + write `.result` metadata file
   - On failure: write `.result` with error, leave in queue (retry next cycle)
   - On version skip: leave in queue (will re-check next cycle after update)
3. Post to #command-center if any directives ran or failed
4. Log to `/data/workspace/logs/directives-YYYY-MM-DD.log`

### Molty directive writer (`write_directive.py`)
Helper for Molty to create directives without manual file writing:

```python
write_directive(
    agent="raphael",
    slug="secrets-migration",
    script_path="/data/shared/credentials/apply-secrets.sh raphael",
    requires_version="v2026.2.26",
    idempotent=True,
)
```

Integrated into fleet-update.py for post-update config tasks.

---

## Sequence

### Stage 1 — Infrastructure ✅ (done)
- [x] Directory structure created at `/data/shared/pending-directives/`

### Stage 2 — Runner script
- [ ] Write `/data/shared/scripts/check_directives.py` (shared — all agents use same script)
- [ ] Test on Molty: drop a test directive, verify it runs and moves to done/

### Stage 3 — Writer helper
- [ ] Write `/data/workspace/scripts/write_directive.py` (Molty-local)
- [ ] Integrate into fleet-update.py: after confirmed update, queue version-dependent tasks

### Stage 4 — Bootstrap Raphael + Leonardo
- [ ] Add 15-min cron to Raphael + Leonardo (one-time Discord message — last manual step)
- [ ] Drop secrets migration as a proper directive (with REQUIRES_VERSION: v2026.2.26)
- [ ] Verify it runs and posts to #command-center

### Stage 5 — Document + add to AGENTS.md
- [ ] Add directive protocol to AGENTS.md
- [ ] Document in MEMORY.md
- [ ] Update fleet-update.py to use write_directive for all post-update tasks

---

## Preconditions gate (lesson from today)

Before ANY version-dependent script is sent fleet-wide:
1. Confirm each agent's actual running version (not just health 200)
2. For webhook-updated agents: version is UNCONFIRMED until they self-report
3. Only queue directives for agents whose version satisfies REQUIRES_VERSION

This is enforced by the directive runner — it parses the header and skips
directives the agent isn't ready for.

---

## Blast radius

- `/data/shared/pending-directives/` — new shared volume directory
- `/data/shared/scripts/check_directives.py` — new shared script
- `/data/workspace/scripts/write_directive.py` — Molty-local writer
- `fleet-update.py` — integrated post-update directive queuing
- New 15-min cron on each agent (bootstrap step)
- No changes to openclaw.json, auth, or existing crons

---

## Lessons Learned

- **Lesson added to MEMORY.md:** health check ≠ version confirmed for async webhook updates
- **Never run version-dependent scripts without confirmed version gate**
- **fleet-update.py now marks remote agents as `pending_update`, not `current`**
