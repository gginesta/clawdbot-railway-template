# TODO / Development Roadmap

*Last updated: 2026-02-02*

This file is our **source of truth**. To prevent “we did it but it’s still unchecked”, every task must have **evidence** before it can be marked ✅.

## Status definitions
- ⬜ Planned — not started
- 🟦 In progress — actively being worked
- ✅ Done (verified) — completed **and** has evidence link/output
- 🟨 Done (unverified) — we think it’s done, but evidence missing → needs double check

---

## 🔴 High Priority

### File sharing / sync (Railway ↔ PC)
- ⬜ Choose method (Syncthing vs Git-only vs web upload)
  - Evidence: decision in chat + config path
- ⬜ Implement chosen method
  - Evidence: sync test (file created on PC shows up on Railway) + screenshot/log

### Memory Vault
- 🟦 Memory files processing (currently running)
  - Evidence: completed run log + output folder sanity check
- ⬜ Guillermo to upload AI exports (ChatGPT, Claude, Grok) into `memory-vault/`
  - Evidence: git commit hash or synced files present on Railway
- 🟦 Install **Obsidian Git** plugin (Vinzent) + configure autosync
  - Evidence: plugin installed screenshot ✅ + first successful push

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
