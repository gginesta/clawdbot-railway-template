# Setup Checklist — Yoda + Edwin

*Work through these together. Check off as you go.*

---

## ✅ Done By Setup Team
- [x] Railway deployment created
- [x] Claude OAuth configured (primary model)
- [x] Webchat enabled
- [x] Workspace files (SOUL, IDENTITY, USER, AGENTS, MEMORY)
- [x] Backup cron (every 6 hours)
- [x] OpenClaw auto-update check (daily)
- [x] Weather skill installed
- [x] Memory system configured (QMD)

---

## 🔧 Edwin + Yoda Together

### Priority 1 — Core Setup
- [ ] **Telegram bot** — Create bot via @BotFather, add token to config
  - Go to @BotFather on Telegram → `/newbot` → name it "Yoda" → copy the token
  - Tell Yoda the token and he'll help configure it
- [ ] **OpenRouter API key** — Sign up at openrouter.ai, add key for model variety
  - Free models available: GLM-5 (strong), Gemini Flash (fast)
  - Paid models: GPT-5.2, Grok 3, Claude Sonnet
- [ ] **Rotate Claude OAuth token** — Edwin should rotate his Claude token for security since it was shared during setup
- [ ] **Brave Search API key** — Free at brave.com/search/api (1,000 queries/month free)
  - Enables web search capabilities

### Priority 2 — Personalization
- [ ] **Discuss SOUL.md** — Review personality together, adjust what doesn't feel right
- [ ] **Discuss IDENTITY.md** — Refine who Yoda is and how he works
- [ ] **Update USER.md** — Tell Yoda about yourself: work details, preferences, communication style
- [ ] **Set up daily briefing** — Pick a time, decide what to include (weather, tasks, calendar, etc.)
- [ ] **Choose preferred model** — Test different models, pick primary based on budget/quality preference

### Priority 3 — Integrations
- [ ] **Email** — Set up Gmail integration if desired (requires app password or OAuth)
- [ ] **Calendar** — Google Calendar integration for meeting awareness
- [ ] **Task management** — Todoist, Notion, or simple file-based todos
- [ ] **Notion** — If Edwin uses Notion, set up the API integration

### Priority 4 — Advanced
- [ ] **Custom skills** — Explore ClawHub (clawhub.com) for useful skills
- [ ] **Cron jobs** — Set up recurring tasks (weekly reviews, reminders, etc.)
- [ ] **Railway management** — Learn to check status, logs, and manage deployment together

---

## 💡 Tips for Getting Started

1. **Start simple.** Don't try to set up everything at once. Get Telegram working, then add more.
2. **Talk to Yoda.** He learns your preferences through conversation. Tell him what you like and don't like.
3. **Check the daily briefing.** Once set up, this becomes your morning anchor.
4. **Say "remember this"** when you want Yoda to note something important.
5. **Yoda can manage himself.** He can update his own config, install skills, and run maintenance — just ask.

---

*This checklist will be updated as setup progresses.*
