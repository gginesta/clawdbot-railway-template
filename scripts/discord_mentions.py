"""
discord_mentions.py — PLAN-017c: Discord @mention validation (Python module)

Import and use validate_mentions() to convert @Name → <@USER_ID> before sending.

Usage:
    from discord_mentions import validate_mentions
    safe_msg = validate_mentions("Hey @Guillermo this is done")
    # → "Hey <@779143499655151646> this is done"
"""

import re

MENTION_MAP = {
    "guillermo": "<@779143499655151646>",
    "molty":     "<@1468162520958107783>",
    "raphael":   "<@1468164929285783644>",
    "leonardo":  "<@1470919061763522570>",
    "april":     "<@1481167770191401021>",
}

def validate_mentions(text: str) -> str:
    """Convert plain @Name mentions to <@USER_ID> format.
    
    - Case-insensitive
    - Skips already-formatted <@123456> mentions
    - Leaves unknown @names unchanged
    """
    def _replace(match):
        name = match.group(1).lower()
        return MENTION_MAP.get(name, match.group(0))

    return re.sub(r'(?<!<)@([A-Za-z][A-Za-z0-9_-]*)', _replace, text)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(validate_mentions(" ".join(sys.argv[1:])))
    else:
        # Self-test
        tests = [
            ("Hey @Guillermo",          "Hey <@779143499655151646>"),
            ("@molty @RAPHAEL @April",  "<@1468162520958107783> <@1468164929285783644> <@1481167770191401021>"),
            ("<@779143499655151646>",   "<@779143499655151646>"),  # no double-convert
            ("@Donatello pending",      "@Donatello pending"),      # unknown → unchanged
        ]
        passed = 0
        for inp, expected in tests:
            result = validate_mentions(inp)
            status = "✅" if result == expected else "❌"
            print(f"{status} '{inp}' → '{result}'")
            if result == expected:
                passed += 1
        print(f"\n{passed}/{len(tests)} tests passed")
