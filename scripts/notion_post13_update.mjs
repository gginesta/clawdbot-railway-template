// Node.js script to update Notion Post 13 from thread to article format
// Run with: node scripts/notion_post13_update.mjs

const NOTION_API_KEY = "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";
const BLOCK_ID = "30839dd6-9afd-812c-91a2-d71aeea0e249";
const PAGE_ID = "30839dd6-9afd-812c-91a2-d71aeea0e249";
const NOTION_VERSION = "2022-06-28";

const headers = {
  "Authorization": `Bearer ${NOTION_API_KEY}`,
  "Notion-Version": NOTION_VERSION,
  "Content-Type": "application/json"
};

async function notionRequest(url, method = "GET", body = null) {
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json();
  if (!res.ok) {
    console.error(`Error ${res.status}:`, JSON.stringify(data, null, 2));
  }
  return data;
}

// Helper to create text segments with optional annotations
function text(content, annotations = {}) {
  const t = { type: "text", text: { content } };
  if (Object.keys(annotations).length > 0) t.annotations = annotations;
  return t;
}

function paragraph(...richText) {
  return { object: "block", type: "paragraph", paragraph: { rich_text: richText } };
}

function heading2(content) {
  return { object: "block", type: "heading_2", heading_2: { rich_text: [text(content)] } };
}

