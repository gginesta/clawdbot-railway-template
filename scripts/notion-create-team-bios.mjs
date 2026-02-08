import fs from 'fs';
import path from 'path';

const NOTION_API_KEY = process.env.NOTION_API_KEY;
if (!NOTION_API_KEY) throw new Error('NOTION_API_KEY not set');

const PARENT_PAGE_ID = process.env.NOTION_PARENT_PAGE_ID || '2fc39dd69afd81d698d8c9d99306d115';

const TEAM_DIR = '/data/shared/memory-vault/knowledge/projects/brinc/team';
const agents = [
  { slug: 'bowser', title: 'Bowser 🐢 — Sales (Bio)', emoji: '🐢' },
  { slug: 'toad', title: 'Toad 🍄 — SDR/Materials (Bio)', emoji: '🍄' },
  { slug: 'yoshi', title: 'Yoshi 🦖 — Proposals (Bio)', emoji: '🦖' },
  { slug: 'luigi', title: 'Luigi 💚 — Research (Bio)', emoji: '💚' },
  { slug: 'peach', title: 'Peach 👑 — Marketing (Bio)', emoji: '👑' },
];

async function notionFetch(url, { method = 'GET', body } = {}) {
  const res = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${NOTION_API_KEY}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let json;
  try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text }; }
  if (!res.ok) {
    throw new Error(`Notion API ${method} ${url} failed: ${res.status} ${res.statusText}\n${JSON.stringify(json, null, 2)}`);
  }
  return json;
}

function chunkText(str, max = 1800) {
  const chunks = [];
  let cur = '';
  for (const line of str.split('\n')) {
    // +1 for newline
    if ((cur + line + '\n').length > max) {
      if (cur.trim().length) chunks.push(cur.trimEnd());
      cur = '';
    }
    cur += line + '\n';
  }
  if (cur.trim().length) chunks.push(cur.trimEnd());
  return chunks;
}

function paragraphsFromMarkdown(md) {
  // Minimal safe conversion: keep as plain text paragraphs, chunked.
  const chunks = chunkText(md);
  return chunks.map((t) => ({
    object: 'block',
    type: 'paragraph',
    paragraph: {
      rich_text: [{ type: 'text', text: { content: t } }],
    },
  }));
}

async function createBioPage({ title, emoji, md }) {
  const children = paragraphsFromMarkdown(md);
  const page = await notionFetch('https://api.notion.com/v1/pages', {
    method: 'POST',
    body: {
      parent: { type: 'page_id', page_id: PARENT_PAGE_ID },
      icon: { type: 'emoji', emoji },
      properties: {
        title: {
          title: [{ type: 'text', text: { content: title } }],
        },
      },
      children,
    },
  });
  return { id: page.id, url: page.url };
}

async function appendLinksToParent(links) {
  const now = new Date().toISOString().slice(0, 10);
  const blocks = [
    {
      object: 'block',
      type: 'heading_2',
      heading_2: {
        rich_text: [{ type: 'text', text: { content: `Team bios (auto-added ${now})` } }],
      },
    },
    ...links.map((l) => ({
      object: 'block',
      type: 'bulleted_list_item',
      bulleted_list_item: {
        rich_text: [
          { type: 'text', text: { content: l.title + ' — ', link: null } },
          { type: 'text', text: { content: l.url, link: { url: l.url } } },
        ],
      },
    })),
  ];

  await notionFetch(`https://api.notion.com/v1/blocks/${PARENT_PAGE_ID}/children`, {
    method: 'PATCH',
    body: { children: blocks },
  });
}

async function main() {
  const created = [];
  for (const a of agents) {
    const bioPath = path.join(TEAM_DIR, a.slug, 'BIO.md');
    if (!fs.existsSync(bioPath)) {
      console.error(`Missing BIO.md for ${a.slug}: ${bioPath}`);
      continue;
    }
    const md = fs.readFileSync(bioPath, 'utf8');
    const { url } = await createBioPage({ title: a.title, emoji: a.emoji, md });
    created.push({ title: a.title, url });
    console.log(`Created: ${a.title} -> ${url}`);
  }

  if (created.length) {
    await appendLinksToParent(created);
    console.log('Appended links to parent page.');
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
