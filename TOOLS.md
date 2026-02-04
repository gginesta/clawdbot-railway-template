# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## GitHub API

**Token:** `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`
**Scope:** Repo access for openclaw/openclaw issue submission
**Added:** 2026-02-03 (received via Telegram)

### Submit Issue via API
```bash
curl -X POST https://api.github.com/repos/openclaw/openclaw/issues \
  -H "Authorization: token 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" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"title": "...", "body": "..."}'
```
