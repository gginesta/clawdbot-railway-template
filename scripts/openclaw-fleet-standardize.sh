#!/usr/bin/env bash
set -euo pipefail

export HOME="${OPENCLAW_RUNTIME_HOME:-/data}"
export OPENCLAW_HOME="${OPENCLAW_HOME:-/data}"
export OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-/data/.openclaw}"
export OPENCLAW_WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-/data/workspace}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/data/.config}"

CHROME_BIN="${OPENCLAW_FLEET_CHROME_BIN:-/usr/bin/google-chrome-stable}"
BRAVE_PLUGIN_SPEC="${OPENCLAW_FLEET_BRAVE_PLUGIN_SPEC:-npm:@openclaw/brave-plugin@2026.5.4}"
PATCH_FILE="$(mktemp)"
trap 'rm -f "$PATCH_FILE"' EXIT

log() { printf '[fleet-standardize] %s\n' "$*" >&2; }

if [ "${OPENCLAW_FLEET_STANDARDIZE:-1}" = "0" ]; then
  log "disabled by OPENCLAW_FLEET_STANDARDIZE=0"
  exit 0
fi

mkdir -p "$OPENCLAW_STATE_DIR" "$XDG_CONFIG_HOME" "$OPENCLAW_WORKSPACE_DIR"

if [ "${OPENCLAW_FLEET_SKIP_CHROME_CHECK:-0}" != "1" ]; then
  if [ ! -x "$CHROME_BIN" ]; then
    log "missing executable Chrome at $CHROME_BIN"
    exit 1
  fi
  "$CHROME_BIN" --version >&2
else
  log "skipping Chrome executable check"
fi

if ! openclaw plugins inspect brave --json >/dev/null 2>&1; then
  log "Brave Search plugin missing; installing $BRAVE_PLUGIN_SPEC"
  openclaw plugins install "$BRAVE_PLUGIN_SPEC"
fi

if ! openclaw plugins inspect brave --json >/dev/null 2>&1; then
  log "Brave Search plugin still unavailable after install"
  exit 1
fi

if [ -n "${BRAVE_API_KEY:-}" ]; then
  SEARCH_PROVIDER="brave"
else
  SEARCH_PROVIDER="duckduckgo"
  log "BRAVE_API_KEY is not present; using keyless duckduckgo search fallback for this container"
fi
export SEARCH_PROVIDER

python3 > "$PATCH_FILE" <<'PY'
import json
import os

search = {
    "enabled": True,
    "provider": os.environ.get("SEARCH_PROVIDER", "duckduckgo"),
    "maxResults": 5,
    "timeoutSeconds": 30,
    "cacheTtlMinutes": 15,
    "openaiCodex": {
        "enabled": True,
        "mode": "cached",
    },
}

entries = {
    "browser": {"enabled": True, "config": {}},
}

if os.environ.get("BRAVE_API_KEY"):
    entries["brave"] = {
        "enabled": True,
        "config": {
            "webSearch": {
                "apiKey": {"source": "env", "provider": "default", "id": "BRAVE_API_KEY"},
            },
        },
    }

if os.environ.get("GEMINI_API_KEY"):
    entries["google"] = {
        "enabled": True,
        "config": {
            "webSearch": {
                "apiKey": {"source": "env", "provider": "default", "id": "GEMINI_API_KEY"},
            },
        },
    }

if os.environ.get("OPENROUTER_API_KEY"):
    entries["perplexity"] = {
        "enabled": True,
        "config": {
            "webSearch": {
                "apiKey": {"source": "env", "provider": "default", "id": "OPENROUTER_API_KEY"},
                "baseUrl": "https://openrouter.ai/api/v1",
                "model": "perplexity/sonar-pro",
            },
        },
    }

patch = {
    "browser": {
        "enabled": True,
        "executablePath": "/usr/bin/google-chrome-stable",
        "headless": True,
        "noSandbox": True,
        "attachOnly": False,
        "defaultProfile": "openclaw",
        "localLaunchTimeoutMs": 30000,
        "localCdpReadyTimeoutMs": 15000,
    },
    "tools": {"web": {"search": search}},
    "plugins": {"entries": entries},
}

print(json.dumps(patch, indent=2))
PY

openclaw config patch --file "$PATCH_FILE" --dry-run --json >/dev/null
openclaw config patch --file "$PATCH_FILE" >/dev/null
openclaw config validate >/dev/null
log "browser/search standard applied with provider=$SEARCH_PROVIDER"
