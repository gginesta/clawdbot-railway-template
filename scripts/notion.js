#!/usr/bin/env bun
/**
 * Notion API helper script
 * Usage:
 *   notion.js page <page_id>              - Get page info
 *   notion.js blocks <block_id>           - Get block children
 *   notion.js append <page_id> <markdown> - Append markdown to page
 *   notion.js update <page_id> <json>     - Update page properties
 */

const { Client } = require('@notionhq/client');

const notion = new Client({ auth: process.env.NOTION_API_KEY });

const [,, cmd, id, ...rest] = process.argv;

async function main() {
  switch (cmd) {
    case 'page': {
      const page = await notion.pages.retrieve({ page_id: id });
      console.log(JSON.stringify(page, null, 2));
      break;
    }
    
    case 'blocks': {
      const blocks = await notion.blocks.children.list({ block_id: id });
      console.log(JSON.stringify(blocks.results, null, 2));
      break;
    }
    
    case 'append': {
      const text = rest.join(' ');
      // Convert simple markdown to Notion blocks
      const lines = text.split('\n');
      const children = lines.map(line => {
        if (line.startsWith('# ')) {
          return {
            object: 'block',
            type: 'heading_1',
            heading_1: { rich_text: [{ type: 'text', text: { content: line.slice(2) } }] }
          };
        } else if (line.startsWith('## ')) {
          return {
            object: 'block',
            type: 'heading_2',
            heading_2: { rich_text: [{ type: 'text', text: { content: line.slice(3) } }] }
          };
        } else if (line.startsWith('- ')) {
          return {
            object: 'block',
            type: 'bulleted_list_item',
            bulleted_list_item: { rich_text: [{ type: 'text', text: { content: line.slice(2) } }] }
          };
        } else if (line.trim()) {
          return {
            object: 'block',
            type: 'paragraph',
            paragraph: { rich_text: [{ type: 'text', text: { content: line } }] }
          };
        }
        return null;
      }).filter(Boolean);
      
      const result = await notion.blocks.children.append({
        block_id: id,
        children
      });
      console.log(JSON.stringify(result, null, 2));
      break;
    }
    
    case 'db': {
      const db = await notion.databases.retrieve({ database_id: id });
      console.log(JSON.stringify(db, null, 2));
      break;
    }
    
    case 'query': {
      const results = await notion.databases.query({ database_id: id });
      console.log(JSON.stringify(results.results, null, 2));
      break;
    }
    
    default:
      console.log('Usage: notion.js <page|blocks|append|db|query> <id> [args...]');
  }
}

main().catch(e => {
  console.error('Error:', e.message);
  process.exit(1);
});
