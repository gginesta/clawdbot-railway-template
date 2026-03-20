#!/data/workspace/.venv/bin/python3
"""morning_briefing.py

Generates Guillermo's daily morning briefing (HKT) as a Telegram-ready text message.

Data sources:
- Open-Meteo (weather; no API key)
- Google Calendar API (via service account / OAuth refresh token)
- Todoist REST v1
- Gmail via `gog` CLI (gogcli.sh)

Exit codes:
- 0 success
- 1 catastrophic failure (should be rare; script is designed to degrade gracefully)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, date, time
from zoneinfo import ZoneInfo

HKT = ZoneInfo("Asia/Hong_Kong")
UTC = ZoneInfo("UTC")

CALENDAR_CONFIG = "/data/workspace/credentials/calendar-config.json"
CAL_TOKENS = "/data/workspace/credentials/calendar-tokens-brinc.json"
GOOGLE_OAUTH = "/data/workspace/credentials/google-oauth.json"
GOOGLE_SA = "/data/workspace/credentials/google-service-account.json"
TODOIST_ENV = "/data/workspace/credentials/todoist.env"

GOG_ACCOUNT = "ggv.molt@gmail.com"
GOG_KEYRING_PASSWORD = "molty2026"
GOG_BIN = "/usr/local/bin/gog"
GOG_CREDENTIALS_BACKUP = "/data/workspace/credentials/google-oauth-client.json"
GOG_KEYRING_BACKUP = "/data/workspace/credentials/gogcli-keyring/keyring"
GOG_KEYRING_DIR = "/root/.config/gogcli/keyring"
GOG_CREDENTIALS_DIR = "/root/.config/gogcli"


def ensure_gog_setup() -> None:
    """Self-healing: restore gog auth and sync backup via setup-gog-auth.sh."""
    setup_script = "/data/workspace/scripts/setup-gog-auth.sh"
    if os.path.exists(setup_script):
        try:
            env = {**os.environ, "GOG_KEYRING_PASSWORD": GOG_KEYRING_PASSWORD}
            subprocess.run(["/bin/bash", setup_script], env=env, timeout=30,
                           capture_output=True)
        except Exception as e:
            print(f"⚠️ setup-gog-auth.sh failed: {e}", file=sys.stderr)

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


def _smart_truncate(text: str, max_len: int) -> str:
    """Truncate text at word boundary, not mid-word."""
    if len(text) <= max_len:
        return text
    # Find last space before max_len
    truncated = text[:max_len]
    last_space = truncated.rfind(' ')
    if last_space > max_len // 2:  # Only use space if it's not too early
        return truncated[:last_space] + "…"
    return truncated[:-1] + "…"


# -----------------------------
# gog CLI helper
# -----------------------------

def _gog_json(args: list[str], *, errors: list[str], timeout: int = 30) -> dict | None:
    """Run a gog command with --json and return parsed output."""
    cmd = ["/usr/local/bin/gog"] + args + ["--json", "-a", GOG_ACCOUNT]
    env = {**os.environ, "GOG_KEYRING_PASSWORD": GOG_KEYRING_PASSWORD}
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        if result.returncode != 0:
            errors.append(f"gog {args[0]} error: {result.stderr.strip()[:200]}")
            return None
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        errors.append(f"gog {args[0]} timed out")
        return None
    except Exception as e:
        errors.append(f"gog {args[0]} failed: {e}")
        return None


# -----------------------------
# Google OAuth refresh (for Calendar only - Gmail uses gog CLI)
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
            msg = f"Google token refresh failed for {os.path.basename(token_path)}"
            if msg not in errors:
                errors.append(msg)
            return None

        tokens["access_token"] = refreshed["access_token"]
        _write_json(token_path, tokens)

        status, payload = do_get(tokens["access_token"])

    if status and 200 <= status < 300:
        return payload

    msg = f"Google API error {status} for {os.path.basename(token_path)}"
    if msg not in errors:
        errors.append(msg)
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
    """Return today's weather plus an outlook for the next 3 days (HKO official API)."""

    # PSR (Probability of Significant Rain) → approximate % for display
    _PSR_MAP = {"Low": 15, "Medium": 50, "High": 75, "Very High": 95}

    # Current weather for today (flw = local weather forecast)
    status_flw, flw = _http_json(
        "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang=en"
    )
    
    # 9-day forecast — temps + PSR per day (starts from tomorrow)
    status, fnd = _http_json(
        "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=en"
    )
    if not status or status >= 300:
        errors.append(f"Weather unavailable (HKO): HTTP {status}")
        return None

    try:
        fc_by_date: dict[date, dict] = {}
        for fc in fnd.get("weatherForecast", []):
            d_str = str(fc.get("forecastDate", ""))
            if len(d_str) == 8:
                try:
                    d = date(int(d_str[:4]), int(d_str[4:6]), int(d_str[6:8]))
                    fc_by_date[d] = fc
                except Exception:
                    pass

        def mk_day(d: date) -> ForecastDay:
            fc = fc_by_date.get(d)
            if not fc:
                return ForecastDay(day=d, tmin=None, tmax=None, rain_prob_max=None)
            tmin_v = fc.get("forecastMintemp", {}).get("value")
            tmax_v = fc.get("forecastMaxtemp", {}).get("value")
            psr = fc.get("PSR", "")
            rain = _PSR_MAP.get(psr)
            return ForecastDay(
                day=d,
                tmin=float(tmin_v) if tmin_v is not None else None,
                tmax=float(tmax_v) if tmax_v is not None else None,
                rain_prob_max=rain,
            )

        # For today, use tomorrow's forecast as proxy (9-day doesn't include today)
        # Or extract from flw if available
        tomorrow = today + timedelta(days=1)
        tomorrow_fc = fc_by_date.get(tomorrow, {})
        
        # Build today's forecast from tomorrow's data (best available)
        today_fc = ForecastDay(
            day=today,
            tmin=tomorrow_fc.get("forecastMintemp", {}).get("value"),
            tmax=tomorrow_fc.get("forecastMaxtemp", {}).get("value"),
            rain_prob_max=_PSR_MAP.get(tomorrow_fc.get("PSR", ""))
        )
        
        # If flw has today's outlook, try to extract temp range
        if status_flw and status_flw < 300 and flw:
            outlook_text = flw.get("forecastDesc", "") + " " + flw.get("outlook", "")
            # Try to find temperature mentions like "around 21 degrees"
            import re
            temps = re.findall(r'(\d{1,2})\s*(?:to|and|–|-)\s*(\d{1,2})\s*degrees', outlook_text, re.I)
            if temps:
                today_fc = ForecastDay(
                    day=today,
                    tmin=float(temps[0][0]),
                    tmax=float(temps[0][1]),
                    rain_prob_max=today_fc.rain_prob_max
                )
        
        outlook: list[ForecastDay] = [mk_day(today + timedelta(days=i)) for i in range(1, 4)]

        # Drop-off rain proxy
        dropoff = None
        if school_day and today_fc.rain_prob_max is not None:
            dropoff = today_fc.rain_prob_max

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


