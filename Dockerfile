# Build openclaw from source to avoid npm packaging gaps (some dist files are not shipped).
FROM node:22-bookworm AS openclaw-build

# Dependencies needed for openclaw build
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    curl \
    python3 \
    make \
    g++ \
  && rm -rf /var/lib/apt/lists/*

# Install Bun (openclaw build uses it)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN corepack enable

WORKDIR /openclaw

# Pin to a known-good ref (tag/branch). Override in Railway template settings if needed.
# Using a released tag avoids build breakage when `main` temporarily references unpublished packages.
ARG OPENCLAW_GIT_REF=v2026.2.21
RUN git clone --depth 1 --branch "${OPENCLAW_GIT_REF}" https://github.com/openclaw/openclaw.git .

# Patch: relax version requirements for packages that may reference unpublished versions.
# Apply to all extension package.json files to handle workspace protocol (workspace:*).
RUN set -eux; \
  find ./extensions -name 'package.json' -type f | while read -r f; do \
    sed -i -E 's/"openclaw"[[:space:]]*:[[:space:]]*">=[^"]+"/\"openclaw\": \"*\"/g' "$f"; \
    sed -i -E 's/"openclaw"[[:space:]]*:[[:space:]]*"workspace:[^"]+"/\"openclaw\": \"*\"/g' "$f"; \
  done

RUN pnpm install --no-frozen-lockfile
RUN pnpm build
ENV OPENCLAW_PREFER_PNPM=1
RUN pnpm ui:install && pnpm ui:build


# Runtime image
FROM node:22-bookworm
ENV NODE_ENV=production

# Install OS deps + Syncthing
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    chromium \
    chromium-sandbox \
    fonts-liberation \
    fonts-noto-color-emoji \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    syncthing \
    supervisor \
    python3 \
    python3-pip \
    python3-venv \
    python-is-python3 \
  && rm -rf /var/lib/apt/lists/*

# Install Tailscale (Debian repo does not include it by default)
RUN set -eux; \
  mkdir -p /usr/share/keyrings; \
  curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg \
    -o /usr/share/keyrings/tailscale-archive-keyring.gpg; \
  curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list \
    -o /etc/apt/sources.list.d/tailscale.list; \
  apt-get update; \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tailscale; \
  rm -rf /var/lib/apt/lists/*

# Install Brave browser (works better than Chromium with OpenClaw browser control)
RUN set -eux; \
  curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg \
    https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg; \
  echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" \
    > /etc/apt/sources.list.d/brave-browser-release.list; \
  apt-get update; \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends brave-browser; \
  rm -rf /var/lib/apt/lists/*


# Install gogcli (Google Workspace CLI for Gmail, Calendar, Drive)
# Baked in so it survives container restarts/redeployments
RUN set -eux; \
  curl -fsSL https://github.com/steipete/gogcli/releases/download/v0.11.0/gogcli_0.11.0_linux_amd64.tar.gz \
    -o /tmp/gogcli.tar.gz; \
  tar -xzf /tmp/gogcli.tar.gz -C /usr/local/bin gog; \
  chmod +x /usr/local/bin/gog; \
  rm /tmp/gogcli.tar.gz

# `openclaw update` expects pnpm. Provide it in the runtime image.
RUN corepack enable && corepack prepare pnpm@10.23.0 --activate

# Install Bun + QMD (memory search backend) in runtime image
# QMD provides hybrid BM25 + vector search for OpenClaw memory
RUN curl -fsSL https://bun.sh/install | bash \
  && /root/.bun/bin/bun install -g @tobilu/qmd \
  && ln -sf /root/.bun/bin/qmd /usr/local/bin/qmd
ENV PATH="/root/.bun/bin:${PATH}"

ENV CHROME_PATH=/usr/bin/chromium
ENV BRAVE_PATH=/usr/bin/brave-browser
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV CHROMIUM_USER_DATA_DIR=/data/.chromium

# Syncthing config - data persists on Railway volume
ENV SYNCTHING_HOME=/data/.syncthing
ENV STNODEFAULTFOLDER=1

# Tailscale state (persist on Railway volume)
ENV TAILSCALE_STATE_DIR=/data/.tailscale

WORKDIR /app

# Wrapper deps
COPY package.json ./
RUN npm install --omit=dev && npm cache clean --force

# Copy built openclaw
COPY --from=openclaw-build /openclaw /openclaw

# Provide an openclaw executable
RUN printf '%s\n' '#!/usr/bin/env bash' 'exec node /openclaw/dist/entry.js "$@"' > /usr/local/bin/openclaw \
  && chmod +x /usr/local/bin/openclaw

COPY src ./src

# Supervisor config for running multiple processes
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Helper to bring Tailscale up on container start (userspace networking; no /dev/net/tun needed)
RUN printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -euo pipefail' \
  '' \
  'echo "[tailscale-up] starting"' \
  ': "${TAILSCALE_AUTHKEY:?TAILSCALE_AUTHKEY is required}"' \
  'mkdir -p "${TAILSCALE_STATE_DIR:-/data/.tailscale}"' \
  '' \
  '# Wait for tailscaled socket' \
  'for i in $(seq 1 200); do' \
  '  if [ -S /tmp/tailscaled.sock ]; then break; fi' \
  '  if [ $i -eq 200 ]; then echo "[tailscale-up] ERROR: tailscaled socket not found" >&2; exit 1; fi' \
  '  sleep 0.1' \
  'done' \
  '' \
  'HOSTNAME_ARG=""' \
  'if [ -n "${TAILSCALE_HOSTNAME:-}" ]; then HOSTNAME_ARG="--hostname=${TAILSCALE_HOSTNAME}"; fi' \
  '' \
  '# Try tailscale up (supervisord will retry if this exits non-zero)' \
  'set -x' \
  'tailscale --socket=/tmp/tailscaled.sock up --reset \' \
  '  --authkey="${TAILSCALE_AUTHKEY}" \' \
  '  ${HOSTNAME_ARG} \' \
  '  --accept-dns=false --accept-routes=false' \
  'set +x' \
  '' \
  'echo "[tailscale-up] up complete; status:"' \
  'tailscale --socket=/tmp/tailscaled.sock status || true' \
  'tailscale --socket=/tmp/tailscaled.sock set --shields-up=false || true' \
  'tailscale --socket=/tmp/tailscaled.sock serve --bg --tcp=8384 127.0.0.1:8384 || true' \
  > /usr/local/bin/tailscale-up.sh \
  && chmod +x /usr/local/bin/tailscale-up.sh

# The wrapper listens on this port
ENV OPENCLAW_PUBLIC_PORT=8080
ENV PORT=8080

# Ports:
# 8080 = OpenClaw web UI (proxied)
# 8384 = Syncthing web UI
# 22000 = Syncthing sync protocol
EXPOSE 8080 8384 22000/tcp 22000/udp

# Use supervisor to run both OpenClaw and Syncthing

# Startup cleanup script — clears stale browser singleton lock files
# These persist on the Railway volume across container restarts and block Brave from starting
RUN printf '%s\n' \
  '#!/usr/bin/env bash' \
  '# Clear stale Brave/Chrome singleton locks left by previous container instances' \
  'BROWSER_DATA="/data/.openclaw/browser"' \
  'for profile_dir in "$BROWSER_DATA"/*/user-data; do' \
  '  [ -d "$profile_dir" ] || continue' \
  '  rm -f "$profile_dir/SingletonLock" "$profile_dir/SingletonSocket" "$profile_dir/SingletonCookie"' \
  '  echo "[startup] Cleared browser locks in $profile_dir"' \
  'done' \
  '# Restore gog credentials + keyring from persistent volume backup' \
  '# (/root/.config is ephemeral -- wiped on every container restart/redeploy)' \
  'GOG_KEYRING_BACKUP="/data/workspace/credentials/gogcli-keyring/keyring"' \
  'GOG_KEYRING_DIR="/root/.config/gogcli/keyring"' \
  'GOG_CREDS_BACKUP="/data/workspace/credentials/google-oauth-client.json"' \
  'GOG_CREDS_DIR="/root/.config/gogcli/credentials.json"' \
  'if [ -d "$GOG_KEYRING_BACKUP" ] && [ "$(ls -A "$GOG_KEYRING_BACKUP" 2>/dev/null)" ]; then' \
  '  mkdir -p "$GOG_KEYRING_DIR"' \
  '  cp -f "$GOG_KEYRING_BACKUP"/token:* "$GOG_KEYRING_DIR/" 2>/dev/null && echo "[startup] gog keyring restored"' \
  'fi' \
  'if [ ! -f "$GOG_CREDS_DIR" ] && [ -f "$GOG_CREDS_BACKUP" ]; then' \
  '  mkdir -p "$(dirname "$GOG_CREDS_DIR")"' \
  '  cp -f "$GOG_CREDS_BACKUP" "$GOG_CREDS_DIR" && echo "[startup] gog credentials restored"' \
  'fi' \
  'exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf' \
  > /usr/local/bin/startup.sh \
  && chmod +x /usr/local/bin/startup.sh

CMD ["/usr/local/bin/startup.sh"]
