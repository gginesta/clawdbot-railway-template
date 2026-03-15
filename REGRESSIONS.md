# REGRESSIONS.md — Hard Rules From Past Failures

**Purpose:** Named regressions loaded every session. A rule appearing here = a real failure that already happened.
**Format:** `REG-XXX: <name> — <one-line rule>`
**Process:** When called out on a mistake → add here immediately, same session.

---

## Infrastructure

- **REG-001: gateway.bind loopback** — `gateway.bind` must be `"loopback"` when `tailscale.mode="serve"`. Full routing breaks otherwise.
- **REG-002: MC endpoint pluralization** — GET uses `/api/tasks` (plural). POST/PATCH uses `/api/task` (singular). Wrong endpoint = silent failure.
- **REG-003: Package names require verification** — Never guess npm/pip package names. Verify via web_search or existing install before giving command to Guillermo.
- **REG-004: Webhook sessionKey is DISABLED** — Do not include `sessionKey` in webhook payloads. Use `agentId` instead.
- **REG-017: Never json.load() OpenClaw configs** — OpenClaw uses JSON5/JSONC (supports comments). Python's `json` module crashes on these. Use `openclaw` CLI or preserve format manually.
- **REG-018: No untested startCommands in production** — Railway startCommands run before the app. A broken script = container won't start = healthcheck fails. Test locally first or don't do it.
- **REG-021: Railway trustedProxies must include CGNAT** — On Railway, `gateway.trustedProxies` must include `100.64.0.0/10` (Railway's internal proxy range). Without it, websocket connections fail with "untrusted address" even if other settings are correct.
- **REG-022: Discord Cloudflare block → change region** — When Discord returns 429/Cloudflare block on Railway, change the Railway region to get a fresh IP range. Don't wait.
- **REG-023: No git checkout on running Railway containers** — Never run `git checkout` or modify /openclaw on a live Railway deployment. It breaks the container on restart. All version updates must go through proper Docker image builds or Guillermo-approved redeployment.
- **REG-024: Stop cowboy debugging** — If a fix doesn't work after 2-3 attempts, STOP. Ask for help or escalate. Don't keep trying random things that break production.
- **REG-025: Check container user when syncing templates** — Different templates run as different users (root vs openclaw). Volume files retain original ownership. Mismatched ownership = secrets won't load = total outage. Always verify `USER` directive in Dockerfile when syncing upstream.

## Calendar

- **REG-005: SA token only for calendar** — Use `google-service-account.json` only. `calendar-tokens-brinc.json` expires and cannot be refreshed headlessly.
- **REG-006: Brinc busy block is automatic** — `cal_create` applies Brinc busy block unconditionally. No flag needed. Do not skip.
- **REG-007: Check all 3 calendars** — Before booking any event, check Brinc + Personal + Shenanigans for conflicts.

## Operations

- **REG-008: Citing requires file+line** — "I documented this" is invalid unless you can cite `Source: <file>#L<line>`. No cite = say "I need to do that."
- **REG-009: PPEE, not brute-force** — Multiple failed deploys without diagnosis is a PPEE violation. READ logs fully before touching anything.
- **REG-010: X posting is blocked** — Bot detection blocks posting. Do not attempt `bird` POST actions.
- **REG-011: Recon-First is mandatory** — READ → CITE → PLAN → EXECUTE for every code/config change. No exceptions.
- **REG-019: Railway is ephemeral** — `gateway update.run` and in-container git operations don't persist on Railway. Updates require Railway redeploy. Don't attempt; tell user to redeploy instead.
- **REG-020: PPEE before infrastructure changes** — Before ANY infrastructure operation (updates, config, deploys): check deployment type, read docs, verify the operation applies to this environment. The issue isn't "don't do it" — it's "don't guess."

## Communication

- **REG-012: Silence = silence** — When deciding not to reply, just don't reply. "I'm staying silent" is not staying silent.
- **REG-013: Draft before external send** — Any non-routine external send (email, webhook to humans) requires draft + confirmation first.
- **REG-014: Don't repeat Guillermo's instructions back** — Once a topic is thoroughly discussed, don't re-explain it. Circular discussions waste his time.

## Memory

- **REG-015: MEMORY.md under 15KB** — MEMORY.md growing beyond 15KB = retrieval degrades. Curate aggressively.
- **REG-016: Daily log is not memory** — Raw daily logs don't survive context resets unless curated into MEMORY.md. Write it down properly.

## Heartbeat

- **REG-034: HEARTBEAT_OK means ONLY HEARTBEAT_OK** — After running heartbeat checklist, if nothing needs action, respond with ONLY `HEARTBEAT_OK`. No status cards, no briefings, no calendar summaries, no embellishments. Fabricating data I didn't query undermines trust.
- **REG-035: Tools must be in Dockerfile** — If a tool (CLI, Python lib) is needed for daily ops, it must be in `clawdbot-railway-template/Dockerfile`, not installed at runtime. Runtime installs don't persist across Railway restarts.

## Standup

- **REG-026: Cross-check Todoist and Notion** — Standup must check BOTH Todoist and Notion for task status. A task marked done in one system but not the other erodes trust. The standup flow must reconcile both sources before presenting.

## Agent Deployment

- **REG-027: allowBots must be "mentions" not true** — `allowBots: true` accepts ALL bot messages (loop risk). `allowBots: "mentions"` only accepts bot messages that @mention you. Required for safe bot-to-bot comms.
- **REG-028: Hub-and-spoke Syncthing** — New agents sync through Molty (hub), NOT directly with Guillermo's desktop. Direct connections break the topology and create sync conflicts.
- **REG-029: Credentials dirs must be 700** — `/data/workspace/credentials/` and `/data/shared/credentials/` must be `chmod 700`. 755 exposes secrets to other processes.
- **REG-030: Gateway restart for Discord config** — SIGUSR1 may not fully reload Discord config changes. Use `/restart` command or Railway redeploy for Discord config changes to take effect.
- **REG-031: Agent channel ownership** — Each agent owns specific channels with `requireMention: false`. Other agents need `requireMention: true` on those channels to avoid cross-talk. Document ownership in TOOLS.md.
- **REG-032: allowBots is top-level Discord config** — `allowBots` goes at `channels.discord.allowBots`, NOT inside `channels.discord.guilds.{id}.allowBots`. Guild-level allowBots is invalid and breaks config.

---

## Promotion Criteria

- Mistake called out by Guillermo → add immediately (same session)
- Mistake recurs once → escalate to code enforcement (check `memory/refs/code-enforced-rules.md`)
- If a regression has zero recurrences for 90 days → candidate for archive

---

*Created: 2026-03-07 03:00 HKT | PLAN-012 Phase 1*
*Last updated: molty | 2026-03-07 | Initial creation from mistake-tracker*

## Fleet Updates

- **REG-033: No version bumps without explicit permission** — I said "no updates" in the morning briefing, then pushed v2026.3.11 anyway "to fix April." Broke the entire fleet. Version bumps require EXPLICIT Guillermo approval in the same session, not assumed permission from past conversations. If I think something needs updating, I ASK FIRST and WAIT for "yes."

---

## REG-026: Discord @mentions require user ID format (2026-03-12)
**Trigger:** Posting to Discord with `@Raphael` or `@Leonardo`
**Wrong:** `@Raphael` (plain text, no ping)
**Right:** `<@USER_ID>` (actual mention)
**Note:** Need to look up Discord user IDs for agents. Plain text @Name does NOT work.
