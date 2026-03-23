#!/usr/bin/env python3
"""
Memory Audit Script — scans MEMORY.md for stale items.

Checks:
1. Items with [verified: YYYY-MM-DD] older than 7 days → marks ⚠️ STALE
2. Pending/blocked items without any verification date → flags them
3. Outputs a report of what needs verification

Run weekly via cron or manually before any standup/briefing.
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_PATH = Path("/data/workspace/MEMORY.md")
STALENESS_DAYS = 7

def audit():
    if not MEMORY_PATH.exists():
        print("ERROR: MEMORY.md not found")
        sys.exit(1)

    content = MEMORY_PATH.read_text()
    lines = content.split("\n")
    today = datetime.now().date()
    threshold = today - timedelta(days=STALENESS_DAYS)

    stale_items = []
    unverified_items = []
    verified_ok = []

    # Only audit items in these sections (track current section by headers)
    auditable_sections = [
        'Active Projects', 'Pending', 'Parked', '⏳', '🅿️', '📋'
    ]
    in_auditable_section = False

    # Verification date pattern
    verified_re = re.compile(r'\[verified:\s*(\d{4}-\d{2}-\d{2})\]')

    # Done/completed items to skip
    done_re = re.compile(r'DONE|COMPLETE|✅|FULLY OPERATIONAL|SUPERSEDED', re.IGNORECASE)

    for i, line in enumerate(lines, 1):
        # Track which section we're in
        if line.startswith('## '):
            in_auditable_section = any(s in line for s in auditable_sections)
            continue

        # Only audit lines in relevant sections
        if not in_auditable_section:
            continue

        # Skip non-content lines
        if not line.strip() or line.startswith('---') or line.startswith('*') or line.startswith('#'):
            continue

        # Skip bullet items that are clearly done
        if not line.strip().startswith('- '):
            continue
        if done_re.search(line):
            continue

        # Every remaining bullet in an auditable section should have a verification date
        match = verified_re.search(line)
        if match:
            verified_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
            if verified_date < threshold:
                stale_items.append({
                    'line': i,
                    'text': line.strip()[:120],
                    'verified': str(verified_date),
                    'days_old': (today - verified_date).days
                })
            else:
                verified_ok.append({
                    'line': i,
                    'text': line.strip()[:80],
                    'verified': str(verified_date)
                })
        else:
            unverified_items.append({
                'line': i,
                'text': line.strip()[:120]
            })

    # Report
    print(f"=== MEMORY AUDIT ({today}) ===\n")

    if stale_items:
        print(f"⚠️  STALE ({len(stale_items)} items — verified >{STALENESS_DAYS} days ago):")
        for item in stale_items:
            print(f"  L{item['line']}: {item['text']}")
            print(f"         Last verified: {item['verified']} ({item['days_old']} days ago)")
        print()

    if unverified_items:
        print(f"❌ UNVERIFIED ({len(unverified_items)} pending items — no verification date):")
        for item in unverified_items:
            print(f"  L{item['line']}: {item['text']}")
        print()

    if verified_ok:
        print(f"✅ FRESH ({len(verified_ok)} items verified within {STALENESS_DAYS} days)")
        print()

    total_issues = len(stale_items) + len(unverified_items)
    if total_issues == 0:
        print("MEMORY_AUDIT_OK — all pending items are verified and fresh.")
    else:
        print(f"MEMORY_AUDIT_ISSUES — {total_issues} items need verification before reporting to Guillermo.")

    return total_issues

if __name__ == "__main__":
    issues = audit()
    sys.exit(1 if issues > 0 else 0)
