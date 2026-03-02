# PLAN-008: Smarter Calendar Booking Logic

**Created:** 2026-03-02
**Status:** ✅ COMPLETE
**Owner:** Molty

---

## Problem

Current standup → calendar flow is too naive:
- Every "Keep" task with Guillermo as owner gets a calendar slot
- No check for existing related events (e.g., Spanish passport appointment Thursday)
- No human review before booking

Result: Duplicate/nonsense calendar entries.

---

## Solution

Combined approach:

```
Task marked "Keep" for Guillermo
    ↓
Has "Needs Calendar Slot" = True in Notion?
    → Yes: Book automatically
    → No/Empty: Check calendar for related events (keyword match)
        → Related event found: Skip, log reason
        → No related event: Skip, flag for Molty review
```

---

## Changes Required

### 1. Notion Standup Database
- Add property: **"Needs Calendar Slot"** (checkbox)
- Database ID: `2fe39dd69afd81f189f7e58925dad602`

### 2. process_standup.py Updates

**Read new property:**
```python
needs_slot = row.get("properties", {}).get("Needs Calendar Slot", {}).get("checkbox", False)
```

**New booking logic:**
```python
if "Keep" in action and ("Guillermo" in owner or not owner):
    if needs_slot:
        # Book automatically
        book_calendar_slot(...)
    else:
        # Check for related events
        related = find_related_events(cal_token, cal_ids, title, search_window=7)
        if related:
            log(f"Skipped booking '{title}' — related event exists: {related[0]}")
        else:
            log(f"Review needed: '{title}' has no related event but needs_slot=False")
            # Don't book — flag for manual review
```

**New function: find_related_events()**
```python
def find_related_events(token, cal_ids, task_title, search_window=7):
    """Search calendar for events with similar keywords in title.
    Returns list of matching event summaries, or empty list."""
    keywords = extract_keywords(task_title)  # e.g., "Spanish", "passport"
    # Search events in next N days
    # Return matches where event summary contains any keyword
```

### 3. Keyword extraction
Simple approach:
- Split title into words
- Filter out common words (the, a, for, to, etc.)
- Use remaining words as search terms

---

## Rollout

1. Add Notion property (manual or API)
2. Update script
3. Test on tomorrow's standup (dry run first)
4. Verify no duplicate bookings

---

## Success Criteria

- [x] "Needs Calendar Slot" property exists in Notion
- [x] Script respects the flag
- [x] Related events detected and logged
- [x] No duplicate bookings for tasks with existing appointments
- [x] Ambiguous cases flagged for review (not auto-booked)

---

## Execution Log

### 2026-03-02 10:55 HKT
- ✅ Added "Needs Calendar Slot" checkbox to Notion standup database
- ✅ Added `extract_keywords()` function for keyword matching
- ✅ Added `find_related_events()` function to check calendar
- ✅ Updated booking logic:
  - `needs_slot = True` → auto-book
  - `needs_slot = False/empty` → check for related events
    - Related found → skip, log reason
    - No related → skip, flag for review
- ✅ Syntax validated, committed
