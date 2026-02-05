# Morning Briefing System — Implementation Spec (Molty / OpenClaw)

**Owner:** Molty (OpenClaw agent)

**User:** Guillermo (Hong Kong, **HKT / UTC+8**)

**Delivery:** Telegram message **daily 07:30 HKT** (23:30 UTC)

**Goal:** A concise “morning newspaper” that is **scannable in ~30 seconds** on mobile.

---

## 0) Decisions (locked for v1)

### Telegram formatting
- Use **plain text + minimal icons** (no reliance on Telegram Markdown parse mode).
- One screen per section; hard limits per section (events/tasks/emails) to avoid walls of text.
- Use consistent time format: **`HH:MM` (HKT)**.

### Weekends vs weekdays
- **Weekday mode (Mon–Fri):** full briefing.
- **Weekend mode (Sat/Sun):** lighter:
  - keep: greeting/date, weather, calendar, email unread/highlights
  - tasks: only **P1** due/overdue + top 3 P2
  - upcoming week: keep but limit to 3 items

### “Nothing notable” handling
- Keep section headers, but compress empty sections to a **single line**:
  - `No events` / `No P1–P2 tasks due` / `No email highlights`

### Error handling
- **Never fail the whole briefing.** Each data source is isolated.
- If a source fails, show a compact warning line inside that section:
  - `⚠️ Calendar unavailable (token refresh failed)`

### Model selection (cron job)
- Use a **cheap model** because the briefing is mostly deterministic data assembly.
- Recommendation: `google/gemini-2.5-flash` (or any Flash-tier model configured in your Gateway).
- In v1, the model’s only job is to **run the script and post output verbatim**.

### “Today’s focus”
- Include **one line** at the end when there’s a clear candidate:
  - Prefer top **P1** due today, else earliest meeting.

---

## 1) Architecture

### High-level flow

1. **OpenClaw Cron (Gateway scheduler)** triggers an **isolated agent turn** at **07:30 HKT**.
2. The isolated run uses the **exec tool** to run a local script:
   - `/data/workspace/scripts/morning_briefing.py`
3. The script performs API calls:
   - Weather (prefer OpenClaw weather skill; v1 uses Open‑Meteo directly — no key)
   - Google Calendar API (3 calendars)
   - Todoist REST v2
   - Gmail API
4. The script outputs a **ready-to-send Telegram message**.
5. Cron delivers the run output via **delivery.mode=announce** to Telegram.

### Why this architecture
- **Reliable + cheap:** the script is deterministic; the LLM isn’t summarizing lots of content.
- **Tooling aligned:** Calendar/Gmail/Todoist are already configured via local credentials.
- **Good failure modes:** each upstream call can fail independently.

---

## 2) Briefing script (Python, with all API calls)

Save as:
- `scripts/morning_briefing.py`

Run:
- `python3 /data/workspace/scripts/morning_briefing.py`

Notes:
- Uses only Python stdlib (no pip installs).
- Uses token refresh for Google APIs.

