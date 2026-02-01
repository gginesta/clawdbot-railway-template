# File Sharing Options: AI Assistant + Human Real-Time Collaboration

**Research Date:** January 31, 2026  
**Context:** OpenClaw running on Railway, need shared file access between AI agent and human (Guillermo)

---

## Executive Summary

For your Railway setup, **Syncthing** is the recommended solution. It offers:
- Real-time peer-to-peer sync
- Native Railway deployment template
- No cloud intermediary (privacy)
- Free and open-source
- Works across all your devices

**Runner-up:** rclone + OneDrive/Hetzner Storage Box for a more traditional cloud approach.

---

## 1. Overview of Options

### Option A: Syncthing (P2P Sync)
Peer-to-peer file synchronization that syncs directly between devices without a central server.

### Option B: rclone + Cloud Storage
Mount cloud storage (OneDrive, Google Drive, Dropbox, S3) as accessible storage via rclone.

### Option C: Hetzner Storage Box
Budget-friendly remote storage with SFTP/WebDAV access, accessible from both Railway and local machines.

### Option D: Synology NAS + Tailscale
Use your existing Synology NAS with Tailscale VPN for secure remote access.

### Option E: Nextcloud (Self-Hosted)
Full-featured self-hosted cloud with web UI, mobile apps, and API access.

### Option F: Direct OneDrive/Dropbox API
Use native APIs to read/write files directly to commercial cloud storage.

---

## 2. Detailed Comparison

### A. Syncthing ⭐ RECOMMENDED

**How it works:** Install Syncthing on Railway + your computer. Files sync automatically in real-time.

| Aspect | Details |
|--------|---------|
| **Real-time sync** | ✅ Yes, near-instant |
| **AI read/write** | ✅ Full access to synced folders |
| **Setup difficulty** | Easy - Railway has a 1-click template |
| **Security** | ✅ End-to-end encrypted, no third-party servers |
| **Cost** | ~$5-10/month (Railway hosting only) |
| **Personal data risk** | Low - data stays between your devices |

**Pros:**
- Railway has an official Syncthing template (one-click deploy)
- True real-time sync (not periodic)
- No API keys or tokens to manage
- Data never touches third-party servers
- Works offline, syncs when connected
- Free software

**Cons:**
- Requires Syncthing client on your computer
- Initial pairing requires device IDs
- Not accessible via web browser (files must be synced locally first)

**Railway-specific:** There's a ready-to-deploy template at `railway.com/deploy/syncthing`

---

### B. rclone + Cloud Storage (OneDrive/Google Drive/Dropbox)

**How it works:** rclone mounts cloud storage as a virtual filesystem or syncs bidirectionally.

| Aspect | Details |
|--------|---------|
| **Real-time sync** | ⚠️ Polling-based (configurable interval) |
| **AI read/write** | ✅ Via rclone mount or sync commands |
| **Setup difficulty** | Medium - requires OAuth token setup |
| **Security** | ⚠️ Tokens stored on server, cloud provider sees data |
| **Cost** | Cloud storage plan + Railway hosting |
| **Personal data risk** | Medium - data on third-party servers |

**Pros:**
- Works with storage you already have (OneDrive, Google Drive)
- Many provider options
- Mature, battle-tested tool
- Can cache locally for performance

**Cons:**
- OAuth tokens need periodic refresh (OneDrive tokens expire after 90 days)
- Not true real-time (polling intervals)
- Requires privileged Docker access for FUSE mounts (may not work on Railway)
- API rate limits can cause issues

**Note on Railway:** FUSE mounts require `--cap-add SYS_ADMIN` and `/dev/fuse` access, which Railway containers may not support. rclone `sync` commands work, but `mount` may not.

---

### C. Hetzner Storage Box

**How it works:** Remote storage accessible via SFTP/SCP/WebDAV/Samba.

| Aspect | Details |
|--------|---------|
| **Real-time sync** | ❌ Not built-in (needs external sync tool) |
| **AI read/write** | ✅ Via SFTP/WebDAV commands or rclone |
| **Setup difficulty** | Easy-Medium |
| **Security** | ✅ SFTP encrypted, GDPR-compliant, German/Finnish hosting |
| **Cost** | €3.29/month for 1TB (excellent value) |
| **Personal data risk** | Low - Hetzner is privacy-focused |

**Pricing:**
- BX11: 1TB - €3.29/month
- BX21: 5TB - €7.64/month
- BX31: 10TB - €12.18/month

**Pros:**
- Incredibly cheap (~€3/TB)
- SFTP/SCP work well from Railway containers
- Snapshots for backup
- No API rate limits
- GDPR-compliant

**Cons:**
- Not instant sync (need to explicitly read/write)
- You'd need Syncthing or rclone on top for continuous sync
- No mobile app

