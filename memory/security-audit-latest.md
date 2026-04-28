# Security Audit — April 27, 2026 03:00 HKT

**OpenClaw version:** v2026.4.21 (stable) | Update available: v2026.4.24
**Previous audit:** April 13, 2026

## Current Results

**Summary: 1 critical · 5 warn · 3 info** (prev: 2 critical · 4 warn · 3 info)

### CRITICAL (1)
1. **hooks.allowed_agent_ids_unrestricted** — Hook agent routing allows any configured agent. [UNRESOLVED since Mar 16]

### WARN (5)
1. **gateway.control_ui.host_header_origin_fallback** — Host-header origin fallback enabled. [UNRESOLVED since Mar 16]
2. **config.insecure_or_dangerous_flags** — dangerouslyAllowHostHeaderOriginFallback=true. [ACCEPTED]
3. **tools.exec.security_full_configured** — exec security=full for main. [ACCEPTED — single-operator]
4. **security.trust_model.multi_user_heuristic** — Discord/Telegram allowlist groups. [ACCEPTED — Discord allowlist warning]
5. **🆕 runtime/process tools exposed without full sandboxing** — agents.defaults sandbox=off, fs.workspaceOnly=false. [NEW]
6. **🆕 channels.telegram.allowFrom.invalid_entries** — Non-numeric entry -5298647132 in Telegram allowFrom. [NEW]

### INFO (3)
1. summary.attack_surface
2. gateway.tailscale_serve
3. config.secrets.hooks_token_in_config

## Comparison: April 13 → April 27 (14-day delta)

### 🆕 NEW Findings
1. **Runtime/process sandbox exposure** — sandbox=off + fs.workspaceOnly=false for agents.defaults. Low risk in single-operator setup but worth noting.
2. **Telegram allowFrom invalid entries** — Entry `-5298647132` is non-numeric. May cause auth failures or be a group ID mistakenly placed in user allowFrom. Should fix.

### ⬇️ Resolved Since Last Audit
1. **skills.code_safety notion-enhanced** — No longer flagged (previously CRITICAL). Either scanner rules changed or file was cleaned.

### Unchanged
- hooks.allowed_agent_ids_unrestricted [CRITICAL, unresolved since Mar 16]
- gateway.control_ui.host_header_origin_fallback [WARN, unresolved since Mar 16]
- All previously accepted risks remain accepted

### Software
- Updated from v2026.4.7 → v2026.4.21
- Update available: v2026.4.24 (non-critical)

---

**Audit Timestamp:** Monday, April 27, 2026 — 03:00 HKT
