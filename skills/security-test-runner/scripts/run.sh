#!/usr/bin/env bash
set -euo pipefail

# Defensive security testing runner
# - SAST (semgrep if available)
# - Secrets (gitleaks if available)
# - Dependency checks (npm/pnpm/pip-audit if available)
# - Baseline DAST (OWASP ZAP if available; fallback lightweight checks)

usage() {
  cat <<'EOF'
Usage:
  run.sh --target <name> [--repo <path>] [--url <https://...>] [--out <report.md>]

Examples:
  run.sh --target my-repo --repo /data/workspace/my-repo
  run.sh --target staging --url https://staging.example.com
  run.sh --target both --repo . --url https://localhost:3000
EOF
}

TARGET=""
REPO=""
URL=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --repo)   REPO="${2:-}"; shift 2 ;;
    --url)    URL="${2:-}"; shift 2 ;;
    --out)    OUT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "--target is required"; usage; exit 2
fi

DATE_UTC=$(date -u +%F)
DATE_LOCAL=$(date +%F)

REPORT_DIR="/data/workspace/reports/security-test"
mkdir -p "$REPORT_DIR"

if [[ -z "$OUT" ]]; then
  OUT="$REPORT_DIR/${DATE_LOCAL}-${TARGET}.md"
fi

# Simple markdown append helper
md() { printf "%s\n" "$*" >> "$OUT"; }

# Capture environment (minimal, no secrets)
have_cmd() { command -v "$1" >/dev/null 2>&1; }

md "# Security Test Report — ${TARGET}"
md ""
md "- Date (local): ${DATE_LOCAL}"
md "- Date (UTC): ${DATE_UTC}"
md "- Repo: ${REPO:-N/A}"
md "- URL: ${URL:-N/A}"
md "- Runner host: $(hostname)"
md ""
md "> Defensive scanning only. No exploitation, no brute force, no auth bypass attempts."
md ""

# Model note (requested by spec)
md "## Runner Note (Model)"
md "This skill was authored in the OpenClaw workspace. Requested model was **openai-codex/gpt-5.3**; if unavailable, a best-available fallback was used by the agent environment."
md ""

md "## Tooling Summary"
md ""
md "| Category | Tool | Status |"
md "|---|---|---|"
for t in semgrep gitleaks npm pnpm pip-audit python3 curl; do
  if have_cmd "$t"; then md "| deps | \\`$t\\` | ✅ found |"; else md "| deps | \\`$t\\` | ❌ missing |"; fi
done
md ""

md "## Results"
md ""

STATUS=0

# --- SAST (semgrep) ---
if [[ -n "$REPO" ]]; then
  md "### SAST — Semgrep"
  if have_cmd semgrep; then
    md "Running semgrep (OWASP Top 10 + default rules if available)..."
    md ""
    md "\`\`\`bash"
    md "semgrep --config p/owasp-top-ten --config p/security-audit --error --json"
    md "\`\`\`"

    TMP_JSON=$(mktemp)
    set +e
    (cd "$REPO" && semgrep --config p/owasp-top-ten --config p/security-audit --error --json >"$TMP_JSON" 2>/dev/null)
    SEMGREP_EXIT=$?
    set -e

    # Semgrep returns non-zero on findings with --error; treat as findings not runner failure.
    if [[ $SEMGREP_EXIT -ne 0 ]]; then
      STATUS=1
    fi

    if have_cmd python3; then
      md "\nSummary (best-effort):"
      md "\`\`\`"
      python3 - <<'PY' "$TMP_JSON" >>"$OUT" || true
import json,sys
p=sys.argv[1]
try:
  data=json.load(open(p))
except Exception as e:
  print(f"Could not parse semgrep JSON: {e}")
  raise SystemExit(0)
results=data.get('results',[])
print(f"Findings: {len(results)}")
# show top 10
for r in results[:10]:
  path=r.get('path')
  start=r.get('start',{})
  check=r.get('check_id')
  msg=(r.get('extra',{}) or {}).get('message','')
  sev=((r.get('extra',{}) or {}).get('severity') or '').upper()
  line=start.get('line')
  print(f"- [{sev or 'N/A'}] {check} at {path}:{line} — {msg}")
