#!/usr/bin/env python3
"""skill-gen.py

Phase 1 (MVP) Endpoint Extractor & API Skill Generator for Unbrowse DIY.

Reads CDP capture JSONL produced by cdp-capture.js and generates a reusable
OpenClaw-style API skill directory:
  /data/shared/api-skills/{domain}/

Outputs:
  - SKILL.md
  - api.sh
  - endpoints.json
  - .meta.json
  - scripts/{resource}-{action}.sh

Constraints:
  - No external pip packages.
  - Never hardcode credentials (only reference env vars).

Usage:
  python3 skill-gen.py --input /data/workspace/data/captures/hubspot-*.jsonl --domain hubspot.com
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse

SKILL_VERSION = "1.0.0"

CAPTURE_VERSION_SUPPORTED = {1}

GENERIC_SEGMENTS = {
    "api", "rest", "graphql", "rpc", "services", "service",
    "v1", "v2", "v3", "v4", "v5",
    "oauth", "auth", "login", "token",
}

TRACKING_QUERY_KEYS_PREFIX = ("utm_",)
TRACKING_QUERY_KEYS = {"gclid", "fbclid", "msclkid"}

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
MONGO_RE = re.compile(r"^[0-9a-f]{24}$", re.I)
HEX_LONG_RE = re.compile(r"^[0-9a-f]{16,}$", re.I)
NUM_RE = re.compile(r"^\d{2,}$")


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def read_jsonl(paths: List[str]) -> Iterable[Dict[str, Any]]:
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception as ex:
                        eprint(f"[skill-gen] Skipping bad JSON in {p}:{line_no}: {ex}")
                        continue
                    yield obj
        except FileNotFoundError:
            eprint(f"[skill-gen] Missing input file: {p}")


def norm_host(host: str) -> str:
    return host.lower().strip(".")


def is_probable_id_segment(seg: str) -> bool:
    if not seg:
        return False
    s = seg.strip()
    sl = s.lower()

    # Keep common version markers
    if re.fullmatch(r"v\d+", sl):
        return False

    if UUID_RE.match(sl):
        return True
    if MONGO_RE.match(sl):
        return True
    if HEX_LONG_RE.match(sl):
        return True
    if NUM_RE.match(sl):
        # Avoid replacing years like 2024? (still often IDs, but keep a soft exception)
        if len(sl) == 4 and sl.startswith("20"):
            return False
        return True

    # Very long mixed tokens (often opaque IDs)
    if len(s) >= 18 and re.fullmatch(r"[A-Za-z0-9_-]+", s):
        return True

    return False


def normalize_path(path: str) -> str:
    parts = [p for p in path.split("/") if p]
    out = []
    for p in parts:
        if is_probable_id_segment(p):
            out.append("{id}")
        else:
            out.append(p)
    return "/" + "/".join(out)


def normalize_query(query: str) -> Tuple[str, List[str]]:
    """Return normalized query string (values removed) and list of param keys."""
    if not query:
        return "", []
    pairs = []
    keys = []
    for k, v in parse_qsl(query, keep_blank_values=True):
        kl = k.lower()
        if kl in TRACKING_QUERY_KEYS or any(kl.startswith(p) for p in TRACKING_QUERY_KEYS_PREFIX):
            continue
        keys.append(k)
        # We normalize by keeping key but blank value
        pairs.append((k, ""))
    if not pairs:
        return "", sorted(set(keys))
    pairs.sort(key=lambda kv: kv[0])
    return "?" + urlencode(pairs), sorted(set(keys))


def normalize_url(url: str) -> Tuple[str, str, str, List[str]]:
    """Return (scheme, host, normalized_path_with_query, query_keys)."""
    u = urlparse(url)
    scheme = u.scheme or "https"
    host = norm_host(u.netloc)
    npath = normalize_path(u.path or "/")
    nquery, qkeys = normalize_query(u.query or "")
    return scheme, host, npath + nquery, qkeys


def resource_from_path(path: str) -> str:
    """Best-effort resource inference for clustering."""
    segs = [s for s in path.split("/") if s and s != "{id}"]
    if not segs:
        return "root"

    # Prefer pattern /api/v3/objects/deals/{id}
    if "objects" in segs:
        idx = segs.index("objects")
        if idx + 1 < len(segs):
            return segs[idx + 1]

    # Skip generic prefixes
    for s in segs:
        sl = s.lower()
        if sl in GENERIC_SEGMENTS:
            continue
        return sl

    return segs[-1].lower()


def action_from(method: str, norm_path: str) -> str:
    m = method.upper()
    p = norm_path

    # Detect common special actions
    if p.endswith("/search") or "/search?" in p:
        return "search"
    if p.endswith("/batch"):
        return "batch"

    if m == "GET":
        return "get" if p.rstrip("/").endswith("/{id}") else "list"
    if m == "POST":
        return "create"
    if m in ("PUT", "PATCH"):
        return "update"
    if m == "DELETE":
        return "delete"
    return m.lower()


@dataclass
class AuthInfo:
    kind: str  # bearer | api_key | cookie | basic | none | unknown
    header_name: Optional[str] = None


def detect_auth(captures: List[Dict[str, Any]]) -> AuthInfo:
    """Detect predominant auth style from captured request headers."""
    bearer = 0
    basic = 0
    cookie = 0
    api_key_headers = Counter()

    for cap in captures:
        req = (cap.get("request") or {})
        headers = (req.get("headers") or {})
        # Normalize to lower-case keys for matching
        lh = {str(k).lower(): str(v) for k, v in headers.items()}

        auth = lh.get("authorization", "")
        if auth.lower().startswith("bearer "):
            bearer += 1
        elif auth.lower().startswith("basic "):
            basic += 1

        if "cookie" in lh and lh.get("cookie"):
            cookie += 1

        for k in lh.keys():
            if k in ("x-api-key", "x-apikey", "api-key", "apikey"):
                api_key_headers[k] += 1
            if k.startswith("x-") and "key" in k and k not in ("x-requested-with",):
                api_key_headers[k] += 1

    if bearer:
        return AuthInfo(kind="bearer", header_name="authorization")
    if basic:
        return AuthInfo(kind="basic", header_name="authorization")
    if api_key_headers:
        header_name, _ = api_key_headers.most_common(1)[0]
        return AuthInfo(kind="api_key", header_name=header_name)
    if cookie:
        return AuthInfo(kind="cookie", header_name="cookie")
    if captures:
        return AuthInfo(kind="unknown", header_name=None)
    return AuthInfo(kind="none", header_name=None)


def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in (headers or {}).items():
        kl = str(k).lower()
        if kl in ("authorization", "cookie", "x-api-key", "api-key", "apikey"):
            out[k] = "<redacted>"
            continue
        if "token" in kl or "secret" in kl or "key" == kl:
            out[k] = "<redacted>"
            continue
        if len(str(v)) > 200:
            out[k] = str(v)[:200] + "…"
        else:
            out[k] = str(v)
    return out


def confidence_score(count: int, is_json: bool) -> int:
    # Simple, predictable scoring for MVP.
    score = 10
    if is_json:
        score += 50
    score += min(40, count * 10)  # repeated use increases confidence
    return min(100, score)


def safe_filename(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "endpoint"


SCRIPT_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

DOMAIN={domain_q}
ENV_FILE="/data/workspace/credentials/api-auth/${DOMAIN}.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
else
  echo "Missing credentials env: $ENV_FILE" >&2
  echo "Create it based on the template printed in SKILL.md" >&2
  exit 2
fi

: "${BASE_URL:?Set BASE_URL (e.g., https://api.example.com) in $ENV_FILE}"

METHOD={method_q}
PATH_TEMPLATE={path_q}

ID=""
LIMIT=""
QUERY=""     # raw query string, e.g. "foo=bar&baz=1"
DATA=""      # JSON string or @file
DRY_RUN=0
RAW=0

EXTRA_HEADERS=()

usage() {
  cat >&2 <<'USAGE'
Usage:
  {script_name} [--id VALUE] [--limit N] [--query "a=b&c=d"] [--data JSON|@file] [--dry-run] [--raw]

Flags:
  --id        Value to substitute for {id} in the URL path (if present)
  --limit     Adds limit=N query parameter
  --query     Additional raw query string appended to the request
  --data      Request JSON body (for POST/PUT/PATCH). Use @file to read from file.
  --dry-run   Print the curl command and exit
  --raw       Print raw response (no jq formatting)
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id) ID="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --query) QUERY="$2"; shift 2 ;;
    --data) DATA="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift 1 ;;
    --raw) RAW=1; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

URL="${BASE_URL}${PATH_TEMPLATE}"

if [[ "$URL" == *"{id}"* ]]; then
  if [[ -z "$ID" ]]; then
    echo "This endpoint requires --id" >&2
    exit 2
  fi
  URL="${URL//\\{id\\}/$ID}"
fi

# Build query string
QS=""
add_q() {
  local kv="$1"
  if [[ -z "$kv" ]]; then return 0; fi
  if [[ -z "$QS" ]]; then QS="?${kv}"; else QS="${QS}&${kv}"; fi
}

if [[ -n "$LIMIT" ]]; then add_q "limit=${LIMIT}"; fi
if [[ -n "$QUERY" ]]; then
  # Allow user to pass leading '?' or '&'
  local_q="$QUERY"
  local_q="${local_q#\?}"
  local_q="${local_q#\&}"
  add_q "$local_q"
fi

# Auth headers (based on capture detection)
AUTH_HEADERS=()
{auth_block}

# Data handling
DATA_ARGS=()
if [[ -n "$DATA" ]]; then
  if [[ "$DATA" == @* ]]; then
    f="${DATA#@}"
    if [[ ! -f "$f" ]]; then
      echo "--data file not found: $f" >&2
      exit 2
    fi
    DATA_ARGS+=( -H "Content-Type: application/json" --data-binary "@${f}" )
  else
    DATA_ARGS+=( -H "Content-Type: application/json" --data "$DATA" )
  fi
fi

# Execute request while preserving clean JSON output
TMP_BODY="$(mktemp)"
HTTP_CODE=""

CURL_CMD=(curl -sS -X "$METHOD" "${URL}${QS}" \
  -H "Accept: application/json" \
  "${AUTH_HEADERS[@]}" \
  "${EXTRA_HEADERS[@]}" \
  "${DATA_ARGS[@]}" \
  -o "$TMP_BODY" -w "%{http_code}")

if [[ $DRY_RUN -eq 1 ]]; then
  printf '%q ' "${CURL_CMD[@]}"; echo
  rm -f "$TMP_BODY"
  exit 0
fi

HTTP_CODE="$( "${CURL_CMD[@]}" )"

if [[ ! "$HTTP_CODE" =~ ^[0-9]{3}$ ]]; then
  echo "Request failed (no HTTP code)." >&2
  cat "$TMP_BODY" >&2 || true
  rm -f "$TMP_BODY"
  exit 1
fi

if [[ "$HTTP_CODE" -ge 400 ]]; then
  echo "HTTP $HTTP_CODE" >&2
  cat "$TMP_BODY" >&2 || true
  rm -f "$TMP_BODY"
  exit 22
fi

if [[ $RAW -eq 1 ]]; then
  cat "$TMP_BODY"
  rm -f "$TMP_BODY"
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  # jq will exit non-zero for non-JSON; fall back to raw
  if jq -e . >/dev/null 2>&1 < "$TMP_BODY"; then
    jq . < "$TMP_BODY"
  else
    cat "$TMP_BODY"
  fi
else
  cat "$TMP_BODY"
fi

rm -f "$TMP_BODY"
"""


