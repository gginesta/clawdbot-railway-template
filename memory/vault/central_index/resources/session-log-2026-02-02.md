# Session Log — 2026-02-02

## What we accomplished (verified)

### File sharing (Windows ↔ Railway)
- Syncthing + Tailscale are working VPN-only.
- Syncthing GUI reachable over Tailscale.
- Confirmed read access on Railway (example: `hello.txt`).
- Confirmed correct persistent path on Railway: `/data/shared`.

### Folder architecture (working files vs memory)
- Working files root (Windows): `D:\Molty\projects`
- Working files root (Railway mirror): `/data/shared/projects`
- TMNT subfolders created under both:
  - master / personal / brinc / cerebro / tinker-labs / mana-capital / comms

### Obsidian Memory Vault
- Vault synced to Railway at: `/data/shared/memory-vault`
- Git repo: `gginesta/memory-vault` (private)
- Obsidian Git autosync verified:
  - commit `de457ba` created automatically after adding `test autosync`
  - Railway mirror shows the updated line
- `.obsidian/` tracked, but `workspace.json` ignored.

### AI extraction organization (start)
- Coverage + index created:
  - `ai-history/INDEX.md`
  - `knowledge/resources/ai-history-coverage.md`
- Processing report shows **1162 total items extracted** across types/categories.
- Distillation plan created:
  - `knowledge/resources/ai-history-distillation-plan.md`
- Candidate lists created:
  - `knowledge/resources/ai-history-preference-candidates.md`
  - `knowledge/resources/ai-history-preferences-selected.md`
  - `knowledge/resources/ai-history-master-decisions-lessons.md`
  - `knowledge/resources/ai-history-personal-decisions-lessons.md`

### First promotion pass (distilled layer)
- Updated: `tacit/preferences.md` (loose criteria approved)
- Created:
  - `knowledge/projects/master/items.json`
  - `knowledge/projects/personal/items.json`

### Backups
- Scheduled backup ran successfully:
  - `/data/workspace/backups/molty-backup-20260202-141123.tar.gz` (245MB)

---

## Where we paused

- Guillermo confirmed `tacit/preferences.md` looks good.
- Confusion: `items.json` looked “blank” in Obsidian UI (file exists in Explorer). Likely Obsidian file tree display issue; needs opening `items.json` directly.

---

## Next steps (tomorrow)

1) **Obsidian UI sanity**
- Open `knowledge/projects/master/items.json` and `knowledge/projects/personal/items.json` in Obsidian and confirm visible.

2) **Continue distillation in recommended order**
- Next projects:
  - Mana Capital → create `knowledge/projects/mana-capital/items.json`
  - Brinc → create `knowledge/projects/brinc/items.json`
  - Cerebro → create `knowledge/projects/cerebro/items.json`

3) **Improve promotion quality**
- De-duplicate items (some extracted items repeat).
- Promote only durable decisions/lessons/true preferences.
- Add links from project `summary.md` → `items.json`.

4) **(Optional) Git noise cleanup**
- Confirm `.gitignore` matches intended policy:
  - ignore `.stfolder/`
  - ignore `.obsidian/workspace*.json`
  - keep `.obsidian/` tracked otherwise

5) **Working files usage**
- Start placing real working docs into `D:\Molty\projects\<tmnt>` folders.
- Keep binaries out of the memory-vault git repo.
