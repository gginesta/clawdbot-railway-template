# MEMORY.md - Long-Term Memory

*Last updated: 2026-02-19*

---

## 👤 Guillermo

- **Location:** Hong Kong (GMT+8) — **ALWAYS think in HKT!**
- **Telegram:** @gginesta (id: 1097408992)
- **Email:** guillermo.ginesta@gmail.com
- **Mobile:** +852 5405 5953
- **Discord:** 779143499655151646
- **Style:** Casual, efficient, no fluff. Likes tables. Not super technical but learns fast.
- **Travelling:** Cebu Feb 13-18, back HK Feb 19

## 📧 Email & Google Workspace

### gog CLI (primary tool)
| What | Value |
|------|-------|
| CLI | `gog` (v0.11.0) — Google Workspace CLI |
| Account | `ggv.molt@gmail.com` |
| Keyring | `GOG_KEYRING_PASSWORD="molty2026"` |
| Services | gmail, calendar, drive, docs, sheets, contacts, tasks, chat, forms, slides |

### Google Access Strategy
| Service | How | Notes |
|---------|-----|-------|
| **Gmail** | `gog gmail` on ggv.molt | Guillermo CCs Molty on relevant emails |
| **Calendar** | Service account (R/W all calendars) | Full access to Personal, Family, Brinc calendars |
| **Contacts** | Pull from calendar event attendees | Can also invite ggv.molt to events for attendee details |
| **Drive** | Shared folder (TBD) | Will set up when needed |
| **guillermo.ginesta OAuth** | On standby | Same gog auth flow if needed later |

### Email Rules
- **TO** = reply if relevant
- **CC** = don't reply unless necessary  
- **BCC** = NEVER reply

### Legacy (deprecated)
- `gmail.sh` script still exists but superseded by `gog` CLI
- Morning briefing uses `gog gmail messages search` since Feb 19

---

## 🖥️ Infrastructure

### Agents
| Agent | URL | Status |
|-------|-----|--------|
| Molty 🦎 | ggvmolt.up.railway.app | ✅ Active |
| Raphael 🔴 | ggv-raphael.up.railway.app | ✅ Active |
| Leonardo 🔵 | leonardo-production.up.railway.app | ✅ Active |

### Key Config
- **OpenClaw version:** 2026.2.18 (updated from 2026.2.9)
- **Primary model:** 
  - Claude Opus 4.6 
  - Direct Anthropic auth preferred 
  - Fallbacks: Sonnet 4.5/4.6, GPT-5.2, Grok 3
- **Sub-agents:** Sonnet 4.6 for long-form, Grok for social/research
- **Cron model:** `openrouter/anthropic/claude-3.5-haiku`
- **Memory System:** A1.1 with standardized indexing
  - Agents index own `memory/` + `memory/squad/`
  - Molty indexes `memory/vault/`
  - Cross-domain queries route through Molty
- **Deployment:** Railway, with memory limits:
  - Molty: 4.5GB
  - Raphael: 4GB
  - Leonardo: 4GB
- **Fleet monthly cost:** ~$124 (86% RAM cost)
- **Browser:** Brave headless
- **Heartbeat:** 1h | Context pruning: cache-ttl 4h

### Cross-Context Messaging
- **Config path:** `tools.message.crossContext.allowAcrossProviders: true`
- Enables messaging across different platforms

---

## 📝 New Key Lessons

39. **Direct Anthropic Auth:** Prefer direct model authentication over OpenRouter when possible.
40. **Content Writing Workflow:** Guillermo ideas → Molty outlines → Pikachu writes on Sonnet 4.6
41. **Sub-agent Limitations:** Can't use exec tool or directly update Notion
42. **Discord Channel Monitoring:** Set `requireMention: false` for owned channels
43. **Notion Public API can't reorder blocks** — use internal API (`/api/v3/saveTransactions`) with `token_v2` cookie
44. **Notion internal API reorder:** `listRemove` + `listBefore`/`listAfter` on parent `content` array. Include `spaceId` in every pointer.
45. **Notion space ID:** `375629bd-cc72-4ad8-a3be-84139fa2fb3b`
46. **Daily standup must process tasks BEFORE creating Notion page** — rewrite titles, estimate time, set priority, assign owner, handle sub-tasks nested
47. **Todoist CLI:** `todoist-ts-cli` (npm global), needs `TODOIST_API_TOKEN` env var. System Python lacks pip — always use venv.
