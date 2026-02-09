#!/usr/bin/env node
/**
 * Push markdown file to Notion as a new page
 * Usage: md-to-notion.js <markdown-file> <parent-page-id> <page-title>
 * 
 * Security: Only calls api.notion.com via notion-utils.js
 */

const fs = require('fs');
const { notionRequest, parseMarkdown, normalizeId } = require('./notion-utils.js');

async function createPage(parentId, title, blocks) {
  const nid = normalizeId(parentId);
  const data = {
    parent: { page_id: nid },
    properties: {
      title: { title: [{ text: { content: title } }] }
    },
    children: blocks.slice(0, 100)
  };
  return notionRequest('/v1/pages', 'POST', data);
}

async function appendBlocks(pageId, blocks) {
  return notionRequest(`/v1/blocks/${pageId}/children`, 'PATCH', { children: blocks.slice(0, 100) });
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 3 || args[0] === '--help') {
    console.log('Usage: md-to-notion.js <markdown-file> <parent-page-id> <page-title>');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const [mdFile, parentId, pageTitle] = args;

  if (!fs.existsSync(mdFile)) {
    console.error(`Error: File not found: ${mdFile}`);
    process.exit(1);
  }

  try {
    const markdown = fs.readFileSync(mdFile, 'utf8');
    const blocks = parseMarkdown(markdown);
    console.error(`Parsed ${blocks.length} blocks from markdown`);

    const page = await createPage(parentId, pageTitle, blocks);
    console.log(`✓ Created page: ${page.url}`);
    console.log(`  Page ID: ${page.id}`);

    // Append remaining blocks in batches of 100
    for (let i = 100; i < blocks.length; i += 100) {
      const batch = blocks.slice(i, i + 100);
      await appendBlocks(page.id, batch);
      console.log(`✓ Appended ${batch.length} blocks (${i}-${i + batch.length})`);
      await new Promise(r => setTimeout(r, 350)); // Rate limiting
    }

    console.log(`\n✅ Done! ${blocks.length} blocks → ${page.url}`);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
