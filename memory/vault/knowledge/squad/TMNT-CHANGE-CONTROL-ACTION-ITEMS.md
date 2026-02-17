# TMNT Change Control — Action Items (v1.0)

*Created: 2026-02-16 | Source: TMNT-CHANGE-CONTROL-INCIDENT-PROTOCOL.md*

## Goal
Turn the protocol into concrete, checkable work across the squad architecture.

---

## P0 (Do now / this week)

### A) Fleet: create a standard “Change Ticket” template message
**Owner:** Molty 🦎
- Add a copy/paste template to squad KB (and pin in #command-center):
  - Hypothesis
  - Single change
  - Blast radius
  - Rollback target
  - Acceptance tests

### B) Fleet: standard acceptance test checklist
**Owner:** Molty 🦎
- Add a pinned checklist:
  - Telegram text `Test`
  - Webchat text `Test`
  - Discord mention/response
  - Cron announce to #command-center
  - Verify `delivery.to=channel:<id>`

### C) Fleet: lock “maintenance isolation”
**Owner:** Molty 🦎
- Audit all crons and automation jobs for:
  - `sessionTarget=isolated`
  - Discord-only delivery
  - No `message` tool usage inside agentTurn

### D) Fleet: rollback inventory
**Owner:** Molty 🦎
- Document where last-known-good configs live for each agent:
  - backup filenames convention
  - restore command / steps
  - where config files are stored inside backup

---

## P1 (Next)

### E) Per-agent: surface routing sanity
**Owners:** Each lead (Raphael 🔴, Leonardo 🔵, Molty 🦎)
- Confirm per-surface routing is clean:
  - webchat sessions don’t have `to=telegram:...`
  - crons don’t deliver into interactive sessions

### F) Provider route standardization table (per surface)
**Owner:** Molty 🦎 (with input from leads)
- Create a table:
  - Surface: Telegram / Webchat / Discord / Cron
  - Primary provider route
  - Allowed fallbacks
  - Thinking/reasoning defaults

---

## P2 (Hardening)

### G) “Restart etiquette” automation
**Owner:** Molty 🦎
- Add a pre-restart guard:
  - check active runs = 0 (or drain) before restart
  - if drain times out, stop and escalate

### H) Media guard for Telegram
**Owner:** Molty 🦎
- If channel plugin cannot support media:
  - add a single-response guard (no retry loop)
  - document: “Telegram = text only; send images via Discord/webchat”

---

## Deliverables
- KB: `TMNT-CHANGE-CONTROL-INCIDENT-PROTOCOL.md` (policy)
- KB: `TMNT-CHANGE-CONTROL-ACTION-ITEMS.md` (this file)
- Pinned messages in #command-center: ticket template + acceptance checklist
