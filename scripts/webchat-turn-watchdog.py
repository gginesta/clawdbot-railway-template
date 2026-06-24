#!/usr/bin/env python3
"""Detect WebChat turns lost by Gateway/container restarts and alert Guillermo."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path(os.environ.get("OPENCLAW_STATE_DIR", "/data/.openclaw"))
DEFAULT_WORKSPACE_DIR = Path(os.environ.get("OPENCLAW_WORKSPACE_DIR", "/data/workspace"))
DEFAULT_STATE_FILE = DEFAULT_WORKSPACE_DIR / ".webchat-turn-watchdog-state.json"
DEFAULT_LOG_FILE = DEFAULT_WORKSPACE_DIR / "logs" / "webchat-turn-watchdog.log"
DEFAULT_SESSIONS_DIR = DEFAULT_STATE_DIR / "agents" / "main" / "sessions"
DEFAULT_SCAN_LOOKBACK_SECONDS = int(os.environ.get("WEBCHAT_WATCHDOG_SCAN_LOOKBACK_SECONDS", "86400"))
ERROR_NEEDLE = "client closed before turn completed"


@dataclass(frozen=True)
class LostTurn:
    event_id: str
    ts_ms: int
    ts_iso: str
    session_key: str
    session_id: str
    run_id: str
    prompt_error: str


def now_ms() -> int:
    return int(time.time() * 1000)


def parse_ts_ms(ts: str | None) -> int:
    if not ts:
        return 0
    normalized = ts.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return 0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def load_state(path: Path, initial_lookback_seconds: int) -> dict[str, Any]:
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if isinstance(data, dict):
                data.setdefault("processed", [])
                return data
        except Exception:
            pass
    return {
        "last_scan_ms": max(0, now_ms() - initial_lookback_seconds * 1000),
        "processed": [],
    }


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n")
    tmp.replace(path)


def log_line(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with path.open("a") as fh:
        fh.write(f"[{ts}] {message}\n")


def iter_candidate_trajectories(sessions_dir: Path, since_ms: int) -> list[Path]:
    cutoff = since_ms / 1000
    if not sessions_dir.exists():
        return []
    paths: list[Path] = []
    for path in sessions_dir.glob("*.trajectory.jsonl"):
        try:
            if path.stat().st_mtime >= cutoff:
                paths.append(path)
        except OSError:
            continue
    return sorted(paths, key=lambda p: p.stat().st_mtime)


def scan_trajectory(path: Path, since_ms: int, processed: set[str]) -> list[LostTurn]:
    lost: list[LostTurn] = []
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return lost
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "session.ended":
            continue
        data = event.get("data")
        if not isinstance(data, dict):
            continue
        prompt_error = str(data.get("promptError") or "")
        if ERROR_NEEDLE not in prompt_error:
            continue
        session_key = str(event.get("sessionKey") or "")
        if ":dashboard:" not in session_key:
            continue
        ts_iso = str(event.get("ts") or "")
        ts_ms = parse_ts_ms(ts_iso)
        if ts_ms and ts_ms < since_ms:
            continue
        event_id = f"{event.get('traceId')}:{event.get('runId')}:{event.get('seq')}"
        if event_id in processed:
            continue
        lost.append(
            LostTurn(
                event_id=event_id,
                ts_ms=ts_ms or now_ms(),
                ts_iso=ts_iso,
                session_key=session_key,
                session_id=str(event.get("sessionId") or ""),
                run_id=str(event.get("runId") or ""),
                prompt_error=prompt_error,
            )
        )
    return lost


def mark_session_interrupted(sessions_json: Path, lost: LostTurn) -> bool:
    try:
        store = json.loads(sessions_json.read_text())
    except Exception:
        return False
    entry = store.get(lost.session_key)
    if not isinstance(entry, dict):
        return False
    entry["abortedLastRun"] = True
    entry["updatedAt"] = max(int(entry.get("updatedAt") or 0), now_ms())
    entry["lastRestartInterruptedRunId"] = lost.run_id
    store[lost.session_key] = entry
    tmp = sessions_json.with_suffix(sessions_json.suffix + ".webchat-watchdog.tmp")
    tmp.write_text(json.dumps(store, sort_keys=False, indent=2) + "\n")
    tmp.replace(sessions_json)
    return True


def alert_message(lost: LostTurn, marked: bool) -> str:
    hkt = time.strftime(
        "%Y-%m-%d %H:%M:%S HKT",
        time.gmtime((lost.ts_ms / 1000) + 8 * 3600),
    )
    marker = "marked interrupted" if marked else "could not mark session"
    return (
        "Molty WebChat watchdog: a WebChat turn was interrupted by a restart before I could reply.\n"
        f"- Time: {hkt}\n"
        f"- Session: {lost.session_key}\n"
        f"- Run: {lost.run_id}\n"
        f"- Recovery: {marker}\n"
        "Please resend the last instruction in WebChat if I have not already resumed it."
    )


def send_telegram(message: str) -> tuple[bool, str]:
    cmd = [
        "openclaw",
        "message",
        "send",
        "--channel",
        "telegram",
        "--target",
        os.environ.get("WEBCHAT_WATCHDOG_TELEGRAM_TARGET", "1097408992"),
        "--message",
        message,
    ]
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=30, check=False)
    except Exception as exc:
        return False, str(exc)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def scan_once(args: argparse.Namespace) -> int:
    state = load_state(args.state_file, args.initial_lookback_seconds)
    processed = set(str(x) for x in state.get("processed", []) if x)
    since_ms = int(state.get("last_scan_ms") or 0)
    scan_since_ms = max(0, since_ms - max(0, args.scan_lookback_seconds) * 1000)
    found: list[LostTurn] = []
    for path in iter_candidate_trajectories(args.sessions_dir, scan_since_ms):
        found.extend(scan_trajectory(path, scan_since_ms, processed))
    max_seen = max([since_ms, now_ms() - 60_000, *[turn.ts_ms for turn in found]])
    for lost in found:
        marked = False if args.dry_run else mark_session_interrupted(args.sessions_dir / "sessions.json", lost)
        message = alert_message(lost, marked)
        if args.no_alert or args.dry_run:
            ok, output = True, "alert suppressed"
        else:
            ok, output = send_telegram(message)
        log_line(
            args.log_file,
            f"lost_turn event_id={lost.event_id} session_key={lost.session_key} marked={marked} alert_ok={ok} output={output[:500]!r}",
        )
        if ok:
            processed.add(lost.event_id)
        else:
            log_line(args.log_file, f"lost_turn_retry_pending event_id={lost.event_id}")
    state["last_scan_ms"] = max_seen
    state["processed"] = sorted(processed)[-200:]
    save_state(args.state_file, state)
    return len(found)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-dir", type=Path, default=DEFAULT_SESSIONS_DIR)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    parser.add_argument("--log-file", type=Path, default=DEFAULT_LOG_FILE)
    parser.add_argument("--interval-seconds", type=int, default=int(os.environ.get("WEBCHAT_WATCHDOG_INTERVAL_SECONDS", "60")))
    parser.add_argument("--initial-lookback-seconds", type=int, default=int(os.environ.get("WEBCHAT_WATCHDOG_INITIAL_LOOKBACK_SECONDS", "900")))
    parser.add_argument("--scan-lookback-seconds", type=int, default=DEFAULT_SCAN_LOOKBACK_SECONDS)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--no-alert", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Scan without mutating session state or sending alerts")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.log_file.parent.mkdir(parents=True, exist_ok=True)
    log_line(args.log_file, f"starting loop={args.loop} sessions_dir={args.sessions_dir}")
    while True:
        try:
            scan_once(args)
        except Exception as exc:
            log_line(args.log_file, f"ERROR {exc!r}")
        if not args.loop:
            return 0
        time.sleep(max(10, args.interval_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
