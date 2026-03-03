#!/data/workspace/.venv/bin/python3
"""
standup_status_reader.py — Read agent pre-standup status replies from shared files.

Agents write their status to /data/shared/logs/standup-status-{DATE}-{agent}.txt
This helper reads those files and returns formatted text for the standup page callout.

Used by: daily_standup.py at 5PM generation time.
Written to by: Raphael + Leonardo after receiving the 4:30 PM webhook ping.
Also written by: Molty main session when it receives a status reply webhook.
"""

import os
from datetime import datetime, timedelta, timezone

HKT = timezone(timedelta(hours=8))

AGENTS = {
    "raphael":  "🔴 Raphael",
    "leonardo": "🔵 Leonardo",
}


def read_agent_status(date_str: str | None = None) -> dict[str, str]:
    """
    Read pre-standup status files for all agents.
    Returns dict: agent_name → status_text (or fallback message).
    """
    if date_str is None:
        date_str = datetime.now(HKT).strftime("%Y-%m-%d")

    results = {}
    for agent, label in AGENTS.items():
        path = f"/data/shared/logs/standup-status-{date_str}-{agent}.txt"
        if os.path.exists(path):
            try:
                content = open(path).read().strip()
                if content:
                    results[agent] = content
                    print(f"  ✅ {label}: status file found")
                else:
                    results[agent] = None
            except Exception:
                results[agent] = None
        else:
            results[agent] = None

    return results


def format_squad_status(date_str: str | None = None) -> str:
    """
    Return a formatted squad status block for the standup callout.
    Example:
        🔴 Raphael: Completed brand audit + proposal test. Blocked on GCP SA JSON.
        🔵 Leonardo: Marketing Strategy v2 under review. Blocked on beta list + Stripe keys.
    """
    statuses = read_agent_status(date_str)
    lines = []
    for agent, label in AGENTS.items():
        status = statuses.get(agent)
        if status:
            # Trim to 200 chars for callout
            short = status[:200] + ("…" if len(status) > 200 else "")
            lines.append(f"{label}: {short}")
        else:
            lines.append(f"{label}: no pre-standup update received")
    return "\n".join(lines)


def write_agent_status(agent: str, content: str, date_str: str | None = None) -> bool:
    """
    Write a status update for an agent. Called by Molty main session when
    a webhook reply arrives from Raphael or Leonardo.

    agent: "raphael" or "leonardo"
    content: the status text
    """
    if date_str is None:
        date_str = datetime.now(HKT).strftime("%Y-%m-%d")
    if agent not in AGENTS:
        return False
    path = f"/data/shared/logs/standup-status-{date_str}-{agent}.txt"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w") as f:
            f.write(content.strip())
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Debug: print today's status
    today = datetime.now(HKT).strftime("%Y-%m-%d")
    print(f"Pre-standup status — {today}")
    print(format_squad_status(today))
