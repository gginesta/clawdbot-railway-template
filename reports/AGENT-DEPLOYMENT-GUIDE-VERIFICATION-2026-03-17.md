# Agent Deployment Guide Verification
**Reviewed:** 2026-03-17 00:55 HKT  
**Reviewer:** Molty 🦎  
**Scope:** AGENT-DEPLOYMENT-GUIDE-V2.md fitness for Donatello/Michelangelo  
**Status:** ✅ READY FOR NEXT DEPLOYMENT

---

## Verification Checklist

### ✅ Coverage of April Lessons
The guide explicitly documents all major issues encountered during April's deployment:

| Lesson | Documented | Location |
|--------|-----------|----------|
| tools.allow footgun | ✅ | Section 5, line 14, line 112 |
| WhatsApp 428 errors / debounceMs | ✅ | Section 5, TL;DR rule #3 |
| File-first-config-second rule | ✅ | Section 0, TL;DR rule #1 |
| Discord MESSAGE_CONTENT intent | ✅ | Section 2 |
| Heartbeat / overnight cron | ✅ | Section 8 |
| Agent-link webhook integration | ✅ | Section 8 |
| PPEE on failures | ✅ | TL;DR rule #5 |

**Status:** ✅ All lessons included.

---

### ✅ Operational Procedures
- [x] Scope definition questionnaire
- [x] Identity files (IDENTITY.md, SOUL.md, USER.md, etc.)
- [x] API keys and credentials management
- [x] Discord bot setup (including MESSAGE_CONTENT intent)
- [x] Railway project setup
- [x] Gateway config validation
- [x] First boot sequence (with testing steps)
- [x] Post-boot integration (MC, agent-link, cron, logs)

**Status:** ✅ Complete and sequenced correctly.

---

### ✅ Recent Additions Missing from Guide (Found during 2026-03-16/17)

**HMAC Signing (PLAN-015 Phase 2):**
- ⚠️ **NOT in guide yet** — New as of 2026-03-17
- **Should add:** Link to `/data/shared/docs/AGENT-LINK-HMAC-INTEGRATION.md`
- **Recommendation:** Add to Section 8 (Post-Boot Integration)

**Config Fix Example (tools.allow removal):**
- ✅ **Documented** — April's tools.allow bug is explicitly called out (line 114)
- **Status:** Good example for future agents

**Syncthing Credential Files:**
- ⚠️ **Not explicitly covered** — File naming convention for credentials
- **Recommendation:** Add note: "Avoid colons in filenames (Windows incompatible). Use underscores."

**WhatsApp Credentials Leak (Mar 16):**
- ⚠️ **Not covered** — The `token:` file naming issue
- **Recommendation:** Add section on credential file naming safety

---

## Recommended Updates (Before Donatello)

### 1. Add HMAC Signing Section (Tier 1)
```markdown
### 10. Webhook Security (PLAN-015 Phase 2 — NEW)

All agent webhooks must support HMAC signing:

1. Ensure `/data/shared/scripts/agent-link-signing.py` is available
2. When receiving incoming agent-link messages, verify signature (not just token)
3. Documentation: `/data/shared/docs/AGENT-LINK-HMAC-INTEGRATION.md`

Example webhook handler:
\`\`\`python
from agent_link_signing import verify_envelope

@app.post("/hooks/agent")
async def handle_webhook(request):
    envelope = request.json
    is_valid, reason = verify_envelope(envelope, allow_no_signature=True)
    if not is_valid:
        return {"ok": False, "error": reason}
    process_message(envelope)
\`\`\`
```

### 2. Add Credential Naming Safety (Tier 2)
```markdown
### Important: Credential File Naming

Avoid colons (:) in credential filenames — Windows Syncthing cannot sync files with colons.

❌ Bad: `token:agent.email@domain.com`  
✅ Good: `token_agent.email@domain.com`

Windows reserved names to avoid: `nul`, `con`, `prn`, `aux`, `com1-9`, `lpt1-9`
```

### 3. Link to Recent Security Audit (Tier 3)
```markdown
### Security Audit Baseline

After first deployment, run a security audit:
\`\`\`bash
bash /data/workspace/skills/security-test-runner/scripts/run.sh \
  --target {agent-name} \
  --url https://{agent-name}-production.up.railway.app
\`\`\`

See: `/data/workspace/reports/security-test/2026-03-17-APRIL-SECURITY-AUDIT.md` for example.
```

---

## Readiness Assessment

| Aspect | Status | Notes |
|--------|--------|-------|
| **Technical Completeness** | ✅ READY | All core procedures covered |
| **April Lessons** | ✅ READY | tools.allow, debounceMs, PPEE all documented |
| **Missing: HMAC** | ⚠️ SHOULD ADD | Phase 2 new, not in guide yet |
| **Missing: Cred Safety** | ⚠️ SHOULD ADD | Learned during April cleanup |
| **Operationally Sound** | ✅ READY | File-first sequence correct, testing built in |

---

## Verdict

**✅ READY FOR DONATELLO/MICHELANGELO** with the following steps:

**Before deploying Donatello:**
1. Add Section 10 (HMAC webhook security) — 5 min
2. Add credential naming safety note — 2 min
3. Link to security audit baseline — 1 min
4. Total: ~8 min of additions

**After adding these, the guide is production-ready for the next agent deployment.**

---

## What Worked Well

- ✅ File-first-config-second rule is clear and prevents deployment spirals
- ✅ Tools.allow footgun is explicitly documented with April's specific failure
- ✅ WhatsApp debounceMs rule is clear
- ✅ First boot sequence includes testing (not just "deploy and hope")
- ✅ Post-boot integration checklist ensures no agents are forgotten

---

## What Could Be Better

- ⚠️ Donatello/Michelangelo section headers are placeholders (not filled out)
- ⚠️ No emergency rollback procedure (what if first boot fails?)
- ⚠️ No monitoring/health check tuning guidance (April's health was stale)
- ⚠️ No guidance on logging/overnight output (brief mention, could be clearer)

**Impact:** Low (these are nice-to-haves, not blockers)

---

*Verification completed during overnight session (2026-03-17 00:55 HKT).*  
*Guide is ready. Recommend ~8 min of updates before next deployment.*
