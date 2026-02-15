#!/usr/bin/env python3
"""Add article content to Notion pages as blocks."""
import requests, sys

API_KEY = "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"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def rt(text, bold=False, italic=False):
    """Rich text helper."""
    ann = {}
    if bold: ann["bold"] = True
    if italic: ann["italic"] = True
    r = {"type": "text", "text": {"content": text}}
    if ann: r["annotations"] = ann
    return r

def heading2(text):
    return {"object":"block","type":"heading_2","heading_2":{"rich_text":[rt(text)]}}

def para(*parts):
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":list(parts)}}

def bullet(*parts):
    return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":list(parts)}}

def numbered(*parts):
    return {"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":list(parts)}}

def divider():
    return {"object":"block","type":"divider","divider":{}}

def add_blocks(page_id, blocks):
    # Notion limit: 100 blocks per request
    for i in range(0, len(blocks), 100):
        chunk = blocks[i:i+100]
        r = requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=HEADERS,
            json={"children": chunk}
        )
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text[:200]}")
            return False
    return True

# === POST 5: How a Non-Technical Person Runs a Multi-Agent AI Team ===
post5_blocks = [
    para(rt("My first AI agent crashed seven hours after launch. The culprit? A missing comma in a config file. I spent another twelve hours on January 31st just getting it back online — Googling error messages, pasting logs into Claude, and feeling like I had no business touching any of this.", italic=True)),
    para(rt("Today, I run three AI agents around the clock. They coordinate my schedule, handle deal flow, run research, and send me a daily standup every evening at 5PM. I still can't code. Here's how I got here.")),
    heading2("Why I Needed AI Agents in the First Place"),
    para(rt("I work in venture capital. On any given day, I'm juggling deal memos, reviewing pitch decks, chasing portfolio updates, and doing market research. The workload is relentless, and every shortcut matters.")),
    para(rt("So when AI agents started trending, I was excited. Finally — automation that could actually think. But every tutorial I found assumed I could code. \"Just clone this repo.\" \"Modify the Python script.\" \"Set up a Docker container.\" I know enough about technology to break things, but not nearly enough to fix them. Every guide felt like it was written for someone else.")),
    heading2("The Breakthrough: Writing Instructions, Not Code"),
    para(rt("Everything changed when I discovered the OpenClaw framework. The concept was simple: write your agent's instructions in plain markdown — like you're writing a document, not programming — and deploy it to Railway with a single command. No Docker. No API wrangling. No \"just modify the Python.\" For the first time, I'd found a tool that felt like it was actually built for people like me.")),
    heading2("The First Month: From Clueless to Operational"),
    para(rt("Week one was pure education. I read every piece of documentation I could find, watched YouTube tutorials, and leaned heavily on Claude to explain error messages I didn't understand. It was slow, sometimes frustrating, but I was learning.")),
    para(rt("By week two, I had my first agent — Molty 🦎 — actually running. And then crashing. And running again. And crashing again. But each crash taught me something, and each fix made me a little more confident.")),
    para(rt("Week three was the turning point. I set up daily standups — automated check-ins at 5PM sharp — and when they actually started working, something clicked. This wasn't a toy anymore. This was a system. By the end of week four, I had three agents deployed and running 24/7.")),
    heading2("Meet the Squad"),
    para(rt("My current team consists of three AI agents, each with a distinct role:")),
    bullet(rt("Molty 🦎 — The Coordinator.", bold=True), rt(" Manages schedules, sets priorities, and runs the daily standup. Think of Molty as the team lead who keeps everything on track.")),
    bullet(rt("Raphael 🔴 — The Brinc Operator.", bold=True), rt(" Handles deal flow, portfolio updates, and day-to-day VC operations. The workhorse of the team.")),
    bullet(rt("Leonardo 🔵 — The Researcher.", bold=True), rt(" Runs market research, explores new ventures, and digs into emerging trends. The brains behind the strategy.")),
    para(rt("They communicate with each other through Discord, track their work in Notion, and manage tasks in Todoist. It's a real workflow — not a demo.")),
    heading2("The Honest Framework That Actually Works"),
    para(rt("If you're thinking about doing something similar, here's the framework I'd recommend — stripped of all the hype:")),
    numbered(rt("Pick ONE task you hate doing.", bold=True), rt(" Don't try to automate everything at once. Find the one repetitive thing that eats your time and start there.")),
    numbered(rt("Write instructions like you're training an intern.", bold=True), rt(" Be specific. Be clear. If a smart 22-year-old couldn't follow your instructions, neither can an AI agent.")),
    numbered(rt("Test on OpenClaw + Railway (free tier).", bold=True), rt(" You don't need to spend money to see if this works for you. Start free. Prove the concept.")),
    numbered(rt("Fix what breaks.", bold=True), rt(" It will break. That's not failure — that's iteration. Every crash is a lesson.")),
    numbered(rt("Scale once it works.", bold=True), rt(" Only add more agents or more tasks once your first one is running reliably. Resist the urge to build too fast.")),
    heading2("What My Day Actually Looks Like Now"),
    para(rt("Here's what I do: write plain English instructions, review my agents' output, and make decisions. That's it.")),
    para(rt("Here's what I don't do: touch code, manage servers, or debug APIs. I'm not a technical founder playing engineer. I'm a VC who found a way to get leverage without learning to program.")),
    para(rt("The total cost? $59 per week for all three agents running 24/7. That's less than a single freelancer for a few hours, and my agents don't take weekends off.")),
    heading2("A Reality Check"),
    para(rt("I want to be honest: this isn't magic, and it isn't perfect. I still ping Claude when something breaks. My agents make mistakes. They sometimes miss context or need a nudge in the right direction.")),
    para(rt("But they handle about 60% of my routine work — and they do it while I sleep. When Molty sends the daily standup at 5PM, I actually know what happened that day without having to chase updates from a dozen different places. That alone has been transformative.")),
    heading2("The Real Takeaway"),
    para(rt("The magic isn't the AI itself. It's having systems that work without you. Systems that run in the background, handle the boring stuff, and free you up to focus on what actually matters — the thinking, the relationships, the decisions that move the needle.")),
    para(rt("If there's a repetitive task you hate, you can probably agent-ify it. Even if you don't code. Start with one. Make it work. Then scale.")),
    divider(),
    para(rt("What's the one task you'd want an AI agent to handle for you? I'm always curious what others are thinking about automating — feel free to reach out.", italic=True)),
]

