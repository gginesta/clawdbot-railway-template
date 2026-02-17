# Archived MEMORY.md Sections
# Moved 2026-02-11 to reduce context size

## 🚀 Active Roadmap (as of 2026-02-05)

### Build Queue (Molty's Den 🦎)
| Project | Status | Priority | Next Step |
|---------|--------|----------|-----------|
| **Unbrowse DIY** (API Skill Auto-Capture) | ✅ Phase 1 live | P2 | Test on real authenticated site (HubSpot?) |
| **Morning Briefing** (7:30 AM Telegram) | Script ready | P2 | Deploy cron when Guillermo says go |
| **WebClaw** (Better web UI) | Scoped | P2 | Deploy vanilla this weekend |
| **Smart Scheduling Engine** | Spec done | P2 | Build Phase 1 (fetch + classify) |
| **Whoop Health Integration** | Spec done | P3 | Need Guillermo's Whoop dev app registration |
| **Discord Allowlists** | Blocked | P2 | Need Guillermo's Discord user ID |

### Specs Ready to Build
| Spec | Path | Size |
|------|------|------|
| Smart Scheduling Engine | `scripts/SMART-SCHEDULING-SPEC.md` | ~20KB |
| API Skill Capture (full) | `scripts/API-SKILL-CAPTURE-SPEC.md` | 105KB |
| Morning Briefing | `scripts/MORNING-BRIEFING-SPEC.md` | 31KB |
| Whoop Integration | `scripts/WHOOP-INTEGRATION-SPEC.md` | ~30KB |
| Codex Integration Plan | `docs/CODEX-INTEGRATION-PLAN.md` | ~29KB |
| Agent Deployment Guide | `docs/AGENT-DEPLOYMENT-GUIDE.md` | ~5KB |

### New This Session (Late Feb 5)
| Item | Status | Priority | Next |
|------|--------|----------|------|
| **Codex Integration Plan** | ✅ Plan done + Raphael reviewed | P2 | Pilot with WebClaw or Morning Briefing repo |
| **Cross-Agent Task Protocol** | Todoist P1 (9988892081) | P1 | Build by Feb 8, ref Mission Control tweet |
| **Molty's Pokémon Squad** | Notion page created, Guillermo editing | P2 | Implement after Guillermo approves roster |
| **Pikachu (Marketing)** | Role defined, content ideas queued | P2 | Start sharing with community |
| **Agent Deployment Guide** | ✅ Created + synced | Ready | Use for Leonardo next week |
| **Leonardo deployment** | Deferred to next week | — | Use AGENT-DEPLOYMENT-GUIDE.md |

---


## 👀 Watching / Revisit Later

### OpenClaw PR #6797 — Message Hooks (`message:received` + `message:sent`)
- **PR:** https://github.com/openclaw/openclaw/pull/6797
- **Issue:** #5053
- **Status:** Open (as of 2026-02-05)
- **Why we care:**
  1. **Notion standup auto-trigger** — Notion webhook → message hook → auto-process standup decisions (no more "ping me when done")
  2. **Automatic inbox processing** — Pre-process incoming messages for task extraction
  3. **Cross-agent events** — Structured hook events for Raphael coordination
- **Action:** When this merges and we update OpenClaw, revisit and implement hooks for standup + inbox automation

---


## 🔓 Unbrowse DIY (API Skill Auto-Capture)

**Status:** Phase 1 MVP LIVE (2026-02-05)
**Concept:** Browse a site once → capture API traffic via CDP → auto-generate reusable curl skills → share fleet-wide

| Component | Path | Status |
|-----------|------|--------|
| CDP Capture | `scripts/api-capture/cdp-capture.js` | ✅ Working |
| Skill Generator | `scripts/api-capture/skill-gen.py` | ✅ Working |
| Wrapper | `scripts/api-capture/capture-and-generate.sh` | ✅ Working |
| Generated skills | `/data/shared/api-skills/` | ✅ Syncthing shared |
| Credentials | `credentials/api-auth/` | ✅ Local only |
| Full spec | `scripts/API-SKILL-CAPTURE-SPEC.md` | ✅ 2300 lines |

**How to use:** Start capture → browse site → stop → skill generated automatically
```bash
bash scripts/api-capture/capture-and-generate.sh example.com --timeout 120
```

**Fleet sharing:** Generated skills land in `/data/shared/api-skills/` → Syncthing pushes to all agents → sub-agents call via `exec` + curl

**Remaining phases:** P2 fleet distribution polish, P3 self-healing, P4 sub-agent integration, P5 advanced (GraphQL, WebSocket)

---


## 📝 Preferences & Decisions

### Accepted Risks
- **Port 8080 exposed:** Mitigated by VPN + token auth
- **Device auth disabled:** Needed for web UI access

### Rejected
- **Supermemory plugin:** Reviewed 2026-01-31 — code is safe but sends all conversations to third-party cloud. Privacy trade-off not worth it when local memory works fine.

