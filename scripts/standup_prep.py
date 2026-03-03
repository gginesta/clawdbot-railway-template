#!/data/workspace/.venv/bin/python3
"""
standup_prep.py — Pre-standup intelligence gathering (runs at 4:30 PM HKT)

Runs silently before the 5PM standup cron. Does the heavy lifting so that
when the standup page is generated, it already reflects the day's reality.

Steps:
  1. Fetch new Todoist tasks since last standup → triage each one
  2. Webhook Raphael + Leonardo: "what did you complete today?" → wait 10 min
  3. Cross-sync MC completions → Todoist (close tasks done by agents)
  4. Scan ggv.molt inbox for relevant items
  5. Write prep state file → daily_standup.py consumes it at 5PM

Output: /data/workspace/logs/standup-prep-YYYY-MM-DD.json
"""

import json, os, re, sys, time, difflib, urllib.request, urllib.parse, subprocess
from datetime import datetime, timedelta, timezone

HKT = timezone(timedelta(hours=8))
NOW = datetime.now(HKT)
TODAY = NOW.strftime("%Y-%m-%d")

# ── Credentials ──────────────────────────────────────────────────────────────
NOTION_KEY    = "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"
TODOIST_TOKEN = "9a26743814658c9e82d92aa716b46a9b0a2257c4"
MC_TOKEN      = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
MC_API        = "https://resilient-chinchilla-241.convex.site"
TG_BOT_TOKEN  = "8292515315:AAETOvDJgl4r13qF3_32qhpn8h7jIOVJQDA"
TG_CHAT_ID    = "1097408992"
GOG_BIN       = "/usr/local/bin/gog"
GOG_ACCOUNT   = "ggv.molt@gmail.com"
GOG_KEYRING   = "molty2026"

