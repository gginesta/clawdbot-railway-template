# What AI Agents Actually Do For Me (Beyond the Cool Setup)

*By Guillermo Ginesta*

---

There's a phase everyone goes through when they first build an AI agent setup: you spend weeks configuring integrations, debugging API calls, naming your agents, and feeling incredibly productive — even though you haven't actually *done* anything with them yet.

I called mine Molty, Raphael, and Leonardo. I gave them personalities, connected them to my calendars, my CRM, my task manager. I felt like a sci-fi protagonist.

Then one Tuesday morning, at 6:30 AM, my phone buzzed. Not an alarm. Not a news notification. It was Molty — giving me a weather update, my calendar for the day, my top three priorities, and a task overview. All in Telegram. All formatted cleanly. All without me asking for it.

That was the moment I stopped feeling like a builder and started feeling like a user. And that shift? That's what this article is about.

---

## The Morning I Stopped Setting My Own Agenda

Most mornings used to start with a small, invisible tax. Before I could think clearly, I had to think *about* thinking clearly — what's on my calendar today? What was I supposed to follow up on? What's the weather like for my commute?

Now I wake up to a briefing.

Every day at 6:30 AM, Molty delivers a structured morning update to my Telegram:

- **Weather** in Hong Kong (yes, it matters — typhoon signals are a real thing here)
- **Calendar overview** for the day
- **Top priorities** — not just what's scheduled, but what actually needs attention
- **Task snapshot** from Todoist

[SCREENSHOT: Morning briefing message in Telegram — clean card format with weather emoji, calendar summary, and prioritized task list]

I read it like a morning briefing from a chief of staff. I don't have to open five apps. I don't have to reconstruct context from the night before. I just read, orient, and go.

It took maybe two weeks of iteration to get this working consistently. Now I don't think about it. It just happens — the same way the sun rises.

---

## The 5 PM Standup That Runs Itself

This one surprised me the most, because it's the thing that saves me the most cognitive energy in a week.

Every day at 5 PM, Molty runs through my entire Todoist inbox. Not just reads it — *processes* it. Here's what happens:

1. **Rewrites vague tasks** into actionable ones. "Email João" becomes "Follow up with João on Brinc proposal — sent last Thursday, awaiting feedback"
2. **Estimates time** for each task
3. **Categorizes and prioritizes** — urgent vs. important, Brinc vs. personal
4. **Creates a Notion standup page** with the full breakdown
5. **Suggests calendar time blocks** for tomorrow

[SCREENSHOT: Auto-generated Notion standup page — task table with categories, time estimates, and priority flags]

My job is to review it, approve or adjust, and move on. That's it. The whole thing takes me maybe three minutes instead of thirty.

Before this, I had what I'd call "inbox guilt" — that low-grade anxiety of knowing your task list is a mess but not having the energy to deal with it at the end of the day. Now the agent deals with it. I just sign off.

[SCREENSHOT: Calendar time blocks suggestion in Telegram — "I suggest blocking 10-11 AM tomorrow for the pitch deck review"]

---

## The Tamagotchi Problem (And Why You Need to Survive It)

Here's something nobody tells you about building AI agents: **the setup phase feels like the product**.

You're connecting APIs, writing prompts, debugging webhooks. It's stimulating. It *feels* like you're building something valuable. And you are — but it's infrastructure, not output.

The real value only shows up after the Tamagotchi phase ends.

Remember Tamagotchis? You had to feed them, play with them, keep them alive. It was exhausting and weirdly addictive. Building AI agents in the early days felt the same way — constant attention, constant adjustment.

But once the infrastructure stabilizes, something magical happens: **you forget the agent exists**. You just enjoy the output. You stop thinking "Molty will send me a briefing" and start thinking "oh, there's my briefing."

That's the goal. Infrastructure that disappears into the background. That's when agents actually start delivering value.

---

## What Molty Actually Does for Me Day-to-Day

Beyond the morning briefing and standup, Molty handles the kind of tasks that are individually small but collectively exhausting.

**Booked my haircut.** I mentioned I needed one. Molty checked my calendar for a free slot, found a time on Friday afternoon, and confirmed it. I didn't touch WhatsApp or make a call.

**Managed my Cebu trip logistics.** When I traveled to Cebu for work, Molty adapted the morning briefings to be location-aware — local weather, adjusted timezones, relevant context. It felt like having a travel assistant who actually knew where I was.

[SCREENSHOT: Cebu morning briefing — showing different weather/location context vs. regular Hong Kong version]

**Generated Chinese New Year social media images.** Not just pulled a stock photo — actually generated custom images for social content. I gave a brief direction, Molty produced options, I picked one.

