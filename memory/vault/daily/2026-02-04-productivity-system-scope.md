# Molty Productivity System — Scope Discovery

**Status:** 🟡 Scoping  
**Owner:** Guillermo + Molty  
**Created:** 2026-02-04  

---

## Vision

> Molty manages my email, calendar, and task list. Daily/weekly reviews help me prioritize. Time-blocking ensures tasks actually get done.

---

## 🎯 Discovery Questions

*Guillermo: answer inline below each question. Delete the placeholder "→" when done.*

---

### 1. Current State

#### Calendar

**How many Google Calendars do you actively use?**  
*(e.g., "Work", "Personal", "Brinc", shared family calendar?)*

Personal (just mine); Shenanigans (family); Brinc (most active); Mana Capital

**Which calendar(s) should Molty be able to WRITE to vs just READ?**

All? Raphael could manage Brinc. Or read Brinc and write in Personal and Shenanigans as long as time blocks appear in Brinc to avoid double booking meetings

**Do you already time-block, or is your calendar mostly meetings/events that happen *to* you?**

I try, but need to get stricter. I get invited to meetings/calls constantly. 

---

#### Todoist

**Do you already use Todoist?**

Yes

**If yes:**

- How many projects do you have roughly?  
  Personal, Brinc/Work, Mana Capital 

- Do you use labels, priorities, due dates consistently?  
  Not yet but with a good automation and system hygiene we can 

- What's broken about your current system? (Too many tasks? Never review them? Wrong granularity?)  
  Tasks are never reviewed and prioritised. Need consistency for it to really work - translate from a random group of tasks, to an executive list with priorities, due dates and estimated how long it would take, then prioritise and time block to ensure stuff is done 

**If no:** Are you open to starting fresh with a structure Molty helps design?

Absolutely! That's why Molty's here 

---

#### Current Pain Points

**What's the #1 thing that falls through the cracks today?**

Lack of time blocks. New things come up to my plate and existing prior tasks just get punted. Things compete for priorities and there's no good system of urgent vs important The [Eisenhower Matrix](https://asana.com/resources/eisenhower-matrix) (or Urgent-Important Matrix) is ==a 2x2, four-quadrant productivity framework that organizes tasks by urgency and importance to prioritize effectively==. It helps users move from reactive "fire-fighting" to strategic planning by deciding whether to immediately **Do** (urgent/important), **Schedule** (important/not urgent), **Delegate** (urgent/not important), or **Delete** (neither) tasks.
![[Pasted image 20260204184303.png]]

**When you say "something always comes up" — is that external interruptions, or you deprioritizing your own tasks?**

New tasks come into the funnel. New priorities, competing schedules. As the most senior person in Asia for Brinc I need to balance between what I can/should do (and show face or add value) vs delegate. 

Also need to time block things for my personal life that keep getting punted. Donate clothes and spring cleaning? Waiting since winter. Apply for a new passport. Book a haircut for me or my son. Lots of admin things that I need to get done, or that Molty could do for me.

---

### 2. Desired Workflow

#### Daily Review

**What time (HKT) would work for a daily check-in?**

end of day seems right, so we hit the ground running next day. avoid scrambling first thing. This can be reviewed obviously 

**What should it cover?**  
*(Today's calendar, overdue tasks, top 3 priorities, something else?)*

Review of overdue tasks, review of new tasks that have come in and where they fit (ie re-priorisation of other things) and what we want to work tomorrow (whats the **one thing** we need to get done tomorrow for it to be a good day) and for the rest of the week. 

**Channel preference:**  
☐ Telegram DM  
x Webchat  
☐ Discord  
☐ Other: webchat or whatsapp (later, once its live. but this is the easiest)

---

#### Weekly Review

**Which day/time works best?**  
*(e.g., Sunday evening, Monday morning)*

Sunday afternoon/early evening as a test, to start monday well (my week starts monday in my head) 

**Should this include:**  
☐ Week-ahead calendar preview  
☐ Task triage (what's overdue, what to defer)  
☐ Goal-setting for the week  
☐ Retrospective on last week  
x Other: lets start with the above and iterate

---

#### Time-Blocking

**Should Molty SUGGEST blocks for your approval, or AUTO-BOOK certain task types?**

Not sure; lets start with a mix and iterate

**Do you want generic "focus time" blocks, or specifically named blocks (e.g., "Work on Brinc proposal")?**

Some named specifically so other Brinc employees can see it; and some more generic when I need to be more discrete/private

**Buffer time between meetings?**  
*(e.g., always leave 15 min before next call)*

Yes please. Ideally 15mins, but ideally a call starts :15mins after the hour. For example a call should be booked at 3:15pm not 3pm. That way I always have 15mins protected as meetings can overrun.

---

### 3. Boundaries & Autonomy

**Calendar edits:** Can Molty move/reschedule existing events, or only ADD new blocks?

Move with approval

**Todoist:** Can Molty mark things complete, or only Guillermo?

→ Molty can complete (as long as Guillermo is made aware somehow, end of day review or something)

**Email (ggv.molt@gmail.com):** What's this inbox for?  
*(Just assistant ops, subscriptions, or will real humans email it?)*

Probably all of the above. 

---

### 4. TMNT Integration

**Should Raphael / future agents have visibility into your calendar or Todoist?**

Todoist: Yes but partial, set to their own projects/teams to follow architecture and permissions. Calendar, Raphael should definitely see my Brinc calendar to help book client meetings. Molty should see it all.

**Or is this strictly Molty ↔ Guillermo, and project-specific tasks stay in project channels?**

Open to suggestions 

---

Resources for research:
https://reclaim.ai/
## Next Steps (Molty fills in after scoping)

*Once answers are complete, Molty will:*
- [ ] Summarize requirements
- [ ] Propose integration plan (Google OAuth vs App Password, Todoist API, etc.)
- [ ] Estimate setup time
- [ ] Create implementation checklist

---

*Save this file after answering. Molty will pick it up via Syncthing.*
