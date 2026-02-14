# Project Yoda — Deployment Plan (v3, Final)

*Applies lessons from Leonardo deployment (see DEPLOYMENT-LESSONS-LEONARDO.md)*
*Core principle: FILES FIRST → CONFIG SECOND → BOOT THIRD*

---

## Pre-Flight: What We Need Before Starting

| Item | Who Provides | Status |
|------|-------------|--------|
| Edwin's Claude OAuth token | Edwin → Guillermo | ⬜ Pending |
| Railway project created | Guillermo | ⬜ Pending |
| Workspace files staged | Molty | ✅ Ready (`projects/yoda/workspace/`) |
| Break Glass Guide | Molty | ✅ Ready (`projects/yoda/docs/BREAK-GLASS-GUIDE.md`) |

---

## Phase 0: Pre-Requisites (Before Touching Railway)
*Leonardo lesson: Collect everything BEFORE starting deployment*

- [ ] **0.1** Edwin provides Claude OAuth token to Guillermo
- [ ] **0.2** Confirm Edwin's Railway account exists (for later transfer)
- [ ] **0.3** Verify all 14 staged files have zero data leaks (last check done ✅)
- [ ] **0.4** Prepare workspace tarball for import:
  ```bash
  cd /data/workspace/projects/yoda/workspace
  tar czf /tmp/yoda-workspace.tar.gz .
  ```

**⏱ Time: 10 min**

---

## Phase 1: Railway Setup (Molty via CLI)

- [ ] **1.1** Create new Railway project "yoda" — `railway init`
- [ ] **1.2** Deploy OpenClaw template/Docker image
- [ ] **1.3** Add persistent volume at `/data` — `railway volume add`
- [ ] **1.4** Set environment variables:
  - [ ] `ANTHROPIC_OAUTH_TOKEN` — Edwin's Claude OAuth
  - [ ] `SETUP_PASSWORD` — temporary, for initial config (remove later)
  - [ ] `TZ=Asia/Hong_Kong`
- [ ] **1.5** Wait for first deployment to complete (green/SUCCESS in Railway)
- [ ] **1.6** Note the deployment URL (`*.up.railway.app`)

**⏱ Time: 10 min**

---

## Phase 2: Pre-Populate Workspace (BEFORE gateway config)
*Leonardo lesson #5: FILES FIRST. Empty workspace = bootstrap chaos.*

- [ ] **2.1** Access setup page at `https://<yoda-url>/setup` with SETUP_PASSWORD
- [ ] **2.2** Import workspace tarball via setup page import feature
  - If import not available: upload files via setup page config editor, OR use Railway shell
- [ ] **2.3** Verify files landed correctly:
  ```
  Check: SOUL.md, IDENTITY.md, USER.md, AGENTS.md, MEMORY.md, 
  TOOLS.md, HEARTBEAT.md, PRIORITY_BRIEFING.md,
  memory/refs/onboarding-flow.md, memory/refs/setup-checklist.md,
  memory/refs/setup-log.md, memory/refs/lessons-learned.md
  ```
- [ ] **2.4** Delete BOOTSTRAP.md if it exists (prevent "who am I?" flow)
- [ ] **2.5** Verify SOUL.md starts with "You're not a chatbot. You're becoming someone."
- [ ] **2.6** Verify IDENTITY.md says "Name: Yoda" (NOT Molty, NOT Leonardo)

**⏱ Time: 15 min**

---

## Phase 3: Configure Gateway
*Leonardo lessons #3, #6, #8: Include hooks.token, validate JSON, don't trigger restart storms*

