#!/bin/bash
# discord-mention-validator.sh — PLAN-017c
# Converts plain @Name mentions to <@USER_ID> format before Discord posts.
# Prevents silent non-pings.
#
# Usage: discord-mention-validator.sh "Your message with @Guillermo here"
# Output: Message with @Name → <@USER_ID> replacements
#
# Supported names (case-insensitive):
#   @Guillermo → <@779143499655151646>
#   @Molty     → <@1468162520958107783>
#   @Raphael   → <@1468164929285783644>
#   @Leonardo  → <@1470919061763522570>
#   @April     → <@1481167770191401021>
#
# Examples:
#   discord-mention-validator.sh "Hey @Guillermo this is done"
#   → "Hey <@779143499655151646> this is done"
#
#   discord-mention-validator.sh "Thanks @Molty and @Leonardo"
#   → "Thanks <@1468162520958107783> and <@1470919061763522570>"

MSG="${1:-}"

if [ -z "$MSG" ]; then
    # Read from stdin if no argument
    MSG=$(cat)
fi

# Run through Python for reliable case-insensitive replacement
python3 << PYTHON
import re
import sys

msg = """$MSG"""

MENTIONS = {
    "guillermo": "<@779143499655151646>",
    "molty":     "<@1468162520958107783>",
    "raphael":   "<@1468164929285783644>",
    "leonardo":  "<@1470919061763522570>",
    "april":     "<@1481167770191401021>",
}

def replace_mention(match):
    name = match.group(1).lower()
    if name in MENTIONS:
        return MENTIONS[name]
    return match.group(0)  # leave unchanged if not in map

# Match @Word patterns (plain mentions only — skip already-formatted <@123>)
result = re.sub(r'(?<!<)@([A-Za-z][A-Za-z0-9_-]*)', replace_mention, msg)

print(result, end="")
PYTHON
