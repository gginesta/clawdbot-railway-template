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


def main():
    parser = argparse.ArgumentParser(description="Write a fleet directive")
    parser.add_argument("--agent", required=True, help="Agent name or 'all'")
    parser.add_argument("--slug", required=True, help="Short identifier")
    parser.add_argument("--script", required=True, help="Script path to run")
    parser.add_argument("--script-args", default="", help="Args to pass to script")
    parser.add_argument("--requires-version", default=None, help="Min OpenClaw version required")
    parser.add_argument("--requires-version-op", default=">=", help="Version operator (>= == >)")
    parser.add_argument("--no-idempotent", action="store_true", help="Mark as non-idempotent")
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


if __name__ == "__main__":
    main()
