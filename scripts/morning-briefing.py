#!/usr/bin/env python3
"""
Morning briefing v3.0 — matches standup-process.md Phase 6 spec exactly.

Format:
1. 🎯 Focus — the ONE thing for today
2. 🚧 Blocked — max 3 items needing Guillermo's input
3. 👀 Ready for review — max 3 items
4. 📅 Today — condensed calendar (skip noise)
5. 🔜 Heads up — notable upcoming only
6. 🌤 Weather — single line
7. 🔧 OpenClaw — update status (only if update available)

Run: python3 /data/workspace/scripts/morning-briefing.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

HKT = timezone(timedelta(hours=8))
MC_API = "https://resilient-chinchilla-241.convex.site"
MC_KEY = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
SA_FILE = "/data/workspace/credentials/google-service-account.json"
CALENDARS = [
    ("guillermo.ginesta@gmail.com", "Personal"),
    ("guillermo.ginesta@brinc.io", "Brinc"),
    ("vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com", "Family"),
]
NOISE = ["busy", "focus time", "deep work", "block", "mayleen", "mie", "helper",
         "domestic", "school drop", "drop-off", "pickup", "pick-up",
         "desk work", "admin", "lunch break"]
NOTABLE_KW = ["birthday", "anniversary", "flight", "travel", "trip",
              "dinner", "lunch with", "drinks", "doctor", "dentist", "appointment"]

AGENT_EMOJI = {"molty": "🦎", "raphael": "🔴", "leonardo": "🔵", "april": "🌸", "guillermo": "👤"}

GWS_BIN = "gws"


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def get_weather():
    try:
        out = run(["curl", "-s", "wttr.in/Hong+Kong?format=%c+%t"], timeout=10)
        return out if out and "Unknown" not in out else None
    except Exception:
        return None


def get_calendar_events(day_offset=0, days=1):
    """Get calendar events for a date range. Returns list of (sort_key, time_str, summary)."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds = service_account.Credentials.from_service_account_file(
            SA_FILE, scopes=["https://www.googleapis.com/auth/calendar.readonly"])
        service = build("calendar", "v3", credentials=creds)

        base = datetime.now(HKT).replace(hour=0, minute=0, second=0, microsecond=0)
        start = base + timedelta(days=day_offset)
        end = start + timedelta(days=days)

        events = []
        for cal_id, label in CALENDARS:
            try:
                result = service.events().list(
                    calendarId=cal_id,
                    timeMin=start.astimezone(timezone.utc).isoformat(),
                    timeMax=end.astimezone(timezone.utc).isoformat(),
                    singleEvents=True, orderBy="startTime"
                ).execute()
                for e in result.get("items", []):
                    summary = e.get("summary", "No title")
                    if any(n in summary.lower() for n in NOISE):
                        continue
                    start_raw = e.get("start", {}).get("dateTime", e.get("start", {}).get("date", ""))
                    if "T" in start_raw:
                        dt = datetime.fromisoformat(start_raw)
                        time_str = dt.astimezone(HKT).strftime("%H:%M")
                        sort_key = start_raw
                    else:
                        time_str = "all-day"
                        sort_key = start_raw + "T00:00"
                    events.append((sort_key, time_str, summary, label))
            except Exception:
                pass

        events.sort(key=lambda x: x[0])
        # Dedupe by summary
        seen = set()
        unique = []
        for sk, ts, summ, lbl in events:
            if summ not in seen:
                seen.add(summ)
                unique.append((sk, ts, summ, lbl))
        return unique
    except Exception:
        return []


def get_mc_tasks(status):
    try:
        out = run(["curl", "-s", "-H", f"Authorization: Bearer {MC_KEY}",
                    f"{MC_API}/api/tasks?status={status}"])
        return json.loads(out) if out else []
    except Exception:
        return []


