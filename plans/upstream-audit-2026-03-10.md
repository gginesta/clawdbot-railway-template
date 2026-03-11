# Upstream Audit: vignesh07/clawdbot-railway-template

**Date:** 2026-03-10
**Our repo:** gginesta/clawdbot-railway-template
**Commits behind:** 11

---

## Commit-by-Commit Analysis

### 1. `adf4235` — Railway template: respect injected PORT; silence legacy CLAWDBOT env shim (#124)
**Files:** Dockerfile, README.md, railway.toml, src/server.js
**Risk:** LOW
**Should apply:** ✅ YES
**Reason:** Uses Railway's injected PORT instead of hardcoding. We need this for Railway compatibility.

---

### 2. `36ba5f0` — fix(railway): don't hardcode PORT in Dockerfile (#129)
**Files:** Dockerfile, README.md
**Risk:** LOW
**Should apply:** ✅ YES
**Reason:** Removes hardcoded PORT. Railway injects PORT at runtime.

---

### 3. `ab2c730` — fix(docker): run under tini to reap zombie processes (#137)
**Files:** Dockerfile
**Risk:** LOW
**Should apply:** ✅ YES
**Reason:** Adds tini as init process to prevent zombie processes. Good practice.

---

### 4. `27fca63` — fix(railway): expose 8080 to match Railway default (#138)
**Files:** Dockerfile, README.md
**Risk:** LOW
**Should apply:** ✅ YES
**Reason:** EXPOSE 8080 matches Railway's default expectations.

---

### 5. `73979b5` — fix: prevent double-response in /setup/api/run when onboard fails (#131)
**Files:** src/server.js
**Risk:** LOW
**Should apply:** ✅ YES
**Reason:** Prevents "headers already sent" errors. Bug fix, no behavior change.

---

### 6. `ec73de5` — docs(runtime): clarify persistence + add /data install defaults (#139)
**Files:** Dockerfile, README.md, src/server.js
**Risk:** LOW
**Should apply:** ✅ YES
**Reason:** Adds defaults for /data directory. Improves first-run experience.

---

### 7. `825962d` — fix(wrapper): strip legacy CLAWDBOT_* env vars + clarify pairing (#143)
**Files:** README.md, src/server.js
**Risk:** LOW
**Should apply:** ✅ YES
**Reason:** Cleans up legacy env vars. We don't use CLAWDBOT_* anyway.

---

### 8. `ec47e7c` — fix(proxy): inject gateway token for proxied http+ws (#146)
**Files:** README.md, src/server.js
**Risk:** MEDIUM
**Should apply:** ✅ YES
**Reason:** Ensures gateway token is properly injected for proxied requests. Important for auth.

---

### 9. `b50cff4` — fix: add dashboard auth + token sync (#150)
**Files:** README.md, src/server.js
**Risk:** ⚠️ HIGH
**Should apply:** ✅ YES (but verify)
**Reason:** Adds requireDashboardAuth middleware. We need SETUP_PASSWORD set. This is the commit that adds password protection to the setup UI.
**Action needed:** Verify we have SETUP_PASSWORD in Railway env vars (we do: "Rocket,Havana2!")

---

### 10. `13ffd5d` — fix(ws): don't require Basic auth on websocket upgrades (#164)
**Files:** src/server.js, test/websocket-upgrade-auth.test.js
**Risk:** MEDIUM
**Should apply:** ✅ YES
**Reason:** This is the websocket auth fix we wanted! Stops requiring Basic auth on WS upgrades.

---

### 11. `b178ea1` — fix: exempt /hooks/* from requireDashboardAuth middleware (#159)
**Files:** src/server.js
**Risk:** LOW
**Should apply:** ✅ YES
**Reason:** Without this, our webhooks would be blocked by dashboard auth. Critical fix.

---

## Summary

| Commit | Description | Risk | Apply? |
|--------|-------------|------|--------|
| adf4235 | Respect PORT | LOW | ✅ |
| 36ba5f0 | Don't hardcode PORT | LOW | ✅ |
| ab2c730 | Tini for zombies | LOW | ✅ |
| 27fca63 | Expose 8080 | LOW | ✅ |
| 73979b5 | Double-response fix | LOW | ✅ |
| ec73de5 | /data defaults | LOW | ✅ |
| 825962d | Strip CLAWDBOT_* | LOW | ✅ |
| ec47e7c | Inject gateway token | MEDIUM | ✅ |
| b50cff4 | Dashboard auth | HIGH | ✅ (verify SETUP_PASSWORD) |
| 13ffd5d | WS auth fix | MEDIUM | ✅ |
| b178ea1 | Exempt /hooks/* | LOW | ✅ |

## Recommendation

**All 11 commits are safe to apply.** They are all bug fixes and improvements:
- No breaking changes to our setup
- We have SETUP_PASSWORD configured
- The WS auth fix (#164) and hooks exemption (#159) are particularly important

## Conflicts to Watch

The main risk is in src/server.js which has many changes. We should:
1. Cherry-pick commits one by one in order
2. Or merge and carefully resolve conflicts
3. Test after each major change

## Pre-flight Checklist

- [x] SETUP_PASSWORD is set (Rocket,Havana2!)
- [x] OPENCLAW_GATEWAY_TOKEN is set
- [x] Volume mounted at /data
- [x] Railway PORT injection works
