# 🚨 Break Glass Guide — Yoda Troubleshooting

*Keep this somewhere Edwin can access WITHOUT Yoda (Google Doc, bookmark, etc.)*

---

## Yoda Not Responding?

### Step 1: Check Railway
1. Go to [railway.com](https://railway.com) → sign in
2. Find the "yoda" project
3. Check if the service is running (green = good, red = problem)
4. If red: click the service → "Restart" button

### Step 2: Check Webchat
1. Go to your Railway deployment URL (the one ending in `.up.railway.app`)
2. Try sending a message in webchat
3. If webchat works but Telegram doesn't → Telegram config issue, not Yoda

### Step 3: Check Logs
1. In Railway → click your service → "Logs" tab
2. Look for red error messages
3. Common issues:
   - "OAuth token expired" → re-authenticate (ask Yoda via webchat, or re-run OAuth setup)
   - "Out of memory" → Railway may need a larger instance
   - "Rate limited" → too many API calls, wait a few minutes

---

## Yoda Saying Weird Things?

- **Acting like someone else?** Check SOUL.md and IDENTITY.md in the workspace. Someone may have overwritten them.
- **Forgetting things?** Memory might need maintenance. Ask Yoda: "Check your memory system status"
- **Sending duplicate messages?** Check if multiple sessions are active. Ask Yoda: "How many active sessions do you have?"

---

## Need to Reset?

### Soft Reset (keeps everything)
- In webchat, type: `/restart`
- Or: Railway dashboard → Restart service

### Hard Reset (last resort)
- Railway dashboard → Deployments → Redeploy latest
- This restarts everything but keeps your persistent volume (files, memory)

---

## Costs Running High?

1. Ask Yoda: "What's my model usage this month?"
2. Check Railway billing: railway.com → Settings → Billing
3. Check OpenRouter: openrouter.ai → Dashboard
4. To reduce costs: Ask Yoda to switch to cheaper models for routine tasks

---

## Emergency Contacts

- **Railway support:** railway.com/support
- **OpenClaw docs:** docs.openclaw.ai
- **OpenClaw community:** discord.com/invite/clawd
- **Setup team contact:** *(add Guillermo's contact or your preferred support channel)*

---

*Last updated: 2026-02-12*