def get_focus():
    """Try to read yesterday's Tomorrow's Focus from standup state."""
    state_file = "/data/workspace/logs/standup-state.json"
    try:
        if not os.path.exists(state_file):
            return None
        with open(state_file) as f:
            state = json.load(f)
        focus = state.get("tomorrows_focus") or state.get("focus")
        if focus and len(focus.strip()) > 3:
            return focus.strip()
    except Exception:
        pass
    return None


def get_overnight_summary():
    """Read overnight squad logs."""
    now = datetime.now(HKT)
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    lines = []

    agents = [
        ("🔴", "Raphael", "raphael"),
        ("🔵", "Leonardo", "leonardo"),
        ("🦎", "Molty", "molty"),
    ]
    for emoji, label, name in agents:
        for d in [today, yesterday]:
            path = f"/data/shared/logs/overnight-{name}-{d}.md"
            if os.path.exists(path):
                summary = _parse_agent_log(path)
                if summary:
                    lines.append(f"{emoji} {label}: {summary}")
                break
    return lines if lines else None


def _parse_agent_log(path):
    try:
        with open(path) as f:
            content = f.read()
        completed, review, failed, blocked = 0, 0, 0, 0
        section = None
        for line in content.split("\n"):
            line = line.strip()
            if "## ✅" in line or "Completed" in line and line.startswith("##"):
                section = "done"
            elif "## 👀" in line or "Under Review" in line and line.startswith("##"):
                section = "review"
            elif "## ❌" in line or "Failed" in line and line.startswith("##"):
                section = "failed"
            elif "## 🚧" in line or "Blocked" in line and line.startswith("##"):
                section = "blocked"
            elif line.startswith("## "):
                section = None
            elif line.startswith("- ") and section:
                item = line[2:].strip().lower()
                if item in ("none", "(none)", ""):
                    continue
                if section == "done":
                    completed += 1
                elif section == "review":
                    review += 1
                elif section == "failed":
                    failed += 1
                elif section == "blocked":
                    blocked += 1
        parts = []
        if completed:
            parts.append(f"✅{completed}")
        if review:
            parts.append(f"👀{review}")
        if failed:
            parts.append(f"❌{failed}")
        if blocked:
            parts.append(f"🚧{blocked}")
        return " ".join(parts) if parts else None
    except Exception:
        return None


def get_email_highlights():
    """Check ggv.molt inbox for important unread emails using gws CLI.
    
    Returns (ok: bool, items: list[str]).
    ok=False means email access is broken — surface that clearly.
    """
    try:
        # Pre-flight: can we reach gmail at all?
        triage = run([GWS_BIN, "gmail", "+triage", "--max", "10"], timeout=20)
        if not triage or "error" in triage.lower():
            return False, ["⚠️ Email access broken — gws triage failed"]

        # Parse triage output (table format: date | from | id | subject)
        lines = triage.strip().split("\n")
        # Find data lines (skip header + separator)
        data_lines = []
        past_header = False
        for line in lines:
            if line.startswith("──"):
                past_header = True
                continue
            if past_header and line.strip():
                data_lines.append(line)

        if not data_lines:
            return True, []  # No unread emails — that's fine

        # For each email, extract sender + subject from the table
        highlights = []
        for row in data_lines[:5]:
            # Split by multiple spaces (table columns)
            parts = [p.strip() for p in row.split("  ") if p.strip()]
            if len(parts) >= 4:
                sender = parts[1]
                subject = parts[3]
                # Clean sender name
                if "<" in sender:
                    sender = sender.split("<")[0].strip().strip('"')
                # Flag emails from Guillermo
                prefix = "⭐" if "guillermo" in sender.lower() else "📧"
                highlights.append(f"{prefix} {sender}: {subject}")
            elif len(parts) >= 2:
                highlights.append(f"📧 {parts[-1]}")

        # Dedupe by subject
        seen_subjects = set()
        deduped = []
        for h in highlights:
            # Extract subject part after ": "
            subj = h.split(": ", 1)[-1].lower().strip() if ": " in h else h.lower()
            if subj not in seen_subjects:
                seen_subjects.add(subj)
                deduped.append(h)
        return True, deduped[:5]

    except Exception as e:
        return False, [f"⚠️ Email check failed: {e}"]


