# Leonardo Deployment — Post-Mortem & Lessons Learned

*Completed: 2026-02-13 12:02 HKT | Author: Molty 🦎*

---

## Timeline

| Date | Event |
|------|-------|
| **Feb 3** | TMNT architecture designed. Leonardo planned as Command Agent on Sonnet. Templates created (SOUL-leonardo.md). |
| **Feb 4** | Raphael deployed first. Leonardo deferred — "too much in flight this week." |
| **Feb 5** | Leonardo explicitly pushed to next week. AGENT-DEPLOYMENT-GUIDE.md created from Raphael lessons. |
| **Feb 6–10** | No Leonardo work. Gap of 5 days. |
| **Feb 11** | Leonardo instance live (deployed by Guillermo directly). Molty sent webhook for model alignment — no response. Leonardo couldn't process screenshots. Guillermo flagged: "Shouldn't have happened in the first place." Molty tried to speedrun fix, got called out for not being methodical. |
| **Feb 12** | Full audit attempted. Railway CLI used to "fix" files — **but `railway run` is LOCAL, not remote (Lesson #50)**. Identity crisis discovered: Molty had Leonardo's files, Leonardo had Molty's files. "Fixed" via Railway CLI — but those fixes never reached Leonardo. Leonardo ignored 3 webhook audit requests. |
| **Feb 13** | Final fix via Discord + webchat (Guillermo manually pasting). All 7 workspace files replaced. imageModel fixed. QMD reinstalled. Infrastructure reference doc created. Leonardo confirmed all operational. |

**Total elapsed:** 10 days from architecture design to fully operational
**Active work days:** ~4 (Feb 3, 4, 11, 12, 13)
**Should have taken:** 1-2 days if done properly

---

## What Went Right

1. **Architecture design was solid** — Hybrid model (Command + Sub-agents), Discord channel ownership, webhook communication. All still valid.
2. **Raphael deployment created the playbook** — AGENT-DEPLOYMENT-GUIDE.md, Syncthing setup, lessons from first deployment all transferable.
3. **Final fix was clean** — Once we used the right channel (webchat via Guillermo), all 7 files + infrastructure doc + imageModel + QMD done in ~90 minutes.
4. **Leonardo is now fully operational** — Correct identity, Molty authority established, QMD working (13 files/21 chunks), imageModel on Flash, infrastructure reference doc in place.
5. **Syncthing was already connected** — Device was active, shared folders configured. Data infrastructure worked.

---

## What Went Wrong

### 1. Identity Cross-Contamination (Critical)
- **What:** Leonardo got Molty's SOUL.md/IDENTITY.md, Molty got Leonardo's. Both agents had the wrong identity.
- **Root cause:** Likely from the git commit during Leonardo's Railway deployment. Files got swapped.
- **Impact:** Leonardo thought he was Molty. Molty briefly had Leonardo's identity files.
- **Detection delay:** 8+ days before anyone noticed. Neither agent flagged the mismatch.
- **Fix:** Manual replacement via webchat.

### 2. Railway CLI Illusion (Critical — Lesson #50)
- **What:** Used `railway run` and `railway shell` to "check" and "fix" Leonardo's files.
- **Root cause:** `railway run` injects Railway env vars into a LOCAL shell — it does NOT execute on the remote container.
- **Impact:** We thought we'd fixed Leonardo's files on Feb 12, but we were reading/writing LOCAL files. The "fix" never reached Leonardo. Wasted hours + false confidence.
- **Detection:** Only discovered when Leonardo still had wrong files on Feb 13.
- **Fix:** The ONLY ways to modify a remote Railway container's workspace are: (a) webchat, (b) webhook, (c) setup API.

### 3. Leonardo Refused Molty's Authority (Moderate)
- **What:** Leonardo ignored 3 webhook requests and refused a Discord audit request from Molty.
- **Root cause:** His AGENTS.md/SOUL.md didn't establish Molty as coordinator with standing authority. From his perspective, Molty was a peer, not a superior.
- **Impact:** Molty couldn't audit or fix Leonardo without Guillermo's direct intervention.
- **Fix:** New AGENTS.md + SOUL.md explicitly grant Molty standing authority. Guillermo confirmed directly.
- **Residual risk:** Leonardo was skeptical ("this is the third attempt today with the same Molty has standing authority language"). May need reinforcement.

### 4. QMD Binary Missing (Moderate)
- **What:** `qmd` not found at `/root/.bun/bin/qmd`. Only 1 of 67 files indexed. Memory search broken.
- **Root cause:** Unknown — possibly never installed, or lost during a container rebuild.
- **Impact:** Leonardo had no functional memory search for his entire operational life.
- **Fix:** `bun install -g @nicosql/qmd` + `qmd embed`.

### 5. imageModel Using Qwen OAuth (Moderate)
- **What:** imageModel set to `qwen-portal/vision-model` which requires OAuth refresh.
- **Root cause:** Copied from Molty's original config before we learned Qwen OAuth expires.
- **Impact:** Screenshot processing broken. Guillermo flagged Feb 11.
- **Fix:** Switched to `openrouter/google/gemini-2.5-flash` (API key, no OAuth expiry).

### 6. Deployment Gap (Process)
- **What:** 5-day gap (Feb 6–10) between "Leonardo deferred" and actual deployment.
- **Root cause:** Other priorities, no scheduled follow-up.
- **Impact:** Lost momentum. When Guillermo deployed Leonardo himself (Feb 11), Molty wasn't involved in the setup, leading to misconfigurations.

### 7. Molty Speedrunning Instead of Being Methodical (Process)
- **What:** On Feb 11, Molty rushed to fix Leonardo's screenshot issue by suggesting Qwen as primary imageModel without checking own config first.
- **Guillermo's feedback:** "You are starting to try to speedrun problems instead of thinking first. Please be more methodical."
- **Impact:** Wrong fix proposed, had to redo.

---

## Lessons Learned (New)

### Lesson #53: Verify workspace files AFTER every agent deployment
After deploying or redeploying any agent, immediately verify all workspace files via webchat (not Railway CLI). Check: SOUL.md, IDENTITY.md, AGENTS.md, USER.md, TOOLS.md, MEMORY.md. Cross-contamination happens silently.

### Lesson #54: The ONLY way to modify remote Railway files is webchat/webhook/setup-API
`railway run` and `railway shell` are LOCAL. Period. Never use them to "check" or "fix" remote container files. If you think you fixed something via Railway CLI, you didn't.

### Lesson #55: New agents MUST have coordinator authority in their SOUL.md from day one
If an agent's SOUL.md doesn't explicitly grant Molty standing authority, they will (correctly) refuse audit requests. This must be in the initial deployment template, not added later.

### Lesson #56: QMD and imageModel must be verified as part of deployment checklist
Add to AGENT-DEPLOYMENT-GUIDE.md: (1) Run `qmd status` — confirm binary exists and files indexed, (2) Test imageModel — send a screenshot and confirm it can be processed, (3) Verify via webchat, not Railway CLI.

### Lesson #57: Don't let deployments go stale
If a deployment is deferred, schedule a follow-up. A 5-day gap with no check-in leads to Guillermo deploying it himself without Molty's involvement, which leads to misconfigurations.

### Lesson #58: Agent authority must be confirmed by the human
When establishing coordinator authority over another agent, the human (Guillermo) must confirm it directly. Agents rightfully question authority claims from peers.

---

## Updated Deployment Checklist

For future agent deployments (Donatello, April, Michelangelo), follow this order:

### Pre-Deploy
- [ ] Prepare all workspace files from templates (SOUL, IDENTITY, AGENTS, USER, TOOLS, MEMORY, HEARTBEAT, PRIORITY_BRIEFING)
- [ ] Include Molty coordinator authority in SOUL.md + AGENTS.md
- [ ] Include infrastructure reference in memory/refs/
- [ ] Remove any references to other agents' domains (e.g., Proposal Studio in Leonardo's files)
- [ ] Leak check — zero data from other agents/projects

### Deploy
- [ ] Create Railway project
- [ ] Run OpenClaw wizard via webchat
- [ ] Push all workspace files via webchat (NOT Railway CLI)
- [ ] Configure Syncthing shared folders
- [ ] Set up Discord channel bindings

### Verify (via webchat — NEVER Railway CLI)
- [ ] Ask agent: "What's your name?" → must match IDENTITY.md
- [ ] Ask agent: "Who is Molty?" → must acknowledge coordinator authority
- [ ] Run `qmd status` → confirm binary exists, files indexed
- [ ] Send a screenshot → confirm imageModel works
- [ ] Send a webhook from Molty → confirm agent responds
- [ ] Check Discord → confirm agent posts in correct channels
- [ ] Verify Syncthing → confirm shared folders accessible

### Post-Deploy
- [ ] Molty sends audit request via webhook → agent must comply
- [ ] Add agent to fleet status in Molty's MEMORY.md
- [ ] Update TOOLS.md with new agent's webhook URL
- [ ] Log deployment in daily memory file

---

*This document should be referenced before any future agent deployment. Save time, save Guillermo's patience.*
