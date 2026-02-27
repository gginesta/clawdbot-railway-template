#!/data/workspace/.venv/bin/python3
"""write_directive.py — Molty's directive writer for the TMNT fleet.

Writes a .sh directive to /data/shared/pending-directives/<agent>/
so the agent's 15-min cron picks it up and runs it automatically.

Usage:
  write_directive.py --agent raphael --slug secrets-migration \
    --script /data/shared/credentials/apply-secrets.sh \
    --script-args raphael \
    --requires-version v2026.2.26

  write_directive.py --agent all --slug some-task --script /path/to/script.sh
"""
from __future__ import annotations
import argparse, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo

HKT = ZoneInfo("Asia/Hong_Kong")
DIRECTIVES_ROOT = "/data/shared/pending-directives"
AGENTS = ["molty", "raphael", "leonardo"]

RAILWAY_TOKEN = "1d318b62-a713-4fd6-80cf-c54c0934f5d8"
RAILWAY_API = "https://backboard.railway.app/graphql/v2"
RAILWAY_IDS = {
    "molty":    {"svc": "3daf200b-6fdb-4ead-a850-b7d33301f3b0", "env": "f55df1f4-35ed-4ae7-9300-ec74ee9035be"},
    "raphael":  {"svc": "fc8720f0-cd59-48b1-93a2-c8b53e7faa90", "env": "88c2c024-7471-4483-81f5-786f5c95c49b"},
    "leonardo": {"svc": "02713288-b633-4f01-8bfe-e8ef9a739605", "env": "ffa245c6-0eac-40aa-bcf3-9edd7cdd8de9"},
}


def write_directive(
    agent: str,
    slug: str,
    script: str,
    script_args: str = "",
    requires_version: str | None = None,
    requires_version_op: str = ">=",
    idempotent: bool = True,
    posted_by: str = "molty",
) -> str:
    queue_dir = os.path.join(DIRECTIVES_ROOT, agent)
    os.makedirs(queue_dir, exist_ok=True)

    ts = datetime.now(HKT).strftime("%Y%m%d-%H%M%S")
    fname = f"{ts}-{slug}.sh"
    fpath = os.path.join(queue_dir, fname)

    lines = [
        "#!/bin/bash",
        f"# DIRECTIVE: {slug}",
        f"# POSTED_BY: {posted_by}",
        f"# POSTED_AT: {datetime.now(HKT).isoformat()}",
        f"# IDEMPOTENT: {'true' if idempotent else 'false'}",
    ]
    if requires_version:
        lines.append(f"# REQUIRES_VERSION: {requires_version}")
        lines.append(f"# REQUIRES_VERSION_OP: {requires_version_op}")

    lines += [
        "",
        "set -euo pipefail",
        "",
        f'echo "▶ Running directive: {slug}"',
        f"bash {script} {script_args}".strip(),
        f'echo "✅ Directive complete: {slug}"',
    ]

    with open(fpath, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(fpath, 0o755)
    return fpath


def railway_redeploy(agent: str) -> bool:
    import urllib.request
    ids = RAILWAY_IDS.get(agent)
    if not ids:
        return False
    svc, env = ids["svc"], ids["env"]
    payload = json.dumps({
        "query": f'mutation {{ serviceInstanceRedeploy(serviceId: "{svc}", environmentId: "{env}") }}'
    }).encode()
    req = urllib.request.Request(RAILWAY_API, data=payload, method="POST",
        headers={"Authorization": f"Bearer {RAILWAY_TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        return bool(data.get("data", {}).get("serviceInstanceRedeploy"))
    except Exception as e:
        print(f"  ⚠️  Railway redeploy failed for {agent}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Write a fleet directive")
    parser.add_argument("--agent", required=True, help="Agent name or 'all'")
    parser.add_argument("--slug", required=True, help="Short identifier")
    parser.add_argument("--script", required=True, help="Script path to run")
    parser.add_argument("--script-args", default="", help="Args to pass to script")
    parser.add_argument("--requires-version", default=None, help="Min OpenClaw version required")
    parser.add_argument("--requires-version-op", default=">=", help="Version operator (>= == >)")
    parser.add_argument("--no-idempotent", action="store_true", help="Mark as non-idempotent")
    parser.add_argument("--no-redeploy", action="store_true", help="Skip Railway redeploy trigger")
    args = parser.parse_args()

    targets = AGENTS if args.agent == "all" else [args.agent]

    for agent in targets:
        path = write_directive(
            agent=agent,
            slug=args.slug,
            script=args.script,
            script_args=args.script_args,
            requires_version=args.requires_version,
            requires_version_op=args.requires_version_op,
            idempotent=not args.no_idempotent,
        )
        print(f"✅ Written: {path}")

        if not args.no_redeploy:
            if agent == "molty":
                print(f"  ℹ️  Molty: run check_directives.py locally (no self-redeploy)")
            else:
                ok = railway_redeploy(agent)
                print(f"  {'✅' if ok else '❌'} Railway redeploy triggered for {agent}")


if __name__ == "__main__":
    main()