if len(results)>10:
  print(f"... ({len(results)-10} more)")
PY
      md "\`\`\`"
    else
      md "python3 not available to summarize semgrep JSON; see raw output file (not saved by default)."
    fi

    rm -f "$TMP_JSON"
  else
    md "Semgrep not installed. Install manually (no auto-install):"
    md "\`\`\`bash"
    md "python3 -m pip install --user semgrep"
    md "# or see https://semgrep.dev/docs/getting-started/"
    md "\`\`\`"
  fi
  md ""
fi

# --- Secrets scanning (gitleaks) ---
if [[ -n "$REPO" ]]; then
  md "### Secrets Scan — Gitleaks"
  if have_cmd gitleaks; then
    md "Running gitleaks (repo scan; redacts values by default)..."
    md ""
    md "\`\`\`bash"
    md "gitleaks detect --source <repo> --redact --report-format json"
    md "\`\`\`"

    TMP_JSON=$(mktemp)
    set +e
    gitleaks detect --source "$REPO" --redact --report-format json --report-path "$TMP_JSON" >/dev/null 2>&1
    GITLEAKS_EXIT=$?
    set -e

    if [[ $GITLEAKS_EXIT -ne 0 ]]; then
      STATUS=1
    fi

    if have_cmd python3; then
      md "\nSummary (best-effort):"
      md "\`\`\`"
      python3 - <<'PY' "$TMP_JSON" >>"$OUT" || true
import json,sys
p=sys.argv[1]
try:
  data=json.load(open(p))
except Exception as e:
  print(f"Could not parse gitleaks JSON: {e}")
  raise SystemExit(0)
# gitleaks json can be array
items=data if isinstance(data,list) else data.get('findings',[])
print(f"Findings: {len(items)}")
for f in items[:10]:
  fp=f.get('File','?')
  line=f.get('StartLine','?')
  rule=f.get('RuleID','?')
  desc=f.get('Description','')
  print(f"- {rule} at {fp}:{line} — {desc}")
if len(items)>10:
  print(f"... ({len(items)-10} more)")
PY
      md "\`\`\`"
    else
      md "python3 not available to summarize gitleaks JSON."
    fi

    rm -f "$TMP_JSON"
  else
    md "Gitleaks not installed. Install manually (no auto-install):"
    md "\`\`\`bash"
    md "# see https://github.com/gitleaks/gitleaks#installing"
    md "# mac/linux (example): curl -sSL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_...tar.gz"
    md "\`\`\`"
  fi
  md ""
fi

# --- Dependency scanning ---
if [[ -n "$REPO" ]]; then
  md "### Dependency Scanning"

  # Node
  if [[ -f "$REPO/package.json" ]]; then
    md "#### Node.js (npm/pnpm audit)"
    if have_cmd pnpm && [[ -f "$REPO/pnpm-lock.yaml" ]]; then
      md "Running pnpm audit..."
      md "\`\`\`bash"
      md "(cd <repo> && pnpm audit --prod)"
      md "\`\`\`"
      set +e
      (cd "$REPO" && pnpm audit --prod) >>"$OUT" 2>&1
      PNPM_EXIT=$?
      set -e
      [[ $PNPM_EXIT -ne 0 ]] && STATUS=1
    elif have_cmd npm; then
      md "Running npm audit..."
      md "\`\`\`bash"
      md "(cd <repo> && npm audit --omit=dev)"
      md "\`\`\`"
      set +e
      (cd "$REPO" && npm audit --omit=dev) >>"$OUT" 2>&1
      NPM_EXIT=$?
      set -e
      [[ $NPM_EXIT -ne 0 ]] && STATUS=1
    else
      md "Neither pnpm nor npm found; cannot run Node audit."
    fi
    md ""
  fi

  # Python
  if [[ -f "$REPO/requirements.txt" || -f "$REPO/pyproject.toml" ]]; then
    md "#### Python (pip-audit or basic checks)"
    if have_cmd pip-audit; then
      md "Running pip-audit..."
      md "\`\`\`bash"
      if [[ -f "$REPO/requirements.txt" ]]; then
        md "pip-audit -r requirements.txt"
      else
        md "pip-audit"
      fi
      md "\`\`\`"

      set +e
      if [[ -f "$REPO/requirements.txt" ]]; then
        (cd "$REPO" && pip-audit -r requirements.txt) >>"$OUT" 2>&1
      else
        (cd "$REPO" && pip-audit) >>"$OUT" 2>&1
      fi
      PIP_AUDIT_EXIT=$?
      set -e
      [[ $PIP_AUDIT_EXIT -ne 0 ]] && STATUS=1

    else
      md "pip-audit not installed. Install manually (no auto-install):"
      md "\`\`\`bash"
      md "python3 -m pip install --user pip-audit"
      md "\`\`\`"
      md "Fallback: ensure dependencies are pinned (requirements.txt with versions) and run \`pip list --outdated\` in your venv."
    fi
    md ""
  fi
