#!/bin/bash
set -e

export HOME="${OPENCLAW_RUNTIME_HOME:-/data}"
export OPENCLAW_HOME="${OPENCLAW_HOME:-/data}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/data/.config}"

mkdir -p "$HOME" "$XDG_CONFIG_HOME"
# Targeted ownership repair: avoid expensive recursive chown of all shared/project data.
for dir in /data/.openclaw /data/workspace /data/.syncthing /data/npm /data/.npm /data/pnpm /data/pnpm-store /data/.config /data/.cache /data/.local; do
  if [ -e "$dir" ]; then
    chown -R openclaw:openclaw "$dir"
  fi
done
chown openclaw:openclaw /data
chmod 700 /data

# Git safe.directory — prevents "dubious ownership" errors on /data/workspace
gosu openclaw git config --global --add safe.directory /data/workspace 2>/dev/null || true

# Converge durable fleet browser/search infrastructure before the Gateway starts.
gosu openclaw /usr/local/bin/openclaw-fleet-standardize.sh

# Set GitHub remote URL with current token (if set)
if [ -n "${GITHUB_API_TOKEN}" ] && [ -d /data/workspace/.git ]; then
  git -C /data/workspace remote set-url backup \
    "https://gginesta:${GITHUB_API_TOKEN}@github.com/gginesta/clawdbot-railway-template.git" 2>/dev/null || true
fi

if [ ! -d /data/.linuxbrew ]; then
  cp -a /home/linuxbrew/.linuxbrew /data/.linuxbrew
fi

rm -rf /home/linuxbrew/.linuxbrew
ln -sfn /data/.linuxbrew /home/linuxbrew/.linuxbrew

if [ "${OPENCLAW_DIRECT_RUN:-}" = "1" ]; then
  exec /usr/local/bin/openclaw-start-guard.sh
fi

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
