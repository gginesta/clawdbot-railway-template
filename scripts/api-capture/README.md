# API Skill Auto-Capture (Phase 1 MVP)

This folder contains the Phase 1 MVP of the **Unbrowse DIY** API skill auto-capture system.

It has 4 components:

1. `cdp-capture.js` — attaches to Brave/Chromium CDP and records API-like requests/responses as JSONL
2. `skill-gen.py` — reads JSONL capture(s), extracts endpoints, generates an API skill directory
3. Credential handler — implemented via auth detection + an `.env` template in generated `SKILL.md`
4. `capture-and-generate.sh` — wrapper that runs capture then runs generation

## Prerequisites

- Brave running with remote debugging enabled:

```bash
/usr/bin/brave-browser --remote-debugging-port=18800
```

- Ensure directories exist (wrapper will create them):
  - Captures: `/data/workspace/data/captures/`
  - Credentials: `/data/workspace/credentials/api-auth/`
  - Generated skills (shared): `/data/shared/api-skills/`

## Quick start

```bash
# If the scripts are not executable in your environment, call via bash/python/node directly.

bash /data/workspace/scripts/api-capture/capture-and-generate.sh hubspot.com --timeout 120

# Then edit credentials (template is in the generated SKILL.md)
ls -la /data/shared/api-skills/hubspot.com/
cat /data/shared/api-skills/hubspot.com/SKILL.md
```

## Capture format

`cdp-capture.js` writes one JSON object per line (JSONL). Each record includes:

- `request`: URL, method, headers, body, initiator, resourceType
- `response`: status, headers, mimeType, body
- `timing`: timestamps and CDP timing struct (if present)

## Notes / limitations (MVP)

- CDP target discovery chooses the first **page** tab matching `--domain`. If you have multiple tabs open, close extras or pass `--ws` to `cdp-capture.js`.
- Some responses are not retrievable via `Network.getResponseBody` (redirects, cached, opaque). Those may be skipped.
- URL normalization replaces likely IDs with `{id}`. Verify before relying on a generated script.
- Auth detection is best-effort. You may need to adjust the generated scripts or env file.

## Manual runs

Capture only:

```bash
node /data/workspace/scripts/api-capture/cdp-capture.js --port 18800 --domain example.com
```

Generate only:

```bash
python3 /data/workspace/scripts/api-capture/skill-gen.py \
  --input /data/workspace/data/captures/example.com-*.jsonl \
  --domain example.com
```
