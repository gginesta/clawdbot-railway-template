FROM node:22-bookworm

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    gosu \
    procps \
    python3 \
    build-essential \
    zip \
    supervisor \
  && rm -rf /var/lib/apt/lists/*

# Install Tailscale
RUN curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null \
  && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list \
  && apt-get update \
  && apt-get install -y tailscale \
  && rm -rf /var/lib/apt/lists/*

# Install Syncthing
RUN curl -fsSL https://syncthing.net/release-key.gpg | tee /usr/share/keyrings/syncthing-archive-keyring.gpg >/dev/null \
  && echo "deb [signed-by=/usr/share/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable" | tee /etc/apt/sources.list.d/syncthing.list \
  && apt-get update \
  && apt-get install -y syncthing \
  && rm -rf /var/lib/apt/lists/*

ARG OPENCLAW_VERSION=2026.4.25
ARG CACHE_BUST=1777337021
RUN npm install -g openclaw@${OPENCLAW_VERSION} @railway/cli

# Write tailscale-up one-shot script
RUN printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -euo pipefail' \
  '' \
  'echo "[tailscale-up] starting"' \
  ': "${TAILSCALE_AUTHKEY:?TAILSCALE_AUTHKEY is required}"' \
  'mkdir -p "${TAILSCALE_STATE_DIR:-/data/.tailscale}"' \
  '' \
  '# Wait for tailscaled socket' \
  'for i in $(seq 1 30); do' \
  '  [ -S /tmp/tailscaled.sock ] && break' \
  '  echo "[tailscale-up] waiting for tailscaled ($i/30)..."' \
  '  sleep 1' \
  'done' \
  '' \
  'tailscale --socket=/tmp/tailscaled.sock up \\' \
  '  --authkey="${TAILSCALE_AUTHKEY}" \\' \
  '  --hostname="${TAILSCALE_HOSTNAME:-openclaw}" \\' \
  '  --accept-routes \\' \
  '  --reset' \
  '' \
  'echo "[tailscale-up] done"' \
  > /usr/local/bin/tailscale-up.sh \
  && chmod +x /usr/local/bin/tailscale-up.sh

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile --prod

COPY src ./src
COPY --chmod=755 entrypoint.sh ./entrypoint.sh
COPY config/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN useradd -m -s /bin/bash openclaw \
  && chown -R openclaw:openclaw /app \
  && mkdir -p /data && chown openclaw:openclaw /data \
  && mkdir -p /home/linuxbrew/.linuxbrew && chown -R openclaw:openclaw /home/linuxbrew

USER openclaw
RUN NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

ENV PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:${PATH}"
ENV HOMEBREW_PREFIX="/home/linuxbrew/.linuxbrew"
ENV HOMEBREW_CELLAR="/home/linuxbrew/.linuxbrew/Cellar"
ENV HOMEBREW_REPOSITORY="/home/linuxbrew/.linuxbrew/Homebrew"

ENV PORT=8080
ENV OPENCLAW_ENTRY=/usr/local/lib/node_modules/openclaw/dist/entry.js

# Persistence: runtime npm/pnpm installs survive redeploys
ENV NPM_CONFIG_PREFIX=/data/npm
ENV PNPM_HOME=/data/pnpm
ENV PNPM_STORE_DIR=/data/pnpm-store

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -f http://localhost:8080/setup/healthz || exit 1

USER root
ENTRYPOINT ["./entrypoint.sh"]
