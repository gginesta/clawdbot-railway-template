# TMNT Change Control + Incident Protocol (v1.0)

*Created: 2026-02-16 | Owner: Guillermo | Maintainers: Molty 🦎 (primary), all leads (secondary)*

## Purpose
Prevent “thrash days” (rapid guessing + cascading fixes) by enforcing a lightweight, auditable process for:
- configuration changes (models, gateway, channels, crons)
- incident response (Telegram/webchat outages, API 400/404 loops, delivery misrouting)

## Definitions
- **Production channels:** Telegram + Webchat (human-facing), Discord (team-facing)
- **Risky change:** anything that can affect delivery, auth, or model routing
  - gateway config changes (`gateway config.patch/apply`, provider/model routing)
  - gateway restarts
  - cron creation/edits, delivery routing
  - channel connector changes (Telegram/webchat)
  - memory automation that reads/writes shared vault

## Non‑negotiable rules
1) **One owner per incident.**
   - Owner is accountable for coordination + final decision.
   - Everyone else supplies evidence, not parallel fixes.

2) **One change per cycle.**
   - Make exactly one change → run acceptance tests → either proceed or rollback.

3) **STOP means STOP.**
   - When Guillermo says stop, all agents cease changes and only answer direct questions.

4) **No live‑fire changes without rollback target.**
   - Every risky change must name the rollback point (backup file / config hash / timestamp).

5) **Maintenance must be isolated.**
   - PARA/guardrails/audits run in **isolated** contexts.
   - Output is a clean summary to Discord only.
   - Never leak tool output into Telegram/webchat.

## Change control workflow (for any risky change)
### Step 0 — Identify
- What is broken / what is being improved?
- Which surfaces are impacted (Telegram/webchat/Discord)?

### Step 1 — Write the change ticket (2 minutes)
Post a single message (in #command-center) containing:
- **Hypothesis:** why this change fixes the problem
- **Change:** exactly what will be changed (1 item)
- **Expected outcome:** what should improve
- **Rollback:** exact rollback target (file/hash/time)
- **Acceptance tests:** 2–4 quick checks (below)

### Step 2 — Approval
- For incidents: incident owner decides and proceeds.
- For non-urgent changes: Guillermo approves.

### Step 3 — Execute
- Apply exactly the change described.
- Restart only if required.
- Do not add “extra” tweaks.

### Step 4 — Acceptance tests (mandatory)
Run the relevant tests and report pass/fail only:
- **Telegram text:** send `Test` → 1 normal reply, no error spam
- **Webchat text:** send `Test` → normal reply, no metadata/tool leakage
- **Cron announce:** force-run light cron → posts to Discord channel only
- **Routing:** verify `delivery.to` uses explicit `channel:<id>` (no raw ids)

### Step 5 — Rollback criteria
If any acceptance test fails:
- rollback immediately to the named target
- do not attempt a second fix until the incident owner posts a new ticket

## Incident protocol (when something breaks)
### Step 1 — Contain
If a human-facing channel is spamming/errors:
- disable the failing channel temporarily (if possible)
- route ops/cron messages to Discord only

### Step 2 — Gather evidence (no fixes yet)
Incident owner requests:
- exact timestamp(s)
- screenshot(s)
- last 50–200 lines of gateway logs around the failure
- current config diff vs last-known-good

### Step 3 — Single fix cycle
Follow change control workflow above.

## Cron hygiene rules
- All ops crons must be `sessionTarget=isolated`.
- Crons must **never** call the `message` tool; delivery handles posting.
- Cron `delivery.to` must be explicit: `channel:<discord_channel_id>`.
- Ops crons must not deliver into Telegram/webchat.
- **Cron restart rule:** crons must not restart the gateway unless (a) they first check active runs = 0, and (b) the change ticket explicitly authorizes restart.

## Channel hygiene rules
- Telegram may be **text-only** unless image endpoints/guards exist.
- Add a guard: if inbound has media, reply once with instructions (no retries/spam).
- **No ops noise to humans:** incidents and cron summaries post to Discord only; Telegram/webchat should never receive stack traces, tool output, or raw provider errors.

## Post‑mortem (required after major incident)
Within 24h, incident owner posts:
- timeline
- root cause
- what fixed it
- preventive controls added

## Extra guardrails (additions by Leonardo 🔵)
1) **Declare the "blast radius" up front.**
   - Every change ticket must state whether it impacts: (a) one agent, (b) one surface (Telegram/webchat/Discord), or (c) fleet-wide.

2) **Pin the incident owner + rollback command in the first message.**
   - Make it copy/pasteable (e.g., exact backup filename or config hash).

3) **No mixed objectives in one cycle.**
   - Reliability fixes first; improvements (new features, refactors, cleanup) only after the incident is closed.

4) **Restart etiquette (avoid cutting active runs).**
   - Before any restart: confirm "active runs = 0" or wait for drain.
   - If drain times out, stop and reassess rather than force-restarting repeatedly.

5) **Provider route standardization.**
   - For each surface, standardize the provider route (e.g., OpenAI OAuth vs OpenRouter) to reduce debugging across different adapters.
   - Avoid toggling routes during an incident unless it is the single approved change for that cycle.

---

## Appendix: Minimal acceptance test template
Copy/paste after a change:
- Telegram text Test: ✅/❌
- Webchat text Test: ✅/❌
- Cron announce to #command-center only: ✅/❌
- Rollback target available: ✅/❌
