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


def _http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict | None = None,
    data: dict | None = None,
    timeout: int = 30,
):
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Accept": "application/json",
            **(headers or {}),
            **({"Content-Type": "application/json"} if body else {}),
        },
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
class ForecastDay:
    day: date
    tmin: float | None
    tmax: float | None
    rain_prob_max: int | None


@dataclass
class WeatherSummary:
    today: ForecastDay
    outlook_3d: list[ForecastDay]
    dropoff_rain_prob: int | None


def get_weather(today: date, *, school_day: bool, errors: list[str]) -> WeatherSummary | None:
    """Return today's weather plus an outlook for the next 3 days (Open-Meteo)."""
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
        errors.append(
            f"Weather unavailable: {payload.get('reason', payload.get('error', 'unknown error'))}"
        )
        return None

    try:
        daily = payload["daily"]

        days = [date.fromisoformat(d) for d in daily["time"]]
        i = days.index(today)

        def mk_day(idx: int) -> ForecastDay:
            tmax = float(daily["temperature_2m_max"][idx]) if daily.get("temperature_2m_max") else None
            tmin = float(daily["temperature_2m_min"][idx]) if daily.get("temperature_2m_min") else None
            rain = None
            if daily.get("precipitation_probability_max"):
                v = daily["precipitation_probability_max"][idx]
                rain = int(v) if v is not None else None
            return ForecastDay(day=days[idx], tmin=tmin, tmax=tmax, rain_prob_max=rain)

        today_fc = mk_day(i)
        outlook: list[ForecastDay] = []
        for j in range(i + 1, min(i + 4, len(days))):
            outlook.append(mk_day(j))

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

        return WeatherSummary(today=today_fc, outlook_3d=outlook, dropoff_rain_prob=dropoff)
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


def get_calendar_events(
    *,
    cal_id: str,
    cal_label: str,
    start: datetime,
    end: datetime,
    errors: list[str],
) -> list[CalEvent]:
    base = "https://www.googleapis.com/calendar/v3"
    params = {
        "timeMin": _rfc3339(start),
        "timeMax": _rfc3339(end),
        "singleEvents": "true",
        "orderBy": "startTime",
        "maxResults": "50",
    }
    url = f"{base}/calendars/{urllib.parse.quote(cal_id, safe='')}/events?{urllib.parse.urlencode(params)}"

    payload = _google_authed_get(
        url, token_path=CAL_TOKENS, oauth_path=GOOGLE_OAUTH, errors=errors
    )
    if not payload:
        return []

    out: list[CalEvent] = []
    for ev in payload.get("items", []):
        summary = ev.get("summary") or "(no title)"
        s = ev.get("start", {})
        e = ev.get("end", {})
        if "dateTime" in s:
            start_dt = _parse_rfc3339(s["dateTime"]).astimezone(HKT)
            end_dt = (
                _parse_rfc3339(e["dateTime"]).astimezone(HKT) if "dateTime" in e else None
            )
            out.append(
                CalEvent(
                    start=start_dt,
                    end=end_dt,
                    all_day=False,
                    summary=summary,
                    calendar_label=cal_label,
                )
            )
        elif "date" in s:
            # All-day; treat as local date.
            d0 = date.fromisoformat(s["date"])
            out.append(
                CalEvent(
                    start=datetime.combine(d0, time(0, 0), tzinfo=HKT),
                    end=None,
                    all_day=True,
                    summary=summary,
                    calendar_label=cal_label,
                )
            )
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


def get_todoist(token: str, *, errors: list[str]) -> list[Task]:
    base = "https://api.todoist.com/rest/v2"

    projects = _todoist_get(f"{base}/projects", token, errors) or []
    proj_map = {
        str(p["id"]): p.get("name", "(unknown)") for p in projects if "id" in p
    }

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


def _gmail_get(url: str, errors: list[str]) -> dict | None:
    return _google_authed_get(url, token_path=GMAIL_TOKENS, oauth_path=GOOGLE_OAUTH, errors=errors)


def get_gmail_unread_count(errors: list[str]) -> int | None:
    base = "https://gmail.googleapis.com/gmail/v1/users/me"
    q = "is:unread"
    url = f"{base}/messages?{urllib.parse.urlencode({'q': q, 'maxResults': '1'})}"
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

    headers = {
        h.get("name"): h.get("value")
        for h in (payload.get("payload", {}).get("headers", []) or [])
    }
    sender = headers.get("From", "(unknown)")
    subject = headers.get("Subject", "(no subject)")

    # Cheap cleanup: strip email address part for readability
    if "<" in sender and ">" in sender:
        sender = sender.split("<", 1)[0].strip().strip('"')

    return EmailHighlight(sender=sender, subject=subject)


def get_gmail_highlights(*, errors: list[str]) -> list[EmailHighlight]:
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


