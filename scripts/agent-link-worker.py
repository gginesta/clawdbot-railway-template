#!/usr/bin/env python3
"""
Agent-Link v2 Worker
====================
Reliable agent-to-agent communication for TMNT fleet.

Features:
- tmnt-v1 envelope format for trusted messages
- Persistent queue with retry backoff
- Health-aware routing
- ACK confirmation
- Full delivery logging

Usage:
  python3 agent-link-worker.py send <to> <type> <message> [--priority p1] [--reply-to discord:channel_id]
  python3 agent-link-worker.py process-queue
  python3 agent-link-worker.py check-health
  python3 agent-link-worker.py update-health <agent> <status>
"""

import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Paths
QUEUE_DIR = Path("/data/workspace/state/agent-queue")
PENDING_DIR = QUEUE_DIR / "pending"
DELIVERED_DIR = QUEUE_DIR / "delivered"
FAILED_DIR = QUEUE_DIR / "failed"
HEALTH_DIR = Path("/data/shared/health")
LOG_FILE = Path("/data/shared/logs/agent-link-deliveries.log")
TOKEN_FILE = Path("/data/shared/credentials/agent-link-token.txt")

# Agent directory
AGENTS = {
    "molty": {
        "webhook": "https://ggvmolt.up.railway.app/hooks/agent",
        "token": "ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562",
    },
    "raphael": {
        "webhook": "https://ggv-raphael.up.railway.app/hooks/agent",
        "token": "ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd",
    },
    "leonardo": {
        "webhook": "https://leonardo-production.up.railway.app/hooks/agent",
        "token": "08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758",
    },
    "april": {
        "webhook": "https://april-agent-production.up.railway.app/hooks/agent",
        "token": "7159178afb1c2c24b1e98bbbac0f0f02dc759aa038cd49ae7fac7873d8acf3ee",
    },
}

# Retry backoff schedule (seconds)
RETRY_SCHEDULE = [30, 120, 600, 3600]  # 30s, 2m, 10m, 1h

# Health threshold (seconds)
HEALTH_THRESHOLD = 600  # 10 minutes


