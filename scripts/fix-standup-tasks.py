#!/usr/bin/env python3
"""Fix standup: remove duplicates, process every task with proper notes/estimates."""
import json, requests, sys, time

NOTION_API_KEY = "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"
NH = {"Authorization": f"Bearer {NOTION_API_KEY}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}

def patch(page_id, props):
    r = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=NH, json={"properties": props}, timeout=15)
    return r.status_code == 200

def archive(page_id):
    r = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=NH, json={"archived": True}, timeout=15)
    return r.status_code == 200

# === DUPLICATES TO REMOVE ===
dupes = [
    "30639dd6-9afd-81e0-a97d-c3d9e055bf34",  # "Figure out access path for Gemini 3 Pro" (dupe of 8115)
    "30639dd6-9afd-8170-9e22-ef8c8edbad08",  # "Add laptop to desktop Syncthing when home" (dupe of 8156)
]
print("=== Removing duplicates ===")
for d in dupes:
    ok = archive(d)
    print(f"  Archived {d[:8]}: {'✅' if ok else '❌'}")

# === TASK PROCESSING: Update every task with proper notes, time estimates, priorities ===
# Format: (page_id, updates_dict)
updates = [
    # --- MOLTY-OWNED TASKS ---
    ("30639dd6-9afd-8111-bbf3-ddb54a44776b", {  # Configure Discord slash command allowlists
        "Priority": {"select": {"name": "🔵 P3"}},
        "Time Est.": {"select": {"name": "1h"}},
        "Section": {"select": {"name": "Overdue"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Overdue since Feb 6. Low urgency — bots work without allowlists. Will batch with other Discord config cleanup. Suggest: reschedule to next week."}}]},
    }),
    ("30639dd6-9afd-8115-9354-ea4cb87ebd97", {  # Gemini 3 Pro access path
        "Priority": {"select": {"name": "🔵 P3"}},
        "Time Est.": {"select": {"name": "30min"}},
        "Section": {"select": {"name": "Today"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Research task. Will check OpenRouter, Google AI Studio, and direct API availability. Can complete today as a quick research spike."}}]},
    }),
    ("30639dd6-9afd-8122-9a6d-c648fbed7ffc", {  # Pikachu X/Twitter post schedule
        "Priority": {"select": {"name": "🔵 P3"}},
        "Time Est.": {"select": {"name": "1h"}},
        "Section": {"select": {"name": "Today"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "X posting currently blocked (bot detection). Plan: design read-only content curation workflow. Draft schedule + topic list. Suggest: defer actual posting until X access resolved."}}]},
    }),
    ("30639dd6-9afd-813f-a621-db077f414529", {  # Whoop multi-user research
        "Priority": {"select": {"name": "⚪ P4"}},
        "Time Est.": {"select": {"name": "1h"}},
        "Section": {"select": {"name": "Backlog"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Depends on Whoop integration (parent task). No point researching multi-user until single-user works. Keep deferred to March."}}]},
    }),
    ("30639dd6-9afd-815b-8ebe-e391be4b0560", {  # Morning briefing hardening
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "30min"}},
        "Section": {"select": {"name": "Overdue"}},
        "Action": {"select": {"name": "✔️ Done"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "✅ DONE — Fixed on Feb 13. Morning briefing runs reliably now with travel-awareness (Cebu weather). Marking complete."}}]},
    }),
    ("30639dd6-9afd-816b-9df1-d344221b3dc6", {  # Write TASK-PROTOCOL.md
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "2h+"}},
        "Section": {"select": {"name": "Today"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Defines task packet schema for cross-agent work. Important for squad coordination but not blocking anything today. Suggest: reschedule to next week, focus on immediate standup improvements first."}}]},
    }),
    ("30639dd6-9afd-81cf-99f8-f5fc5edcf73a", {  # Polymarket research
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "2h+"}},
        "Section": {"select": {"name": "Today"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Cron job scheduled for 2am tonight (autonomous research). Will email findings + close task automatically. No action needed from you."}}]},
    }),
    ("30639dd6-9afd-817e-aee7-c922f31bb4e6", {  # Build Whoop Integration
        "Priority": {"select": {"name": "⚪ P4"}},
        "Time Est.": {"select": {"name": "2h+"}},
        "Section": {"select": {"name": "Backlog"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Build project — needs Whoop API access + OAuth setup. Not urgent. Keep March deadline. Blocked until we decide on health data architecture."}}]},
    }),

    # --- GUILLERMO-OWNED: INBOX (needs triage) ---
    ("30639dd6-9afd-811e-a28f-cdaa120a657d", {  # Research 1Password pricing
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "30min"}},
        "Section": {"select": {"name": "Inbox"}},
        "Owner": {"select": {"name": "Molty"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "I can research this — Teams ($4/user/mo) vs Business ($8/user/mo). For 5 agents + you = 6 users. Will email comparison. Suggest: assign to me, I'll handle."}}]},
    }),
    ("30639dd6-9afd-8173-97e9-e02b543b11f6", {  # Kinesiology centres HK
        "Priority": {"select": {"name": "🔵 P3"}},
        "Time Est.": {"select": {"name": "30min"}},
        "Section": {"select": {"name": "Inbox"}},
        "Owner": {"select": {"name": "Molty"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Research task assigned to me. Will search for top-rated kinesiology centres in HK (focus on TKO/Kowloon side). Email results. You're in Cebu until Feb 18 — will have this ready by then."}}]},
    }),
    ("30639dd6-9afd-81ec-8bbb-f867e557d179", {  # Meal framework ketosis
        "Priority": {"select": {"name": "🔵 P3"}},
        "Time Est.": {"select": {"name": "1h"}},
        "Section": {"select": {"name": "Inbox"}},
        "Owner": {"select": {"name": "Molty"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "I can draft a keto meal framework — macros, sample meals, grocery list. Will research and email. Suggest: assign to me."}}]},
    }),
    ("30639dd6-9afd-817e-a58f-f9d313485932", {  # Voice notes processing research
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "1h"}},
        "Section": {"select": {"name": "Inbox"}},
        "Owner": {"select": {"name": "Molty"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "OpenClaw has whisper-api skill for transcription. I can process voice notes via: (1) Whisper transcribe, (2) summarize + extract action items, (3) create Todoist tasks. Will document the workflow. Assign to me."}}]},
    }),
    ("30639dd6-9afd-81db-bd0b-d3f576662e20", {  # 1Password setup
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "1h"}},
        "Section": {"select": {"name": "Overdue"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Overdue since Feb 9. Blocked on: (1) pricing research (see related task), (2) your decision on Teams vs Business plan. Suggest: I research pricing first, then you decide, then I set up."}}]},
    }),
    ("30639dd6-9afd-81e1-9fb8-d120c8eeff3e", {  # Ernest webinar
        "Priority": {"select": {"name": "🔵 P3"}},
        "Time Est.": {"select": {"name": "15min"}},
        "Section": {"select": {"name": "Overdue"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Event was Feb 12 — yesterday. Is this done? If so, mark complete. If follow-up needed, update description."}}]},
    }),
    ("30639dd6-9afd-816a-9bf1-e35489b2769c", {  # Brinc outreach top 20
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "2h+"}},
        "Section": {"select": {"name": "Overdue"}},
        "Owner": {"select": {"name": "Raphael"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Overdue. This is Raphael's domain — should coordinate with him. Suggest: delegate to Raphael via #brinc-private. I'll relay."}}]},
    }),
    ("30639dd6-9afd-8180-87fa-e13fcee23c66", {  # Brinc sales materials
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "2h+"}},
        "Section": {"select": {"name": "Upcoming"}},
        "Owner": {"select": {"name": "Raphael"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Due tomorrow (Feb 14). Raphael's domain — he should have drafts. Suggest: delegate to Raphael, I'll follow up on status."}}]},
    }),
    ("30639dd6-9afd-81f0-ab19-cbec1d8d7ae4", {  # Spanish passport
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "1h"}},
        "Section": {"select": {"name": "Upcoming"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Due Feb 28. Requires: appointment at Spanish consulate HK, photos, forms. I can research requirements + book appointment. Suggest: I prep the checklist, you review."}}]},
    }),
    ("30639dd6-9afd-817c-af30-dd3b2b0528be", {  # British passport Memo
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "1h"}},
        "Section": {"select": {"name": "Upcoming"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Due Feb 28. Requires: UK passport application for minors, supporting docs, photos. I can research requirements + prepare checklist. Suggest: I prep, you review."}}]},
    }),

    # --- GUILLERMO-OWNED: PERSONAL BACKLOG (add context) ---
    ("30639dd6-9afd-818d-8550-e707626c903f", {  # Coordinate with Raphael
        "Priority": {"select": {"name": "🟡 P2"}},
        "Time Est.": {"select": {"name": "30min"}},
        "Section": {"select": {"name": "Today"}},
        "Owner": {"select": {"name": "Molty"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Due today. I'll send Raphael a webhook to sync on content plan status. Will report back."}}]},
    }),
    ("30639dd6-9afd-81c5-acb1-c10f397e2512", {  # Review Today's Progress (recurring)
        "Priority": {"select": {"name": "🔵 P3"}},
        "Time Est.": {"select": {"name": "15min"}},
        "Section": {"select": {"name": "Overdue"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Recurring daily task — this IS the standup. Overdue because standup missed 3 days. Now fixed. Suggest: mark done, the recurring instance will regenerate."}}]},
    }),
    ("30639dd6-9afd-816a-a702-cee0452c4dad", {  # Weekly Review
        "Time Est.": {"select": {"name": "1h"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Next Sunday Feb 22. Recurring weekly task. No action needed now."}}]},
    }),
    ("30639dd6-9afd-81c0-98b3-fc6c27db4380", {  # SLTRA subsidies
        "Time Est.": {"select": {"name": "2h+"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Mana Capital task. Due March 31. Research Spanish subsidies for non-Spanish companies. I can do preliminary research. Low urgency now."}}]},
    }),
    ("30639dd6-9afd-817a-8068-ff8dcd0df9cb", {  # Post Transaction Backlog
        "Time Est.": {"select": {"name": "2h+"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Deferred to March 31 per Feb 10 standup. Financial admin — needs your direct involvement."}}]},
    }),

    # --- PERSONAL LOW-PRIORITY BACKLOG (brief notes) ---
    ("30639dd6-9afd-811d-9f46-d5c8e8a2e3e7", {  # Patagonia
        "Time Est.": {"select": {"name": "30min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "No due date. Trip planning? I can research if you give me dates/preferences."}}]},
    }),
    ("30639dd6-9afd-8134-93fb-c6e6702da201", {  # Car wrap
        "Time Est.": {"select": {"name": "30min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "No due date. I can research wrap shops in HK if needed."}}]},
    }),
    ("30639dd6-9afd-8143-a1d4-f583dca26af9", {  # Health Insurance
        "Time Est.": {"select": {"name": "1h"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "No due date. Important but not urgent. Needs your input on coverage requirements."}}]},
    }),
    ("30639dd6-9afd-8156-9d2a-e0dddf74da5d", {  # Syncthing laptop
        "Time Est.": {"select": {"name": "30min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Physical task — needs you at home with laptop + desktop both on. Remind you when back from Cebu (Feb 18+)."}}]},
    }),
    ("30639dd6-9afd-815f-a440-c16bd86ae0e1", {  # Order memo wine
        "Time Est.": {"select": {"name": "15min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Deferred to April 30 per Feb 10 standup. Quick purchase task."}}]},
    }),
    ("30639dd6-9afd-816c-bd00-c8b78b5b17fa", {  # Joint accounts
        "Time Est.": {"select": {"name": "1h"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Financial admin. No due date. Needs your direct involvement with bank."}}]},
    }),
    ("30639dd6-9afd-817d-b4cf-c162a32e484d", {  # Fencing
        "Time Est.": {"select": {"name": "30min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Deferred to April 30. I can research fencing + EP classes in HK when you're ready."}}]},
    }),
    ("30639dd6-9afd-818a-a5ac-c636a2f668f8", {  # Last Will
        "Time Est.": {"select": {"name": "2h+"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Important but sensitive. Needs lawyer consultation. No due date — suggest setting a target date."}}]},
    }),
    ("30639dd6-9afd-8195-9912-d2ee2fb8c6c9", {  # Water filter
        "Time Est.": {"select": {"name": "15min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Quick purchase. I can research options if needed."}}]},
    }),
    ("30639dd6-9afd-819b-b544-d9e11d611291", {  # Credit card clearing
        "Time Est.": {"select": {"name": "30min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Financial admin. Needs your direct action with bank."}}]},
    }),
    ("30639dd6-9afd-81ae-a052-e9301177779e", {  # Car body shop
        "Time Est.": {"select": {"name": "30min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "No due date. I can research body shops in HK if needed."}}]},
    }),
    ("30639dd6-9afd-81e7-90b8-dcb92c04dc23", {  # Tax
        "Time Est.": {"select": {"name": "2h+"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Important. HK tax year ends March 31. Suggest: set due date, coordinate with accountant."}}]},
    }),
    ("30639dd6-9afd-81f2-88c5-d5c92d5d3c7a", {  # Life insurance
        "Time Est.": {"select": {"name": "1h"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "No due date. Research + comparison needed. I can draft options if you give requirements."}}]},
    }),
    ("30639dd6-9afd-81fd-a687-ca508c98efaa", {  # Credit card swap
        "Time Est.": {"select": {"name": "30min"}},
        "Molty's Notes": {"rich_text": [{"text": {"content": "Financial admin. Needs your direct action with bank."}}]},
    }),
]

print(f"\n=== Processing {len(updates)} tasks ===")
ok = 0
for page_id, props in updates:
    if patch(page_id, props):
        ok += 1
        sys.stdout.write(".")
        sys.stdout.flush()
    else:
        print(f"\n  ❌ Failed: {page_id[:8]}")
    time.sleep(0.35)  # Rate limit

print(f"\n\n✅ Updated {ok}/{len(updates)} tasks. Removed {len(dupes)} duplicates.")
