#!/usr/bin/env node
/**
 * Search Notion workspace
 * Usage: search-notion.js <query> [--filter page|database] [--limit N]
 * 
 * Security: Only calls api.notion.com via notion-utils.js
 */

const { notionRequest } = require('./notion-utils.js');

(async () => {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log('Usage: search-notion.js <query> [--filter page|database] [--limit N]');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const query = args[0];
  let filter = null, limit = 10;

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--filter' && args[i + 1]) {
      filter = { property: 'object', value: args[i + 1] };
      i++;
    } else if (args[i] === '--limit' && args[i + 1]) {
      limit = parseInt(args[i + 1]);
      i++;
    }
  }

  try {
    const payload = { query, page_size: Math.min(limit, 100) };
    if (filter) payload.filter = filter;

    const result = await notionRequest('/v1/search', 'POST', payload);
    
    const items = result.results.map(item => ({
      id: item.id,
      object: item.object,
      title: item.object === 'page' 
        ? (Object.values(item.properties || {}).find(p => p.type === 'title')?.title?.map(t => t.plain_text).join('') || 'Untitled')
        : (item.title?.[0]?.plain_text || 'Untitled'),
      url: item.url,
      lastEdited: item.last_edited_time
    }));

    console.log(JSON.stringify(items, null, 2));
    console.error(`\n✓ Found ${items.length} result(s)`);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();