def build_message(
    *,
    now: datetime,
    school_day: bool,
    weather: WeatherSummary | None,
    todays_events: list[CalEvent],
    tasks_due: list[Task],
    tasks_upcoming: list[Task],
    upcoming_events: list[CalEvent],
    unread_count: int | None,
    email_highlights: list[EmailHighlight],
    errors: list[str],
) -> str:
    today = now.date()

    lines: list[str] = []

    # 1) Good morning + date/day
    lines.append(f"Good morning, Guillermo — {_fmt_day(today)} (HKT)")

    if school_day:
        lines.append("School day: yes (drop-off 08:00–08:30)")

    lines.append("")

    # 2) Weather
    if weather:
        tmin = weather.today.tmin
        tmax = weather.today.tmax
        rain = weather.today.rain_prob_max

        wline = "Weather:"
        if tmin is not None and tmax is not None:
            wline += f" {int(round(tmin))}–{int(round(tmax))}°C"
        if rain is not None:
            wline += f" · Rain chance up to {rain}%"
        lines.append("🌤 " + wline)

        # Next 3 days outlook
        if weather.outlook_3d:
            parts = []
            for fc in weather.outlook_3d[:3]:
                label = fc.day.strftime("%a")
                if fc.tmin is not None and fc.tmax is not None:
                    p = f"{label} {int(round(fc.tmin))}–{int(round(fc.tmax))}°C"
                else:
                    p = f"{label}"
                if fc.rain_prob_max is not None:
                    p += f" ({fc.rain_prob_max}%)"
                parts.append(p)
            lines.append("   Outlook: " + " · ".join(parts))

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
        grouped: dict[str, list[Task]] = {}
        for t in tasks_due:
            grouped.setdefault(t.project, []).append(t)

        for proj in sorted(grouped.keys()):
            lines.append(proj)
            items = sorted(
                grouped[proj],
                key=lambda x: (
                    -x.priority,
                    x.due_dt
                    or datetime.combine(
                        x.due_date or today, time(23, 59), tzinfo=HKT
                    ),
                    x.content.lower(),
                ),
            )
            for t in items[:MAX_TASKS_PER_PROJECT]:
                due = ""
                if t.due_dt:
                    due = f" @ {_fmt_hhmm(t.due_dt)}"
                elif t.due_date and t.due_date != today:
                    due = f" ({t.due_date.isoformat()})"
                lines.append(
                    f"• [{_prio_label(t.priority)}]{due} {t.content}{_fmt_duration(t.duration_min)}"
                )
            if len(items) > MAX_TASKS_PER_PROJECT:
                lines.append(f"  … +{len(items) - MAX_TASKS_PER_PROJECT} more")
    else:
        lines.append("No P1–P2 tasks due")

    lines.append("")

    # 5) Upcoming this week (next 3–5 days)
    lines.append("🔜 Next 5 days")
    upcoming_lines = 0

    if upcoming_events:
        for ev in upcoming_events[:MAX_UPCOMING]:
            d = ev.start.astimezone(HKT).date() if ev.start else today
            label = d.strftime("%a")
            if ev.all_day:
                lines.append(
                    f"{label}  all-day  {ev.summary}  · {ev.calendar_label}"
                )
            else:
                lines.append(
                    f"{label}  {_fmt_hhmm(ev.start)}  {ev.summary}  · {ev.calendar_label}"
                )
            upcoming_lines += 1

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

    if errors:
        lines.append("")
        lines.append("⚠️ Notes")
        for err in errors[:5]:
            lines.append(f"- {err}")

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

    weather = get_weather(today, school_day=school_day, errors=errors)

    cfg = _read_json(CALENDAR_CONFIG)
    cals = cfg.get("calendars", {})

    start_today = datetime.combine(today, time(0, 0), tzinfo=HKT)
    end_today = start_today + timedelta(days=1)

    todays_events: list[CalEvent] = []

    for key, label in [("personal", "Personal"), ("shenanigans", "Family"), ("brinc", "Brinc")]:
        cal_id = (cals.get(key) or {}).get("id")
        if cal_id:
            todays_events.extend(
                get_calendar_events(
                    cal_id=cal_id,
                    cal_label=label,
                    start=start_today,
                    end=end_today,
                    errors=errors,
                )
            )

    todays_events.sort(key=lambda e: (e.start or start_today, e.all_day))

    start_up = end_today
    end_up = end_today + timedelta(days=5)

    upcoming_events: list[CalEvent] = []
    for key, label in [("personal", "Personal"), ("shenanigans", "Family"), ("brinc", "Brinc")]:
        cal_id = (cals.get(key) or {}).get("id")
        if cal_id:
            upcoming_events.extend(
                get_calendar_events(
                    cal_id=cal_id,
                    cal_label=label,
                    start=start_up,
                    end=end_up,
                    errors=errors,
                )
            )

    upcoming_events.sort(key=lambda e: (e.start or start_up, e.all_day))

    env = _load_env_file(TODOIST_ENV)
    todo_token = env.get("TODOIST_API_TOKEN") or os.environ.get("TODOIST_API_TOKEN")

    tasks_due: list[Task] = []
    tasks_upcoming: list[Task] = []

    if todo_token:
        tasks = get_todoist(todo_token, errors=errors)

        end_of_today = datetime.combine(today, time(23, 59), tzinfo=HKT)
        for t in tasks:
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
                if due_dt and due_dt.date() <= (today + timedelta(days=5)):
                    tasks_upcoming.append(t)
                elif due_d and due_d <= (today + timedelta(days=5)):
                    tasks_upcoming.append(t)

        tasks_due.sort(
            key=lambda x: (
                -x.priority,
                x.due_dt
                or datetime.combine(x.due_date or today, time(23, 59), tzinfo=HKT),
            )
        )
        tasks_upcoming.sort(
            key=lambda x: (
                x.due_dt
                or datetime.combine(x.due_date or today, time(23, 59), tzinfo=HKT)
            )
        )
    else:
        errors.append("Todoist token missing (credentials/todoist.env)")

    unread_count = get_gmail_unread_count(errors)
    email_highlights = get_gmail_highlights(errors=errors)

    # Weekend mode adjustments
    if dow in {"SA", "SU"}:
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
