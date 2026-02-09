---
name: security-test-runner
description: Defensive, read-only security testing runner (SAST + secrets + deps + baseline DAST) for repos/targets we own.
version: 0.1.0
runtime: bash
---

# security-test-runner

Defensive security testing only. Produces a Markdown report under:
`/data/workspace/reports/security-test/YYYY-MM-DD-<target>.md`

## SECURITY (Non-negotiable)
This skill **will not**:
- exploit vulnerabilities or attempt RCE
- brute-force / credential-stuff / password-spray
- bypass auth, MFA, WAF, rate limits, or access controls
- scan third-party targets you don’t own/control
- run destructive actions (no writes to target systems)

It **will**:
- run **read-only** static analysis and dependency checks on local repos
- run **baseline** web app checks on URLs you own (staging/local)

## Requirements
The runner is designed to work in Railway containers (no Docker assumed).
It uses tools **only if already installed**.

Optional tools (NOT auto-installed):
- `semgrep` (SAST)
- `gitleaks` (secrets scanning)
- `pip-audit` (Python dependency audit)
- OWASP ZAP (`zap-baseline.py` or `zap.sh`) OR Docker image `zaproxy/zap2docker-stable`

Installation guidance is printed into the report when tools are missing.

## Usage

### 1) Repo scan (SAST + secrets + deps)
```bash
bash skills/security-test-runner/scripts/run.sh \
  --target proposal-studio \
  --repo /data/workspace/proposal-studio
```

### 2) URL scan (baseline DAST)
```bash
bash skills/security-test-runner/scripts/run.sh \
  --target considerate-light-staging \
  --url https://considerate-light-production.up.railway.app
```

### 3) Repo + URL
```bash
bash skills/security-test-runner/scripts/run.sh \
  --target ps-staging \
  --repo /data/workspace/proposal-studio \
  --url  https://wonderful-harmony-production.up.railway.app
```

### Notion save (optional)
Requires Notion Enhanced skill + `NOTION_API_KEY`.

```bash
source /data/workspace/credentials/notion.env
export NOTION_PARENT_PAGE_ID="<page-id>"  # parent page to create report under

bash skills/security-test-runner/scripts/notion-save.sh \
  /data/workspace/reports/security-test/2026-02-09-ps-staging.md \
  "Security Test — ps-staging — 2026-02-09"
```

## Notes
- By default, the runner uses the best-available configuration for each tool.
- If you want stricter policies (block merges, fail CI), wrap `scripts/run.sh` in your CI and enforce exit codes.