def build_auth_block(auth: AuthInfo) -> str:
    # IMPORTANT: these reference env vars only. Never include captured values.
    if auth.kind == "bearer":
        return (
            "if [[ -n \"${BEARER_TOKEN:-}\" ]]; then\n"
            "  AUTH_HEADERS+=( -H \"Authorization: Bearer ${BEARER_TOKEN}\" )\n"
            "fi\n"
        )
    if auth.kind == "basic":
        return (
            "if [[ -n \"${BASIC_AUTH:-}\" ]]; then\n"
            "  AUTH_HEADERS+=( -H \"Authorization: Basic ${BASIC_AUTH}\" )\n"
            "fi\n"
        )
    if auth.kind == "api_key":
        # If we detected a specific header name, use that.
        header = auth.header_name or "x-api-key"
        # preserve original-ish casing for readability
        header_out = "X-API-Key" if header.lower() == "x-api-key" else header
        return (
            "if [[ -n \"${API_KEY:-}\" ]]; then\n"
            f"  AUTH_HEADERS+=( -H \"{header_out}: ${{API_KEY}}\" )\n"
            "fi\n"
        )
    if auth.kind == "cookie":
        return (
            "if [[ -n \"${COOKIE:-}\" ]]; then\n"
            "  AUTH_HEADERS+=( -H \"Cookie: ${COOKIE}\" )\n"
            "fi\n"
        )
    # unknown/none: provide nothing by default
    return "# No auth headers automatically added (auth not detected)\n"