def log_delivery(from_agent: str, to_agent: str, msg_type: str, msg_id: str, status: str, extra: str = ""):
    """Append to delivery log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{timestamp} | FROM={from_agent} TO={to_agent} TYPE={msg_type} ID={msg_id} STATUS={status}"
    if extra:
        line += f" {extra}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_health(agent: str) -> dict:
    """Get agent health status."""
    health_file = HEALTH_DIR / f"{agent}.json"
    if not health_file.exists():
        return {"agent": agent, "status": "unknown", "last_seen": None}
    try:
        with open(health_file) as f:
            return json.load(f)
    except Exception:
        return {"agent": agent, "status": "error", "last_seen": None}


def update_health(agent: str, status: str):
    """Update agent health status."""
    health_file = HEALTH_DIR / f"{agent}.json"
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Load existing data or create new
    if health_file.exists():
        try:
            with open(health_file) as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}
    
    data["agent"] = agent
    data["status"] = status
    data["last_seen"] = now
    if agent in AGENTS:
        data["webhook_url"] = AGENTS[agent]["webhook"]
    
    HEALTH_DIR.mkdir(parents=True, exist_ok=True)
    with open(health_file, "w") as f:
        json.dump(data, f, indent=2)


def is_healthy(agent: str) -> bool:
    """Check if agent is healthy (responded within threshold)."""
    health = get_health(agent)
    if health.get("status") == "down":
        return False
    last_seen = health.get("last_seen")
    if not last_seen:
        return False
    try:
        last_dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
        now = datetime.now(last_dt.tzinfo)
        return (now - last_dt).total_seconds() < HEALTH_THRESHOLD
    except Exception:
        return False


def create_envelope(
    from_agent: str,
    to_agent: str,
    msg_type: str,
    message: str,
    priority: str = "p2",
    sensitivity: str = "internal",
    reply_to: Optional[dict] = None,
    context: Optional[dict] = None,
) -> dict:
    """Create a tmnt-v1 envelope."""
    msg_id = str(uuid.uuid4())[:12]
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    envelope = {
        "envelope": "tmnt-v1",
        "from": from_agent,
        "to": to_agent,
        "type": msg_type,
        "priority": priority,
        "sensitivity": sensitivity,
        "sent_at": now,
        "message_id": msg_id,
        "payload": {
            "message": message,
        },
    }
    
    if reply_to:
        envelope["reply_to"] = reply_to
    
    if context:
        envelope["payload"]["context"] = context
    
    return envelope


def send_webhook(agent: str, envelope: dict, timeout: int = 15) -> tuple[bool, str]:
    """Send envelope to agent via webhook. Returns (success, error_message)."""
    if agent not in AGENTS:
        return False, f"Unknown agent: {agent}"
    
    url = AGENTS[agent]["webhook"]
    token = AGENTS[agent]["token"]
    
    # Wrap envelope in message field for webhook handler
    payload = {
        "message": json.dumps(envelope),
        "wakeMode": "now"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                return True, ""
            return False, result.get("error", "Unknown error")
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"URL error: {e.reason}"
    except TimeoutError:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def queue_message(envelope: dict):
    """Save message to pending queue."""
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    msg_id = envelope["message_id"]
    queue_entry = {
        **envelope,
        "_queue": {
            "attempts": 0,
            "last_attempt": None,
            "next_retry": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    }
    with open(PENDING_DIR / f"{msg_id}.json", "w") as f:
        json.dump(queue_entry, f, indent=2)


def send_message(
    to_agent: str,
    msg_type: str,
    message: str,
    from_agent: str = "molty",
    priority: str = "p2",
    sensitivity: str = "internal",
    reply_to: Optional[dict] = None,
    context: Optional[dict] = None,
    queue_on_fail: bool = True,
) -> tuple[bool, str, str]:
    """
    Send a message to another agent.
    Returns (success, message_id, error).
    """
    envelope = create_envelope(
        from_agent=from_agent,
        to_agent=to_agent,
        msg_type=msg_type,
        message=message,
        priority=priority,
        sensitivity=sensitivity,
        reply_to=reply_to,
        context=context,
    )
    msg_id = envelope["message_id"]
    
    # Check health first
    if not is_healthy(to_agent):
        if queue_on_fail:
            queue_message(envelope)
            log_delivery(from_agent, to_agent, msg_type, msg_id, "queued", "REASON=unhealthy")
            return False, msg_id, "Agent unhealthy, queued for retry"
        return False, msg_id, "Agent unhealthy"
    
    # Try to send
    success, error = send_webhook(to_agent, envelope)
    
    if success:
        # Mark as delivered
        DELIVERED_DIR.mkdir(parents=True, exist_ok=True)
        envelope["_delivered_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(DELIVERED_DIR / f"{msg_id}.json", "w") as f:
            json.dump(envelope, f, indent=2)
        log_delivery(from_agent, to_agent, msg_type, msg_id, "delivered")
        update_health(to_agent, "up")
        return True, msg_id, ""
    else:
        if queue_on_fail:
            queue_message(envelope)
            log_delivery(from_agent, to_agent, msg_type, msg_id, "queued", f"REASON={error}")
            return False, msg_id, f"Failed: {error}, queued for retry"
        return False, msg_id, error


def process_queue():
    """Process pending messages, retry as needed."""
    if not PENDING_DIR.exists():
        return {"processed": 0, "delivered": 0, "failed": 0, "waiting": 0}
    
    now = datetime.utcnow()
    stats = {"processed": 0, "delivered": 0, "failed": 0, "waiting": 0}
    
    for msg_file in PENDING_DIR.glob("*.json"):
        stats["processed"] += 1
        
        try:
            with open(msg_file) as f:
                entry = json.load(f)
        except Exception as e:
            print(f"Error reading {msg_file}: {e}")
            continue
        
        queue_info = entry.get("_queue", {})
        attempts = queue_info.get("attempts", 0)
        next_retry_str = queue_info.get("next_retry")
        
        # Check if it's time to retry
        if next_retry_str:
            try:
                next_retry = datetime.fromisoformat(next_retry_str.replace("Z", "+00:00"))
                if now < next_retry.replace(tzinfo=None):
                    stats["waiting"] += 1
                    continue
            except Exception:
                pass
        
        to_agent = entry.get("to")
        msg_type = entry.get("type")
        msg_id = entry.get("message_id")
        from_agent = entry.get("from", "molty")
        
        # Try to send
        success, error = send_webhook(to_agent, entry)
        
        if success:
            # Move to delivered
            DELIVERED_DIR.mkdir(parents=True, exist_ok=True)
            entry["_delivered_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            del entry["_queue"]
            with open(DELIVERED_DIR / f"{msg_id}.json", "w") as f:
                json.dump(entry, f, indent=2)
            msg_file.unlink()
            log_delivery(from_agent, to_agent, msg_type, msg_id, "delivered", f"ATTEMPT={attempts+1}")
            update_health(to_agent, "up")
            stats["delivered"] += 1
        else:
            # Update retry info
            attempts += 1
            if attempts >= len(RETRY_SCHEDULE):
                # Max retries exceeded, move to failed
                FAILED_DIR.mkdir(parents=True, exist_ok=True)
                entry["_failed_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                entry["_queue"]["attempts"] = attempts
                entry["_queue"]["last_error"] = error
                with open(FAILED_DIR / f"{msg_id}.json", "w") as f:
                    json.dump(entry, f, indent=2)
                msg_file.unlink()
                log_delivery(from_agent, to_agent, msg_type, msg_id, "failed", f"ATTEMPTS={attempts} ERROR={error}")
                stats["failed"] += 1
            else:
                # Schedule next retry
                delay = RETRY_SCHEDULE[attempts - 1] if attempts > 0 else RETRY_SCHEDULE[0]
                next_retry = now + timedelta(seconds=delay)
                entry["_queue"]["attempts"] = attempts
                entry["_queue"]["last_attempt"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                entry["_queue"]["next_retry"] = next_retry.strftime("%Y-%m-%dT%H:%M:%SZ")
                entry["_queue"]["last_error"] = error
                with open(msg_file, "w") as f:
                    json.dump(entry, f, indent=2)
                log_delivery(from_agent, to_agent, msg_type, msg_id, "retry", f"ATTEMPT={attempts} NEXT={next_retry.strftime('%H:%M:%S')}")
                stats["waiting"] += 1
    
    return stats


def check_all_health():
    """Check health of all agents."""
    results = {}
    for agent in AGENTS:
        health = get_health(agent)
        healthy = is_healthy(agent)
        results[agent] = {
            "status": health.get("status", "unknown"),
            "last_seen": health.get("last_seen"),
            "healthy": healthy,
        }
    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "send":
        if len(sys.argv) < 5:
            print("Usage: agent-link-worker.py send <to> <type> <message> [options]")
            sys.exit(1)
        
        to_agent = sys.argv[2]
        msg_type = sys.argv[3]
        message = sys.argv[4]
        
        # Parse optional args
        priority = "p2"
        reply_to = None
        for i, arg in enumerate(sys.argv[5:], 5):
            if arg == "--priority" and i + 1 < len(sys.argv):
                priority = sys.argv[i + 1]
            if arg == "--reply-to" and i + 1 < len(sys.argv):
                parts = sys.argv[i + 1].split(":")
                if len(parts) == 2:
                    reply_to = {"channel": parts[0], "target": parts[1]}
        
        success, msg_id, error = send_message(
            to_agent=to_agent,
            msg_type=msg_type,
            message=message,
            priority=priority,
            reply_to=reply_to,
        )
        
        if success:
            print(f"✅ Sent: {msg_id}")
        else:
            print(f"⚠️ {error} (ID: {msg_id})")
        
        sys.exit(0 if success else 1)
    
    elif cmd == "process-queue":
        stats = process_queue()
        print(f"Queue processed: {stats['delivered']} delivered, {stats['failed']} failed, {stats['waiting']} waiting")
        sys.exit(0)
    
    elif cmd == "check-health":
        results = check_all_health()
        for agent, info in results.items():
            status = "✅" if info["healthy"] else "❌"
            print(f"{status} {agent}: {info['status']} (last: {info['last_seen']})")
        sys.exit(0)
    
    elif cmd == "update-health":
        if len(sys.argv) < 4:
            print("Usage: agent-link-worker.py update-health <agent> <status>")
            sys.exit(1)
        agent = sys.argv[2]
        status = sys.argv[3]
        update_health(agent, status)
        print(f"Updated {agent} health to {status}")
        sys.exit(0)
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
