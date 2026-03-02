# Cerebro Feature Spec — CRM Reminders & Touch-Base System
**Author:** Molty 🦎  
**Date:** 2026-03-03  
**Status:** Draft — For Leonardo/Codex to implement  
**Source task:** Todoist [6g5FH7H9wgmjmr3x]  
**Priority:** P2 — Next feature sprint after M0.3 analytics  

---

## 1. Problem Statement

Guillermo's value as a networker comes from staying in touch with the right people at the right time. Cerebro already holds his contacts — but it's passive. Right now, there's no mechanism to:
- Know when he last interacted with someone
- Get nudged to reconnect with a contact he's been ignoring
- Mark a contact as "VIP" or "keep warm"
- Set manual reminders per contact

This spec defines the **Touch-Base Reminder System** — a lightweight CRM layer that makes Cerebro proactive.

---

## 2. Feature Overview

### 2.1 Core Concepts

**Last Contacted Date** — When was this contact last interacted with?  
**Relationship Tier** — How important is this contact? (VIP / Active / Warm / Cold)  
**Touch Frequency** — How often should Guillermo check in? (weekly / monthly / quarterly / never)  
**Reminder** — A scheduled nudge to reconnect  

### 2.2 User Stories

1. As Guillermo, I want to see which top contacts I haven't spoken to in 30+ days, so I can proactively reach out.
2. As Guillermo, I want to mark a contact as "VIP" and set a monthly reminder to touch base.
3. As Guillermo, I want to log "I just met/called/emailed this person" with a single tap to reset their timer.
4. As Guillermo, I want a weekly digest (Friday) showing which contacts need attention.
5. As Guillermo, I want the chatbot to answer "Who should I reconnect with this week?"

---

## 3. Database Changes

### 3.1 New fields on `contacts` table

```sql
-- Add to existing contacts table
ALTER TABLE contacts ADD COLUMN relationship_tier VARCHAR(20) DEFAULT 'warm'
  CHECK (relationship_tier IN ('vip', 'active', 'warm', 'cold', 'dormant'));

ALTER TABLE contacts ADD COLUMN touch_frequency_days INTEGER DEFAULT NULL;
-- NULL = no reminder set. 7=weekly, 30=monthly, 90=quarterly

ALTER TABLE contacts ADD COLUMN last_contacted_at TIMESTAMP DEFAULT NULL;
-- Manually set by user OR auto-detected from interaction log

ALTER TABLE contacts ADD COLUMN next_reminder_at TIMESTAMP DEFAULT NULL;
-- Computed: last_contacted_at + touch_frequency_days
```

### 3.2 New `interactions` table

```sql
CREATE TABLE interactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  interaction_type VARCHAR(20) NOT NULL 
    CHECK (interaction_type IN ('call', 'email', 'meeting', 'message', 'note', 'other')),
  notes TEXT,
  interacted_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_interactions_contact ON interactions(contact_id);
CREATE INDEX idx_interactions_user_date ON interactions(user_id, interacted_at DESC);
```

---

## 4. API Endpoints

### 4.1 Log an interaction
```
POST /api/contacts/:id/interactions
Body: { type: 'call'|'email'|'meeting'|'message'|'note'|'other', notes?: string, interacted_at?: ISO8601 }
Effect: Creates interaction record. Updates contact.last_contacted_at. Recalculates contact.next_reminder_at.
Auth: Required (JWT)
```

### 4.2 Set relationship tier + reminder frequency
```
PATCH /api/contacts/:id/relationship
Body: { tier?: 'vip'|'active'|'warm'|'cold'|'dormant', touch_frequency_days?: number|null }
Effect: Updates tier and frequency. Recalculates next_reminder_at.
Auth: Required (JWT)
```

### 4.3 Get contacts due for touch-base
```
GET /api/contacts/reminders?limit=10&overdue_only=true
Response: Array of contacts sorted by overdue days (most overdue first)
  Each contact includes: id, name, company, tier, last_contacted_at, next_reminder_at, days_overdue
Auth: Required (JWT)
```

### 4.4 Get interaction history for a contact
```
GET /api/contacts/:id/interactions?limit=10
Response: Array of interactions, newest first
Auth: Required (JWT)
```

---

## 5. UI Changes

