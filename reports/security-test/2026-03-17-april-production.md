# Security Test Report — april-production

- Date (local): 2026-03-17
- Date (UTC): 2026-03-16
- Repo: N/A
- URL: https://april-agent-production.up.railway.app
- Runner host: f2861bfe3c48

> Defensive scanning only. No exploitation, no brute force, no auth bypass attempts.

## Runner Note (Model)
This skill was authored in the OpenClaw workspace. Requested model was **openai-codex/gpt-5.3**; if unavailable, a best-available fallback was used by the agent environment.

## Tooling Summary

| Category | Tool | Status |
|---|---|---|
| deps | \ | ❌ missing |
| deps | \ | ❌ missing |
| deps | \ | ✅ found |
| deps | \ | ✅ found |
| deps | \ | ❌ missing |
| deps | \ | ✅ found |
| deps | \ | ✅ found |

## Results

### DAST Baseline
Target URL: https://april-agent-production.up.railway.app
OWASP ZAP not available in this environment.

**Railway-friendly fallback (lightweight, non-invasive):**
- Fetch `/robots.txt`, `/.well-known/security.txt` if present
- Check basic security headers
- Confirm TLS + redirects behavior (if https)

```bash
curl -sS -D - -o /dev/null <url>
```
\nHeaders (best-effort):
```
HTTP/2 401 
content-type: text/html; charset=utf-8
date: Mon, 16 Mar 2026 16:30:39 GMT
etag: W/"d-Ez3bAdjUD1fWXMob+3PvJWPLlMI"
server: railway-edge
www-authenticate: Basic realm="OpenClaw Dashboard"
x-railway-edge: railway/us-west2
x-railway-request-id: oj6FIx25RaSA-3O6npoFkQ
content-length: 13

```
\nGET /robots.txt:
```
Auth required```
\nGET /.well-known/security.txt:
```
Auth required```
\nHeader checklist (manual review):
- Strict-Transport-Security (HSTS)
- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options / frame-ancestors
- Referrer-Policy
- Permissions-Policy
\n**How to run full ZAP baseline elsewhere (recommended):**
```bash
docker run --rm -t owasp/zap2docker-stable zap-baseline.py -t <url> -r zap.html
```

## Overall Status
✅ No blocking issues detected by the runner (tools may have been missing).

## Next Actions (Suggested)
- Triage findings by severity and confirm reproducibility.
- Fix and re-run this report against the same target.
- Add CI wrapper if you want to enforce policy gates.
