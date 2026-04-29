#!/bin/bash
set -e

chown -R openclaw:openclaw /data
chmod 700 /data

# Git safe.directory — prevents "dubious ownership" errors on /data/workspace
git config --global --add safe.directory /data/workspace 2>/dev/null || true

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
  exec gosu openclaw node src/server.js
fi

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