def _get_sa_access_token(errors: list[str]) -> str | None:
    """Get access token from Google service account."""
    try:
        from google.oauth2 import service_account as _sa
        creds = _sa.Credentials.from_service_account_file(
            GOOGLE_SA,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        )
        creds.refresh(__import__("google.auth.transport.requests", fromlist=["Request"]).Request())
        return creds.token
    except Exception as exc:
        errors.append(f"Service account auth failed: {exc}")
        return None


def _sa_authed_get(url: str, *, errors: list[str]) -> dict | None:
    """GET request using service account token."""
    token = _get_sa_access_token(errors)
    if not token:
        return None
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as exc:
        errors.append(f"Calendar API error: {exc}")
        return None


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

    # Use service account if available, fall back to OAuth
    if os.path.exists(GOOGLE_SA):
        payload = _sa_authed_get(url, errors=errors)
    else:
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
    parent_id: str | None = None
    subtask_count: int = 0
    subtask_summary: str = ""


def _todoist_auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _todoist_get(url: str, token: str, errors: list[str]):
    status, payload = _http_json(url, headers=_todoist_auth_headers(token))
    if status and 200 <= status < 300:
        return payload
    errors.append(f"Todoist API error {status}: {payload.get('error', payload)}")
    return None


def _unwrap_todoist(payload):
    """Todoist v1 API wraps results in {"results": [...], "next_cursor": ...}."""
    if isinstance(payload, dict) and "results" in payload:
        return payload["results"]
    if isinstance(payload, list):
        return payload  # legacy v2 format fallback
    return []


def get_todoist(token: str, *, errors: list[str]) -> list[Task]:
    base = "https://api.todoist.com/api/v1"

    projects = _unwrap_todoist(_todoist_get(f"{base}/projects", token, errors) or [])
    proj_map = {
        str(p["id"]): p.get("name", "(unknown)") for p in projects if "id" in p
    }

    tasks_raw = _unwrap_todoist(_todoist_get(f"{base}/tasks?limit=200", token, errors) or [])

    # REG-038/REG-039: Group subtasks under parent tasks, never show standalone
    # Step 1: Index all tasks by ID, track parent→children relationships
    all_by_id: dict[str, dict] = {}
    children_of: dict[str, list[dict]] = {}  # parent_id → list of child raw dicts
    for t in tasks_raw:
        tid = str(t.get("id", ""))
        all_by_id[tid] = t
        parent_id = t.get("parent_id")
        if parent_id:
            parent_id = str(parent_id)
            children_of.setdefault(parent_id, []).append(t)

    tasks: list[Task] = []
    for t in tasks_raw:
        prio = int(t.get("priority", 1))
        parent_id = t.get("parent_id")

        # Skip subtasks entirely — they'll be counted under their parent
        if parent_id:
            continue

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

        pid_str = str(t.get("project_id", ""))
        pname = proj_map.get(pid_str, "(No project)")

        # Count and summarize subtasks
        tid = str(t.get("id", ""))
        kids = children_of.get(tid, [])
        subtask_count = len(kids)
        subtask_summary = ""
        if kids:
            names = [k.get("content", "?")[:25] for k in kids[:3]]
            subtask_summary = ", ".join(names)
            if len(kids) > 3:
                subtask_summary += f", +{len(kids) - 3} more"

        tasks.append(
            Task(
                content=t.get("content") or "(no title)",
                project=pname,
                priority=prio,
                due_dt=due_dt,
                due_date=due_d,
                duration_min=duration_min,
                parent_id=None,
                subtask_count=subtask_count,
                subtask_summary=subtask_summary,
            )
        )

    return tasks


# -----------------------------
# Gmail (via gog CLI)
# -----------------------------

@dataclass
class EmailHighlight:
    sender: str
    subject: str


def get_gmail_unread_count(errors: list[str]) -> int | None:
    """Get unread count using gog gmail messages search."""
    data = _gog_json(["gmail", "messages", "search", "is:unread", "--max", "200"], errors=errors)
    if data is None:
        return None
    return len(data.get("messages", []))