None of these are earth-shattering individually. But add them up across a week and you're looking at maybe two to three hours of small-task friction that just... vanishes.

---

## Where Raphael Earns His Keep (The Business Side)

Molty is my personal assistant. Raphael is my Brinc agent — focused on sales, marketing, and business development.

At Brinc, we're in the business of corporate venture building. We work with large companies to stand up new ventures. That means a constant flow of leads, conversations, proposals, and follow-ups — the kind of CRM hygiene that's easy to let slide.

Raphael sits on top of HubSpot.

Here's what that looks like in practice:

**Lead triage.** When a new contact comes into HubSpot, Raphael classifies it — is this a warm intro, a cold inbound, a conference connection? What's the likely use case? What's the priority level? Instead of me staring at a CRM full of undifferentiated names, I get a qualified view.

[SCREENSHOT: HubSpot lead overview with Raphael's triage notes — priority level, context, suggested next step]

**Deal next steps.** For active deals, Raphael surfaces what's needed: who needs a follow-up, what documents are outstanding, what the timeline looks like. It's like having a sales coordinator who's read every note in the system.

**Proposal support.** When we're putting together a proposal, Raphael helps structure it — not just templates, but context-aware drafts that pull from what we know about the client. First drafts in minutes, not hours.

**Marketing content pipeline.** Raphael manages a consistent flow of content for Brinc's channels — LinkedIn posts, case study outlines, newsletter drafts. Not polished final copy, but strong first drafts I can edit rather than write from scratch.

The business impact here is real. In a small team, nobody has bandwidth to be a dedicated CRM admin or content manager. Raphael fills those gaps without me having to hire for them.

---

## What Doesn't Work (Honest Takes)

I'd be doing you a disservice if I made this sound like a seamless utopia. It's not.

**OAuth tokens expire.** This is the most annoying one. I'll go two weeks of perfect operation and then Molty will flag that a Google Calendar integration has dropped. Fifteen minutes of re-authenticating later, we're back — but it breaks the "magic" illusion. It's solvable, but it requires periodic maintenance.

**Complex tasks need babysitting.** Simple, well-defined tasks? Excellent. Multi-step tasks with ambiguous inputs or judgment calls? The agents need guidance. "Help me figure out our Q2 strategy" is not a task Molty can run with autonomously. I still have to show up for the complex thinking.

**Memory isn't perfect.** The agents have memory systems — daily logs, long-term notes, context files. But it's not the same as human continuity. Occasionally Molty will miss context that I thought was stored, or ask me something I know I've answered before. It's improving, but it's not magic yet.

**The setup cost was real.** I spent probably 40-60 hours over a few months getting the infrastructure right. That's not nothing. If you're thinking about building this, go in eyes open: there's a real time investment before you start getting the returns.

---

## The Honest ROI Calculation

So was it worth it?

Here's my rough math:

- **Time saved daily:** ~45 minutes to 1 hour (briefing review, standup, small tasks)
- **Time saved weekly from Raphael:** ~3-4 hours (CRM, content, follow-ups)
- **Setup cost:** ~50 hours over 3 months
- **Break-even point:** Roughly 2 months in, and now it compounds

The harder thing to quantify is **cognitive load**. The reduction in background anxiety — the inbox guilt, the context-switching, the "I should probably check on that" loop — is real and meaningful. I feel more focused during the hours I'm actually working because the scaffolding around my work is handled.

That's not something I can put a number on. But I notice it every day.

---

## What This Actually Is

I want to be clear about something: what I've built is not a replacement for strategic thinking, creative work, or human judgment. My agents can't run Brinc. They can't have the conversations that matter. They can't make the calls that require experience and intuition.

What they can do is **remove the drag**.

Every morning I used to spend ten minutes reconstructing my context. That's gone. Every Friday afternoon I used to spend an hour cleaning up tasks I didn't do. That's gone. Every week I used to feel behind on CRM hygiene. Less so now.

The agents are not doing my job. They're doing the meta-work *around* my job — the administration, the reminders, the first drafts, the organization — so that the actual job gets more of my attention.

Leonardo handles the venture-building side — startup evaluation, framework application, research synthesis — but that's a story for another article.

The point is this: the cool setup is not the point. The cool setup is the foundation. What happens *after* the setup stabilizes — when you forget the agents exist and just notice that your week runs better — that's the actual product.

And yes, it took me a few months of Tamagotchi energy to get there. But I'd do it again.

---

*Guillermo Ginesta is Managing Partner at Brinc, a corporate venture building firm based in Hong Kong. He writes about the practical side of AI tools, venture building, and what actually works when you try to run a small team at scale.*
