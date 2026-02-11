# DIY Unbrowse — API Skill Auto-Capture System (MVP)

Date: 2026-02-10

This MVP turns a manual browsing session into a reusable **API skill folder** by:

1) capturing API-like network traffic from a Chromium/Brave tab (CDP)
2) extracting candidate endpoints (method + normalized URL template)
3) generating runnable curl wrapper scripts + metadata

The focus is **deterministic** (scripts, no LLM dependency) and **safe by default** (redaction of secrets).

---

## Files / entrypoint

Primary entrypoint:

- `/data/workspace/scripts/api-capture/capture-and-generate.sh`

Core components:

- `/data/workspace/scripts/api-capture/cdp-capture.js`
  - connects to CDP
  - listens to `Network.*` events
  - writes JSONL captures
- `/data/workspace/scripts/api-capture/skill-gen.py`
  - reads capture JSONL
  - clusters endpoints
  - generates skill folder

---

## How it works (data flow)

1. **User starts Brave with remote debugging**
2. `cdp-capture.js` discovers the relevant `page` target via `http://127.0.0.1:<port>/json/list`
3. The capture script records request/response pairs once the response is finished:
   - request: url, method, headers, (optional) body
   - response: status, headers, (optional) body
4. `skill-gen.py`:
   - filters captures to the provided domain
   - chooses a **dominant host** (to avoid mixing app + api subdomains)
   - normalizes URLs (replaces probable IDs with `{id}`, normalizes query keys)
   - creates one bash script per (method + normalized path)
   - writes `endpoints.json` + `.meta.json` + `SKILL.md`

---

## Output format

### Captures

Written to:

- `/data/workspace/data/captures/<domain>-<timestamp>.jsonl`

Each line is one JSON object with:

- `request.headers` + `response.headers` (redacted by default)
- `request.body` + `response.body` (optional; best-effort redaction for sensitive JSON keys)

### Generated skill folder

Default output:

- `/data/shared/api-skills/<domain>/`

Contains:

- `SKILL.md` — usage + credentials template
- `endpoints.json` — machine-readable endpoint catalog
- `.meta.json` — generator metadata
- `api.sh` — dispatcher: `./api.sh <resource> <action> ...`
- `scripts/*.sh` — per-endpoint curl wrapper scripts
- `curl-commands.sh` — prints a reproducible curl command set (one per endpoint)

The folder can be copied into `/data/workspace/skills/<name>/` if desired.

---

## Security / safety notes

Defaults are intended to prevent accidental secret capture:

- **Authorization/Cookie/API-key headers are redacted by default** in `cdp-capture.js`.
- Best-effort body redaction replaces values for keys like: `token`, `secret`, `password`, `api_key`, etc.

If you must debug auth issues, you can opt into unsafe capture:

- `cdp-capture.js --unsafe-keep-auth`

This is *not recommended* unless you understand where the capture file will be stored and who can access it.

If you want to avoid storing response bodies entirely:

- `cdp-capture.js --no-bodies`

---

## Fallback / iteration strategy (MVP)

Many modern web apps require cookies, CSRF headers, or non-obvious flows.

If a generated script fails (common symptoms: `401`, `403`, CSRF errors, “missing header”):

1) Re-run capture against the same domain:

```bash
bash /data/workspace/scripts/api-capture/capture-and-generate.sh <domain> --timeout 120
```

2) In the browser, **repeat the exact action** you want to automate (click the same button, submit the same form).

3) Re-generate and re-try.

Practical tips:

- Capture *after login* and as close as possible to the moment you trigger the action.
- If there are multiple tabs, close extras or pass `--ws` to target a specific tab.
- If you suspect bodies contain sensitive data, capture with `--no-bodies` first.

---

## MVP limitations (known)

- Endpoint parameterization is minimal (supports `{id}` + `--query` for extra params).
- Some sites use non-JSON APIs or opaque responses that CDP won’t expose.
- Auth detection is best-effort; you may need to manually add env vars/headers.

---

## Next improvements (post-MVP)

- Capture and model CSRF header + cookie/session handling more explicitly
- Better endpoint grouping (GraphQL detection; mutation naming)
- Record “request presets” (sample payload templates) without secrets
- Add `--interactive` selector for CDP target tab
