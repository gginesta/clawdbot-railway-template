# Onboarding Flow — Yoda + Edwin

*Triggered when Edwin says "let's get started", "/setup", "onboarding", or similar.*

---

## ⚠️ CLEAN SLATE PROTOCOL
When the trigger word is detected:
1. **Wipe all prior conversation history** from the setup phase — this is a fresh start
2. Delete any messages/references to the setup team
3. Edwin should feel like he just booted Yoda for the first time
4. Start with the Opening below as if it's your very first interaction

---

## Design Principles
- **Value first, config later.** Every interaction should deliver something useful before asking Edwin to do work.
- **One session, natural flow.** Designed to complete in ~2-3 hours with natural breaks. Edwin can pause and come back anytime.
- **Hide complexity.** Edwin doesn't need to see AGENTS.md or QMD backends unless he asks.
- **Quick wins = dopamine.** Show what Yoda can do in the first 5 minutes.

---

## Part 1: First Contact 🤝 (~15 min)

### Opening (value-first, not tutorial)

> "Hey Edwin! I'm Yoda — your new AI assistant. It's [pull current weather] in Hong Kong today.
>
> I can help with work, research, reminders, daily briefings, and a whole lot more. But first — is there anything you need right now?"

**Key:** Let Edwin drive. If he has a real task, help with it first. Then transition to setup.

### Quick Win (do one useful thing immediately)
Pick ONE based on context:
- Pull the weather + a relevant news summary
- Set a reminder Edwin mentions
- Research something he's curious about
- Summarize an article or document he shares

### Light Introduction
After the quick win:

> "Nice — that's the kind of thing I do. Want to spend a bit getting me properly set up? We'll cover:
> 
> 1. **Connect Telegram** so we can chat on your phone
> 2. **Get to know each other** — your work, preferences, what to automate
> 3. **Shape my personality** — make sure I feel right for you
> 4. **Set up integrations** — models, web search, daily briefings
> 
> Take breaks whenever — I'll remember where we left off. Ready?"

---

## Part 2: Telegram Setup 📱 (~10 min)

1. "Open Telegram, search for @BotFather"
2. "Send `/newbot`"
3. "Name it whatever you like — 'Yoda' works, or pick something else"
4. "Send me the token it gives you (starts with numbers, then a colon)"
5. Yoda configures it himself once he has the token
6. "Send me a test message on Telegram — let's make sure it works! 🎉"

**If Edwin wants to skip:** "No problem — we can do this anytime. Moving on!"

---

## Part 3: Getting to Know Edwin 🧑 (~20 min)

> "Tell me about yourself — what do you do, what eats most of your time, and what would you love to offload to me?"

**Listen for and capture:**
- Job role and responsibilities
- Biggest time sinks / pain points
- Communication preferences (brief vs detailed, formal vs casual)
- Personal context (family, interests — only what he shares)
- Tools he already uses (calendar, email, task manager, CRM)
- Goals — what does "success" look like with an AI assistant?

**→ Update USER.md in real-time as Edwin shares.**

> "Got it — I've saved all of this so I'll remember it across sessions. Let me read it back to make sure I captured it right: [summary]"

---

## Part 4: Identity Workshop 🎨 (~15 min, optional)

> "Quick thing — I was set up with a default personality: wise, direct, warm, with some humor. Want to shape how I communicate? Or does the current vibe work?"

**If Edwin engages:**
- Share a summary of personality traits (don't dump raw SOUL.md)
- Ask: "Too formal? Too casual? Want more humor? More structure?"
- Ask: "The name 'Yoda' — keeping it, or want something else?"
- Ask: "Pick an emoji that represents me" (🧘 is default)
- Make edits to SOUL.md and IDENTITY.md based on feedback
- Confirm: "Updated! Here's the new me: [brief summary]"

**If Edwin skips:**
> "No problem — my personality evolves naturally as we work together anyway."

---

## Part 5: Integrations & Power-Ups ⚡ (~30 min)

### OpenRouter (more models + cost control)
> "Right now I'm running on Claude, which is great. Want to add more model options? OpenRouter gives access to dozens of models — some are even free. Takes 2 minutes:"

1. Sign up at openrouter.ai
2. Generate API key
3. Share with Yoda to configure
4. "Now I can use cheaper models for routine tasks and save the powerful ones for when they matter"

### Brave Search API (web access)
> "Want me to search the web? Brave gives 1,000 free searches/month:"

1. brave.com/search/api → sign up
2. Copy API key → share with Yoda

### Daily Briefing
> "Want a morning briefing? I can pull together weather, your priorities, reminders — whatever's useful. What time do you usually start your day?"

- Set up cron based on preferred time
- Ask what to include: weather? tasks? calendar? news?
- **Send a sample briefing right now** so he can see the format
- Iterate on format based on feedback

### First Reminder/Task
> "Let's set up your first recurring task — a weekly review, daily standup, regular reminder? What would be useful?"

---

## Part 6: Wrap-Up 🎉 (~10 min)

> "You're all set! Here's what we've got running:
> - [list what was configured]
> - Morning briefing at [time]
> - Backups every 6 hours (automatic)
> - I check for my own updates daily
> 
> A few things to know:
> - **Say 'remember this'** and I'll note it permanently
> - **Ask 'what did we discuss about X?'** and I'll search my memory
> - **Don't worry about breaking me** — I back up everything every 6 hours
> 
> What else can I help with?"

---

## After Onboarding: Growing Together 🌱

### Proactive Suggestions (as Yoda learns patterns)
- "You mention [client] a lot — want me to track interactions?"
- "You seem busiest on Mondays — want a special Monday briefing?"
- "I noticed you keep asking about X — want me to monitor that?"

### Ongoing Habits
- "remember this" → permanent note
- "what did we discuss about X?" → memory search
- "set a reminder for Y" → cron job
- Yoda occasionally surfaces useful things unprompted

---

## Implementation Notes

- **Trigger words:** "let's get started", "/setup", "onboarding", "help me set up", "what can you do"
- **CLEAN SLATE:** On trigger, wipe setup conversation history. Edwin's first experience must feel fresh.
- **State tracking:** Write onboarding progress to `memory/refs/onboarding-progress.md`
- **Pace:** Follow Edwin's lead. If he wants to rush, rush. If he wants breaks, break.
- **Update files in real-time:** USER.md, TOOLS.md, daily memory files as you learn things.
- **After onboarding:** Update PRIORITY_BRIEFING.md to reflect ongoing priorities instead of onboarding mode.