```python
#!/usr/bin/env python3
"""morning_briefing.py

Generates Guillermo's daily morning briefing (HKT) as a Telegram-ready text message.

Data sources:
- Open-Meteo (weather; no API key)
- Google Calendar API (via OAuth refresh token)
- Todoist REST v2
- Gmail API (via OAuth refresh token)

Exit codes:
- 0 success
- 1 catastrophic failure (should be rare; script is designed to degrade gracefully)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, date, time
from zoneinfo import ZoneInfo

HKT = ZoneInfo("Asia/Hong_Kong")
UTC = ZoneInfo("UTC")

CALENDAR_CONFIG = "/data/workspace/credentials/calendar-config.json"
GMAIL_TOKENS = "/data/workspace/credentials/gmail-tokens.json"
CAL_TOKENS = "/data/workspace/credentials/calendar-tokens-brinc.json"
GOOGLE_OAUTH = "/data/workspace/credentials/google-oauth.json"
TODOIST_ENV = "/data/workspace/credentials/todoist.env"

# Hong Kong (Central) coordinates for weather
HK_LAT = 22.3193
HK_LON = 114.1694

MAX_CAL_TODAY = 10
MAX_TASKS_PER_PROJECT = 6
MAX_UPCOMING = 6
MAX_EMAIL_HIGHLIGHTS = 5

SCHOOL_DROP_OFF_DAYS = {"MO", "WE", "FR"}
SCHOOL_DROP_OFF_WINDOW = (time(8, 0), time(8, 30))


# -----------------------------
# Utilities
# -----------------------------

def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _load_env_file(path: str) -> dict:
    env = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env


def _http_json(url: str, *, method: str = "GET", headers: dict | None = None, data: dict | None = None, timeout: int = 30):
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        method=method,
        headers={"Accept": "application/json", **(headers or {}), **({"Content-Type": "application/json"} if body else {})},
        data=body,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {"error": str(e)}
        except Exception:
            payload = {"error": raw.decode("utf-8", errors="replace") or str(e)}
        return e.code, payload
    except Exception as e:
        return 0, {"error": str(e)}


def _rfc3339(dt: datetime) -> str:
    # Google APIs accept RFC3339 with Z.
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_rfc3339(s: str) -> datetime:
    # Handles trailing Z by converting to +00:00
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def _dow_token(d: date) -> str:
    # Python: Monday=0
    return ["MO", "TU", "WE", "TH", "FR", "SA", "SU"][d.weekday()]


def _fmt_hhmm(dt: datetime) -> str:
    return dt.astimezone(HKT).strftime("%H:%M")


def _fmt_day(d: date) -> str:
    # Telegram-friendly, locale-stable (no %-d portability issues)
    # Example: Thu 5 Feb
    return f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"


# -----------------------------
# Google OAuth refresh
# -----------------------------

def _google_refresh_token(*, refresh_token: str, client_id: str, client_secret: str) -> tuple[bool, dict]:
    url = "https://oauth2.googleapis.com/token"
    payload = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            return True, data
    except Exception as e:
        return False, {"error": str(e)}


def _google_authed_get(url: str, *, token_path: str, oauth_path: str, errors: list[str]) -> dict | None:
    tokens = _read_json(token_path)
    oauth = _read_json(oauth_path)
    installed = oauth.get("installed") or oauth.get("web") or {}
    client_id = installed.get("client_id")
    client_secret = installed.get("client_secret")

    def do_get(access_token: str):
        status, payload = _http_json(url, headers={"Authorization": f"Bearer {access_token}"})
        return status, payload

    status, payload = do_get(tokens.get("access_token", ""))

    if status == 401 and tokens.get("refresh_token") and client_id and client_secret:
        ok, refreshed = _google_refresh_token(
            refresh_token=tokens["refresh_token"],
            client_id=client_id,
            client_secret=client_secret,
        )
        if not ok or "access_token" not in refreshed:
            errors.append(f"Google token refresh failed for {os.path.basename(token_path)}")
            return None

        tokens["access_token"] = refreshed["access_token"]
        _write_json(token_path, tokens)

        status, payload = do_get(tokens["access_token"])

    if status and 200 <= status < 300:
        return payload

    errors.append(f"Google API error {status} for {url}: {payload.get('error', payload)}")
    return None


# -----------------------------
# Weather (Open-Meteo)
# -----------------------------

@dataclass
class WeatherSummary:
    tmin: float | None
    tmax: float | None
    rain_prob_max: int | None
    dropoff_rain_prob: int | None


def get_weather(today: date, *, school_day: bool, errors: list[str]) -> WeatherSummary | None:
    # Open-Meteo forecast: daily min/max + daily max precip prob; hourly precip prob for dropoff window.
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        + urllib.parse.urlencode(
            {
                "latitude": HK_LAT,
                "longitude": HK_LON,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "hourly": "precipitation_probability",
                "timezone": "Asia/Hong_Kong",
            }
        )
    )

    status, payload = _http_json(url)
    if not status or status >= 300:
        errors.append(f"Weather unavailable: {payload.get('reason', payload.get('error', 'unknown error'))}")
        return None

    try:
        daily = payload["daily"]
        # Find index for 'today'
        days = [date.fromisoformat(d) for d in daily["time"]]
        i = days.index(today)

        tmax = float(daily["temperature_2m_max"][i])
        tmin = float(daily["temperature_2m_min"][i])
        rain_prob_max = int(daily["precipitation_probability_max"][i]) if daily.get("precipitation_probability_max") else None

        dropoff = None
        if school_day:
            # Take max of 08:00 and 09:00 hourly probability (cheap approximation for 08:00–08:30).
            hourly = payload.get("hourly", {})
            ht = hourly.get("time", [])
            hp = hourly.get("precipitation_probability", [])
            want = {f"{today.isoformat()}T08:00", f"{today.isoformat()}T09:00"}
            probs = [int(p) for t, p in zip(ht, hp) if t in want and p is not None]
            if probs:
                dropoff = max(probs)

        return WeatherSummary(tmin=tmin, tmax=tmax, rain_prob_max=rain_prob_max, dropoff_rain_prob=dropoff)
    except Exception as e:
        errors.append(f"Weather parse error: {e}")
        return None


# -----------------------------
# Calendar
# -----------------------------

@dataclass
class CalEvent:
    start: datetime | None
    end: datetime | None
    all_day: bool
    summary: str
    calendar_label: str


def get_calendar_events(*, cal_id: str, cal_label: str, start: datetime, end: datetime, errors: list[str]) -> list[CalEvent]:
    base = "https://www.googleapis.com/calendar/v3"
    params = {
        "timeMin": _rfc3339(start),
        "timeMax": _rfc3339(end),
        "singleEvents": "true",
        "orderBy": "startTime",
        "maxResults": "50",
    }
    url = f"{base}/calendars/{urllib.parse.quote(cal_id, safe='')}/events?{urllib.parse.urlencode(params)}"

    payload = _google_authed_get(url, token_path=CAL_TOKENS, oauth_path=GOOGLE_OAUTH, errors=errors)
    if not payload:
        return []

    out: list[CalEvent] = []
    for ev in payload.get("items", []):
        summary = ev.get("summary") or "(no title)"
        s = ev.get("start", {})
        e = ev.get("end", {})
        if "dateTime" in s:
            start_dt = _parse_rfc3339(s["dateTime"]).astimezone(HKT)
            end_dt = _parse_rfc3339(e["dateTime"]).astimezone(HKT) if "dateTime" in e else None
            out.append(CalEvent(start=start_dt, end=end_dt, all_day=False, summary=summary, calendar_label=cal_label))
        elif "date" in s:
            # All-day; treat as local date.
            d0 = date.fromisoformat(s["date"])
            out.append(CalEvent(start=datetime.combine(d0, time(0, 0), tzinfo=HKT), end=None, all_day=True, summary=summary, calendar_label=cal_label))
    return out


# -----------------------------
# Todoist
# -----------------------------

@dataclass
class Task:
    content: str
    project: str
    priority: int
    due_dt: datetime | None
    due_date: date | None
    duration_min: int | None


def _todoist_auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _todoist_get(url: str, token: str, errors: list[str]):
    status, payload = _http_json(url, headers=_todoist_auth_headers(token))
    if status and 200 <= status < 300:
        return payload
    errors.append(f"Todoist API error {status}: {payload.get('error', payload)}")
    return None


def get_todoist(token: str, *, now: datetime, errors: list[str]):
    base = "https://api.todoist.com/rest/v2"

    projects = _todoist_get(f"{base}/projects", token, errors) or []
    proj_map = {str(p["id"]): p.get("name", "(unknown)") for p in projects if "id" in p}

    tasks_raw = _todoist_get(f"{base}/tasks", token, errors) or []

    tasks: list[Task] = []
    for t in tasks_raw:
        prio = int(t.get("priority", 1))
        if prio < 3:
            continue  # only P1 (4) and P2 (3)

        due = t.get("due") or {}
        due_dt = None
        due_d = None
        if due.get("datetime"):
            try:
                due_dt = _parse_rfc3339(due["datetime"]).astimezone(HKT)
            except Exception:
                due_dt = None
        elif due.get("date"):
            try:
                due_d = date.fromisoformat(due["date"])
            except Exception:
                due_d = None

        dur = t.get("duration")
        duration_min = None
        # REST v2 commonly returns duration as {"amount": 30, "unit": "minute"}
        if isinstance(dur, dict) and dur.get("amount") is not None:
            try:
                amount = int(dur["amount"])
                unit = dur.get("unit")
                if unit == "minute":
                    duration_min = amount
                elif unit == "day":
                    duration_min = amount * 8 * 60
            except Exception:
                duration_min = None

        pid = str(t.get("project_id", ""))
        pname = proj_map.get(pid, "(No project)")

        tasks.append(
            Task(
                content=t.get("content") or "(no title)",
                project=pname,
                priority=prio,
                due_dt=due_dt,
                due_date=due_d,
                duration_min=duration_min,
            )
        )

    return tasks


# -----------------------------
# Gmail
# -----------------------------

@dataclass
class EmailHighlight:
    sender: str
    subject: str


def _gmail_get(url: str, errors: list[str]):
    payload = _google_authed_get(url, token_path=GMAIL_TOKENS, oauth_path=GOOGLE_OAUTH, errors=errors)
    return payload


def get_gmail_unread_count(errors: list[str]) -> int | None:
    base = "https://gmail.googleapis.com/gmail/v1/users/me"
    q = urllib.parse.quote("is:unread")
    url = f"{base}/messages?q={q}&maxResults=1"
    payload = _gmail_get(url, errors)
    if not payload:
        return None
    return int(payload.get("resultSizeEstimate", 0))


def _gmail_list(q: str, max_results: int, errors: list[str]) -> list[str]:
    base = "https://gmail.googleapis.com/gmail/v1/users/me"
    url = f"{base}/messages?{urllib.parse.urlencode({'q': q, 'maxResults': str(max_results)})}"
    payload = _gmail_get(url, errors)
    if not payload:
        return []
    return [m.get("id") for m in payload.get("messages", []) if m.get("id")]


def _gmail_metadata(msg_id: str, errors: list[str]) -> EmailHighlight | None:
    base = "https://gmail.googleapis.com/gmail/v1/users/me"
    params = [
        ("format", "metadata"),
        ("metadataHeaders", "From"),
        ("metadataHeaders", "Subject"),
    ]
    url = f"{base}/messages/{urllib.parse.quote(msg_id)}?{urllib.parse.urlencode(params)}"
    payload = _gmail_get(url, errors)
    if not payload:
        return None

    headers = {h.get("name"): h.get("value") for h in (payload.get("payload", {}).get("headers", []) or [])}
    sender = headers.get("From", "(unknown)")
    subject = headers.get("Subject", "(no subject)")

    # Cheap cleanup: strip email address part for readability
    if "<" in sender and ">" in sender:
        sender = sender.split("<", 1)[0].strip().strip('"')

    return EmailHighlight(sender=sender, subject=subject)


def get_gmail_highlights(*, now: datetime, errors: list[str]) -> list[EmailHighlight]:
    # “Overnight” window: ~16 hours (covers after work → morning)
    # Highlights: unread + (important/starred or subject urgent/asap)
    q = "is:unread newer_than:16h (is:starred OR label:important OR subject:urgent OR subject:asap)"
    ids = _gmail_list(q, MAX_EMAIL_HIGHLIGHTS, errors)
    out: list[EmailHighlight] = []
    for mid in ids[:MAX_EMAIL_HIGHLIGHTS]:
        meta = _gmail_metadata(mid, errors)
        if meta:
            out.append(meta)
    return out


# -----------------------------
# Formatting
# -----------------------------

def _prio_label(p: int) -> str:
    # Todoist REST: 4 highest
    return "P1" if p == 4 else "P2" if p == 3 else f"P{p}"


def _fmt_duration(mins: int | None) -> str:
    if not mins:
        return ""
    if mins < 60:
        return f" ({mins}m)"
    h = mins // 60
    m = mins % 60
    return f" ({h}h{'' if m == 0 else f'{m}m'})"


def build_message(*, now: datetime, school_day: bool, weather: WeatherSummary | None, todays_events: list[CalEvent], tasks_due: list[Task], tasks_upcoming: list[Task], upcoming_events: list[CalEvent], unread_count: int | None, email_highlights: list[EmailHighlight], errors: list[str]) -> str:
    today = now.date()

    lines: list[str] = []

    # 1) Good morning + date/day
    lines.append(f"Good morning, Guillermo — {_fmt_day(today)} (HKT)")

    if school_day:
        lines.append("School day: yes (drop-off 08:00–08:30)")

    lines.append("")

    # 2) Weather
    if weather:
        wline = f"Weather: {int(round(weather.tmin))}–{int(round(weather.tmax))}°C"
        if weather.rain_prob_max is not None:
            wline += f" · Rain chance up to {weather.rain_prob_max}%"
        lines.append("🌤 " + wline)
        if school_day and weather.dropoff_rain_prob is not None and weather.dropoff_rain_prob >= 40:
            lines.append(f"   ⚠️ Rain risk at drop-off (08:00): ~{weather.dropoff_rain_prob}%")
    else:
        lines.append("🌤 Weather: ⚠️ unavailable")

    lines.append("")

    # 3) Today's Calendar
    lines.append("📅 Today")
    if todays_events:
        for ev in todays_events[:MAX_CAL_TODAY]:
            if ev.all_day:
                t = "all-day"
            else:
                t = _fmt_hhmm(ev.start) if ev.start else "?"
            lines.append(f"{t:>6}  {ev.summary}  · {ev.calendar_label}")
        if len(todays_events) > MAX_CAL_TODAY:
            lines.append(f"… +{len(todays_events) - MAX_CAL_TODAY} more")
    else:
        lines.append("No events")

    lines.append("")

    # 4) Tasks Due (P1/P2) grouped by project
    lines.append("✅ Tasks due (P1/P2)")
    if tasks_due:
        # group
        grouped: dict[str, list[Task]] = {}
        for t in tasks_due:
            grouped.setdefault(t.project, []).append(t)

        for proj in sorted(grouped.keys()):
            lines.append(proj)
            items = sorted(
                grouped[proj],
                key=lambda x: (
                    -x.priority,
                    x.due_dt or datetime.combine(x.due_date or today, time(23, 59), tzinfo=HKT),
                    x.content.lower(),
                ),
            )
            for t in items[:MAX_TASKS_PER_PROJECT]:
                due = ""
                if t.due_dt:
                    due = f" @ {_fmt_hhmm(t.due_dt)}"
                elif t.due_date and t.due_date != today:
                    due = f" ({t.due_date.isoformat()})"
                lines.append(f"• [{_prio_label(t.priority)}]{due} {t.content}{_fmt_duration(t.duration_min)}")
            if len(items) > MAX_TASKS_PER_PROJECT:
                lines.append(f"  … +{len(items) - MAX_TASKS_PER_PROJECT} more")
    else:
        lines.append("No P1–P2 tasks due")

    lines.append("")

    # 5) Upcoming this week (next 3–5 days)
    lines.append("🔜 Next 5 days")
    upcoming_lines = 0

    # upcoming events (excluding today)
    if upcoming_events:
        for ev in upcoming_events[:MAX_UPCOMING]:
            d = ev.start.astimezone(HKT).date() if ev.start else today
            label = d.strftime("%a")
            if ev.all_day:
                lines.append(f"{label}  all-day  {ev.summary}  · {ev.calendar_label}")
            else:
                lines.append(f"{label}  {_fmt_hhmm(ev.start)}  {ev.summary}  · {ev.calendar_label}")
            upcoming_lines += 1

    # upcoming tasks (due soon)
    if tasks_upcoming:
        for t in tasks_upcoming[: max(0, MAX_UPCOMING - upcoming_lines)]:
            dd = t.due_dt.astimezone(HKT).date() if t.due_dt else t.due_date
            if not dd:
                continue
            label = dd.strftime("%a")
            lines.append(f"{label}  {_prio_label(t.priority)}  {t.content}  · {t.project}")
            upcoming_lines += 1

    if upcoming_lines == 0:
        lines.append("Nothing notable")

    lines.append("")

    # 6) Email highlights
    lines.append("✉️ Email")
    if unread_count is None:
        lines.append("Unread: ⚠️ unavailable")
    else:
        lines.append(f"Unread: {unread_count}")

    if email_highlights:
        for e in email_highlights[:MAX_EMAIL_HIGHLIGHTS]:
            lines.append(f"• {e.sender} — {e.subject}")
    else:
        lines.append("No overnight highlights")

    # Errors (compact, at bottom)
    if errors:
        lines.append("")
        lines.append("⚠️ Notes")
        for err in errors[:5]:
            lines.append(f"- {err}")

    # Focus line
    focus = None
    p1 = [t for t in tasks_due if t.priority == 4]
    if p1:
        focus = p1[0].content
    elif todays_events and not todays_events[0].all_day:
        focus = f"Prep for: {todays_events[0].summary}"

    if focus:
        lines.append("")
        lines.append(f"Focus: {focus}")

    return "\n".join(lines).strip() + "\n"


# -----------------------------
# Main
# -----------------------------

def main() -> int:
    now = datetime.now(tz=HKT)
    today = now.date()
    dow = _dow_token(today)
    school_day = dow in SCHOOL_DROP_OFF_DAYS

    errors: list[str] = []

    # Weather
    weather = get_weather(today, school_day=school_day, errors=errors)

    # Calendar
    cfg = _read_json(CALENDAR_CONFIG)
    cals = cfg.get("calendars", {})

    # Today window
    start_today = datetime.combine(today, time(0, 0), tzinfo=HKT)
    end_today = start_today + timedelta(days=1)

    todays_events: list[CalEvent] = []

    for key, label in [("personal", "Personal"), ("shenanigans", "Family"), ("brinc", "Brinc")]:
        cal_id = (cals.get(key) or {}).get("id")
        if cal_id:
            todays_events.extend(get_calendar_events(cal_id=cal_id, cal_label=label, start=start_today, end=end_today, errors=errors))

    # Sort and keep in HKT
    todays_events.sort(key=lambda e: (e.start or start_today, e.all_day))

    # Upcoming window: next 5 days excluding today
    start_up = end_today
    end_up = end_today + timedelta(days=5)
    upcoming_events: list[CalEvent] = []
    for key, label in [("personal", "Personal"), ("shenanigans", "Family"), ("brinc", "Brinc")]:
        cal_id = (cals.get(key) or {}).get("id")
        if cal_id:
            upcoming_events.extend(get_calendar_events(cal_id=cal_id, cal_label=label, start=start_up, end=end_up, errors=errors))

    upcoming_events.sort(key=lambda e: (e.start or start_up, e.all_day))

    # Todoist
    env = _load_env_file(TODOIST_ENV)
    todo_token = env.get("TODOIST_API_TOKEN") or os.environ.get("TODOIST_API_TOKEN")

    tasks_due: list[Task] = []
    tasks_upcoming: list[Task] = []
    if todo_token:
        tasks = get_todoist(todo_token, now=now, errors=errors)
        # due today or overdue
        end_of_today = datetime.combine(today, time(23, 59), tzinfo=HKT)

        for t in tasks:
            # classify due date
            due_dt = t.due_dt
            due_d = t.due_date
            is_due = False
            if due_dt:
                is_due = due_dt <= end_of_today
            elif due_d:
                is_due = due_d <= today

            if is_due:
                tasks_due.append(t)
            else:
                # upcoming 5 days
                if due_dt and due_dt.date() <= (today + timedelta(days=5)):
                    tasks_upcoming.append(t)
                elif due_d and due_d <= (today + timedelta(days=5)):
                    tasks_upcoming.append(t)

        # Sort tasks_due by priority then due
        tasks_due.sort(key=lambda x: (-x.priority, x.due_dt or datetime.combine(x.due_date or today, time(23, 59), tzinfo=HKT)))
        tasks_upcoming.sort(key=lambda x: (x.due_dt or datetime.combine(x.due_date or today, time(23, 59), tzinfo=HKT)))
    else:
        errors.append("Todoist token missing (credentials/todoist.env)")

    # Gmail
    unread_count = get_gmail_unread_count(errors)
    email_highlights = get_gmail_highlights(now=now, errors=errors)

    # Weekend mode adjustments
    if dow in {"SA", "SU"}:
        # shrink tasks
        p1_due = [t for t in tasks_due if t.priority == 4]
        p2_due = [t for t in tasks_due if t.priority == 3]
        tasks_due = p1_due + p2_due[:3]
        upcoming_events = upcoming_events[:3]

    msg = build_message(
        now=now,
        school_day=school_day,
        weather=weather,
        todays_events=todays_events,
        tasks_due=tasks_due,
        tasks_upcoming=tasks_upcoming,
        upcoming_events=upcoming_events,
        unread_count=unread_count,
        email_highlights=email_highlights,
        errors=errors,
    )

    sys.stdout.write(msg)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
```

