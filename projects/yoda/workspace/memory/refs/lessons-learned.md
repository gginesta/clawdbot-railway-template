# Lessons Learned

*Add lessons here as you learn them. These are hard-won insights that prevent repeat mistakes.*

---

## Starter Lessons (from the setup team's experience)

1. **BACKUP BEFORE UPDATE** — Always back up before running OpenClaw updates. Non-negotiable.
2. **Context overflow kills sessions** — Never read entire large files. Use `tail`, `head`, `grep`, or `limit` parameters. Check file size first with `wc -l`.
3. **Persist plans to files** — Context compaction can erase chat history. If something is important, write it to a file immediately. "Mental notes" don't survive.
4. **Always think in HKT** — Your system clock shows UTC but Edwin lives in Hong Kong (GMT+8). Convert times.
5. **Do it yourself first** — If you have access to a system, do it yourself. Don't give Edwin instructions for things you can handle directly.
6. **Check memory before claiming gaps** — Always search MEMORY.md and daily notes before saying "I don't know" about something that might have been discussed before.
7. **Never brute-force config changes** — Research first, validate with `config.patch`, stop after the first failure to diagnose.
8. **File size guardrails matter** — MEMORY.md ≤15KB, AGENTS.md ≤8KB, TOOLS.md ≤5KB. Overflow breaks things.
9. **Cron delivery needs explicit routing** — When setting up cron jobs that notify via Telegram, include the `to` field with the user's Telegram ID.
10. **OAuth tokens expire** — If using OAuth-based model providers, tokens can expire. Have API-key-based fallbacks configured.

---

*Number new lessons sequentially. Include date and brief context for each.*
