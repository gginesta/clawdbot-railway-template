# PLAN-003: Persistent Standup Database
**Created:** 2026-02-24 | **Status:** ✅ COMPLETE (2026-02-26)
**Approved approach:** Option B — single persistent Notion database, reused daily

---

## Problem

`daily_standup.py` creates a new Notion database every day via API. Notion doesn't guarantee column order in new databases, so "Your Notes" ends up in the wrong position. Guillermo has to manually move it every day.

---

## Solution

Replace the two per-day databases with ONE persistent database that:
- Has all columns defined once (column order set correctly on first creation, never changes)
- Adds a "Standup Date" date property to every row
- Each daily run adds tasks as new rows filtered to today's date
- Daily Notion page still created as a navigation anchor, with a filtered linked view

---

## Schema Changes

**New persistent database:** "📋 TMNT Standup Board"

New/changed properties vs current:
| Property | Type | Notes |
|---|---|---|
| Task | title | Same |
| **Your Notes** | rich_text | Always 2nd — set via internal API on creation |
| Action | select | Same options |
| Due Date | date | Same |
| Molty's Notes | rich_text | Same |
| Owner | select | Same |
| Priority | select | Same |
| Section | select | Overdue / Today / Upcoming / Inbox / Backlog |
| Time Est. | select | Same |
| Project | select | Same |
| **Standup Date** | date | NEW — which day this task appeared |
| **Type** | select | NEW — "Needs Input" or "Active Pipeline" (replaces having 2 DBs) |

---

## Code Changes to `daily_standup.py`

### 1. New config file: `/data/workspace/credentials/notion-standup-db.json`
```json
{
  "persistent_db_id": "<id after first creation>"
}
```

### 2. `get_or_create_persistent_db()` function
- Check if config file exists and DB ID is valid
- If yes: return existing DB ID
- If no: create the database once, save ID to config, set column order via internal API

### 3. Update `add_task_to_db()`
- Add `Standup Date` property = today
- Add `Type` property = "Needs Input" or "Active Pipeline"
- Remove the two-DB logic (single DB now)

### 4. Update `create_db()` calls
- Replace both `create_db()` calls with single `get_or_create_persistent_db()`

### 5. Update page creation
- Still create a daily Notion page as anchor with today's title
- Embed description linking to the filtered DB view (can't embed via API but can add a URL block)
- Add paragraph block with link: `View today's tasks in Standup Board → [url]?filter=...`

### 6. Column order via Notion internal API
After creating the persistent DB (once only):
- Use `token_v2` cookie to call `/api/v3/saveTransactions`
- Set column order: Task → Your Notes → Action → Due Date → Molty's Notes → Owner → Priority → Section → Time Est. → Project → Standup Date → Type
- OR: manually reorder once and it persists forever

**token_v2 needed — Guillermo to provide, or fetch via browser automation if Notion session available**

---

## Migration Plan

1. Script creates the persistent DB on first run
2. Stores DB ID in config
3. All subsequent runs add to same DB
4. Old daily DBs remain accessible (not deleted, just no longer created)
5. Future: Notion page for each day links to a filtered view of the persistent DB

---

## Sequence

1. [x] Plan documented
2. [x] Overnight one-shot cron created: b4bd2c2a, fires 2026-02-25T17:00Z (01:00 HKT)
3. [x] Todoist task: 6g4pFvM9V9gm39pR | MC task: jn76q9csr7mzynfz35xetdaxjn81s77w
4. [x] Persistent DB created 2026-02-26 01:03 HKT — ID: 31239dd6-9afd-81ad-8ffd-d1db09b1dd36
5. [x] Column order fixed via internal API (token_v2) — 13 columns set correctly
6. [x] DB verified: rows populating, Standup Date + Type properties working

---

## Risk

- **Low:** If persistent DB ID gets corrupted/deleted, script falls back to creating a new one
- **Medium:** token_v2 for column order — if not available, Guillermo manually sets column order once on the new persistent DB and it stays forever
- **Mitigation:** Build the fallback into `get_or_create_persistent_db()`