async function main() {
  // Step 1: Get existing child blocks
  console.log("=== Step 1: Getting existing child blocks ===");
  const children = await notionRequest(`https://api.notion.com/v1/blocks/${BLOCK_ID}/children?page_size=100`);
  const blockIds = (children.results || []).map(b => b.id);
  console.log(`Found ${blockIds.length} existing blocks`);

  // Step 2: Delete all existing child blocks
  console.log("\n=== Step 2: Deleting existing child blocks ===");
  for (const id of blockIds) {
    console.log(`Deleting block: ${id}`);
    await notionRequest(`https://api.notion.com/v1/blocks/${id}`, "DELETE");
  }
  console.log("All blocks deleted");

  // Step 3: Update page property Type to "Article"
  console.log("\n=== Step 3: Updating page Type to Article ===");
  const pageUpdate = await notionRequest(`https://api.notion.com/v1/pages/${PAGE_ID}`, "PATCH", {
    properties: {
      Type: { select: { name: "Article" } }
    }
  });
  console.log("Page type updated:", pageUpdate.properties?.Type?.select?.name || "check manually");

  // Step 4: Add new article content as blocks
  console.log("\n=== Step 4: Adding new article content ===");
  
  const articleBlocks = [
    // Intro
    paragraph(
      text("I've been running AI agents for two weeks now. The promise was simple: set up some smart assistants, automate the busywork, and ship 10x faster. Instead, I've discovered something nobody warns you about\u200a—\u200athe moment your AI tools stop working for you and start making you work for them.")
    ),
    paragraph(
      text("I'm calling it "),
      text("The Tamagotchi Trap", { bold: true }),
      text(": spending all your time feeding and optimizing your digital pets instead of doing actual work. And I fell into it hard.")
    ),

    // Section 1
    heading2("The Update Spiral"),
    paragraph(
      text("It started innocently enough. OpenClaw released a new version. Then another. Then another. I went from 2026.2.10 to 2026.2.13 to the latest main branch\u200a—\u200a169+ commits of \"improvements.\" Each update broke something. I spent an entire evening resurrecting dead cron jobs, debugging config changes, and patching things back together. In the time it took me to \"upgrade,\" I could have written three blog posts. But hey, at least my agent was running the freshest build, right?")
    ),

    // Section 2
    heading2("The Cron Obsession"),
    paragraph(
      text("I started with three simple cron jobs. Reasonable. Responsible, even. Somehow, over the course of a few days, I ended up with eighteen. Then I spent hours auditing and consolidating them back down to ten, carefully adjusting schedules and eliminating redundancies. At one point I was genuinely debugging why a cron job didn't fire at 2:17 AM. Let me repeat that: I was losing sleep over whether my automation ran at the exact right minute while I was supposed to be sleeping. The irony was not lost on me\u200a—\u200aeventually.")
    ),

    // Section 3
    heading2("The Memory Palace Nobody Asked For"),
    paragraph(
      text("Then came the memory system. I built QMD search, set up Syncthing sync, implemented daily log compaction, added memory guardrails, configured file size caps. A whole architecture for agent memory management. What did my agent actually need to remember? Mostly just what happened yesterday. I built a cathedral when a sticky note would have done the job. Over-engineered doesn't even begin to cover it.")
    ),

    // Section 4
    heading2("The Multi-Agent Money Pit"),
    paragraph(
      text("I spent a full day getting my agents to talk to each other. Discord webhooks, session keys, config patches\u200a—\u200athe works. A beautiful inter-agent communication system. The task I was trying to automate? Something I could have done manually in two hours. Sometimes the \"smart\" solution is the dumb one. When your automation takes 4x longer than doing it by hand, you haven't saved time. You've invested it in an imaginary future that may never arrive.")
    ),

    // Section 5
    heading2("The Perfect Database with Nothing In It"),
    paragraph(
      text("Instead of writing my second Content Hub post, I redesigned the entire Notion database. Perfect schema. Clean migration. Beautiful structure. Posts published after all that work? Still one. The database was pristine and empty. My priorities were clearly not aligned\u200a—\u200aI was polishing the container instead of filling it.")
    ),

    // Section 6
    heading2("The Standup System That Stood Still"),
    paragraph(
      text("My personal favorite: I rewrote my standup system three times. Quality gates, deduplication, sub-task grouping\u200a—\u200athe process became a work of art. The tasks inside it? The same overdue items from a week ago, staring back at me like disappointed parents. I had optimized the view of my failures into a beautifully formatted dashboard of procrastination.")
    ),

    // The Pattern
    heading2("The Pattern"),
    paragraph(
      text("Looking at all of this, the pattern is painfully clear. There's a real tension between building the machine and using the machine. And I kept choosing \"make it perfect\" over \"make it work.\" Every hour I spent optimizing infrastructure was an hour I didn't spend shipping. Every config tweak was a blog post unwritten. Every architectural improvement was a customer conversation I didn't have.")
    ),
    paragraph(
      text("The best AI setup is the one that's good enough\u200a—\u200anot perfect. Perfection is a trap, and with AI tools, it's an especially seductive one because the optimization always "),
      text("feels", { italic: true }),
      text(" productive. You're typing commands, reading logs, solving problems. It looks like work. It feels like work. But it's not "),
      text("your", { italic: true }),
      text(" work.")
    ),

    // Framework
    heading2("Escaping the Trap: A Simple Framework"),
    paragraph(
      text("I've since adopted a few rules to keep myself honest:")
    ),
    paragraph(
      text("The 2-Hour Rule.", { bold: true }),
      text(" If I've spent two hours on infrastructure without shipping anything, I stop. Full stop. I close the terminal, open a doc, and do actual work. The infrastructure will still be there tomorrow.")
    ),
    paragraph(
      text("The Hiring Test.", { bold: true }),
      text(" Would I hire someone to do this task? Would I pay a contractor $100/hour to optimize my cron schedule? If the answer is no, why am I spending my own time on it?")
    ),
    paragraph(
      text("The Tamagotchi Check.", { bold: true }),
      text(" Before any AI infrastructure work, I ask myself one question: Am I feeding the pet, or am I doing my actual job? Your AI agents should make you more productive, not become your productivity problem.")
    ),
    paragraph(
      text("Ship First, Optimize Later.", { bold: true }),
      text(" Get the 80% solution out the door. Your future self can iterate. But your future self can't publish the blog post you never wrote because you were tweaking configs at midnight.")
    ),

    // Takeaway
    heading2("The Takeaway"),
    paragraph(
      text("AI agents are incredible tools. But they come with a hidden cost that nobody talks about: the maintenance tax. Every agent you spin up, every automation you build, every integration you configure\u200a—\u200ait all needs feeding. And if you're not careful, you'll spend more time maintaining the system than benefiting from it.")
    ),
    paragraph(
      text("Sometimes the best optimization is hitting \"good enough\" and moving on. Sometimes the smartest thing you can do with your AI setup is stop touching it.")
    ),
    paragraph(
      text("Now if you'll excuse me, I have actual work to do. My Tamagotchi can wait.")
    ),
  ];

  const result = await notionRequest(
    `https://api.notion.com/v1/blocks/${BLOCK_ID}/children`,
    "PATCH",
    { children: articleBlocks }
  );
  
  console.log(`Added ${result.results?.length || 0} blocks`);
  console.log("\n=== Done! ===");
}

main().catch(console.error);
