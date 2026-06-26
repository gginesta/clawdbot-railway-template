FROM node:22-bookworm

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    gnupg \
    gosu \
    procps \
    python3 \
    build-essential \
    zip \
    supervisor \
    tini \
  && rm -rf /var/lib/apt/lists/*

# Install Google Chrome Stable for OpenClaw browser automation
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg \
  && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] https://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    google-chrome-stable \
    fonts-liberation \
  && /usr/bin/google-chrome-stable --version \
  && ln -sf /usr/bin/google-chrome-stable /usr/bin/chromium \
  && ln -sf /usr/bin/google-chrome-stable /usr/bin/brave-browser \
  && /usr/bin/chromium --version \
  && /usr/bin/brave-browser --version \
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

ARG OPENCLAW_VERSION=2026.6.10
ARG CACHE_BUST=1782500966
RUN echo "Installing OpenClaw ${OPENCLAW_VERSION} (cache bust ${CACHE_BUST})" \
  && node -e "const [major, minor] = process.versions.node.split('.').map(Number); if (major !== 22 || minor < 19) { throw new Error('OpenClaw requires Node.js 22.19+; found ' + process.versions.node); }" \
  && npm install -g --force openclaw@${OPENCLAW_VERSION} @railway/cli \
  && node -p "require('/usr/local/lib/node_modules/openclaw/package.json').version" | grep -Fx "${OPENCLAW_VERSION}" \
  && npm install --prefix /usr/local/lib/node_modules/openclaw sharp

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

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile --prod

COPY src ./src
COPY --chmod=755 entrypoint.sh ./entrypoint.sh
COPY --chmod=755 scripts/openclaw-start-guard.sh /usr/local/bin/openclaw-start-guard.sh
COPY --chmod=755 scripts/openclaw-browser-profile-guard.sh /usr/local/bin/openclaw-browser-profile-guard.sh
COPY --chmod=755 scripts/syncthing-start-guard.sh /usr/local/bin/syncthing-start-guard.sh
COPY --chmod=755 scripts/openclaw-fleet-standardize.sh /usr/local/bin/openclaw-fleet-standardize.sh
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
ENTRYPOINT ["tini", "--", "./entrypoint.sh"]