### 5.1 Contact Profile Screen (new elements)
- **Relationship Tier badge** — VIP 🌟 / Active 🟢 / Warm 🟡 / Cold 🔵 / Dormant ⚫
- **Last contacted** — "3 weeks ago" (human-readable)
- **Touch frequency** — "Monthly reminder" (editable dropdown)
- **Next reminder** — "Due in 5 days" or "⚠️ Overdue by 12 days" (red if overdue)
- **Log Interaction button** — Quick-tap: 📞 Call / 📧 Email / 🤝 Met / 💬 Message
- **Interaction history** — Collapsible list of past interactions with notes

### 5.2 Home Screen / Contact List
- **Filter option:** "Due for touch-base" — shows only contacts with overdue reminders
- **Sort option:** "Most overdue" — sorts by days_overdue DESC
- **Overdue badge** on contact card: small red dot or "⚠️ 12d overdue" label

### 5.3 New "Reminders" Tab (Home Screen nav)
Simple list view:
- **"This week"** — Contacts due in next 7 days
- **"Overdue"** — Contacts past their reminder date
- Each row: Name, company, tier badge, days overdue, [Log Interaction] button
- Empty state: "You're all caught up! 🎉"

### 5.4 Chatbot Integration
Teach the chatbot to handle:
- "Who should I touch base with this week?" → query reminders API, return list
- "I just met [name]" → log interaction automatically
- "Remind me to call [name] every month" → set touch_frequency_days=30
- "Who are my VIP contacts?" → filter by tier=vip

---

## 6. Weekly Digest (Friday)

**Trigger:** Cron job, Friday 09:00 HKT  
**Delivery:** Push notification (mobile) + optional Telegram  
**Content:**
```
📬 Your Weekly Network Check-In

🔴 Overdue (3 contacts)
• Sarah Chen — 45 days since last contact [VIP]
• David Park — 32 days [Active]  
• Marcus Lee — 28 days [Active]

🟡 Due this week (2 contacts)
• Priya Sharma — due tomorrow [VIP]
• Tom Nguyen — due in 3 days [Warm]

✅ Recently connected (this week): 4 contacts
```

---

## 7. Implementation Plan

### Phase 1 — Backend (Est. 3-4h for Codex)
1. DB migration: add columns to `contacts`, create `interactions` table
2. `POST /api/contacts/:id/interactions` endpoint
3. `PATCH /api/contacts/:id/relationship` endpoint
4. `GET /api/contacts/reminders` endpoint
5. `GET /api/contacts/:id/interactions` endpoint
6. Service: `recalculate_reminder(contact_id)` — updates `next_reminder_at`
7. Background job: daily cron to recompute overdue contacts

### Phase 2 — Contact Profile UI (Est. 2-3h for Codex)
1. Tier badge + touch frequency selector
2. Last contacted display
3. Log Interaction quick-action buttons
4. Interaction history section

### Phase 3 — Home Screen + Reminders Tab (Est. 2h for Codex)
1. "Due for touch-base" filter on contact list
2. New Reminders tab with overdue/upcoming sections
3. Chatbot intent handlers

### Phase 4 — Weekly Digest (Est. 1h for Codex)
1. Cron job + digest template
2. Push notification + Telegram delivery

**Total estimate:** ~10h Codex/Leonardo work. Can be broken into 4 GitHub issues.

---

## 8. GitHub Issues to Create

1. `feat: DB migration — relationship fields + interactions table` (P2, Leonardo/Codex)
2. `feat: Touch-base API endpoints (log, set, query)` (P2, Leonardo/Codex)
3. `feat: Contact profile UI — tier badge, log interaction, history` (P2, Leonardo/Codex)
4. `feat: Reminders tab + home screen filter` (P2, Leonardo/Codex)
5. `feat: Weekly network digest (Friday cron)` (P3, Leonardo/Codex)

---

## 9. Out of Scope (for now)

- Auto-detection from Gmail/Calendar (needs OAuth scope expansion)
- LinkedIn message tracking
- Shared reminders with team
- SMS-based nudges
- AI scoring of "relationship strength"

These are good P3 features for v2 once the core is proven.

---

## 10. Open Questions for Guillermo

1. **Default tier for existing contacts?** Suggest: `warm` for all. He can manually promote to `vip`.
2. **Default touch frequency for VIP?** Suggest: 30 days (monthly).
3. **Digest delivery:** Telegram + push, or push only?
4. **Should the AI enrichment engine populate `last_contacted_at`** from LinkedIn activity? (Requires LinkedIn OAuth.)

---

*Spec written by Molty overnight 2026-03-03. Ready for Leonardo to pick up.*
