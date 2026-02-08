import fs from 'fs';
import path from 'path';

const NOTION_API_KEY = process.env.NOTION_API_KEY;
if (!NOTION_API_KEY) throw new Error('NOTION_API_KEY not set');

const BRINC_HQ_PAGE_ID = process.env.NOTION_BRINC_HQ_PAGE_ID || '2fc39dd69afd81d698d8c9d99306d115';
const INDEX_PAGE_ID = process.env.NOTION_TEAM_BIOS_INDEX_PAGE_ID || '30039dd69afd81b28174fc328c94bc58';

const TEAM_DIR = '/data/shared/memory-vault/knowledge/projects/brinc/team';

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
  if (!res.ok) throw new Error(`Notion API error ${res.status}: ${text}`);
  return json;
}

function chunkText(str, max = 1800) {
  const chunks = [];
  let cur = '';
  for (const line of str.split('\n')) {
    if ((cur + line + '\n').length > max) {
      if (cur.trim().length) chunks.push(cur.trimEnd());
      cur = '';
    }
    cur += line + '\n';
  }
  if (cur.trim().length) chunks.push(cur.trimEnd());
  return chunks;
}

function childrenFromMarkdown(md) {
  return chunkText(md).map((t) => ({
    object: 'block',
    type: 'paragraph',
    paragraph: {
      rich_text: [{ type: 'text', text: { content: t } }],
    },
  }));
}

async function createPage({ parentPageId, title, emoji, md }) {
  const page = await notionFetch('https://api.notion.com/v1/pages', {
    method: 'POST',
    body: {
      parent: { type: 'page_id', page_id: parentPageId },
      icon: { type: 'emoji', emoji },
      properties: {
        title: { title: [{ type: 'text', text: { content: title } }] },
      },
      children: childrenFromMarkdown(md),
    },
  });
  return { id: page.id, url: page.url };
}

async function appendLink({ pageId, label, url }) {
  await notionFetch(`https://api.notion.com/v1/blocks/${pageId}/children`, {
    method: 'PATCH',
    body: {
      children: [
        {
          object: 'block',
          type: 'bulleted_list_item',
          bulleted_list_item: {
            rich_text: [
              { type: 'text', text: { content: label + ' — ' } },
              { type: 'text', text: { content: url, link: { url } } },
            ],
          },
        },
      ],
    },
  });
}

async function main() {
  const bioPath = path.join(TEAM_DIR, 'raphael', 'BIO.md');
  const md = fs.readFileSync(bioPath, 'utf8');

  const created = await createPage({
    parentPageId: BRINC_HQ_PAGE_ID,
    title: 'Raphael 🔴 — Team Lead (Bio)',
    emoji: '🔴',
    md,
  });

  await appendLink({ pageId: INDEX_PAGE_ID, label: 'Raphael 🔴 — Team Lead (Bio)', url: created.url });
  await appendLink({ pageId: BRINC_HQ_PAGE_ID, label: 'Raphael 🔴 — Team Lead (Bio)', url: created.url });

  console.log(created.url);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