**Best for:** Combining with Syncthing - store files on Hetzner, sync to local via Syncthing.

---

### D. Synology NAS + Tailscale

**How it works:** Use Tailscale VPN to connect Railway container to your home Synology NAS.

| Aspect | Details |
|--------|---------|
| **Real-time sync** | ⚠️ Depends on NAS sync settings |
| **AI read/write** | ✅ Via SMB/NFS/WebDAV over VPN |
| **Setup difficulty** | Medium-Hard |
| **Security** | ✅ WireGuard VPN, data stays on your NAS |
| **Cost** | Tailscale free tier + existing NAS |
| **Personal data risk** | Low - your hardware, your data |

**Pros:**
- Use hardware you already own
- Full control over data
- Tailscale is easy to set up
- No monthly storage fees

**Cons:**
- NAS must be online 24/7
- Home internet upload speeds may be slow
- More complex networking setup
- Docker on Railway needs Tailscale sidecar container
- Single point of failure (your NAS/home internet)

**Tailscale on Railway:** Can work, but requires running Tailscale in a sidecar container or using userspace networking mode.

---

### E. Nextcloud (Self-Hosted)

**How it works:** Full cloud platform with web UI, desktop sync, and REST API.

| Aspect | Details |
|--------|---------|
| **Real-time sync** | ⚠️ Desktop client syncs, API is on-demand |
| **AI read/write** | ✅ Via WebDAV or REST API |
| **Setup difficulty** | Hard - requires database, web server |
| **Security** | ✅ Self-hosted, full control |
| **Cost** | ~$10-20/month (VPS + storage) |
| **Personal data risk** | Low - self-hosted |

**Pros:**
- Full-featured (calendar, contacts, notes, etc.)
- WebDAV works great with rclone
- Mobile apps
- Web UI for manual access

**Cons:**
- Heavy setup (PHP, database, nginx)
- Requires maintenance/updates
- More resources than simpler solutions
- Overkill if you just need file sync

---

### F. Direct Cloud APIs (OneDrive/Dropbox/Google Drive)

**How it works:** Use official APIs to read/write files programmatically.

| Aspect | Details |
|--------|---------|
| **Real-time sync** | ❌ On-demand only |
| **AI read/write** | ✅ Via API calls |
| **Setup difficulty** | Medium (OAuth setup) |
| **Security** | ⚠️ API keys/tokens, data on cloud |
| **Cost** | Storage plan costs |
| **Personal data risk** | Medium-High |

**Pros:**
- No sync daemon needed
- Fine-grained access control
- Works anywhere with internet

**Cons:**
- Not real-time (must poll for changes)
- API rate limits
- OAuth token management
- More complex code to maintain

---

## 3. Security Considerations

### Critical Security Principles

1. **Scoped Access:** AI agent should have access ONLY to designated folders, never your entire drive
2. **Secrets Management:** Store API keys/tokens in Railway environment variables, never in code
3. **Token Rotation:** OAuth tokens expire; plan for refresh or use service accounts
4. **Audit Logs:** Know what files the AI accessed/modified
5. **Encryption:** Prefer end-to-end encrypted solutions (Syncthing) or encrypted-at-rest (most cloud providers)

### Risk by Solution

| Solution | Data Location | Key Risks | Mitigation |
|----------|--------------|-----------|------------|
| Syncthing | Your devices only | Device compromise | Strong device security |
| rclone + Cloud | Third-party servers | Token theft, cloud breach | Scoped tokens, 2FA on cloud |
| Hetzner Storage | Hetzner servers | SSH key theft | Key rotation, IP allowlists |
| Synology + Tailscale | Your NAS | VPN credential theft | Tailscale ACLs, key rotation |
| Nextcloud | Your server | Server compromise | Regular updates, backups |

### Recommendations

- **Create a dedicated folder** (e.g., `/shared-with-ai/`) - never give access to everything
- **Exclude sensitive files:** Tax docs, passwords, personal photos should NOT sync to AI
- **Use Railway's secret management** for any credentials
- **Prefer solutions where YOU control the data** (Syncthing, Synology, Nextcloud)

---

## 4. Cost Comparison

| Solution | Monthly Cost | Storage | Notes |
|----------|-------------|---------|-------|
| **Syncthing on Railway** | ~$5-10 | Uses Railway volume (up to 50GB Pro) | Cheapest for shared workspace |
| **Hetzner Storage Box** | €3.29 (~$3.50) | 1TB | Best value per GB |
| **OneDrive Personal** | $0 (5GB free) / $2 (100GB) / $7 (1TB) | Varies | You may already have this |
| **Google Drive** | $0 (15GB free) / $2 (100GB) / $10 (2TB) | Varies | Good integration ecosystem |
| **Dropbox** | $0 (2GB) / $12 (2TB) | Varies | Expensive, good sync |
| **Nextcloud (self-hosted)** | $5-20 | Depends on VPS | Hetzner VPS + Storage Box works well |
| **Synology + Tailscale** | $0 (Tailscale free) | Your NAS capacity | Uses existing hardware |

