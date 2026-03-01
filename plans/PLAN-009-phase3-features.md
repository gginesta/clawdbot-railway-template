# PLAN-009: Phase 3 Feature Sprint
**Created:** 2026-03-01 | **Owner:** Molty | **Target:** Tonight 03:00 HKT

---

## PAUSE — What do we have?

### Assets confirmed
- All 3 cron scripts already exist: `mc-usage-report.sh`, `mc-weekly-digest.sh`, `mc-todoist-sync.sh`
- GitHub token valid: `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`
- Vercel auto-deploys on push to main (connected Feb 27)
- MC repo: `gginesta/tmnt-mission-control`
- Overnight window: 03:00 HKT (~90 min, hard stop 2h)

### Constraints
- Code changes = GitHub commit → Vercel auto-deploy (takes ~2-3 min each)
- Convex schema changes = `convex dev` push (requires CLI access)
- No local MC repo clone — must use GitHub API or clone at runtime
- Sub-agent sessions cannot use memory_search (lesson 88)

---

## PLAN — Task Triage

### Stream A: OpenClaw cron config (no code deploy needed, ~25 min)
These are config-only. Do these first — zero deployment risk.

| Task | Effort | Notes |
|------|--------|-------|
| Integrate usage report into heartbeat cron (46d1ca32) | 5 min | Add `mc-usage-report.sh` step to existing heartbeat cron payload |
| Wire Todoist sync cron (every 30min) | 8 min | New cron, script exists |
| Wire weekly digest cron (Fri 17:00 HKT) | 8 min | New cron, script exists |
| Enable MC_PASSWORD on Vercel | 5 min | Vercel API env var set + password to Guillermo |

### Stream B: MC codebase — low-risk fixes (~25 min)
Small changes, no new tables, no schema changes.

| Task | Effort | Risk |
|------|--------|------|
| Clean up ESLint warnings | 10 min | Low — 4 specific unused imports |
| [B1] Mobile-Responsive Polish | 20 min | Medium — CSS/breakpoints across 6 screens |

### Stream C: MC codebase — medium features (~40 min)
New UI, no new Convex tables.

| Task | Effort | Risk |
|------|--------|------|
| [B3] Enhanced Dojo — Quick Actions | 20 min | Medium — UI additions to home |
| [C1] Project Views (Brinc/Cerebro/Mana) | 20 min | Medium — new routes + filtered views |

### Deferred (too complex/risky for solo overnight)
- [A2] Pizza Tracker Cost Tracking — new Convex table + API + UI (needs Guillermo review)
- [B4] Drag-and-Drop Kanban — DnD library, rewrites interaction model
- [D6] User Auth — NextAuth.js, affects all routes, high blast radius
- [D1] Task Templates — new Convex table
- [C2] Todoist Sync UI — already have sync script, just need UI layer
- [C4] Splinter Den — full settings page, complex
- [D2] Notification Preferences — new table + UI
- [D3] Activity Analytics — chart library needed
- [D4] Memory Timeline/Diff — complex UI
- [C5] File Attachments — Convex file storage

---

## EVALUATE

**Budget check:**
- Stream A: 25 min ✅
- Stream B: 30 min ✅
- Stream C: 40 min ✅
- Total: ~95 min → tight but doable if no surprises

**Risk assessment:**
- Streams A + B: safe. No new tables, scripts already exist.
- Stream C: moderate. If a deploy fails, Vercel rolls back automatically.
- Biggest risk: GitHub API rate limits or Vercel deploy taking longer than expected.

**Mitigation:**
- Clone repo once, batch all changes, single push → single Vercel deploy
- If Stream C hits issues at 02:30 HKT, ship what's done and stop

---

## EXECUTE — Tonight's Run Order

1. **Enable MC_PASSWORD** (Vercel API) — pick a strong password, DM Guillermo
2. **Cron: usage report** — update heartbeat cron 46d1ca32 payload
3. **Cron: Todoist sync** — create new cron (every 30min)
4. **Cron: weekly digest** — create new cron (Fri 17:00 HKT)
5. **Clone MC repo** — `git clone https://ghp_...@github.com/gginesta/tmnt-mission-control`
6. **ESLint fixes** — 4 specific import removals
7. **Mobile polish** — sidebar breakpoints, calendar, War Room
8. **Dojo quick actions** — Create Task button, overdue badge, week mini-calendar
9. **Project Views** — `/project/brinc`, `/project/cerebro`, `/project/mana` routes
10. **Git push** → Vercel auto-deploys
11. **Verify** deploy succeeded, post results to #squad-updates + MC activity
12. **Update MC task statuses** — mark completed ones done

---

## MC Task IDs

| Task | MC ID |
|------|-------|
| Integrate usage report | jn7aj2j76f6kpm48swenp6verx81qwg8 |
| Wire weekly digest cron | jn7efj8tj4zg8sxh29rdf41htn81qwvz |
| Wire Todoist sync cron | jn71fqz0ymrkj056n0gkw0218d81qd4j |
| [B1] Mobile Polish | jn701krgqbwv7mw2tmrtqqczeh81q29d |
| [B3] Enhanced Dojo | jn7dzw9b6nnhxc5t75vwaez4fs81q0rd |
| [C1] Project Views | jn737fa7zkc5w7yq48m0rq0g5d81q6j0 |
| [A2] Pizza Tracker | jn73s2szrqhnme2b3ht2zsyjhh81qqd5 |
| [B4] DnD Kanban | jn7e3yky6f87mf8jyjmc827zwx81qg9z |
| ESLint cleanup | jn72t1m0gyp35d4spj2zqhwpjh81qp13 |
| MC_PASSWORD | jn7avzp7axhkc1bazpkmbr5yzs81q95d |
| [D1] Task Templates | jn7ernh8qkh07tv1cevb4ekh1h81p9w1 |
| [C2] Todoist Sync | jn774wcaj5d8zmha6czc7at4f581qke4 |
| [A4] Weekly Digest | jn7fptmxj2jxh823txgbj57adn81q6yf |
| [C4] Splinter Den | jn70x0c2a59amdrdswjtnv6ec981qahx |
| [D6] User Auth | jn75x71ean1btny4nfeqtmf13981pdkn |
| [D2] Notification Prefs | jn74tptpczzy3xsr6305ygkj8h81p2cc |
| [D3] Activity Analytics | jn720qsjv1h7ppn0frhan03ycd81pp98 |
| [D4] Memory Timeline | jn78cxkwq6rn520gy736tqbsqn81qmfr |
| [C5] File Attachments | jn76sahawawayqsbs6r0hzfm3d81qvmq |
