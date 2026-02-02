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

# Pin to a known ref (tag/branch). If it doesn't exist, fall back to main.
ARG OPENCLAW_GIT_REF=main
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

ENV CHROME_PATH=/usr/bin/chromium
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
  'tailscale --socket=/tmp/tailscaled.sock --timeout=30s up --reset \' \
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
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
