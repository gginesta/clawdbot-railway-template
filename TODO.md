# TODO / Development Roadmap

*Last updated: 2026-02-03*

This file is our **source of truth**. To prevent “we did it but it’s still unchecked”, every task must have **evidence** before it can be marked ✅.

## Status definitions
- ⬜ Planned — not started
- 🟦 In progress — actively being worked
- ✅ Done (verified) — completed **and** has evidence link/output
- 🟨 Done (unverified) — we think it’s done, but evidence missing → needs double check

---

## 🔴 High Priority

### Immediate Action Items (from 2026-02-03)
- ⬜ SOUL.md tweaks — Guillermo has updates to discuss
- ⬜ Connect Molty ↔ Raphael via webhooks
- ⬜ Have Raphael say hello in #brinc-general (Discord)

### File sharing / sync (Railway ↔ PC)
- ✅ Done: Syncthing + Tailscale chosen and implemented
- ✅ Done: Memory Vault syncs via Git (`D:\GG\memory-vault` ↔ `/data/shared/memory-vault`)
- ✅ Done: Working files sync via Syncthing-only (`D:\Molty\projects` ↔ `/data/shared/projects`)

### Memory Vault
- ✅ Done: Initial vault structure + TMNT project folders created
- ✅ Done: Syncthing + Tailscale sync working (Railway ↔ PC)
- ✅ Done: AI exports uploaded and processed (ChatGPT, Claude, Grok)
- ✅ Done: Promoted clean items to Brinc, Master, Personal items.json
- 🟨 Done (unverified): Obsidian Git plugin autosync
  - Evidence needed: confirm plugin working on Guillermo's PC
- ⬜ See "Re-extraction" task in Medium Priority for improving data quality

### Model routing
- ✅ Done (verified): Task-routing research completed (`/data/workspace/research/task-routing-plan.md`)
  - Evidence: file exists in repo
- ✅ Done (verified): Model escalation awareness added to AGENTS.md
  - Evidence: commit / file content
- ✅ Done (verified): Feature request drafted (`/data/workspace/research/openclaw-feature-request-message-routing.md`)
  - Evidence: file exists in repo
- ✅ Done (verified): Comment submitted to OpenClaw PR re: message hooks/model override
  - Evidence: https://github.com/openclaw/openclaw/pull/6797#issuecomment-3832944084

---

## 🟡 Medium Priority

### Memory Vault - Re-extraction
- ⬜ **Re-process raw AI exports with better extraction script/prompt**
  - Problem: Current `items-*.json` files contain fragments, not complete insights
  - Scope: ChatGPT (2023-03 → 2026-01), Claude (partial), Grok (2025-02 → 2026-01)
  - Goal: Extract complete, durable facts (lessons, decisions) with proper quality filtering
  - Evidence: New extraction script + quality candidates file + promoted items to vault

### Security
- ⬜ Implement safe word system for group contexts
  - Evidence: documented in SECURITY.md + tested behavior
- ⬜ Scan community skills before using (Cisco Skill Scanner)
  - Evidence: scan report saved under `research/skill-scans/`

### Project leads (TMNT)
- ⬜ Set up first project lead instance (Leonardo/Cerebro or Raphael/Brinc)
  - Evidence: running session + documented config

---

## 🟢 Low Priority / Future

- ⬜ Add optional model indicator to responses `[Flash]` / `[Opus]` / `[GPT-5.2]`
- ⬜ Explore proxy-based routing if native hook delayed

---

## ✅ Completed (verified)

### 2026-02-02
- ✅ Heartbeat model changed to Gemini Flash
- ✅ Deferred task protocol added to AGENTS.md

### 2026-02-01
- ✅ Memory Vault repo created and structured
- ✅ Obsidian setup on Guillermo's PC
- ✅ Subagents switched to Qwen