def get_gmail_highlights(*, errors: list[str]) -> list[EmailHighlight]:
    """Get overnight email highlights using gog gmail messages search.
    
    Always flags:
    - Emails from Guillermo (CC'd to Molty)
    - Starred/important/urgent emails
    """
    seen_ids: set[str] = set()
    out: list[EmailHighlight] = []

    # Priority 1: Always show unread emails from Guillermo
    guillermo_q = "is:unread newer_than:24h from:guillermo.ginesta"
    g_data = _gog_json(["gmail", "messages", "search", guillermo_q, "--max", "10"], errors=errors)
    if g_data:
        for msg in g_data.get("messages", []):
            mid = msg.get("id", "")
            if mid in seen_ids:
                continue
            seen_ids.add(mid)
            sender = msg.get("from", "(unknown)")
            subject = msg.get("subject", "(no subject)")
            if "<" in sender and ">" in sender:
                sender = sender.split("<", 1)[0].strip().strip('"')
            out.append(EmailHighlight(sender=f"⭐ {sender}", subject=subject))

    # Priority 2: Starred/important/urgent
    q = "is:unread newer_than:16h (is:starred OR label:important OR subject:urgent OR subject:asap)"
    data = _gog_json(["gmail", "messages", "search", q, "--max", str(MAX_EMAIL_HIGHLIGHTS)], errors=errors)
    if data:
        for msg in data.get("messages", []):
            mid = msg.get("id", "")
            if mid in seen_ids:
                continue
            seen_ids.add(mid)
            sender = msg.get("from", "(unknown)")
            subject = msg.get("subject", "(no subject)")
            if "<" in sender and ">" in sender:
                sender = sender.split("<", 1)[0].strip().strip('"')
            out.append(EmailHighlight(sender=sender, subject=subject))
            if len(out) >= MAX_EMAIL_HIGHLIGHTS + 5:
                break

    return out[:MAX_EMAIL_HIGHLIGHTS + 5]


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


# -----------------------------
# Paperclip — Squad Status (replaces Mission Control)
# -----------------------------

# Fleet credentials — Molty's CEO tokens per company
PAPERCLIP_API = "https://paperclip-production-83f5.up.railway.app"
PAPERCLIP_COMPANIES = {
    "TMNT Squad": {
        "id": "4d845c5e-5c36-4fc5-827d-5a577e683cdb",
        "token": "pcp_5c66968515127b7b30f95a688a8477955f197666c7cfafbe",
    },
    "Brinc": {
        "id": "bd625bc3-1268-4b0f-a591-06bf06ca8d27",
        "token": "pcp_04dac50473349650e58d3d6cf68447e318c2fb4ec21325a4",
    },
    "Cerebro": {
        "id": "722bc707-271b-43be-a073-059270e031d2",
        "token": "pcp_afd6a737d85638e3ecf1b01ec5fb672785128e03fccd2ea0",
    },
}

AGENT_EMOJI = {
    "molty":     "🦎",
    "raphael":   "🔴",
    "leonardo":  "🔵",
    "donatello": "🟣",
    "april":     "📰",
}

# Legacy MC credentials (kept for overnight report fallback only)
MC_API = "https://resilient-chinchilla-241.convex.site"
MC_KEY = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"


@dataclass
class SquadStatus:
    p0_tasks: list[dict]
    blocked_tasks: list[dict]
    agent_tasks: dict[str, dict]   # agent_name → their top active issue
    guillermo_queue: list[dict]    # issues needing Guillermo's attention


def get_squad_status(errors: list[str]) -> SquadStatus | None:
    """Fetch a compact squad snapshot from Paperclip for the morning briefing.

    Queries all 3 companies for active issues. Format: agent name + in_progress issues.
    """
    all_issues: list[dict] = []

    for company_name, cfg in PAPERCLIP_COMPANIES.items():
        url = f"{PAPERCLIP_API}/api/companies/{cfg['id']}/issues?status=todo,in_progress,blocked"
        status, payload = _http_json(
            url,
            headers={"Authorization": f"Bearer {cfg['token']}"},
            timeout=10,
        )
        if status != 200:
            errors.append(f"Paperclip {company_name} unavailable (HTTP {status})")
            continue
        issues = payload if isinstance(payload, list) else []
        for issue in issues:
            issue["_company"] = company_name
        all_issues.extend(issues)

    if not all_issues:
        return None

    # High-priority issues (Paperclip uses "critical", "high", "medium", "low")
    p0 = [i for i in all_issues if i.get("priority") in ("critical",)][:3]

    blocked = [i for i in all_issues if i.get("status") == "blocked"][:3]

    # Top active issue per agent (in_progress first, then todo)
    agent_tasks: dict[str, dict] = {}
    status_rank = {"in_progress": 0, "todo": 1, "blocked": 2}
    for issue in sorted(all_issues, key=lambda x: status_rank.get(x.get("status", ""), 9)):
        agent_key = issue.get("executionAgentNameKey") or ""
        if agent_key and agent_key != "guillermo" and agent_key not in agent_tasks:
            agent_tasks[agent_key] = issue

    # Issues needing Guillermo's review (assigned to user, not agent)
    g_queue = [
        i for i in all_issues
        if i.get("assigneeUserId") and not i.get("assigneeAgentId")
    ][:5]

    return SquadStatus(
        p0_tasks=p0,
        blocked_tasks=blocked,
        agent_tasks=agent_tasks,
        guillermo_queue=g_queue,
    )


