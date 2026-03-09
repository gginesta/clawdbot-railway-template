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

## Calendar

- **REG-005: SA token only for calendar** — Use `google-service-account.json` only. `calendar-tokens-brinc.json` expires and cannot be refreshed headlessly.
- **REG-006: Brinc busy block is automatic** — `cal_create` applies Brinc busy block unconditionally. No flag needed. Do not skip.
- **REG-007: Check all 3 calendars** — Before booking any event, check Brinc + Personal + Shenanigans for conflicts.

## Operations

- **REG-008: Citing requires file+line** — "I documented this" is invalid unless you can cite `Source: <file>#L<line>`. No cite = say "I need to do that."
- **REG-009: PPEE, not brute-force** — Multiple failed deploys without diagnosis is a PPEE violation. READ logs fully before touching anything.
- **REG-010: X posting is blocked** — Bot detection blocks posting. Do not attempt `bird` POST actions.
- **REG-011: Recon-First is mandatory** — READ → CITE → PLAN → EXECUTE for every code/config change. No exceptions.

## Communication

- **REG-012: Silence = silence** — When deciding not to reply, just don't reply. "I'm staying silent" is not staying silent.
- **REG-013: Draft before external send** — Any non-routine external send (email, webhook to humans) requires draft + confirmation first.
- **REG-014: Don't repeat Guillermo's instructions back** — Once a topic is thoroughly discussed, don't re-explain it. Circular discussions waste his time.

## Memory

- **REG-015: MEMORY.md under 15KB** — MEMORY.md growing beyond 15KB = retrieval degrades. Curate aggressively.
- **REG-016: Daily log is not memory** — Raw daily logs don't survive context resets unless curated into MEMORY.md. Write it down properly.

---

## Promotion Criteria

- Mistake called out by Guillermo → add immediately (same session)
- Mistake recurs once → escalate to code enforcement (check `memory/refs/code-enforced-rules.md`)
- If a regression has zero recurrences for 90 days → candidate for archive

---

*Created: 2026-03-07 03:00 HKT | PLAN-012 Phase 1*
*Last updated: molty | 2026-03-07 | Initial creation from mistake-tracker*
