# Syncthing Integration for Railway Template

## Overview
Add Syncthing to your existing OpenClaw container for real-time file sync.

## Changes to Dockerfile

Add these lines to your `Dockerfile` in the **runtime image** section (after the Chromium installation):

```dockerfile
# ========== ADD THIS SECTION ==========
# Install Syncthing for real-time file sync
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    syncthing \
  && rm -rf /var/lib/apt/lists/*

# Syncthing ports
# 8384 = Web UI (optional, can access via Tailscale only)
# 22000 = Sync protocol (TCP)
# 22000 = Sync protocol (UDP) - for QUIC
EXPOSE 8384 22000/tcp 22000/udp

# Syncthing config/data directories
ENV SYNCTHING_HOME=/data/.syncthing
ENV STNODEFAULTFOLDER=1
# ========== END SECTION ==========
```

## Full Modified Dockerfile

Here's the complete Dockerfile with Syncthing added:

```dockerfile
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

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
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

ENV CHROME_PATH=/usr/bin/chromium
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV CHROMIUM_USER_DATA_DIR=/data/.chromium

# Syncthing config
ENV SYNCTHING_HOME=/data/.syncthing
ENV STNODEFAULTFOLDER=1

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

# The wrapper listens on this port.
ENV OPENCLAW_PUBLIC_PORT=8080
ENV PORT=8080

# Syncthing ports
EXPOSE 8080 8384 22000/tcp 22000/udp

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

## New File: supervisord.conf

Create this file in your repo root:

```ini
[supervisord]
nodaemon=true
user=root
logfile=/tmp/supervisord.log
pidfile=/tmp/supervisord.pid

[program:openclaw]
command=node /app/src/server.js
directory=/app
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=NODE_ENV="production"

[program:syncthing]
command=/usr/bin/syncthing serve --home=/data/.syncthing --gui-address=0.0.0.0:8384 --no-browser
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
```

## Railway Environment Variables (Optional)

Add these in Railway dashboard if you want to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `SYNCTHING_GUI_USER` | (none) | Web UI username |
| `SYNCTHING_GUI_PASSWORD` | (none) | Web UI password |

## After Deployment

1. **Access Syncthing Web UI:** `https://your-app.railway.app:8384` (or via internal port)
2. **Get Device ID:** Actions → Show ID in Syncthing UI
3. **Install Syncthing on Windows:** Download from syncthing.net
4. **Pair devices:** Add Railway's Device ID to your Windows Syncthing
5. **Create shared folder:** Point it at `/data/shared` on Railway

## Security Note

The Syncthing Web UI (port 8384) will be publicly accessible. Set a strong GUI password in Syncthing settings immediately after first deployment, or restrict access via Railway's networking settings.

Alternatively, don't expose port 8384 publicly and only access it via SSH tunnel or Tailscale.