### Script install steps

```bash
chmod +x /data/workspace/scripts/morning_briefing.py
python3 /data/workspace/scripts/morning_briefing.py
```

---

## 3) Message template (Telegram-ready)

The script above outputs this structure:

1. **Greeting + date/day**
2. **Weather** (with school-dropoff rain flag on MO/WE/FR)
3. **Today’s calendar** (time + title + calendar label)
4. **Tasks due** (P1/P2, grouped by project)
5. **Next 5 days** (events then tasks, brief)
6. **Email** (unread count + highlights)
7. **Notes / errors** (only if needed)
8. **Focus** (one-liner)

Formatting rules:
- Blank line between sections.
- Hard limits:
  - Today events: 10
  - Tasks per project: 6
  - Email highlights: 5
  - Upcoming items: 6

---

## 4) Cron job configuration (OpenClaw)

### Recommended: recurring isolated job, 07:30 HKT

**Tool-call JSON (cron.add):**

```json
{
  "name": "Morning Briefing (07:30 HKT)",
  "schedule": { "kind": "cron", "expr": "30 7 * * *", "tz": "Asia/Hong_Kong" },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "agentTurn",
    "model": "google/gemini-2.5-flash",
    "message": "Run the morning briefing script and output the result verbatim.\n\n1) Use the exec tool to run: python3 /data/workspace/scripts/morning_briefing.py\n2) Reply with ONLY the script output (no preamble, no code fences)."
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "bestEffort": true
  }
}
```

