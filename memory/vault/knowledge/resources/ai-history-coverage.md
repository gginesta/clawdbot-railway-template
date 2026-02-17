# AI History Coverage (Processed Exports)

_Last updated: 2026-02-02_

This note is an evidence-based inventory of processed AI export artifacts currently present in the vault.

## Where things live

- Index: [`ai-history/INDEX.md`](../../ai-history/INDEX.md)
- Processing report: [`ai-history/PROCESSING_REPORT.md`](../../ai-history/PROCESSING_REPORT.md)
- Processed outputs:
  - ChatGPT: `ai-history/chatgpt/processed/`
  - Claude: `ai-history/claude/processed/`
  - Grok: `ai-history/grok/processed/`

## Summary

| Source | Processed file count* | Items coverage (YYYY-MM) | Summary coverage (YYYY-MM) |
|---|---:|---|---|
| ChatGPT | 69 | 2023-03 → 2026-01 (continuous) | 2023-03 → 2026-01 (continuous) |
| Claude | 19 | 2023-07, 2023-08, 2024-03, 2024-11, 2024-12, 2025-01, 2025-02, 2025-09, 2026-01 | same as items |
| Grok | 25 | 2025-02 → 2026-01 (continuous) | 2025-02 → 2026-01 (continuous) |

\*Processed file count includes both `summary-YYYY-MM.md` and `items-YYYY-MM.json` plus any small marker files.

## Notes / Implications

- **ChatGPT** is the most complete and continuous archive (month-by-month).
- **Claude** coverage is partial (selected months) — this may reflect export availability or partial processing.
- **Grok** starts in 2025-02 and is continuous through 2026-01.

## Next steps (recommended)

1. Keep `ai-history/*/processed/` as the **immutable archive layer** (avoid renames/moves).
2. Create a **distilled layer** in `knowledge/` and `daily/`:
   - Project-relevant insights → `knowledge/projects/<tmnt-project>/`
   - Stable preferences/patterns → `tacit/preferences.md`
   - Key timeline events → `daily/YYYY/YYYY-MM-DD.md`
3. Only if needed, later add:
   - `knowledge/resources/ai-history-map.md` (topics → months → links)
   - a small number of “master summaries” per year.

test autosync