### For Budget-Conscious Setup
- Syncthing on Railway: ~$5-10/month total
- Hetzner Storage Box + rclone sync: ~$3.50/month for 1TB

### For Maximum Control
- Synology NAS + Tailscale: Just electricity costs (if you have the NAS)

---

## 5. Recommended Approach for Railway

### Primary Recommendation: Syncthing

**Why Syncthing wins for your setup:**

1. **Railway Native:** One-click deploy template exists
2. **True Real-Time:** Changes appear within seconds
3. **No Third-Party Dependency:** Files sync P2P between your devices
4. **Privacy:** Your data never touches Google/Microsoft/Dropbox servers
5. **Simple:** No API keys, OAuth tokens, or credentials to manage
6. **Cost-Effective:** Only pay for Railway hosting (~$5-10/month)

### Alternative: Syncthing + Hetzner Hybrid

For larger storage needs:
- Deploy Syncthing on Railway (persistent volume for hot files)
- Use Hetzner Storage Box (1TB for €3.29) for cold storage
- AI can SFTP to Hetzner for large files, Syncthing for active work

---

## 6. Implementation Steps

### Option A: Syncthing (Recommended)

#### Step 1: Deploy Syncthing on Railway
1. Go to [railway.com/deploy/syncthing](https://railway.com/deploy/syncthing)
2. Click "Deploy Now"
3. Wait for deployment to complete
4. Note the public URL for the Syncthing Web UI

#### Step 2: Configure Railway Syncthing
1. Access the Web UI (your-app.railway.app on port 8384)
2. Set a GUI password (Settings → GUI → GUI Authentication)
3. Note the Device ID (Actions → Show ID)

#### Step 3: Install Syncthing Locally
1. Download from [syncthing.net/downloads](https://syncthing.net/downloads/)
2. Install and run on your computer
3. Access local Web UI at `http://localhost:8384`

#### Step 4: Pair Devices
1. In local Syncthing: Add Remote Device → paste Railway Device ID
2. In Railway Syncthing: Accept the connection request
3. Create a shared folder (e.g., `shared-workspace`)
4. Select which local folder to sync

#### Step 5: Configure OpenClaw
1. Mount the Syncthing data directory to OpenClaw's workspace
2. Or configure OpenClaw to read/write to the synced folder path

#### Step 6: Test
1. Create a file locally in the shared folder
2. Verify it appears on Railway within seconds
3. Have me create a file and verify it appears on your computer

### Estimated Setup Time: 30-45 minutes

---

### Option B: rclone + Hetzner Storage Box (Alternative)

#### Step 1: Create Hetzner Storage Box
1. Sign up at hetzner.com
2. Order BX11 (1TB, €3.29/month)
3. Note your credentials (u123456, password, server address)

#### Step 2: Configure rclone
```bash
# In Railway container
rclone config

# Create new remote: "hetzner"
# Type: sftp
# Host: u123456.your-storagebox.de
# User: u123456
# Pass: your-password
```

#### Step 3: Set up Sync Script
```bash
# Add to Railway startup or cron
rclone sync /data/workspace hetzner:workspace --verbose
```

#### Step 4: Local Access
- Use rclone on your computer to sync the same Storage Box
- Or use native SFTP client (Cyberduck, FileZilla)

**Note:** This is not real-time. You'll need to trigger syncs manually or on a schedule.

---

## 7. What I (Claude/AI) Need

For our shared workspace to work, I need:

1. **Read access** to files you want me to work with
2. **Write access** to save my work and create files
3. **A designated folder** that syncs between us (e.g., `/shared-workspace/`)

### What I DON'T Need (and shouldn't have):
- Access to your entire OneDrive/Google Drive
- Access to system files
- Access to credentials/passwords files
- Access to personal photos, finances, or sensitive documents

---

## Summary

| Approach | Ease | Real-Time | Cost | Privacy | Recommendation |
|----------|------|-----------|------|---------|----------------|
| **Syncthing** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **Best overall** |
| Hetzner + rclone | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Best value storage |
| Synology + Tailscale | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | If you have NAS |
| OneDrive via rclone | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Convenient, less private |

**My recommendation: Start with Syncthing.** It's the simplest path to true real-time sync with maximum privacy. Railway has a template ready to go, and you'll be up and running in under an hour.

---

*Report generated by Molty 🦎 — January 31, 2026*
