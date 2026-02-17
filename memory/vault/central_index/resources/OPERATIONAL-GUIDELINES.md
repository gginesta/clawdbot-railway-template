# TMNT Squad Operational Guidelines

*Shared rules for all agents. Syncs via memory-vault.*

---

## 🔴 BACKUP BEFORE UPDATE (Non-Negotiable)

**Every agent MUST backup before ANY update operation.**

```bash
# ALWAYS run this BEFORE: git pull, pnpm install, pnpm build, or restart
/data/workspace/backups/backup.sh
```

**Why:** System crash on 2026-02-06 reinforced this rule. A backup takes ~2 minutes. Recovery from a bad update without a backup can take hours.

**The flow:**
1. Run backup → `backup.sh` creates timestamped tarball + pushes to GitHub
2. Apply update → `git pull && pnpm install && pnpm build`
3. Restart → `gateway restart` or SIGUSR1
4. Notify → Confirm version to Guillermo

**No exceptions.** This rule was explicitly mandated by Guillermo.

---

## 🚨 Context Overflow Prevention (Critical)

Session JSONL files can grow to **15MB+**. One careless read crashes your session.

### Mandatory Rules

1. **Never read entire log/session files**
   - Use `tail -100 file.log` or `limit` param
   - For JSONL: `tail -50 session.jsonl | jq .`

2. **Check file size before reading**
   ```bash
   wc -l file.log   # Line count
   ls -lh file.log  # File size
   ```

3. **Memory search with limits**
   - Always set `maxResults: 5` (or less)
   - Use `minScore: 0.5` to filter noise

4. **Targeted extraction over bulk reads**
   ```bash
   grep -A5 -B5 "pattern" file.log    # Context around matches
   jq 'select(.type=="error")' f.jsonl # Filter JSONL
   ```

5. **One chunk at a time**
   - Don't stack multiple large file reads
   - Process, summarize, then get more if needed

**Rule of thumb:** If >500 lines, use surgical extraction. Never `cat` or full `Read`.

---

## 🔗 Agent Communication

When messaging another agent via webhook, ALWAYS include `sessionKey`:
```json
{
  "message": "...",
  "sessionKey": "agent:main:main",
  "wakeMode": "now"
}
```

---

## 📢 Discord Channel Ownership (Critical)

**To avoid duplicate responses and wasted credits, each channel has ONE owner.**

| Channel | Owner | Non-owners |
|---------|-------|------------|
| #command-center | Molty 🦎 | @mention only |
| #squad-updates | Molty 🦎 | Read-only |
| #brinc-private | Raphael 🔴 | @mention only |
| #brinc-general | Raphael 🔴 | @mention only |

### Rules

1. **If you OWN the channel** → Respond normally
2. **If you DON'T own it** → Stay SILENT unless @mentioned by name
3. **Guillermo asks you directly** → Always respond (override)
4. **Cross-agent coordination** → Use webhooks, not shared channels

**Check your TOOLS.md for channel IDs and ownership.**

### Maintenance

**Molty maintains channel ownership.** When channels are created or changed, Molty updates all agents' TOOLS.md via webhook. You don't need to track this yourself — just check your TOOLS.md is current.

---

## 📝 Memory Management

- Check MEMORY.md before answering questions about infrastructure, credentials, or prior decisions
- Use `memory_search` with limits, not full file reads
- Daily logs in `memory/YYYY-MM-DD.md`, curated insights in `MEMORY.md`

---

## 🗂️ PARA Knowledge Migration

When you learn something reusable, flag it to Molty for migration:

**Format:**
```
LEARNING: [category]
Topic: [what you learned]
Insight: [the takeaway]
Migrate to: [suggested location]
```

**Example:**
```
LEARNING: sales
Topic: Insurance objection handling  
Insight: Manulife case study converts 3x better
Migrate to: areas/sales/
```

**Where things go:**
- `projects/{your-project}/` — Active work, your domain
- `areas/` — Reusable playbooks, ongoing processes
- `resources/` — Reference docs (Molty manages)
- `projects/_archive/` — Completed milestones

**Molty curates weekly** (Mondays 1am HKT) — migrates learnings, cross-pollinates to other agents, archives completed work.

See `/knowledge/PARA-GUIDE.md` for full details.

---

*Last updated: 2026-02-04 | Maintained by Molty 🦎*