### Style
- **My emoji:** 🦎 (not 🫠 — doesn't render in webchat)
- **Responses:** Casual but efficient, tables for structured data
- **Platform formatting:** No markdown tables for Discord/WhatsApp (use bullets)

---


## 🗂️ Specs & Build Docs (2026-02-05)

| Spec | Path | Status |
|------|------|--------|
| Smart Scheduling Engine | `scripts/SMART-SCHEDULING-SPEC.md` | Spec done, not built |
| API Skill Auto-Capture (Unbrowse) | `scripts/API-SKILL-CAPTURE-SPEC.md` | ✅ Phase 1 built + tested |
| Morning Briefing | `scripts/MORNING-BRIEFING-SPEC.md` + `scripts/morning_briefing.py` | Spec + script done, not deployed |
| Whoop Integration | `scripts/WHOOP-INTEGRATION-SPEC.md` | Spec done, needs Whoop API access |
| Security Hardening Plan | `SECURITY-HARDENING-PLAN.md` | ✅ Mostly complete |
| Codex Integration Plan | `docs/CODEX-INTEGRATION-PLAN.md` | ✅ Plan + Raphael review done |
| Agent Deployment Guide | `docs/AGENT-DEPLOYMENT-GUIDE.md` | ✅ Ready for Leonardo |

---


## 🎮 Codex Integration Strategy (2026-02-05)

**Plan:** `/data/workspace/docs/CODEX-INTEGRATION-PLAN.md` (~29KB)
**Raphael Review:** `/data/shared/codex-raphael-review.md`

**Decision framework:**
- **Use Codex** when: PR-shaped work, clear acceptance criteria, tests exist, parallelizable
- **Use OpenClaw sub-agents** when: coordination-heavy, multi-tool, ambiguous, needs secrets, not PR-shaped

**GitHub label state machine:** `codex-ready` → `codex-running` → `needs-review` → `done`

**Rollout order:**
1. **Pilot:** WebClaw or Morning Briefing repo (1-2 weeks)
2. **Team adoption:** Unbrowse phases + Brinc HubSpot (2-4 weeks)
3. **Full automation:** Discord/Notion auto-updates, Codex auto-review (4-8 weeks)

**Raphael's refinements (approved):**
- Split `src/domain/` vs `src/integrations/` for smaller Codex PRs
- HubSpot CRM = first Brinc Codex pilot
- PII guardrails: never log raw email/phone, sanitized fixtures only
- Staging smoke-test loop + rollback/feature-flag plan per PR

---


## 🦎 Molty's Pokémon Squad (Sub-Agent Roster)

**Theme:** Gen 1 Pokémon (#1-151) — Guillermo's nostalgic preference
**Notion page:** https://www.notion.so/2fe39dd69afd8198ad96d4e2d086de25
**Status:** Updated with OG starters (2026-02-06)

| Phase | Role | Pokémon | Model | Notes |
|-------|------|---------|-------|-------|
| P0 | Spec Writer | Squirtle 🐢 | GPT-5.2 | Fluid, shapes ideas into structured specs |
| P0 | Builder | Charmander 🔥 | GPT-5.2 | Fire energy, makes things happen |
| P0 | Researcher | Bulbasaur 🌱 | Gemini Flash | Grows knowledge, gathers intel |
| P1 | Code Reviewer | Mewtwo 🧬 | Claude Sonnet | Psychic precision, finds flaws |
| P1 | Security Auditor | Arcanine 🔥 | Gemini Flash | Loyal guardian, sniffs threats |
| P1 | Data Wrangler | Porygon 💾 | Qwen | Digital native, transforms data |
| P1 | Strategist | Alakazam 🥄 | Claude Sonnet | IQ 5000, long-term planning, complex decisions |
| P2 | Writer / Comms | Jigglypuff 🎤 | Claude Sonnet | Compelling voice, writes copy |
| P2 | Scheduler | Abra ⏳ | Qwen | Teleports tasks to right times |
| P2 | Fleet Monitor | Electrode ⚡ | Qwen | Fast alerts, watches systems |
| P2 | Batch Processor | Machamp 💪 | GPT-5.2 | Four arms, parallel bulk operations |
| P2 | Flex / Generalist | Eevee 🔎 | Gemini Flash | Adapts to any domain, evolves as needed |
| Special | Marketing / Social | Pikachu ⚡ | Claude Sonnet | Face of the team, community engagement |

**Pikachu content pipeline:** Molty flags moment → Pikachu drafts → Guillermo approves → post via @Molton_Sanchez
**X account:** @Molton_Sanchez (posting currently blocked by Twitter bot detection — revisit)

---


## 📋 Cross-Agent Task Protocol (P1 — Due Feb 8)

**Todoist:** 9988892081 (Molty's Den, P1)
**Reference:** Bhanu Teja's Mission Control guide: https://x.com/pbteja1998/status/2017662163540971756
**Problem:** Current Discord relay is free-form text — doesn't scale past 2 agents
**Solution:** Structured task dispatch + acknowledgment + progress tracking + completion verification
**Integrates with:** Codex GitHub label state machine, existing Discord channels, Todoist

---
