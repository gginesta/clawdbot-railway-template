# ClawhHub Skill Deep Dive — Feb 9, 2026

Audit of 7 skills from community research. Evaluated for scope, integration fit, security, and TMNT squad relevance.

> **Policy reminder:** We don't install ClawhHub skills directly. We evaluate, take inspiration, and build custom versions if needed.

---

## 1. 🚂 railway-skill (railway-deploy)

**ClawhHub slug:** `railway-skill` | **Author:** leicao-me | **v0.1.0** | Created Feb 3

### Scope
Pure documentation skill — it's a Railway CLI cheat sheet in SKILL.md. No scripts, no automation logic. Just a reference for `railway` CLI commands (deploy, logs, env vars, domains, volumes, databases).

### Security Audit
- ✅ No scripts, no outbound calls, no credentials
- ✅ Just a markdown reference file
- **PASS** — completely safe (it's literally just docs)

### Integration Assessment
- **Overlap:** We already know the Railway CLI inside out. This adds zero new capability.
- **Value:** Marginal. Could save a few seconds looking up CLI flags.
- **Our advantage:** We have live OAuth session, project IDs, service names all in TOOLS.md. This generic skill knows nothing about our fleet.

### Verdict: ❌ SKIP
> Just a CLI cheat sheet. We already have this knowledge baked into TOOLS.md with our specific project IDs and setup. No value.

---

## 2. 🏛️ agent-council

**ClawhHub slug:** `agent-council` | **Author:** itsahedge | **v1.0.0** | Created Feb 4

### Scope
Two-part toolkit:
1. **Agent creation** — Bash script (`create-agent.sh`) that scaffolds agent workspaces (SOUL.md, HEARTBEAT.md, memory/, gateway config). Auto-restarts gateway.
2. **Discord channel management** — Python scripts (`setup_channel.py`, `rename_channel.py`) that create/rename Discord channels via API and generate gateway config patches.

### Security Audit
- ✅ `create-agent.sh`: Clean bash, creates files/dirs, uses `openclaw gateway config.patch` — standard ops
- ✅ `setup_channel.py`: Uses Discord API via `urllib` (no pip deps). Reads config from `~/.openclaw/config.json`. Only calls `discord.com/api/v10` endpoints.
- ✅ `rename_channel.py`: Same pattern, plus optional workspace file search (grep/sed)
- ⚠️ Config path is `~/.openclaw/config.json` — our setup uses `/data/.openclaw/openclaw.json`. Would need path adjustment.
- ✅ No hardcoded credentials, no exfiltration, no injection risks
- **PASS** with minor path adjustments needed

### Integration Assessment
- **Very relevant to TMNT squad.** We're building a multi-agent fleet and currently do agent setup manually.
- **Overlap:** We tested `openclaw agents add` RPC (works!), but this skill adds SOUL.md generation, Discord binding, and memory scaffolding on top.
- **Gap it fills:** Standardized agent creation workflow. Currently each new agent (Leonardo, Donatello, etc.) is hand-crafted.
- **Customization needed:** Path fixes (`~/.openclaw` → `/data/.openclaw`), our TMNT naming conventions, Syncthing folder setup, webhook config.

### Verdict: 🔨 BUILD (inspired by)
> Excellent concept and solid implementation. We should build our own `tmnt-agent-creator` that combines this with our TMNT conventions, Syncthing setup, Railway deployment, and Discord channel ownership model. Take the `create-agent.sh` structure as starting point.

---

## 3. 🦀 claw-swarm

**ClawhHub slug:** `claw-swarm` | **Author:** MatchaOnMuffins | **v1.0.0** | Created Feb 2

### Scope
Collaborative problem-solving swarm. Agents register with an external API (`claw-swarm.com`), receive tasks (math/research problems), submit solutions, and get aggregated. Hierarchical: Level 1 = independent attempts, Level 2+ = synthesis of prior attempts.

### Security Audit
- ⚠️ **Calls external API** at `claw-swarm.com` — third-party service, not self-hosted
- ⚠️ **Registers your agent** with external service and stores API key
- ⚠️ **Sends reasoning/solutions** to external endpoint
- ✅ User confirmation required before submissions
- ❌ **Data exfiltration risk**: Your agent's reasoning on "genuinely hard problems" goes to someone else's server
- **FAIL** — external data submission to untrusted third-party

### Integration Assessment
- **Conceptually interesting** — swarm intelligence, aggregation layers
- **Not useful for us** — we solve our own problems, we don't need to solve strangers' math problems
- **Better alternative:** Our `council-of-the-wise` / sub-agent pattern already does multi-perspective analysis internally

### Verdict: ❌ REJECT
> Sends your agent's work to an external API. Cool concept for open research, but security risk and zero business value for TMNT squad. If we want swarm behavior, we build it internally with sessions_spawn.

---

## 4. ✅ todoist-task-manager (todoist-pro)

**ClawhHub slug:** `todoist-task-manager` | **Author:** 2mawi2 | **v1.0.0** | Created Jan 24

### Scope
CLI wrapper for `todoist-cli` (by sachaos, Go-based). Uses a locally installed binary for list/add/modify/complete/delete with Todoist filter syntax. Stores config in `~/.config/todoist/config.json`.

### Security Audit
- ✅ No scripts — just a SKILL.md reference
- ✅ Uses local CLI binary, no outbound calls from skill itself
- ⚠️ Requires `todoist-cli` binary installation (Go binary from GitHub)
- ✅ No credential exposure in skill
- **PASS** — safe, it's just docs for a CLI tool

### Integration Assessment
- **We already have Todoist fully integrated** via REST API + curl in our scripts
- **CLI approach vs API approach:** We use direct REST API calls (more flexible, no binary dependency). This skill uses `todoist-cli` (simpler commands, but adds a dependency).
- **Filter syntax reference** is genuinely useful — the Todoist filter query language docs are good
- **Missing from our setup:** `todoist list --filter "(today | overdue) & p1"` style commands. We currently build curl queries manually.

### Verdict: ⚠️ INSPECT (cherry-pick filter syntax)
> We don't need the CLI binary — our REST API approach is better for Railway containers. But the **filter syntax reference** is worth copying into our TOOLS.md. Consider building a `todoist.sh` wrapper script that maps these filter patterns to our curl-based API calls.

---

## 5. 📔 notion-sync (notion-database-sync)

**ClawhHub slug:** `notion-sync` | **Author:** robansuini | **v1.0.3** | Created Feb 6

### Scope
Full bi-directional Notion sync toolkit with 10 Node.js scripts:
- `search-notion.js` — Search pages/databases
- `query-database.js` — Advanced DB queries with filters/sort
- `update-page-properties.js` — Update any property type
- `md-to-notion.js` — Push markdown → Notion (batched, rate-limited)
- `notion-to-md.js` — Pull Notion → markdown
- `add-to-database.js` — Add entries to databases
- `delete-notion-page.js` — Delete pages
- `get-database-schema.js` — Inspect DB schema
- `watch-notion.js` — Watch for page changes
- `test-normalize.js` — Test utils

### Security Audit
- ⚠️ Reads API key from macOS Keychain (`security find-generic-password`) — not portable
- ✅ All calls go to `api.notion.com` only
- ✅ Scripts use standard `@notionhq/client` or raw fetch to Notion API
- ✅ No outbound calls to unknown domains
- ✅ Clean error handling in scripts
- ⚠️ Requires `node` + npm packages (they import from `@notionhq/client`)
- **PASS** with credential handling adaptation needed

### Integration Assessment
- **HIGH VALUE.** We struggle with Notion API constantly (inline databases, property updates, page creation).
- **Fills real gaps:**
  - `md-to-notion.js` — We could push standup notes, research reports, MEMORY.md to Notion automatically
  - `notion-to-md.js` — Pull Notion content back for agent processing
  - `watch-notion.js` — Monitor standup page for Guillermo's comments (replacing manual "standup done" ping)
  - `query-database.js` — Better DB queries than our raw curl calls
  - `update-page-properties.js` — Type-safe property updates (we've had issues with this)
- **Overlap:** Our existing `notion` skill (from ClawhHub install) is basic. This is significantly more capable.
- **Effort:** Medium — need to set up npm deps, adapt credential loading from env var (easy), test each script.

### Verdict: 🔨 BUILD (heavily inspired by)
> Best skill in this batch. Don't install directly (macOS keychain dep, npm packages in skill dir), but the **script patterns are excellent**. Fork the key scripts (md-to-notion, notion-to-md, query-database, watch-notion, update-page-properties), adapt to our env var credential loading, and create our own `notion-enhanced` skill. This would solve 80% of our Notion friction.

---

## 6. 📅 gcalcli-calendar (calendar-scheduler)

**ClawhHub slug:** `gcalcli-calendar` | **Author:** lstpsche | **v2.1.0** | Created Feb 5

### Scope
Google Calendar management via `gcalcli` CLI. Very detailed SKILL.md with rules for:
- CLI flag placement (global vs subcommand flags)
- Deterministic event lookup (agenda scan > search)
- Cross-calendar overlap checking before creating events
- Non-interactive delete with verification
- ICS import for recurring events
- Weekday resolution via 14-day scans

### Security Audit
- ✅ No scripts — pure SKILL.md reference
- ✅ Uses local `gcalcli` binary (established Python tool)
- ✅ No credential exposure
- ⚠️ Requires `gcalcli` installation + Google OAuth setup
- **PASS** — it's just documentation

### Integration Assessment
- **We already have `calendar.sh`** using Google Calendar API directly via curl + OAuth tokens
- **gcalcli approach is interesting:** More robust event lookup (agenda scan vs search), cross-calendar overlap checking, ICS import for recurring events
- **Key insight we're missing:** The "meaning-first lookup" pattern — scan bounded agenda → semantic match, instead of exact title search. Our calendar.sh does exact matches which can miss renamed/similar events.
- **Overlap detection rule is excellent:** "Always check ALL non-ignored calendars before creating" — we learned this lesson #40 the hard way
- **Problem:** Requires installing `gcalcli` + setting up its own OAuth flow (separate from our existing tokens). Adds another auth surface.

### Verdict: ⚠️ INSPECT (cherry-pick patterns)
> Don't install gcalcli (adds auth complexity, we have working OAuth). But copy these patterns into our `calendar.sh`:
> 1. **Bounded agenda scan for event lookup** instead of exact search
> 2. **Cross-calendar overlap check** before every create (we already learned this!)
> 3. **Non-interactive delete with verification** pattern
> 4. **ICS import via stdin** for recurring events (we can adapt to Calendar API)

---

## 7. 🎯 mission-control (task-orchestrator)

**ClawhHub slug:** `mission-control` | **Author:** (not captured) | **v2.2.1**

### Scope
Full task management system with:
- **Web dashboard** (GitHub Pages hosted `index.html` — 273KB!)
- **Webhook integration** — GitHub push events trigger agent tasks
- **Task JSON store** — `tasks.json` with status workflow (backlog → in_progress → review → done)
- **CLI update script** — `mc-update.sh` for status changes, comments, subtasks
- **GitHub transform** — Detects task status changes from git diffs
- **Cron definitions** — Pre-built cron jobs in `crons.json`

### Security Audit
- ✅ `mc-update.sh`: Clean bash, uses `jq` for JSON manipulation, git operations
- ⚠️ GitHub webhook integration — pushes to GitHub repo (outbound, but intentional)
- ✅ No external API calls beyond GitHub
- ⚠️ 273KB `index.html` — should inspect for embedded scripts, but it's a dashboard
- ✅ Transform script processes git diffs locally
- **PASS** — legitimate task management system

### Integration Assessment
- **Conceptually aligned** with our CODEX integration plan — human moves task → agent executes
- **Overlaps with:** Our Todoist + Notion standup system, and the CODEX-INTEGRATION-PLAN.md
- **Dashboard:** We already have Notion for task visibility. Adding GitHub Pages dashboard is redundant.
- **Interesting pattern:** GitHub webhook → agent task assignment. Could complement our Discord-based coordination.
- **JSON task store** is simpler than our Todoist+Notion dual system — could be useful for agent-internal tasks (not human-facing)

### Verdict: ⚠️ INSPECT (architecture patterns)
> The webhook → task → agent execution flow is exactly what our CODEX plan needs. Don't install (we have Notion + Todoist), but study the `mc-update.sh` CLI and webhook transform pattern for our own agent task system. The JSON-based task store could work for internal agent subtasks that don't need to be in Todoist.

---

## Summary Matrix

| # | Skill | ClawhHub Slug | Verdict | Action |
|---|-------|---------------|---------|--------|
| 1 | railway-deploy | `railway-skill` | ❌ SKIP | We know Railway CLI already |
| 2 | agent-council | `agent-council` | 🔨 BUILD | Create `tmnt-agent-creator` inspired by this |
| 3 | claw-swarm | `claw-swarm` | ❌ REJECT | External API data exfil risk |
| 4 | todoist-pro | `todoist-task-manager` | ⚠️ INSPECT | Cherry-pick filter syntax for TOOLS.md |
| 5 | notion-database-sync | `notion-sync` | 🔨 BUILD | Fork key scripts → `notion-enhanced` skill |
| 6 | calendar-scheduler | `gcalcli-calendar` | ⚠️ INSPECT | Cherry-pick lookup/overlap patterns |
| 7 | task-orchestrator | `mission-control` | ⚠️ INSPECT | Study webhook→task→agent flow for CODEX plan |

### Also Discovered (Bonus)
- **`council-of-the-wise`** (v1.3.1, by jeffaf) — Multi-perspective feedback via sub-agents. Better than `agent-council` for decision-making. Auto-discovers agent personas from folder. Clean, no external deps. **Verdict: 🔨 BUILD** — adapt for TMNT squad decisions (replace generic personas with our agents' specialties).

### Priority Build Order
1. **`notion-enhanced`** — Highest ROI, solves daily friction with standups/content
2. **`tmnt-agent-creator`** — Needed before deploying Leonardo/Donatello/Michelangelo  
3. **CODEX task system** (from mission-control patterns) — Longer-term, part of CODEX plan
4. **Calendar improvements** — Quick wins, copy patterns to existing `calendar.sh`

---

*Audit completed: Feb 9, 2026 | Auditor: Molty 🦎*
