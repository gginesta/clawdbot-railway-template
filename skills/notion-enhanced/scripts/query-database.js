#!/usr/bin/env node
/**
 * Query Notion database with filters and sorts
 * Usage: query-database.js <database-id> [--filter <json>] [--sort <json>] [--limit N] [--all]
 * 
 * Security: Only calls api.notion.com via notion-utils.js
 */

const { notionRequest, extractPropertyValue } = require('./notion-utils.js');

async function queryDatabase(databaseId, filter = null, sorts = null, pageSize = 10, fetchAll = false) {
  const queryPayload = { page_size: Math.min(pageSize, 100) };
  if (filter) queryPayload.filter = filter;
  if (sorts) queryPayload.sorts = sorts;

  let allResults = [];
  let cursor = null;

  do {
    if (cursor) queryPayload.start_cursor = cursor;
    const result = await notionRequest(`/v1/databases/${databaseId}/query`, 'POST', queryPayload);
    
    const mapped = result.results.map(page => {
      const properties = {};
      for (const [key, value] of Object.entries(page.properties)) {
        properties[key] = extractPropertyValue(value);
      }
      return {
        id: page.id,
        url: page.url,
        lastEdited: page.last_edited_time,
        properties
      };
    });

    allResults = allResults.concat(mapped);
    cursor = result.has_more ? result.next_cursor : null;

    if (!fetchAll || allResults.length >= pageSize) break;
  } while (cursor);

  return fetchAll ? allResults : allResults.slice(0, pageSize);
}

(async () => {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log('Usage: query-database.js <database-id> [options]');
    console.log('  --filter <json>  Filter expression');
    console.log('  --sort <json>    Sort expression');
    console.log('  --limit <num>    Max results (default: 10)');
    console.log('  --all            Fetch all results (paginated)');
    process.exit(0);
  }

  const databaseId = args[0];
  let filter = null, sorts = null, limit = 10, fetchAll = false;

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--filter' && args[i + 1]) { filter = JSON.parse(args[i + 1]); i++; }
    else if (args[i] === '--sort' && args[i + 1]) { sorts = JSON.parse(args[i + 1]); i++; }
    else if (args[i] === '--limit' && args[i + 1]) { limit = parseInt(args[i + 1]); i++; }
    else if (args[i] === '--all') { fetchAll = true; }
  }

  try {
    const results = await queryDatabase(databaseId, filter, sorts, limit, fetchAll);
    console.log(JSON.stringify(results, null, 2));
    console.error(`\n✓ Found ${results.length} result(s)`);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();