def write_file(p: str, content: str) -> None:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


def chmod_x(p: str) -> None:
    try:
        st = os.stat(p)
        os.chmod(p, st.st_mode | 0o111)
    except Exception:
        # Not fatal in some environments; wrapper script will also chmod.
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate API skills from CDP capture JSONL")
    ap.add_argument("--input", required=True, nargs="+", help="Input JSONL capture file(s) or globs")
    ap.add_argument("--domain", required=True, help="Domain (e.g., hubspot.com)")
    args = ap.parse_args()

    domain = norm_host(args.domain)

    # Expand globs
    inputs: List[str] = []
    for item in args.input:
        if any(ch in item for ch in "*?["):
            inputs.extend(sorted(glob.glob(item)))
        else:
            inputs.append(item)

    inputs = [p for p in inputs if p]
    if not inputs:
        eprint("[skill-gen] No input files matched.")
        return 2

    captures_raw = list(read_jsonl(inputs))
    if not captures_raw:
        eprint("[skill-gen] No captures found (empty inputs).")
        return 2

    # Filter captures that actually belong to this domain (host endswith domain)
    captures: List[Dict[str, Any]] = []
    for cap in captures_raw:
        req = cap.get("request") or {}
        url = req.get("url")
        if not url:
            continue
        u = urlparse(url)
        host = norm_host(u.netloc)
        if host == domain or host.endswith("." + domain):
            captures.append(cap)

    if not captures:
        eprint(f"[skill-gen] No captures matched domain={domain}. (Inputs had {len(captures_raw)} lines)")
        return 2

    auth = detect_auth(captures)

    # Pick base host as the most frequent host within domain
    host_counts = Counter()
    scheme_counts = Counter()
    for cap in captures:
        url = (cap.get("request") or {}).get("url")
        if not url:
            continue
        u = urlparse(url)
        host_counts[norm_host(u.netloc)] += 1
        scheme_counts[u.scheme or "https"] += 1

    base_host = host_counts.most_common(1)[0][0]
    base_scheme = scheme_counts.most_common(1)[0][0]
    base_url_default = f"{base_scheme}://{base_host}"

    # Aggregate endpoints
    endpoint_counts: Counter[Tuple[str, str]] = Counter()  # (method, norm_path_query)
    endpoint_query_keys: Dict[Tuple[str, str], Counter[str]] = defaultdict(Counter)
    endpoint_samples: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for cap in captures:
        req = cap.get("request") or {}
        resp = cap.get("response") or {}
        url = req.get("url")
        method = (req.get("method") or "GET").upper()
        if not url:
            continue

        scheme, host, norm_pq, qkeys = normalize_url(url)
        # Keep only for dominant host for MVP generation (avoid mixing app/api subdomains)
        if host != base_host:
            continue

        key = (method, norm_pq)
        endpoint_counts[key] += 1
        for k in qkeys:
            endpoint_query_keys[key][k] += 1
        if key not in endpoint_samples:
            endpoint_samples[key] = {
                "request": req,
                "response": resp,
                "normalized": {"scheme": scheme, "host": host, "path_query": norm_pq},
            }

    if not endpoint_counts:
        eprint("[skill-gen] No endpoints remained after filtering to dominant host.")
        return 2

    # Build catalog
    endpoints = []
    script_names = Counter()

    for (method, norm_pq), count in endpoint_counts.most_common():
        sample = endpoint_samples[(method, norm_pq)]
        resp = sample.get("response") or {}
        is_json = bool(resp.get("isJson"))

        norm_path_only = norm_pq.split("?")[0]
        resource = resource_from_path(norm_path_only)
        action = action_from(method, norm_pq)

        score = confidence_score(count=count, is_json=is_json)

        qk_counts = endpoint_query_keys[(method, norm_pq)]
        common_qkeys = [k for (k, c) in qk_counts.most_common() if c >= max(2, int(count * 0.3))]

        script_base = safe_filename(f"{resource}-{action}")
        script_names[script_base] += 1
        script_name = script_base if script_names[script_base] == 1 else f"{script_base}-{script_names[script_base]}"

        endpoints.append({
            "id": f"{method} {norm_pq}",
            "method": method,
            "path_template": norm_pq,  # includes normalized query keys (values removed)
            "path": norm_path_only,
            "resource": resource,
            "action": action,
            "count": count,
            "confidence": score,
            "host": base_host,
            "base_url": base_url_default,
            "query_params_common": common_qkeys,
            "auth": {"kind": auth.kind, "header_name": auth.header_name},
            "sample_request_headers": sanitize_headers((sample.get("request") or {}).get("headers") or {}),
            "sample_status": (sample.get("response") or {}).get("status"),
            "script": f"scripts/{script_name}.sh",
        })

    out_dir = f"/data/shared/api-skills/{domain}"
    scripts_dir = os.path.join(out_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    # Write endpoints.json
    endpoints_path = os.path.join(out_dir, "endpoints.json")
    write_file(endpoints_path, json.dumps({"domain": domain, "generated_at": datetime.now(timezone.utc).isoformat(), "endpoints": endpoints}, indent=2) + "\n")

    # Write .meta.json
    meta_path = os.path.join(out_dir, ".meta.json")
    meta = {
        "version": SKILL_VERSION,
        "domain": domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_files": inputs,
        "capture_lines_total": len(captures_raw),
        "capture_lines_matched_domain": len(captures),
        "base_url_default": base_url_default,
        "auth_detected": {"kind": auth.kind, "header_name": auth.header_name},
    }
    write_file(meta_path, json.dumps(meta, indent=2) + "\n")

    # Generate scripts
    auth_block = build_auth_block(auth)
    generated_scripts = []
    for ep in endpoints:
        script_rel = ep["script"]
        script_path = os.path.join(out_dir, script_rel)
        script_name = os.path.basename(script_path)

        content = SCRIPT_TEMPLATE
        content = content.replace("{domain_q}", json.dumps(domain))
        content = content.replace("{method_q}", json.dumps(ep["method"]))
        content = content.replace("{path_q}", json.dumps(ep["path_template"].split("?")[0]))
        content = content.replace("{auth_block}", auth_block.rstrip())
        content = content.replace("{script_name}", script_name)
        write_file(script_path, content)
        chmod_x(script_path)
        generated_scripts.append(script_rel)

    # Write api.sh dispatcher
    api_sh = f"""#!/usr/bin/env bash
set -euo pipefail

# Auto-generated dispatcher for {domain}
#
# Examples:
#   ./api.sh deals list --limit 10
#   ./api.sh deals get --id 123
#
# It dispatches to scripts/<resource>-<action>.sh.

DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"

usage() {{
  cat >&2 <<'USAGE'
Usage:
  api.sh <resource> <action> [args...]

Examples:
  api.sh deals list --limit 10
  api.sh deals get --id 123

To see available endpoints:
  ls -1 "$DIR/scripts"
USAGE
}}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

RESOURCE="$1"; ACTION="$2"; shift 2

SCRIPT_GLOB="$DIR/scripts/${{RESOURCE}}-${{ACTION}}*.sh"
MATCHES=( $SCRIPT_GLOB )

if [[ ! -e "${{MATCHES[0]}}" ]]; then
  echo "No matching script for resource='${{RESOURCE}}' action='${{ACTION}}'" >&2
  echo "Available scripts:" >&2
  ls -1 "$DIR/scripts" >&2
  exit 2
fi

# If multiple matches exist, use the first (scripts are de-duplicated with suffixes).
exec "${{MATCHES[0]}}" "$@"
"""
    api_path = os.path.join(out_dir, "api.sh")
    write_file(api_path, api_sh)
    chmod_x(api_path)

    # Write SKILL.md
    env_template_lines = [
        f"# {domain}.env",
        "# Save as: /data/workspace/credentials/api-auth/{domain}.env".format(domain=domain),
        "# Do NOT commit this file.",
        "",
        f"BASE_URL=\"{base_url_default}\"",
    ]
    if auth.kind == "bearer":
        env_template_lines.append("BEARER_TOKEN=\"\"")
    elif auth.kind == "basic":
        env_template_lines.append("BASIC_AUTH=\"\"  # base64(user:pass)")
    elif auth.kind == "api_key":
        env_template_lines.append("API_KEY=\"\"")
    elif auth.kind == "cookie":
        env_template_lines.append("COOKIE=\"\"")
    else:
        env_template_lines.extend([
            "# Auth not detected reliably. Add one of:",
            "# BEARER_TOKEN=\"...\"",
            "# API_KEY=\"...\"",
            "# COOKIE=\"...\"",
        ])

    skill_md = f"""# API Skill: {domain}

Generated by `skill-gen.py` (Phase 1 MVP) from CDP network captures.

## What you get

- `api.sh` — dispatcher: `./api.sh <resource> <action> [args...]`
- `scripts/*.sh` — individual endpoint scripts
- `endpoints.json` — machine-readable endpoint catalog

## Credentials

Create this file:

`/data/workspace/credentials/api-auth/{domain}.env`

Template:

```bash
{os.linesep.join(env_template_lines)}
```

## Usage examples

List available endpoint scripts:

```bash
ls -1 scripts/
```

Call via dispatcher:

```bash
./api.sh <resource> <action> --help
./api.sh {endpoints[0]['resource']} {endpoints[0]['action']} --dry-run
```

Call a specific endpoint script:

```bash
./{endpoints[0]['script']} --help
```

## Notes / MVP limitations

- URL normalization replaces likely IDs with `{{id}}`. Always verify templates.
- Query params are not fully parameterized yet; use `--query "a=b&c=d"`.
- Auth detection is best-effort; you may need to adjust env vars or scripts.
"""
    skill_path = os.path.join(out_dir, "SKILL.md")
    write_file(skill_path, skill_md)

    # Try to chmod top-level scripts
    chmod_x(skill_path)  # harmless

    eprint(f"[skill-gen] Wrote skill to: {out_dir}")
    eprint(f"[skill-gen] Endpoints: {len(endpoints)} (scripts: {len(generated_scripts)})")
    eprint(f"[skill-gen] Auth detected: {auth.kind}{' (' + auth.header_name + ')' if auth.header_name else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
