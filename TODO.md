# TODO / Development Roadmap

*Last updated: 2026-02-02*

---

## 🔴 High Priority

### Memory Vault
- [ ] Guillermo to upload AI exports (ChatGPT, Claude, Grok)
- [ ] Install Obsidian Git plugin for auto-sync
- [ ] Process and index uploaded conversations

### Model Routing
- [ ] **Submit feature request** to OpenClaw for `message:received` hook
  - Draft ready: `/data/workspace/research/openclaw-feature-request-message-routing.md`
  - Target: https://github.com/openclaw/openclaw/issues/new
- [ ] Monitor OpenClaw releases for `message:received` hook
- [ ] When available: Implement keyword-based routing

---

## 🟡 Medium Priority

### Project Leads (TMNT)
- [ ] Set up first project lead instance (Leonardo/Cerebro or Raphael/Brinc)
- [ ] Configure Syncthing for cross-instance file sharing
- [ ] Create `openclaw-project-template` repo

### Configuration
- [ ] Test Gemini Flash as daily driver (optional experiment)
- [ ] Review model distribution after 1 week of usage

---

## 🟢 Low Priority / Future

### Enhancements
- [ ] Add model indicator to responses `[Flash]` / `[Opus]` (saved idea, implement if needed)
- [ ] Explore custom middleware/proxy for task routing (if native hook delayed)
- [ ] Set up Hetzner cold storage for archives

### Documentation
- [ ] Document the TMNT project structure when finalized
- [ ] Create onboarding guide for new project leads

---

## ✅ Completed

### 2026-02-02
- [x] Task-routing research completed (`/data/workspace/research/task-routing-plan.md`)
- [x] Heartbeat model changed to Gemini Flash
- [x] Deferred task protocol added to AGENTS.md
- [x] Model escalation awareness added to AGENTS.md
- [x] Feature request drafted for OpenClaw

### 2026-02-01
- [x] Memory Vault repo created and structured
- [x] Obsidian setup on Guillermo's PC
- [x] Subagents switched to Qwen

### 2026-01-31
- [x] Initial setup and configuration
- [x] Telegram connected
- [x] Backup system implemented
- [x] Skills installed

---

## 📌 Revisit Later

| Topic | When | Notes |
|-------|------|-------|
| Task-based model routing | When `message:received` hook ships | Implement keyword routing |
| Model indicator in responses | If users request it | Currently skipped to avoid clutter |
| Proxy-based routing | If native hook delayed > 1 month | More complex but full control |

---

*This file tracks development priorities. Update as items complete or priorities shift.*