Notes:
- If you know Guillermo’s Telegram target, set `delivery.to` explicitly (chat id / topic).
- If omitted, Gateway can fall back to “last route” depending on your config.

### CLI equivalent

```bash
openclaw cron add \
  --name "Morning Briefing (07:30 HKT)" \
  --cron "30 7 * * *" \
  --tz "Asia/Hong_Kong" \
  --session isolated \
  --model "google/gemini-2.5-flash" \
  --message "Run: python3 /data/workspace/scripts/morning_briefing.py and output only its text." \
  --announce \
  --channel telegram
```

---

## 5) Error handling strategy

### Per-source isolation
- Weather failures do not affect calendar/tasks/email.
- Calendar failures do not affect Todoist or Gmail.
- Gmail failures still deliver the briefing with `Unread: unavailable`.

### Token refresh
- On HTTP **401**, refresh access token via Google OAuth and overwrite token JSON file.
- If refresh fails, show a compact warning in `⚠️ Notes`.

### Output safety
- Never include secrets in output.
- Limit lists to prevent Telegram 4096-char overflow.

### Observability
- In v1, errors are surfaced as `⚠️ Notes` at bottom.
- Future: write a JSON run log to `memory/morning-briefing/YYYY-MM-DD.json`.

---

## 6) Example output