NH = {"Authorization": f"Bearer {NOTION_KEY}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
TH = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
MH = {"Authorization": f"Bearer {MC_TOKEN}", "Content-Type": "application/json"}

# ── Todoist project IDs ───────────────────────────────────────────────────────
INBOX_ID    = "6M5rpCXmg7x7RC2Q"
BRINC_ID    = "6M5rpGgV6q865hrX"
CEREBRO_ID  = "6g53F7ccF8HHjgXM"
MANA_ID     = "6Rr9p6MxWHFwHXGC"
PERSONAL_ID = "6M5rpGfw5jR9Qg9R"
MOLTY_ID    = "6fwH32grqrCJF23R"

PROJECT_NAMES = {
    INBOX_ID: "Inbox",
    BRINC_ID: "Brinc",
    CEREBRO_ID: "Cerebro",
    MANA_ID: "Mana Capital",
    PERSONAL_ID: "Personal",
    MOLTY_ID: "Molty's Den",
}

# Webhook endpoints
WEBHOOKS = {
    "raphael":  ("https://ggv-raphael.up.railway.app/hooks/agent",
                 "ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd"),
    "leonardo": ("https://leonardo-production.up.railway.app/hooks/agent",
                 "08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758"),
}

STATE_FILE = "/data/workspace/logs/standup-state.json"
PREP_FILE  = f"/data/workspace/logs/standup-prep-{TODAY}.json"

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def http_get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def http_post(url, headers, body):
    data = json.dumps(body).encode()
    h = {**headers, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, method="POST", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print(f"  POST {url[:60]} failed: {e}")
        return {}

def http_patch(url, headers, body):
    data = json.dumps(body).encode()
    h = {**headers, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, method="PATCH", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print(f"  PATCH {url[:60]} failed: {e}")
        return {}

# ── Todoist helpers ───────────────────────────────────────────────────────────

def todoist_tasks():
    resp = http_get("https://api.todoist.com/api/v1/tasks?limit=200", TH)
    return resp.get("results", resp) if isinstance(resp, dict) else resp

def todoist_close(task_id):
    req = urllib.request.Request(
        f"https://api.todoist.com/api/v1/tasks/{task_id}/close",
        method="POST", headers=TH
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 204
    except Exception:
        return False

def todoist_update(task_id, body):
    data = json.dumps(body).encode()
    h = {**TH, "Content-Type": "application/json"}
    req = urllib.request.Request(
        f"https://api.todoist.com/api/v1/tasks/{task_id}",
        data=data, method="POST", headers=h
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
            return True
    except Exception:
        return False

# ── MC helpers ────────────────────────────────────────────────────────────────

def mc_tasks():
    try:
        resp = http_get(f"{MC_API}/api/tasks", MH)
        return resp if isinstance(resp, list) else []
    except Exception as e:
        print(f"  MC fetch failed: {e}")
        return []

# ── Task triage ───────────────────────────────────────────────────────────────

KEYWORD_OWNER = {
    "raphael": "Raphael", "brinc sales": "Raphael", "hubspot": "Raphael",
    "proposal": "Raphael", "outreach": "Raphael",
    "leonardo": "Leonardo", "cerebro": "Leonardo", "launchpad": "Leonardo",
    "tmnt": "Molty", "openclaw": "Molty", "molty": "Molty",
    "cron": "Molty", "agent": "Molty", "discord": "Molty",
}

PROJECT_OWNER_DEFAULT = {
    BRINC_ID: "Raphael", CEREBRO_ID: "Leonardo",
    MOLTY_ID: "Molty", MANA_ID: "Guillermo",
    PERSONAL_ID: "Guillermo", INBOX_ID: "Guillermo",
}

def determine_owner(task):
    content_lower = task.get("content", "").lower()
    pid = task.get("project_id", "")
    if pid == MOLTY_ID:
        return "Molty"
    for kw, owner in KEYWORD_OWNER.items():
        if kw in content_lower:
            return owner
    return PROJECT_OWNER_DEFAULT.get(pid, "Guillermo")

def determine_project(task):
    pid = task.get("project_id", "")
    if pid != INBOX_ID:
        return pid  # already assigned
    # Infer from content
    content_lower = task.get("content", "").lower()
    if any(w in content_lower for w in ["raphael", "brinc", "hubspot", "proposal", "client", "deal"]):
        return BRINC_ID
    if any(w in content_lower for w in ["cerebro", "leonardo", "launchpad", "stripe", "feature"]):
        return CEREBRO_ID
    if any(w in content_lower for w in ["mana", "portfolio", "investment"]):
        return MANA_ID
    if any(w in content_lower for w in ["tmnt", "openclaw", "agent", "molty", "cron", "fleet"]):
        return MOLTY_ID
    return PERSONAL_ID

def determine_priority(task):
    """Eisenhower: return Todoist priority int (4=P1,3=P2,2=P3,1=P4)."""
    existing = task.get("priority", 1)
    if existing > 1:
        return existing  # already set by Guillermo
    content_lower = task.get("content", "").lower()
    # Urgent + important → P1
    if any(w in content_lower for w in ["urgent", "asap", "critical", "p0", "blocking", "deadline today"]):
        return 4
    # Important, not urgent → P2
    if any(w in content_lower for w in ["proposal", "client", "revenue", "hire", "stripe", "launch", "beta"]):
        return 3
    # Delegate candidates → P3
    if any(w in content_lower for w in ["review", "check", "send", "email", "reply", "book", "schedule"]):
        return 2
    return 2  # default P3

def estimate_time(task):
    content = task.get("content", "").lower()
    if any(w in content for w in ["research", "build", "implement", "develop", "write", "design", "strategy"]):
        return "2h+"
    if any(w in content for w in ["review", "analyze", "investigate", "plan", "setup", "configure"]):
        return "1h"
    if any(w in content for w in ["call", "email", "send", "reply", "check", "fill", "complete", "book"]):
        return "30min"
    return "30min"

def is_processed(task):
    """Check if Molty has already processed this task (has 🦎 marker)."""
    return "🦎" in task.get("content", "")

def rewrite_title(raw_content):
    """Make title specific, actionable, add 🦎 marker at end. One-time only."""
    # Strip existing emoji prefix if any
    content = re.sub(r'^[\U00010000-\U0010ffff\u2600-\u27ff\s]+', '', raw_content).strip()
    if not content:
        content = raw_content
    # Add time estimate inline
    est = estimate_time({"content": content})
    # Don't add 🦎 if already there
    if "🦎" not in content:
        return f"{content} — {est} 🦎"
    return content

# ── Fuzzy match ───────────────────────────────────────────────────────────────

def fuzzy_match(title, candidates, threshold=0.55):
    """Find best fuzzy match for title in list of strings."""
    best, best_score = None, 0
    title_norm = title.lower().strip()
    for c in candidates:
        score = difflib.SequenceMatcher(None, title_norm, c.lower().strip()).ratio()
        if score > best_score:
            best_score, best = score, c
    return best if best_score >= threshold else None

# ── Webhook squad check ───────────────────────────────────────────────────────

def ping_squad_agents():
    """Webhook Raphael + Leonardo. Returns dict of agent → sent successfully."""
    today = NOW.strftime("%Y-%m-%d")
    msg = (
        f"🦎 Pre-standup check (4:30 PM HKT — {today})\n\n"
        "Quick status update needed before today's 5PM standup:\n"
        "1. What did you complete today that may not be updated in MC yet?\n"
        "2. Anything started but not finished?\n"
        "3. Any blockers Guillermo needs to know about tonight?\n\n"
        "IMPORTANT: Write your reply as a plain text file to:\n"
        f"/data/shared/logs/standup-status-{today}-{{AGENT_NAME}}.txt\n"
        "(replace {AGENT_NAME} with raphael or leonardo)\n\n"
        "Format:\n"
        "COMPLETED: [task 1, task 2, ...]\n"
        "IN_PROGRESS: [task 1, ...]\n"
        "BLOCKED: [task 1 — need from Guillermo: ...]\n\n"
        "Write the file first, then reply to this message. Going ahead at 5PM regardless."
    )
    results = {}
    for agent, (url, token) in WEBHOOKS.items():
        body = {"message": msg, "wakeMode": "now"}
        resp = http_post(url, {"Authorization": f"Bearer {token}"}, body)
        results[agent] = resp.get("ok", False)
        status = "✅ sent" if results[agent] else "⚠️ failed"
        print(f"  Webhook {agent}: {status}")
    return results

# ── MC → Todoist sync ─────────────────────────────────────────────────────────

def sync_mc_completions_to_todoist(tasks_list, mc_list):
    """For each MC task marked done today, close the matching Todoist task."""
    synced = []
    today_start_ms = int(NOW.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)

    done_today = [
        t for t in mc_list
        if t.get("status") == "done" and (t.get("updatedAt") or 0) >= today_start_ms
    ]
    todoist_titles = [t.get("content", "") for t in tasks_list]

    for mc_task in done_today:
        mc_title = mc_task.get("title", "")
        match = fuzzy_match(mc_title, todoist_titles)
        if match:
            # Find the Todoist task and close it
            for t in tasks_list:
                if t.get("content", "") == match:
                    ok = todoist_close(t["id"])
                    if ok:
                        synced.append(f"Closed in Todoist (MC done): {match[:50]}")
                        print(f"  ✅ Closed Todoist task (MC done): {match[:50]}")
                    break
    return synced

# ── Email scan ────────────────────────────────────────────────────────────────

def scan_email_inbox():
    """Scan ggv.molt inbox for items since last standup. Returns list of highlights."""
    highlights = []
    try:
        env = {**os.environ, "GOG_KEYRING_PASSWORD": GOG_KEYRING}
        q = "is:unread newer_than:24h"
        result = subprocess.run(
            [GOG_BIN, "gmail", "messages", "search", q, "--max", "20",
             "--json", "-a", GOG_ACCOUNT],
            capture_output=True, text=True, timeout=30, env=env
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            msgs = data.get("messages", [])
            action_keywords = ["action required", "urgent", "asap", "invoice",
                               "contract", "proposal", "signature", "please review",
                               "important", "meeting", "invite"]
            for msg in msgs[:20]:
                subject = msg.get("subject", "").lower()
                sender  = msg.get("from", "")
                if any(kw in subject for kw in action_keywords):
                    highlights.append({
                        "sender": sender.split("<")[0].strip().strip('"')[:40],
                        "subject": msg.get("subject", "")[:80],
                        "action": True,
                    })
            print(f"  Email: {len(msgs)} unread, {len(highlights)} highlights")
        else:
            print(f"  Email scan failed: {result.stderr[:100]}")
    except Exception as e:
        print(f"  Email scan error: {e}")
    return highlights

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n🦎 Standup prep — {TODAY} {NOW.strftime('%H:%M')} HKT\n")

    # Load last standup date from state file
    last_standup_date = None
    if os.path.exists(STATE_FILE):
        try:
            state = json.load(open(STATE_FILE))
            last_standup_date = state.get("date")
            print(f"Last standup: {last_standup_date}")
        except Exception:
            pass

    prep = {
        "prep_time": NOW.isoformat(),
        "date": TODAY,
        "new_tasks_processed": [],
        "mc_synced": [],
        "email_highlights": [],
        "squad_pinged": {},
        "summary": "",
    }

    # ── Step 1: Todoist — fetch + triage new tasks ─────────────────────────────
    print("\n1. Fetching Todoist tasks...")
    tasks = todoist_tasks()
    print(f"   {len(tasks)} active tasks")

    new_unprocessed = [t for t in tasks if not is_processed(t) and t.get("project_id") == INBOX_ID]
    print(f"   {len(new_unprocessed)} unprocessed inbox tasks")

    processed_count = 0
    for task in new_unprocessed:
        raw_content = task.get("content", "")
        print(f"   Processing: {raw_content[:60]}")

        new_content = rewrite_title(raw_content)
        new_project = determine_project(task)
        new_priority = determine_priority(task)
        owner = determine_owner({**task, "project_id": new_project})

        # Update in Todoist: title + project + priority
        updates = {
            "content": new_content,
            "priority": new_priority,
        }
        ok = todoist_update(task["id"], updates)

        # Move to correct project if not Inbox
        if new_project != INBOX_ID:
            move_url = f"https://api.todoist.com/api/v1/tasks/{task['id']}/move"
            http_post(move_url, TH, {"project_id": new_project})

        if ok:
            processed_count += 1
            prep["new_tasks_processed"].append({
                "original": raw_content[:60],
                "rewritten": new_content[:80],
                "project": PROJECT_NAMES.get(new_project, new_project),
                "owner": owner,
                "priority": new_priority,
                "time_est": estimate_time(task),
            })
            print(f"     → {new_content[:60]} [{PROJECT_NAMES.get(new_project, '?')}] [{owner}]")

    print(f"   Processed {processed_count} new tasks")

    # ── Step 2: Webhook squad agents ───────────────────────────────────────────
    print("\n2. Pinging squad agents...")
    squad_results = ping_squad_agents()
    prep["squad_pinged"] = squad_results
    print("   Waiting 10 minutes for responses...")
    time.sleep(600)  # 10 minutes
    print("   Proceeding regardless of responses")

    # Build squad status text from what we know (actual responses come via webhook back to Molty)
    squad_lines = []
    for agent, sent in squad_results.items():
        emoji = {"raphael": "🔴", "leonardo": "🔵"}.get(agent, "•")
        if sent:
            squad_lines.append(f"{emoji} {agent.capitalize()}: status check sent")
        else:
            squad_lines.append(f"{emoji} {agent.capitalize()}: ⚠️ webhook failed — no update received")
    prep["squad_status"] = "\n".join(squad_lines) if squad_lines else "No pre-standup check sent"

    # ── Step 3: MC → Todoist sync ──────────────────────────────────────────────
    print("\n3. Syncing MC completions to Todoist...")
    mc_list = mc_tasks()
    tasks_refreshed = todoist_tasks()  # refresh after triage changes
    synced = sync_mc_completions_to_todoist(tasks_refreshed, mc_list)
    prep["mc_synced"] = synced
    print(f"   Synced {len(synced)} completions")

    # ── Step 4: Email scan ─────────────────────────────────────────────────────
    print("\n4. Scanning ggv.molt inbox...")
    highlights = scan_email_inbox()
    prep["email_highlights"] = highlights

    # ── Step 5: Build summary text for standup page ────────────────────────────
    summary_parts = []
    if processed_count:
        summary_parts.append(f"📥 {processed_count} new task(s) processed and triaged")
    if synced:
        summary_parts.append(f"🔄 {len(synced)} MC completion(s) synced to Todoist")
    if highlights:
        summary_parts.append(f"📬 {len(highlights)} email(s) need your attention")

    prep["summary"] = " · ".join(summary_parts) if summary_parts else "All caught up — no new items to process"

    # ── Write prep state file ──────────────────────────────────────────────────
    os.makedirs(os.path.dirname(PREP_FILE), exist_ok=True)
    with open(PREP_FILE, "w") as f:
        json.dump(prep, f, indent=2)
    print(f"\n✅ Prep state written to {PREP_FILE}")
    print(f"   Summary: {prep['summary']}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
