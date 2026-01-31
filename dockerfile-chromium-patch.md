# Chromium Dockerfile Patch for Railway Template

## Original (in runtime stage):
```dockerfile
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*
```

## Replace with:
```dockerfile
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
  && rm -rf /var/lib/apt/lists/*

# Set Chromium path for OpenClaw browser control
ENV CHROME_PATH=/usr/bin/chromium
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
```

## Why these packages?
- `chromium` - The browser itself
- `chromium-sandbox` - Security sandbox
- `fonts-*` - So pages render text properly
- `lib*` - Dependencies Chromium needs to run
- Environment variables tell OpenClaw where to find it

## After forking:
1. Fork: https://github.com/vignesh07/clawdbot-railway-template
2. Edit the Dockerfile with the changes above
3. In Railway, update your service to point to YOUR fork
4. Redeploy

---