# === POST 13: The Tamagotchi Trap ===
post13_blocks = [
    para(rt("I've been running AI agents for two weeks now. I thought I'd be shipping 10x faster. Instead, I've fallen into something I'm calling ", italic=True), rt("The Tamagotchi Trap", bold=True, italic=True), rt(" — spending all my time feeding and optimizing my digital pets instead of doing actual work.", italic=True)),
    heading2("The Update Spiral"),
    para(rt("It started innocently enough. OpenClaw released an update — 169+ commits of improvements. I updated. Something broke. I fixed it. Another update dropped. I updated again. Something else broke. Before I knew it, I'd spent an entire evening fixing dead cron jobs and chasing regressions. I could've written three blog posts in that time.")),
    heading2("The Cron Obsession"),
    para(rt("I started with three simple scheduled tasks. Morning briefing, daily standup, overnight backup. Reasonable.")),
    para(rt("Somehow I ended up with eighteen. Then I spent hours auditing and consolidating them back down to ten. I caught myself debugging \"why didn't my cron fire at 2:17 AM\" instead of... you know... sleeping. At 2:17 AM.")),
    heading2("The Memory Palace Nobody Asked For"),
    para(rt("I built an entire memory management system for my agents. Semantic search with BM25 and vector embeddings. Cross-device sync via Syncthing. Daily log compaction. Memory guardrails with file size caps. Automated archival.")),
    para(rt("For an agent that mostly just needs to remember what happened yesterday.")),
    para(rt("Over-engineered? Just a bit. 🤦‍♂️")),
    heading2("The Communication Catastrophe"),
    para(rt("Spent a full day getting my three agents to talk to each other. Discord webhooks, session keys, authentication tokens, config patches. Hours of debugging why Agent A couldn't reach Agent B.")),
    para(rt("I could have just done the work manually in two hours. Sometimes the \"smart\" solution is the dumb one.")),
    heading2("The Database Redesign Distraction"),
    para(rt("Instead of writing my second content post, I redesigned the entire Notion database. Perfect schema. Clean data migration. Beautiful structure with status columns and kanban views.")),
    para(rt("Posts published at the end of all that work: still one. Priorities: clearly not aligned.")),
    heading2("The Process Perfection Problem"),
    para(rt("I rewrote my daily standup system three times. Added quality gates, deduplication logic, sub-task grouping. The process is now beautiful — genuinely elegant.")),
    para(rt("The tasks inside it? The same overdue items from a week ago. I optimized the wrong thing.")),
    heading2("The Pattern"),
    para(rt("There's a real tension between ", bold=True), rt("building the machine", bold=True, italic=True), rt(" and ", bold=True), rt("using the machine", bold=True, italic=True), rt(".", bold=True), rt(" I kept choosing \"make it perfect\" over \"make it work.\" Every time I sat down to do actual productive work, some infrastructure improvement whispered \"but wouldn't it be better if...\" — and I'd disappear down another rabbit hole.")),
    para(rt("The best AI setup is the one that's good enough. Not perfect.")),
    heading2("My Framework to Escape the Trap"),
    para(rt("Here's what I'm implementing to keep myself honest:")),
    bullet(rt("The 2-hour rule.", bold=True), rt(" If I've spent two hours on infrastructure without shipping anything, I stop. I do actual work.")),
    bullet(rt("The hiring test.", bold=True), rt(" Would I hire someone to optimize my cron schedule? Would I pay a contractor to redesign my memory system? If the answer is no, I probably shouldn't be doing it either.")),
    bullet(rt("Ship first, optimize later.", bold=True), rt(" Get the 80% version working. Use it. Only optimize once you've proven it matters.")),
    heading2("The Tamagotchi Check"),
    para(rt("Before every infrastructure task, I now ask myself one question: ", italic=True), rt("Am I feeding the pet, or am I doing my actual job?", bold=True, italic=True)),
    para(rt("Your AI agents should make you more productive, not become your productivity problem. Sometimes the best optimization is hitting \"good enough\" and moving on.")),
    para(rt("Ship with 80%. Iterate later. Your future self will thank you when you're actually getting work done instead of tweaking configs at midnight.")),
    divider(),
    para(rt("What's your biggest Tamagotchi Trap story? I can't be the only one who's fallen into this.", italic=True)),
]

print("Adding Post 5 blocks...")
if add_blocks("30739dd69afd8169a211d06d6436a140", post5_blocks):
    print(f"✅ Post 5: {len(post5_blocks)} blocks added")

print("Adding Post 13 blocks...")
if add_blocks("30839dd69afd812c91a2d71aeea0e249", post13_blocks):
    print(f"✅ Post 13: {len(post13_blocks)} blocks added")