def blocker_summary(task):
    """Make a human-readable blocker description."""
    title = task.get("title", "?")
    assignees = task.get("assignees", [])
    agent = assignees[0].title() if assignees else ""
    emoji = AGENT_EMOJI.get(assignees[0] if assignees else "", "")
    # Try to extract what's actually needed
    desc = task.get("description", "")
    if "waiting" in title.lower() or "need" in title.lower() or "blocked" in desc.lower():
        return f"{emoji} {agent}: {title}"
    return f"{emoji} {agent}: {title}"


def review_summary(task):
    """Make a human-readable review item."""
    title = task.get("title", "?")
    assignees = task.get("assignees", [])
    emoji = AGENT_EMOJI.get(assignees[0] if assignees else "", "")
    return f"{emoji} {title}"


def main():
    now = datetime.now(HKT)
    date_str = now.strftime("%a %d %b")
    lines = []

    # --- 1. 🎯 Focus ---
    focus = get_focus()
    if focus:
        lines.append(f"🎯 **{focus}**")
        lines.append("")

    # --- 2. 🚧 Blocked ---
    blocked = get_mc_tasks("blocked")
    if blocked:
        lines.append("🚧 **Blocked** (needs your input)")
        for t in blocked[:3]:
            lines.append(f"  → {blocker_summary(t)}")
        lines.append("")

    # --- 3. 👀 Review ---
    review = get_mc_tasks("review")
    if not review:
        review = get_mc_tasks("under_review")
    if review:
        lines.append("👀 **Ready for review**")
        for t in review[:3]:
            lines.append(f"  → {review_summary(t)}")
        lines.append("")

    # --- 4. 📅 Today ---
    events = get_calendar_events(day_offset=0, days=1)
    lines.append(f"📅 **Today** — {date_str}")
    if events:
        for _, time_str, summary, _ in events[:6]:
            lines.append(f"  {time_str}  {summary}")
    else:
        lines.append("  Clear day")
    lines.append("")

    # --- 5. 🔜 Heads up ---
    upcoming = get_calendar_events(day_offset=1, days=4)
    notable = []
    for _, ts, summ, _ in upcoming:
        if any(kw in summ.lower() for kw in NOTABLE_KW):
            notable.append(summ)
            if len(notable) >= 2:
                break
    if notable:
        lines.append("🔜 " + " · ".join(notable))
        lines.append("")

    # --- 6. 🌤 Weather ---
    weather = get_weather()
    if weather:
        lines.append(f"🌤 HK: {weather}")
        lines.append("")

    # --- 7. 📬 Email ---
    email_ok, email_items = get_email_highlights()
    if not email_ok:
        # Email is broken — say so clearly
        lines.append("📬 " + email_items[0] if email_items else "📬 ⚠️ Email check failed")
        lines.append("")
    elif email_items:
        lines.append("📬 **Email** (unread)")
        for item in email_items[:3]:
            lines.append(f"  → {item}")
        if len(email_items) > 3:
            lines.append(f"  + {len(email_items) - 3} more")
        lines.append("")

    # --- 8. 🔧 OpenClaw ---
    try:
        out = run(["openclaw", "update", "status"])
        if "Update available" in out or "npm update" in out:
            import re
            m = re.search(r"(\d+\.\d+\.\d+)", out)
            ver = m.group(1) if m else "?"
            lines.append(f"🔧 OpenClaw v{ver} available — reply /update to install")
    except Exception:
        pass

    # --- Overnight squad (compact) ---
    overnight = get_overnight_summary()
    if overnight:
        lines.append("🌙 " + " | ".join(overnight))

    print("\n".join(lines).strip())


if __name__ == "__main__":
    main()
