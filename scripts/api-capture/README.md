# API Skill Auto-Capture (DIY Unbrowse) — Phase 1 MVP

This folder contains a usable MVP of the **DIY Unbrowse API skill auto-capture system**.

## What it does

1) **Captures** API/network calls from a browsing session (via CDP)
2) **Extracts** candidate endpoints (method + normalized path) and basic auth style
3) **Generates** a reusable “API skill folder” with:
   - `SKILL.md`
   - `endpoints.json` (+ `.meta.json`)
   - runnable curl-wrapper scripts in `scripts/`
   - `api.sh` dispatcher
   - `curl-commands.sh` (prints reproducible curl commands)

## Components

1. `cdp-capture.js` — attaches to Brave/Chromium CDP and records API-like requests/responses as JSONL
2. `skill-gen.py` — reads JSONL capture(s), extracts endpoints, generates an API skill directory
3. Credential handler — implemented via auth detection + an `.env` template in generated `SKILL.md`
4. `capture-and-generate.sh` — wrapper that runs capture then runs generation

## Safety defaults (important)

- `cdp-capture.js` **redacts** sensitive headers by default (`Authorization`, `Cookie`, API keys, etc.).
- It also does **best-effort redaction** of sensitive JSON fields in request/response bodies.
- If you want extra safety, run capture with `--no-bodies`.
- You can disable header redaction with `--unsafe-keep-auth` (not recommended).

## Prerequisites

Start Brave (or Chromium) with remote debugging enabled:

```bash
/usr/bin/brave-browser --remote-debugging-port=18800
```

## Quick start (recommended)

```bash
bash /data/workspace/scripts/api-capture/capture-and-generate.sh hubspot.com --timeout 120
```

By default this generates:

- Captures → `/data/workspace/data/captures/`
- Skills → `/data/shared/api-skills/<domain>/`
- Credentials template location → `/data/workspace/credentials/api-auth/<domain>.env`

If you want to generate into a local skills folder instead:

```bash
bash /data/workspace/scripts/api-capture/capture-and-generate.sh hubspot.com --timeout 120 \
  --out-base /data/workspace/skills
```

Next steps:

```bash
cd /data/shared/api-skills/hubspot.com
cat SKILL.md

# Print reproducible curl commands (does not require credentials)
./curl-commands.sh

# After you create /data/workspace/credentials/api-auth/hubspot.com.env
./api.sh <resource> <action> --help
./api.sh <resource> <action>
```

## Manual runs

Capture only:

```bash
node /data/workspace/scripts/api-capture/cdp-capture.js --port 18800 --domain example.com
```

Generate only:

```bash
python3 /data/workspace/scripts/api-capture/skill-gen.py \
  --input /data/workspace/data/captures/example.com-*.jsonl \
  --domain example.com \
  --out-base /data/shared/api-skills
```

## Notes / limitations (MVP)

- CDP target discovery chooses the first **page** tab matching `--domain`. If you have multiple tabs open, close extras or pass `--ws` to `cdp-capture.js`.
- Some responses are not retrievable via `Network.getResponseBody` (redirects, cached, opaque). Those may be skipped.
- URL normalization replaces likely IDs with `{id}`. Verify templates.
- Auth detection is best-effort. Many sites require cookies/CSRF headers that only appear in specific flows.