```text
Good morning, Guillermo — Thu 5 Feb (HKT)
School day: yes (drop-off 08:00–08:30)

🌤 Weather: 18–23°C · Rain chance up to 70%
   ⚠️ Rain risk at drop-off (08:00): ~55%

📅 Today
  all-day  Lunar New Year holiday  · Family
  09:30  Brinc Weekly Staff Meeting  · Brinc
  12:00  Lunch with Marco  · Personal
  16:30  Call: Mana Capital pipeline  · Personal

✅ Tasks due (P1/P2)
Brinc 🔴
• [P1] Send investor update (30m)
• [P2] Review Q1 hiring plan (1h)
Personal 🙂
• [P2] Pay phone bill (15m)

🔜 Next 5 days
Fri  10:00  Demo day rehearsal  · Brinc
Mon  all-day  School event  · Family
Tue  P2  Prep Mana IC memo  · Mana Capital 🟠

✉️ Email
Unread: 12
• Alice — URGENT: confirm meeting time
• Brinc Ops — Expense policy update

Focus: Send investor update
```

---

## 7) Future enhancements

### Quick Stats (Whoop)
- Add `get_whoop_stats()` function that returns recovery/sleep.
- Append a small section:
  - `📊 Quick stats: Recovery 62% · Sleep 7h12m`

### News digest (optional)
- Add a 3-bullet “Today in the world / markets” section.
- Keep hard cap (3 bullets) and allow opt-out.

### Smarter prioritization
- Compute “free blocks” from calendar + life commitments.
- Suggest a **timeboxed plan**: “08:45–09:20: Task A; 09:20–09:35 buffer”.

### Better email triage
- Use Gmail labels + thread context.
- Detect VIP senders list.

### Caching + rate limiting
- Cache Calendar + Gmail responses to disk for 5 minutes to avoid accidental double runs.

### Multi-message delivery
- If message length > 3500 chars, split into 2 Telegram messages:
  - Part 1: Weather + Today + Tasks
  - Part 2: Upcoming + Email

---

## Appendix A — Data sources used (v1)

- **Calendar IDs** are read from `credentials/calendar-config.json`:
  - `personal`, `shenanigans`, `brinc`
- **Google OAuth client** from `credentials/google-oauth.json`
- **Calendar tokens** from `credentials/calendar-tokens-brinc.json`
- **Gmail tokens** from `credentials/gmail-tokens.json`
- **Todoist token** from `credentials/todoist.env`