fi

# --- DAST baseline (ZAP) ---
if [[ -n "$URL" ]]; then
  md "### DAST Baseline"
  md "Target URL: ${URL}"

  # If zap-baseline.py exists in PATH
  if have_cmd zap-baseline.py; then
    md "Running OWASP ZAP baseline scan (zap-baseline.py)..."
    md "\`\`\`bash"
    md "zap-baseline.py -t <url> -r zap-report.html"
    md "\`\`\`"
    ZAP_HTML="$REPORT_DIR/${DATE_LOCAL}-${TARGET}-zap.html"
    set +e
    zap-baseline.py -t "$URL" -r "$ZAP_HTML" >>"$OUT" 2>&1
    ZAP_EXIT=$?
    set -e
    [[ $ZAP_EXIT -ne 0 ]] && STATUS=1
    md "\nZAP HTML report saved at: $ZAP_HTML"

  elif have_cmd zap.sh; then
    md "ZAP CLI found (zap.sh), but baseline helper not found. Consider installing zap-baseline.py from ZAP Docker or packaged scripts."

  else
    md "OWASP ZAP not available in this environment."
    md ""
    md "**Railway-friendly fallback (lightweight, non-invasive):**"
    md "- Fetch \`/robots.txt\`, \`/.well-known/security.txt\` if present"
    md "- Check basic security headers"
    md "- Confirm TLS + redirects behavior (if https)"
    md ""

    if have_cmd curl; then
      md "\`\`\`bash"
      md "curl -sS -D - -o /dev/null <url>"
      md "\`\`\`"

      md "\nHeaders (best-effort):"
      md "\`\`\`"
      curl -sS -D - -o /dev/null "$URL" | sed -n '1,40p' >>"$OUT" || true
      md "\`\`\`"

      for path in /robots.txt /.well-known/security.txt; do
        md "\nGET ${path}:"
        md "\`\`\`"
        curl -sS -L "${URL%/}${path}" | head -n 40 >>"$OUT" || true
        md "\`\`\`"
      done

      md "\nHeader checklist (manual review):"
      md "- Strict-Transport-Security (HSTS)"
      md "- Content-Security-Policy"
      md "- X-Content-Type-Options"
      md "- X-Frame-Options / frame-ancestors"
      md "- Referrer-Policy"
      md "- Permissions-Policy"
    else
      md "curl not available; cannot run fallback header checks."
    fi

    md "\n**How to run full ZAP baseline elsewhere (recommended):**"
    md "\`\`\`bash"
    md "docker run --rm -t owasp/zap2docker-stable zap-baseline.py -t <url> -r zap.html"
    md "\`\`\`"
  fi
  md ""
fi

md "## Overall Status"
if [[ $STATUS -eq 0 ]]; then
  md "✅ No blocking issues detected by the runner (tools may have been missing)."
else
  md "⚠️ Findings detected and/or some checks reported non-zero exit codes. Review sections above."
fi

md ""
md "## Next Actions (Suggested)"
md "- Triage findings by severity and confirm reproducibility."
md "- Fix and re-run this report against the same target."
md "- Add CI wrapper if you want to enforce policy gates."

echo "Wrote report: $OUT"
exit $STATUS
