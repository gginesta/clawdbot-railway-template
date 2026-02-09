#!/usr/bin/env node
/**
 * Pull Notion page content and convert to markdown
 * Usage: notion-to-md.js <page-id> [output-file]
 * 
 * Security: Only calls api.notion.com via notion-utils.js
 */

const fs = require('fs');
const { notionRequest, normalizeId, getAllBlocks, blocksToMarkdown } = require('./notion-utils.js');

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log('Usage: notion-to-md.js <page-id> [output-file]');
    console.log('  If output-file specified, writes there. Otherwise prints to stdout.');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const pageId = args[0];
  const outputFile = args[1];

  try {
    // Get page title
    const nid = normalizeId(pageId);
    const page = await notionRequest(`/v1/pages/${encodeURIComponent(nid)}`, 'GET');
    let title = 'Untitled';
    if (page.properties?.title?.title) {
      title = page.properties.title.title.map(t => t.plain_text).join('');
    } else if (page.properties?.Name?.title) {
      title = page.properties.Name.title.map(t => t.plain_text).join('');
    } else {
      // Search through all properties for a title type
      for (const prop of Object.values(page.properties || {})) {
        if (prop.type === 'title' && prop.title?.length) {
          title = prop.title.map(t => t.plain_text).join('');
          break;
        }
      }
    }

    console.error(`📄 ${title}`);

    // Get all blocks
    const blocks = await getAllBlocks(pageId);
    console.error(`   ${blocks.length} blocks fetched`);

    // Convert to markdown
    const markdown = `# ${title}\n\n${blocksToMarkdown(blocks)}`;

    if (outputFile) {
      fs.writeFileSync(outputFile, markdown, 'utf8');
      console.error(`✅ Written to ${outputFile}`);
    } else {
      console.log(markdown);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
