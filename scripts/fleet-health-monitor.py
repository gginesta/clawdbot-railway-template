#!/usr/bin/env python3
"""
Fleet Health Monitor — checks agent gateway health before overnight windows.
Run via cron 30 min before each agent's overnight slot.
"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime

AGENTS = {
    "raphael": {
        "health_url": "https://ggv-raphael.up.railway.app/health",
        "railway_service": "fc8720f0-cd59-48b1-93a2-c8b53e7faa90",
        "railway_env": "88c2c024-7471-4483-81f5-786f5c95c49b",
        "overnight_slot": "00:30 HKT"
    },
    "leonardo": {
        "health_url": "https://leonardo-production.up.railway.app/health", 
        "railway_service": "02713288-b633-4f01-8bfe-e8ef9a739605",
        "railway_env": "ffa245c6-0eac-40aa-bcf3-9edd7cdd8de9",
        "overnight_slot": "01:30 HKT"
    },
    "april": {
        "health_url": "https://april-agent-production.up.railway.app/health",
        "railway_service": "ea026a0b-79e0-433d-907e-5cc4f75385e2", 
        "railway_env": None,  # Need to look this up
        "overnight_slot": "02:00 HKT"
    }
}

RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN", "1d318b62-a713-4fd6-80cf-c54c0934f5d8")
RAILWAY_API = "https://backboard.railway.app/graphql/v2"
DISCORD_SQUAD_UPDATES = "1468164181155909743"

def check_health(agent: str, max_retries: int = 2) -> tuple[bool, str]:
    """Check agent health endpoint. Returns (healthy, error_message)."""
    info = AGENTS.get(agent)
    if not info:
        return False, f"Unknown agent: {agent}"
    
    url = info["health_url"]
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, method="GET")
            req.add_header("User-Agent", "MoltyFleetMonitor/1.0")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    return True, "OK"
                # 401 means service is up but requires auth - that's acceptable
                if resp.status == 401:
                    return True, "OK (auth required)"
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return True, "OK (auth required)"
            if attempt == max_retries - 1:
                return False, f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            if attempt == max_retries - 1:
                return False, f"Connection failed: {e.reason}"
        except Exception as e:
            if attempt == max_retries - 1:
                return False, str(e)
    return False, "Max retries exceeded"

def attempt_redeploy(agent: str) -> tuple[bool, str]:
    """Attempt Railway API redeploy. Returns (success, message)."""
    info = AGENTS.get(agent)
    if not info or not info.get("railway_service"):
        return False, "No Railway service configured"
    
    svc = info["railway_service"]
    env = info["railway_env"]
    if not env:
        return False, "No Railway environment configured"
    
    payload = json.dumps({
        "query": f'mutation {{ serviceInstanceRedeploy(serviceId: "{svc}", environmentId: "{env}") }}'
    }).encode()
    
    try:
        req = urllib.request.Request(RAILWAY_API, data=payload, method="POST")
        req.add_header("Authorization", f"Bearer {RAILWAY_TOKEN}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            if data.get("data", {}).get("serviceInstanceRedeploy"):
                return True, "Redeploy triggered"
            if data.get("errors"):
                return False, data["errors"][0].get("message", "Unknown error")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return False, "Railway token unauthorized (403) — needs refresh"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)
    
    return False, "Unknown failure"

def alert_discord(message: str):
    """Post alert to #squad-updates via openclaw CLI."""
    subprocess.run([
        "openclaw", "message", "send",
        "--channel", "discord",
        "--target", DISCORD_SQUAD_UPDATES,
        "-m", message
    ], capture_output=True, timeout=30)

def main():
    if len(sys.argv) < 2:
        print("Usage: fleet-health-monitor.py <agent|all>")
        sys.exit(1)
    
    target = sys.argv[1].lower()
    agents_to_check = list(AGENTS.keys()) if target == "all" else [target]
    
    results = []
    for agent in agents_to_check:
        if agent not in AGENTS:
            print(f"Unknown agent: {agent}")
            continue
            
        healthy, msg = check_health(agent)
        emoji = "🦎" if agent == "molty" else "🔴" if agent == "raphael" else "🔵" if agent == "leonardo" else "🌸"
        
        if healthy:
            print(f"{emoji} {agent.title()}: ✅ {msg}")
            results.append((agent, True, msg))
        else:
            print(f"{emoji} {agent.title()}: ❌ {msg}")
            
            # Attempt auto-recovery
            print(f"  Attempting Railway redeploy...")
            redeploy_ok, redeploy_msg = attempt_redeploy(agent)
            
            if redeploy_ok:
                print(f"  ✅ {redeploy_msg}")
                alert_discord(f"⚠️ **Fleet Health Alert**\n\n{emoji} **{agent.title()}** gateway was unresponsive.\nAuto-redeploy triggered. Monitoring recovery...")
            else:
                print(f"  ❌ {redeploy_msg}")
                alert_discord(f"🚨 **Fleet Health Alert — Manual Action Needed**\n\n{emoji} **{agent.title()}** gateway is DOWN.\nHealth check: {msg}\nAuto-redeploy failed: {redeploy_msg}\n\n<@779143499655151646> please manually redeploy `{agent}` in Railway.")
            
            results.append((agent, False, msg))
    
    # Summary
    failed = [r for r in results if not r[1]]
    if failed:
        print(f"\n⚠️  {len(failed)} agent(s) unhealthy")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(results)} agent(s) healthy")
        sys.exit(0)

if __name__ == "__main__":
    main()