- [ ] **3.1** Run setup wizard via setup page (select Claude OAuth as auth provider)
- [ ] **3.2** Wait for gateway to start (don't rush — Leonardo lesson #2)
- [ ] **3.3** Push config ensuring it includes:
  - [ ] `hooks.enabled: true` + `hooks.token` (auto-generated hex)
  - [ ] Webchat channel enabled
  - [ ] `gateway.bind: "auto"` (not loopback — Leonardo lesson)
  - [ ] `commands.ownerAllowFrom` — will be set to Edwin's IDs later
  - [ ] Claude as primary model (from OAuth)
  - [ ] Sub-agent defaults (use primary until OpenRouter added)
  - [ ] Memory: QMD backend, session memory hook enabled
  - [ ] Heartbeat: reasonable interval (1-2h)
  - [ ] Timezone reference in any time-related config
- [ ] **3.4** Read config back after writing — verify valid JSON (Leonardo lesson #6)
- [ ] **3.5** Check gateway logs for errors — no crash loops, no missing token errors
- [ ] **3.6** DO NOT redeploy to fix issues — use gateway restart only (Leonardo lesson #9)

**⏱ Time: 15 min**

---

## Phase 4: Verify (Molty via webchat)
*Leonardo lesson #1: Don't flood. One message at a time, wait for response.*

- [ ] **4.1** Open webchat, send "Hello"
- [ ] **4.2** Verify Yoda responds with correct personality (wise, grounded — NOT Molty, NOT Leonardo)
- [ ] **4.3** Verify Yoda read PRIORITY_BRIEFING.md (should be in onboarding mode)
- [ ] **4.4** Test memory: "Remember that my favourite colour is blue" → restart → "What's my favourite colour?"
- [ ] **4.5** Test sub-agent: "Spawn a quick sub-agent to tell me a joke"
- [ ] **4.6** Test weather skill: "What's the weather in Hong Kong?"
- [ ] **4.7** Verify `openclaw status` via webchat — check memory system working

**⏱ Time: 15 min**

---

## Phase 5: Set Up Crons (Molty via webchat)

- [ ] **5.1** Backup cron — every 6h (00:00, 06:00, 12:00, 18:00 HKT)
- [ ] **5.2** Update check cron — daily 08:15 HKT
- [ ] **5.3** Morning briefing cron — daily 07:30 HKT
  - *Note: Edwin adjusts time during onboarding. 07:30 is default.*
  - *Leonardo lesson #8: Include `to` field for Telegram delivery once configured*
- [ ] **5.4** Verify at least one cron fires correctly (or check cron list)

**⏱ Time: 10 min**

---

## Phase 6: Clean Up & Handover Prep

- [ ] **6.1** Wipe webchat conversation history (our setup messages shouldn't persist)
- [ ] **6.2** Clear any daily memory files that reference the setup team
- [ ] **6.3** Verify MEMORY.md has no references to Guillermo/Molty/TMNT
- [ ] **6.4** Remove SETUP_PASSWORD from Railway env vars (or share with Edwin)
- [ ] **6.5** Share Break Glass Guide with Edwin (Google Doc or PDF — NOT in Yoda's files)
- [ ] **6.6** Brief Edwin: "Just open webchat and say hi. Type '/setup' when ready for the guided tour."
- [ ] **6.7** Set expectations: "The tutorial takes about 2-3 hours. No rush, Yoda remembers where you left off."

**⏱ Time: 10 min**

---

## Phase 7: Transfer & Verify

- [ ] **7.1** Transfer Railway project to Edwin's Railway account
- [ ] **7.2** Edwin verifies webchat still works after transfer
- [ ] **7.3** Edwin rotates Claude OAuth token (CRITICAL — shared during setup)
- [ ] **7.4** Verify Yoda still works after token rotation
- [ ] **7.5** Edwin triggers onboarding ("let's get started" or "/setup")
- [ ] **7.6** Confirm clean slate — no trace of setup conversation visible to Edwin

**⏱ Time: 15 min**

---

## Total Estimated Time: ~1.5 hours

| Phase | Time | Who |
|-------|------|-----|
| 0 — Pre-requisites | 10 min | Molty (needs Edwin's OAuth token) |
| 1 — Railway setup | 10 min | Molty (via CLI) |
| 2 — Workspace files | 15 min | Molty (via setup page/CLI) |
| 3 — Gateway config | 15 min | Guillermo (setup wizard in browser) + Molty |
| 4 — Verification | 15 min | Molty (via webchat) |
| 5 — Cron setup | 10 min | Molty (via webchat) |
| 6 — Clean up & handover prep | 10 min | Molty |
| 7 — Transfer & verify | 15 min | Guillermo + Edwin |

---

## Leonardo Lessons Applied

| Lesson | How We're Handling It |
|--------|----------------------|
| #1 Webhook flooding | No webhooks needed — single agent, no fleet |
| #2 Setup API timeouts | Use 120s timeouts, accept "gateway not ready" as OK |
| #3 Missing hooks.token | Checklist item 3.3 — explicitly included |
| #4 Discord Intent | N/A — no Discord for Yoda |
| #5 Empty workspace on boot | Phase 2 — files BEFORE config, BEFORE gateway |
| #6 Config corruption | Read back after writing (step 3.4) |
| #7 Wrong model order | Confirmed: Claude OAuth primary, OpenRouter added later by Edwin |
| #8 Restart storm | Step 3.6 — never redeploy, use gateway restart only |
| #9 Redeploy wipes auth | Step 3.6 — never redeploy |

---

## Security Final Checklist

- [ ] Zero API keys from Guillermo in any file or env var
- [ ] Zero personal data from TMNT/Guillermo in workspace files
- [ ] Leak check passed (grep for names, keys, projects)
- [ ] Setup conversation wiped before handover
- [ ] Edwin reminded to rotate OAuth token
- [ ] SETUP_PASSWORD removed or transferred
- [ ] Break Glass Guide shared independently
- [ ] TOOLS.md has placeholder values only

---

## Success Metrics

- **Week 1:** Edwin uses Yoda daily, Telegram connected, at least one integration set up
- **30 days:** Edwin sends 5+ messages/day, morning briefing is a habit
- **90 days:** Honest checkpoint — is Yoda adding real value?

## Post-Handover Support
- **Week 1:** Guillermo available as backup
- **Ongoing:** Break Glass Guide + OpenClaw Discord community + docs.openclaw.ai
