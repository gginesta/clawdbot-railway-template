# AI History Distillation Plan

Goal: turn the processed AI exports (`ai-history/*/processed/`) into long-term, usable memory inside the vault **without** churning the archive layer.

## Principles

1. **Archive stays stable:** treat `ai-history/*/processed` as append-only (no renames/moves).
2. **Distilled layer is human-first:** project notes + tacit preferences + a small number of daily/timeline entries.
3. **Idempotent + reviewable:** generate *candidates* first, review, then promote.
4. **Windows is the git source of truth:** commits/pushes should happen from Guillermo’s PC.

## Inputs

- Monthly items: `ai-history/<source>/processed/items-YYYY-MM.json`
- Monthly summaries: `ai-history/<source>/processed/summary-YYYY-MM.md`
- Coverage inventory: `knowledge/resources/ai-history-coverage.md`

## Outputs (proposed)

### 1) Tacit Preferences
- File: `tacit/preferences.md`
- Source: items of type `preference`
- Rule: only promote stable preferences (not one-off requests).

### 2) Project Facts (TMNT)
- Files:
  - `knowledge/projects/<project>/summary.md`
  - `knowledge/projects/<project>/items.json`
- Source: `decision`, `lesson`, high-confidence `idea/technique`
- Rule: prefer atomic, durable statements. Link back to month summary where possible.

### 3) Timeline / Daily Notes
- Location: `daily/YYYY/YYYY-MM-DD.md`
- Source: only major events worth remembering; not everything.

## Review Workflow (2-stage)

**Stage A — Candidate generation (no edits to core notes):**
- Create candidate lists per type/tag (e.g., preferences, decisions).
- Files live in `knowledge/resources/` as review artifacts.

**Stage B — Promotion:**
- After approval, move selected candidates into:
  - `tacit/preferences.md`
  - project `items.json`
  - a small number of daily notes

## Next immediate step

- Review: `knowledge/resources/ai-history-preference-candidates.md`
- Decide promotion rules (what counts as a lasting preference vs noise).
