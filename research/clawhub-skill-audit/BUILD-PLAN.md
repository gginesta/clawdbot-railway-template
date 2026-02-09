# Custom Skill Build Plan — Feb 9, 2026

## Skills to Build (Priority Order)

| # | Skill | Inspired By | Status |
|---|-------|-------------|--------|
| 1 | `notion-enhanced` | notion-sync (robansuini) | ✅ Done — 7 scripts, tested |
| 2 | `tmnt-agent-creator` | agent-council (itsahedge) | ✅ Done — tested |
| 3 | `council` | council-of-the-wise (jeffaf) | ✅ Done — 5 personas |
| 4 | Calendar improvements | gcalcli-calendar (lstpsche) | ✅ Done — find + safe-add |

## Build Standards
- Each skill gets: SKILL.md, scripts/, security self-audit
- Save to `/data/workspace/skills/` (local) + `/data/shared/skills/` (Syncthing distribution)
- Pikachu post per skill completion
- No external dependencies we don't already have
- All credentials via env vars, never hardcoded