def _get_notion_comment_mentions(lookback_days: int = 3) -> list[str] | None:
    """Check Notion for recent comments/mentions on recently-modified pages.

    Uses official Notion API (v1). Scans pages modified in the last `lookback_days`
    days, checks each for comments, returns lines for the morning briefing.
    Only surfaces pages that actually have comments (graceful if none found).
    """
    NOTION_KEY = "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"
    headers = {
        "Authorization": f"Bearer {NOTION_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    cutoff = datetime.now(tz=HKT) - timedelta(days=lookback_days)
    found: list[str] = []

    try:
        # 1. Search for recently modified pages
        body = json.dumps({
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
            "page_size": 30,
        }).encode()
        req = urllib.request.Request(
            "https://api.notion.com/v1/search", data=body, headers=headers
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            search_data = json.loads(r.read())
        pages = search_data.get("results", [])

        # 2. For each page edited within lookback window, check comments
        for page in pages:
            edited_str = page.get("last_edited_time", "")
            try:
                edited = datetime.fromisoformat(edited_str.replace("Z", "+00:00")).astimezone(HKT)
            except Exception:
                continue
            if edited < cutoff:
                break  # sorted desc; once past cutoff we can stop

            page_id = page.get("id", "")
            if not page_id:
                continue

            # Fetch comments for this page
            try:
                comment_req = urllib.request.Request(
                    f"https://api.notion.com/v1/comments?block_id={page_id}",
                    headers={"Authorization": f"Bearer {NOTION_KEY}",
                             "Notion-Version": "2022-06-28"},
                )
                with urllib.request.urlopen(comment_req, timeout=10) as cr:
                    comment_data = json.loads(cr.read())
                comments = comment_data.get("results", [])
            except Exception:
                continue

            if not comments:
                continue

            # Get page title for context
            page_url = page.get("url", "")
            props = page.get("properties", {})
            title_text = "Untitled"
            for prop in props.values():
                if prop.get("type") == "title":
                    title_arr = prop.get("title", [])
                    if title_arr:
                        title_text = "".join(t.get("plain_text", "") for t in title_arr)
                        break

            # Filter: any comment in the lookback window
            recent_comments = []
            for c in comments:
                created_str = c.get("created_time", "")
                try:
                    created = datetime.fromisoformat(
                        created_str.replace("Z", "+00:00")
                    ).astimezone(HKT)
                except Exception:
                    created = cutoff  # include if can't parse

                if created >= cutoff:
                    rich = c.get("rich_text", [])
                    text = "".join(t.get("plain_text", "") for t in rich).strip()
                    author_id = c.get("created_by", {}).get("id", "")
                    recent_comments.append((created, text, author_id))

            if recent_comments:
                # Sort newest first
                recent_comments.sort(key=lambda x: x[0], reverse=True)
                short_url = page_url.split("notion.so/")[-1].split("?")[0][:50]
                found.append(f"💬 {title_text[:40]}: {len(recent_comments)} comment(s)")
                for _dt, text, _author in recent_comments[:2]:
                    found.append(f'  \u201c{text[:80]}\u201d')

    except Exception as e:
        # Non-fatal: comment monitoring should never break the briefing
        return None

    return found if found else None


def _get_overnight_summary(today: date) -> list[str] | None:
    """Read last night's task worker log and return summary lines for the briefing."""
    yesterday = today - timedelta(days=1)
    log_dir = "/data/workspace/logs"
    # Check yesterday's log (task worker runs at 02:00 HKT so it's "today" in UTC terms,
    # but the log is dated yesterday HKT — try both dates)
    for d in [today, yesterday]:
        path = os.path.join(log_dir, f"overnight-tasks-{d.isoformat()}.md")
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            lines: list[str] = []
            completed, flagged, failed = [], [], []
            section = None
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("## "):
                    # Reset section on any header, then check for known sections
                    section = None
                if "## ✅ Completed" in line:
                    section = "completed"
                elif "## ⏭️ Flagged" in line:
                    section = "flagged"
                elif "## ❌ Failed" in line:
                    section = "failed"
                elif line.startswith("- ") and section:
                    item = line[2:].strip()
                    if section == "completed":
                        completed.append(item)
                    elif section == "flagged":
                        flagged.append(item)
                    elif section == "failed":
                        failed.append(item)
            if not (completed or flagged or failed):
                return None
            if completed:
                lines.append(f"✅ Done ({len(completed)}): " + " · ".join(
                    c.split("→")[0].strip() for c in completed[:3]
                ) + ("..." if len(completed) > 3 else ""))
            if flagged:
                lines.append(f"⏭️ Flagged ({len(flagged)}) — will surface in standup")
            if failed:
                lines.append(f"❌ Failed ({len(failed)}) — check logs")
            return lines if lines else None
        except Exception:
            continue
    return None


def get_yesterdays_focus(today: date) -> str | None:
    """Read yesterday's standup state file and fetch the Tomorrow's Focus callout text."""
    STATE_FILE = "/data/workspace/logs/standup-state.json"
    NOTION_KEY = "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"
    NH = {"Authorization": f"Bearer {NOTION_KEY}", "Notion-Version": "2022-06-28"}
    yesterday = (today - timedelta(days=1)).isoformat()

    try:
        if not os.path.exists(STATE_FILE):
            return None
        state = json.load(open(STATE_FILE))
        # State file date should be yesterday's standup
        if state.get("date") != yesterday:
            return None
        page_id = state.get("page_id")
        if not page_id:
            return None

        req = urllib.request.Request(
            f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=20",
            headers=NH
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            blocks = json.loads(r.read()).get("results", [])

        for block in blocks:
            if block.get("type") != "callout":
                continue
            rich_text = block.get("callout", {}).get("rich_text", [])
            full_text = "".join(t.get("plain_text", "") for t in rich_text)
            if "Tomorrow's Focus" in full_text or "Tomorrow's Top Priority" in full_text:
                lines = full_text.strip().split("\n")
                content_lines = [
                    l.strip() for l in lines
                    if l.strip()
                    and "Tomorrow's Focus" not in l
                    and "Tomorrow's Top Priority" not in l
                    and "ONE thing" not in l
                    and "makes tomorrow worthwhile" not in l
                    and "calendar event" not in l
                    and "One item only" not in l
                ]
                if content_lines:
                    return " ".join(content_lines)
        return None
    except Exception:
        return None


def get_mc_attention_items(errors: list[str]) -> tuple[list[dict], list[dict]]:
    """Return (under_review_issues, blocked_issues) from Paperclip that need Guillermo's attention.

    Queries all 3 Paperclip companies. Maps Paperclip fields to the dict keys
    expected by build_message() (title, assignees, description, status).
    """
    under_review: list[dict] = []
    blocked: list[dict] = []

    for company_name, cfg in PAPERCLIP_COMPANIES.items():
        for status_filter, target_list in [("blocked", blocked)]:
            url = f"{PAPERCLIP_API}/api/companies/{cfg['id']}/issues?status={status_filter}"
            try:
                st, payload = _http_json(
                    url,
                    headers={"Authorization": f"Bearer {cfg['token']}"},
                    timeout=10,
                )
                if st != 200:
                    continue
                issues = payload if isinstance(payload, list) else []
                for issue in issues:
                    agent_name = issue.get("executionAgentNameKey") or "unassigned"
                    target_list.append({
                        "title": issue.get("title", "?"),
                        "description": issue.get("description", ""),
                        "status": issue.get("status", ""),
                        "assignees": [agent_name],
                        "_company": company_name,
                        "_identifier": issue.get("identifier", ""),
                    })
            except Exception:
                continue

    return under_review[:5], blocked[:5]


def _get_overnight_squad_report(now: datetime) -> list[str] | None:
    """Read overnight report from consolidated log file (PLAN-008).

    Primary: /data/workspace/logs/overnight-consolidated-YYYY-MM-DD.md
    Fallback: individual agent files from /data/shared/logs/ + Molty's own log
    Last resort: MC query (original behaviour, kept as safety net)
    """
    today_str = now.strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    # Try today and yesterday (Molty cron runs at 03:00 so date may be today or yesterday)
    for date_str in [today_str, yesterday_str]:
        consolidated = f"/data/workspace/logs/overnight-consolidated-{date_str}.md"
        if os.path.exists(consolidated):
            return _parse_consolidated_log(consolidated)

    # Fallback: try individual agent files
    lines: list[str] = []
    agents = [
        ("🔴", "Raphael", f"/data/shared/logs/overnight-raphael-{today_str}.md",
                          f"/data/shared/logs/overnight-raphael-{yesterday_str}.md"),
        ("🔵", "Leonardo", f"/data/shared/logs/overnight-leonardo-{today_str}.md",
                           f"/data/shared/logs/overnight-leonardo-{yesterday_str}.md"),
        ("🦎", "Molty",   f"/data/shared/logs/overnight-molty-{today_str}.md",
                          f"/data/shared/logs/overnight-molty-{yesterday_str}.md"),
    ]
    found_any = False
    for emoji, label, path_today, path_yesterday in agents:
        for path in [path_today, path_yesterday]:
            if os.path.exists(path):
                summary = _summarise_agent_log(path, emoji, label)
                if summary:
                    lines.append(summary)
                    found_any = True
                break

    if found_any:
        return lines

    # Last resort: MC query (cannot distinguish daytime vs overnight completions)
    OVERNIGHT_HOURS = 10
    cutoff_ms = int((now.timestamp() - OVERNIGHT_HOURS * 3600) * 1000)
    status_code, payload = _http_json(
        f"{MC_API}/api/tasks",
        headers={"Authorization": f"Bearer {MC_KEY}"},
        timeout=10,
    )
    if status_code != 200 or not payload:
        return None
    tasks = payload if isinstance(payload, list) else payload.get("tasks", [])
    overnight = [t for t in tasks if (t.get("updatedAt") or 0) >= cutoff_ms]
    if not overnight:
        return None
    AGENT_INFO = {
        "raphael":  ("🔴", "Raphael"),
        "leonardo": ("🔵", "Leonardo"),
        "molty":    ("🦎", "Molty"),
    }
    mc_lines: list[str] = []
    for agent_id, (emoji, label) in AGENT_INFO.items():
        agent_tasks = [t for t in overnight if agent_id in t.get("assignees", [])]
        if not agent_tasks:
            continue
        done    = [t for t in agent_tasks if t.get("status") == "done"]
        review  = [t for t in agent_tasks if t.get("status") == "review"]
        blocked = [t for t in agent_tasks if t.get("status") == "blocked"]
        parts: list[str] = []
        if done:
            titles = ", ".join(t["title"][:35] for t in done[:3])
            parts.append(f"✅ {titles}" + (" +" + str(len(done) - 3) + " more" if len(done) > 3 else ""))
        if review:
            titles = ", ".join(t["title"][:35] for t in review[:2])
            parts.append(f"👀 {titles} — needs your review")
        if blocked:
            titles = ", ".join(t["title"][:35] for t in blocked[:2])
            parts.append(f"🚧 {titles} — blocked")
        if parts:
            mc_lines.append(f"{emoji} {label}: " + " | ".join(parts))
    return mc_lines if mc_lines else None


def _parse_consolidated_log(path: str) -> list[str] | None:
    """Parse the consolidated overnight log into briefing lines."""
    try:
        with open(path) as f:
            content = f.read()
        lines: list[str] = []
        current_agent = None
        completed, review, flagged = [], [], []

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## 🔴"):
                if current_agent:
                    lines.extend(_format_agent_summary(current_agent, completed, review, flagged))
                current_agent, completed, review, flagged = line[3:].strip(), [], [], []
            elif line.startswith("## 🔵"):
                if current_agent:
                    lines.extend(_format_agent_summary(current_agent, completed, review, flagged))
                current_agent, completed, review, flagged = line[3:].strip(), [], [], []
            elif line.startswith("## 🦎"):
                if current_agent:
                    lines.extend(_format_agent_summary(current_agent, completed, review, flagged))
                current_agent, completed, review, flagged = line[3:].strip(), [], [], []
            elif line.startswith("## ✅") or "Completed" in line:
                pass  # section marker
            elif line.startswith("## 👀") or "Under Review" in line:
                pass
            elif line.startswith("## 🚩") or "Flagged" in line:
                pass
            elif line.startswith("- ") and current_agent:
                item = line[2:].strip()
                if "→ needs:" in item or "needs your review" in item.lower():
                    review.append(item)
                elif "→" in item and not item.startswith("No summary"):
                    completed.append(item)
                else:
                    flagged.append(item)

        if current_agent:
            lines.extend(_format_agent_summary(current_agent, completed, review, flagged))

        return lines if lines else None
    except Exception:
        return None


def _format_agent_summary(agent: str, completed: list, review: list, flagged: list) -> list[str]:
    """Format one agent's overnight summary into briefing lines."""
    parts = []
    if completed:
        parts.append(f"✅ {len(completed)} done")
    if review:
        titles = ", ".join(r.split("→")[0].strip()[:35] for r in review[:2])
        parts.append(f"👀 {titles} — needs your review")
    if flagged:
        parts.append(f"🚩 {len(flagged)} flagged")
    if not parts:
        return []
    return [f"{agent}: " + " | ".join(parts)]


def _summarise_agent_log(path: str, emoji: str, label: str) -> str | None:
    """Read an individual agent overnight log and return a one-line summary.
    
    Handles new v2.1 log format:
    ## ✅ Completed / ## 👀 Under Review / ## ❌ Failed / ## 🚧 Blocked / ## ⏭ Skipped
    """
    try:
        with open(path) as f:
            content = f.read()
        completed, review, failed, blocked = 0, [], [], []
        section = None
        for line in content.split("\n"):
            line = line.strip()
            if line == "---":
                section = None
                continue
            if line.startswith("## ✅") or "Completed" in line and line.startswith("##"):
                section = "done"
            elif line.startswith("## 👀") or "Under Review" in line and line.startswith("##"):
                section = "review"
            elif line.startswith("## ❌") or "Failed" in line and line.startswith("##"):
                section = "failed"
            elif line.startswith("## 🚧") or "Blocked" in line and line.startswith("##"):
                section = "blocked"
            elif line.startswith("## ⏭") or "Skipped" in line and line.startswith("##"):
                section = "skipped"
            elif line.startswith("## ") or line.startswith("### "):
                section = None
            elif line.startswith("- ") and section:
                item = line[2:].strip()
                if item.lower() in ("none", "(none)", ""):
                    continue
                if section == "done":
                    completed += 1
                elif section == "review":
                    # Extract title before any "→" context
                    review.append(item.split("→")[0].strip()[:40])
                elif section == "failed":
                    # Extract why it failed
                    failed.append(item[:60])
                elif section == "blocked":
                    # Extract the blocker ask
                    blocked.append(item[:60])
        parts = []
        if completed:
            parts.append(f"✅ {completed} done")
        if review:
            parts.append(f"👀 {', '.join(review[:2])} — needs your review")
        if failed:
            parts.append(f"❌ {len(failed)} failed")
        if blocked:
            parts.append(f"🚧 {len(blocked)} blocked")
        if not parts:
            return None
        return f"{emoji} {label}: " + " | ".join(parts)
    except Exception:
        return None


def _get_active_plans() -> list[str] | None:
    """Scan plans/ folder for active plans (Status: Ready|in_progress|active).
    
    Returns list of plan titles that should be surfaced in morning briefing.
    """
    import glob
    plans_dir = "/data/workspace/plans"
    active_plans = []
    
    try:
        for f in glob.glob(os.path.join(plans_dir, "*.md")):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    content = fp.read(2000)  # Read first 2KB only
                
                # Check for active status markers
                if any(marker in content.lower() for marker in [
                    "status:** ready",
                    "status:** in progress",
                    "status:** in_progress", 
                    "status:** active",
                    "status: ready",
                    "status: in progress",
                    "status: in_progress",
                    "status: active",
                ]):
                    # Extract title from first # heading
                    lines = content.split("\n")
                    title = None
                    for line in lines[:10]:
                        if line.startswith("# "):
                            title = line[2:].strip()
                            break
                    if title:
                        active_plans.append(title)
            except Exception:
                continue
        
        return active_plans if active_plans else None
    except Exception:
        return None


def _get_openclaw_update_summary() -> str | None:
    """Check actual OpenClaw update status by running `openclaw update status`.
    
    Returns a concise status line for the briefing.
    Compares available version against BOTH the local install AND the fleet's
    deployed version (from MEMORY.md) to avoid false "update available" when
    the fleet already deployed the newer version.
    """
    import re
    try:
        result = subprocess.run(
            ["openclaw", "update", "status"],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout + result.stderr
        
        # Parse the output for update status
        if "Update available" in output or "npm update" in output:
            # Extract available version number
            match = re.search(r'npm update (\d+\.\d+\.\d+)', output)
            if not match:
                return "Update available"
            available_version = match.group(1)
            
            # Get the fleet's deployed version from MEMORY.md
            fleet_version = _get_fleet_version_from_memory()
            
            # If fleet is already on this version (or newer), it's up to date
            if fleet_version and _version_gte(fleet_version, available_version):
                return None  # Fleet already deployed this version
            
            return f"Update available: v{available_version}"
        elif "up to date" in output.lower() or "deps ok" in output:
            # Check if actually on latest
            if "available" not in output.lower():
                return None  # Will show "Up to date ✅"
        return None
    except Exception:
        return None


def _get_fleet_version_from_memory() -> str | None:
    """Extract the fleet's deployed version from MEMORY.md."""
    import re
    memory_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MEMORY.md")
    try:
        with open(memory_path, "r") as f:
            text = f.read()
        # Match patterns like "v2026.3.13 (deployed" or "Version:** v2026.3.13"
        match = re.search(r'v(\d+\.\d+\.\d+)\s*\(deployed', text)
        if match:
            return match.group(1)
        # Fallback: look for "Version:" line in fleet table
        match = re.search(r'\*\*Version:\*\*\s*v(\d+\.\d+\.\d+)', text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def _version_gte(version_a: str, version_b: str) -> bool:
    """Return True if version_a >= version_b (dotted numeric comparison)."""
    try:
        parts_a = [int(x) for x in version_a.split(".")]
        parts_b = [int(x) for x in version_b.split(".")]
        return parts_a >= parts_b
    except (ValueError, AttributeError):
        return False


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
    squad: SquadStatus | None,
    errors: list[str],
    yesterdays_focus: str | None = None,
    mc_under_review: list[dict] | None = None,
    mc_blocked: list[dict] | None = None,
) -> str:
    """Build a readable morning briefing with full context.
    
    Format (v3.3 — Mar 13 2026):
    Bold headers, full descriptions, weather outlook, no truncation.
    """
    today = now.date()
    lines: list[str] = []

    # Noise patterns to filter
    NOISE_PATTERNS = [
        "mayleen", "mie", "helper", "domestic",
        "busy", "focus time", "deep work", "block",
        "school drop", "drop-off", "pickup", "pick-up",
        "desk work", "admin", "lunch break",
    ]

    # Header with weather + outlook
    weather_line = f"☀️ **{_fmt_day(today)}**"
    if weather and weather.today.tmin is not None and weather.today.tmax is not None:
        temp = f"{int(round(weather.today.tmin))}-{int(round(weather.today.tmax))}°C"
        rain_days = [d for d in weather.outlook_3d if d.rain_prob_max and d.rain_prob_max >= 50]
        if rain_days:
            weather_line += f" · {temp}, rain likely {rain_days[0].day.strftime('%a')}"
        elif weather.today.rain_prob_max and weather.today.rain_prob_max >= 30:
            weather_line += f" · {temp}, {weather.today.rain_prob_max}% rain"
        else:
            weather_line += f" · {temp}"
    lines.append(weather_line)
    lines.append("")

    # Blocked items — full readable descriptions
    if mc_blocked:
        lines.append("🚧 **Blocked**")
        for t in mc_blocked[:4]:
            assignees = t.get("assignees", [])
            owner = assignees[0].title() if assignees else ""
            title = t.get("title", "?")
            desc = t.get("description", "")
            summary = _make_blocker_readable(title, desc, owner)
            lines.append(f"→ {summary}")
        lines.append("")

    # Under review — meaningful descriptions
    if mc_under_review:
        lines.append("👀 **Review**")
        for t in mc_under_review[:4]:
            title = t.get("title", "?")
            readable = _make_title_readable(title)
            lines.append(f"→ {readable}")
        lines.append("")

    # Calendar — full event names
    filtered_events = []
    for ev in todays_events:
        if ev.all_day:
            continue
        summary_lower = ev.summary.lower()
        if any(noise in summary_lower for noise in NOISE_PATTERNS):
            continue
        filtered_events.append(ev)
    
    lines.append("📅 **Today**")
    if filtered_events:
        for ev in filtered_events[:5]:
            t = _fmt_hhmm(ev.start) if ev.start else "?"
            lines.append(f"→ {ev.summary} {t}")
    else:
        lines.append("→ Clear day")
    lines.append("")

    # Coming up — notable events only
    notable = _get_notable_upcoming_filtered(upcoming_events, tasks_upcoming, today, NOISE_PATTERNS)
    if notable:
        lines.append("🔜 **Coming up**")
        lines.append(f"→ {notable}")
        lines.append("")

    # OpenClaw status
    update_summary = _get_openclaw_update_summary()
    if update_summary and "Update available" in update_summary:
        lines.append(f"🔧 {update_summary}")
        lines.append("   Reply /update to install")
    
    # Errors
    critical_errors = [e for e in errors if "unavailable" not in e.lower()]
    if critical_errors:
        lines.append("")
        lines.append("⚠️ " + "; ".join(critical_errors[:2]))

    return "\n".join(lines).strip() + "\n"


def _make_blocker_readable(title: str, desc: str, owner: str) -> str:
    """Convert blocked task to human-readable summary."""
    title_lower = title.lower()
    
    if "waiting" in title_lower:
        if "proposal" in title_lower or "proposal" in desc.lower():
            return f"{owner}: Needs live proposal deck from you"
        if "template" in title_lower:
            return f"{owner}: Needs template from you"
        parts = title.split(":")
        if len(parts) > 1:
            return f"{owner}: {parts[-1].strip()}"
    
    if "research" in title_lower:
        return f"{owner}: Research pending your review"
    
    if title_lower[:1].isalpha() and len(title) > 2 and title[1].isdigit():
        if "proposal" in title_lower or "proposal" in desc.lower():
            return f"{owner}: Needs live proposal deck"
    
    if owner:
        return f"{owner}: {title[:50]}"
    return title[:60]


def _make_title_readable(title: str) -> str:
    """Convert task title to human-readable format."""
    title_lower = title.lower()
    
    if "tmnt" in title_lower and "article" in title_lower:
        return "TMNT Agent Management article"
    if "ginesta.io" in title_lower or "personal website" in title_lower:
        return "Ginesta.io website brief"
    if "crm" in title_lower and "pipeline" in title_lower:
        return "Cerebro CRM Pipelines Phase B"
    if "brief" in title_lower and "plan" in title_lower:
        return "Website brief and plan"
    
    for prefix in ["Write ", "Create ", "Build ", "Design "]:
        if title.startswith(prefix):
            title = title[len(prefix):]
    
    return title[:55] if len(title) > 55 else title



def _get_notable_upcoming(
    upcoming_events: list[CalEvent],
    tasks_upcoming: list[Task],
    today: date,
) -> str | None:
    """Legacy function — use _get_notable_upcoming_filtered instead."""
    return _get_notable_upcoming_filtered(upcoming_events, tasks_upcoming, today, [])


def _get_notable_upcoming_filtered(
    upcoming_events: list[CalEvent],
    tasks_upcoming: list[Task],
    today: date,
    noise_patterns: list[str],
) -> str | None:
    """Return a single-line heads-up for the next 5 days, filtering noise.
    
    Only shows: birthdays, travel, external meetings, P1 deadlines.
    """
    notable = []
    
    for ev in upcoming_events[:15]:
        if not ev.start:
            continue
        
        summary_lower = ev.summary.lower()
        
        # Skip noise events
        if any(noise in summary_lower for noise in noise_patterns):
            continue
        
        d = ev.start.astimezone(HKT).date()
        day_label = d.strftime("%a")
        
        # Only truly notable: birthdays, travel, dinners, external meetings
        is_notable = any(kw in summary_lower for kw in [
            "birthday", "anniversary", 
            "flight", "travel", "trip",
            "dinner", "lunch with", "drinks",
            "doctor", "dentist", "appointment",
        ])
        
        if is_notable:
            t = _fmt_hhmm(ev.start) if not ev.all_day else ""
            short_summary = _smart_truncate(ev.summary, 20)
            notable.append(f"{day_label}: {short_summary}" + (f" {t}" if t else ""))
            if len(notable) >= 2:
                break
    
    # Also check P1 tasks due soon
    for t in tasks_upcoming[:5]:
        if t.priority == 4:  # P1
            dd = t.due_dt.astimezone(HKT).date() if t.due_dt else t.due_date
            if dd and dd > today:
                day_label = dd.strftime("%a")
                notable.append(f"{day_label}: P1 {_smart_truncate(t.content, 18)}")
                if len(notable) >= 2:
                    break
    
    if not notable:
        return None
    
    return ", ".join(notable[:2])

# -----------------------------
# Deduplication
# -----------------------------

def _dedup_events(events: list[CalEvent]) -> list[CalEvent]:
    """Remove duplicate events (same summary + start time) across calendars.
    
    If the same event appears in multiple calendars, merge the calendar labels.
    """
    seen: dict[tuple, CalEvent] = {}
    out: list[CalEvent] = []
    for ev in events:
        key = (ev.summary, ev.start)
        if key in seen:
            existing = seen[key]
            if ev.calendar_label not in existing.calendar_label:
                existing.calendar_label = f"{existing.calendar_label} + {ev.calendar_label}"
        else:
            seen[key] = ev
            out.append(ev)
    return out


# -----------------------------
# Main
# -----------------------------

def main() -> int:
    ensure_gog_setup()
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
    todays_events = _dedup_events(todays_events)

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
    upcoming_events = _dedup_events(upcoming_events)

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

    # Squad status from Mission Control
    squad = get_squad_status(errors)

    # Yesterday's Focus + MC attention items
    yesterdays_focus = get_yesterdays_focus(today)
    mc_under_review, mc_blocked = get_mc_attention_items(errors)

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
        squad=squad,
        errors=errors,
        yesterdays_focus=yesterdays_focus,
        mc_under_review=mc_under_review,
        mc_blocked=mc_blocked,
    )

    sys.stdout.write(msg)

    # ── Fleet update report (sent as separate Telegram message after briefing) ──
    _send_fleet_update_report_if_pending()

    return 0


def _send_fleet_update_report_if_pending():
    """
    If fleet-update.py ran since last briefing, build and send a separate
    Telegram message to Guillermo with version, highlights, and incorporation plan.
    Clears the report file after sending so it doesn't repeat.
    """
    import subprocess
    REPORT_FILE = "/data/workspace/state/fleet-update-report.json"
    TELEGRAM_GUILLERMO = "1097408992"

    if not os.path.exists(REPORT_FILE):
        return

    try:
        with open(REPORT_FILE) as f:
            report = json.load(f)
    except Exception:
        return

    # Only send if not already sent (sent_at field is absent or empty)
    if report.get("sent_at"):
        return  # already delivered — skip

    version = report.get("version", "?")
    results = report.get("results", {})
    highlights = report.get("highlights", [])
    incorporation = report.get("incorporation", [])
    is_critical = report.get("is_critical", False)
    all_ok = report.get("all_ok", False)

    emoji = "🚨" if is_critical else "📦"
    status = "✅ All agents updated" if all_ok else "⚠️ Partial update — check #command-center"

    agent_lines = []
    for agent, result in results.items():
        icons = {"molty": "🦎", "raphael": "🔴", "leonardo": "🔵"}
        agent_lines.append(f"{icons.get(agent, '•')} {agent}: {result}")

    lines = [
        f"{emoji} OpenClaw {version} — {status}",
        "",
        *agent_lines,
    ]

    if highlights:
        lines += ["", "What's new (TMNT-relevant):"]
        for h in highlights[:5]:
            lines.append(f"• {h[:100]}")

    if incorporation:
        lines += ["", "How we're using it:"]
        for i in incorporation:
            lines.append(f"• {i}")

    msg = "\n".join(lines)

    try:
        subprocess.run(
            ["openclaw", "message", "send", "--channel", "telegram",
             "--target", TELEGRAM_GUILLERMO, "-m", msg],
            capture_output=True, timeout=20
        )
        # Mark sent so it won't re-send on next briefing
        report["sent_at"] = datetime.now().isoformat()
        with open(REPORT_FILE, "w") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        print(f"[fleet-report] Telegram send failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
