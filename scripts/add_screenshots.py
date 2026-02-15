#!/usr/bin/env python3
"""Add screenshot content to Notion articles."""
import requests

API_KEY = "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"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def rt(text, bold=False, italic=False, code=False):
    """Rich text helper."""
    ann = {}
    if bold: ann["bold"] = True
    if italic: ann["italic"] = True
    if code: ann["code"] = True
    r = {"type": "text", "text": {"content": text}}
    if ann: r["annotations"] = ann
    return r

def callout(icon, *parts):
    return {"object":"block","type":"callout","callout":{"icon":{"type":"emoji","emoji":icon},"rich_text":list(parts)}}

def code_block(content, lang=""):
    return {"object":"block","type":"code","code":{"rich_text":[{"type":"text","text":{"content":content}}],"language":lang}}

# Post 2: Add Discord standup screenshot placeholder
post2_screenshot = [
    callout("📸", 
        rt("Screenshot: Discord daily standup from Molty 🦎", bold=True),
        rt("\n\nShows the squad in action — Molty posting the 5PM standup with completed tasks, overdue items, and the Notion link. Demonstrates the multi-agent coordination described in the article."),
    ),
    {"object":"block","type":"paragraph","paragraph":{"rich_text":[rt("To capture: Open Discord #command-center, find a standup message, screenshot. Ensure no private task details are visible.")]}},
]

# Post 3: Add cron job table
cron_content = """=== CRON JOB LIST (Feb 15, 2026) ===

Active cron jobs: 12

Name                                    | Schedule (HKT)
----------------------------------------|------------------
Daily Morning Briefing                  | 6:00 AM daily
Memory Size Guardrail                   | 8:00 AM daily
Daily Standup                           | 5:00 PM daily
Daily Log Compaction                    | 11:00 PM daily
Daily Backup + Update                   | 9:00 PM daily
Morning Update Check + Feature Summary  | 8:15 AM daily
Weekly PARA Curation                    | Mon 1:00 AM
Healthcheck Security Audit              | Mon 3:00 AM
GPT-5.3 API Availability Check          | Mon/Thu 10:00 AM
OpenClaw Community Research             | Every 3 days
Polymarket Reminder                     | One-shot (Feb 15)
Travel: Revert to Hong Kong             | One-shot (Feb 18)

Total: 12 active jobs (started with 3, peaked at 18, consolidated back to 12)"""

post3_screenshot = [
    {"object":"block","type":"paragraph","paragraph":{"rich_text":[rt("Example: The Cron Obsession in action", bold=True)]}},
    code_block(cron_content, "plain text"),
]

# Add to Post 2
print("Adding screenshot placeholder to Post 2...")
r = requests.patch(
    "https://api.notion.com/v1/blocks/30739dd69afd8169a211d06d6436a140/children",
    headers=HEADERS,
    json={"children": post2_screenshot}
)
print(f"Post 2: {r.status_code}")

# Add to Post 3
print("Adding cron table to Post 3...")
r = requests.patch(
    "https://api.notion.com/v1/blocks/30839dd69afd812c91a2d71aeea0e249/children",
    headers=HEADERS,
    json={"children": post3_screenshot}
)
print(f"Post 3: {r.status_code}")
