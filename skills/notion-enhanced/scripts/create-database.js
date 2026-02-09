#!/usr/bin/env node
/**
 * Create a Notion database under a parent page.
 * Usage: create-database.js <parent-page-id> <database-title> --schema '<json>'
 *
 * Schema JSON is a Notion database properties object.
 * Example: '{"Name":{"title":{}},"URL":{"url":{}},"Tags":{"multi_select":{}}}'
 */

const { notionRequest, normalizeId } = require('./notion-utils.js');

(async () => {
  const args = process.argv.slice(2);
  if (args.length < 2 || args[0] === '--help') {
    console.log('Usage: create-database.js <parent-page-id> <database-title> --schema \'<json>\'');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const parentPageId = normalizeId(args[0]);
  const title = args[1];
  let schemaJson = null;

  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--schema' && args[i + 1]) { schemaJson = args[i + 1]; i++; }
  }

  if (!schemaJson) {
    console.error('Error: --schema is required');
    process.exit(1);
  }

  let properties;
  try { properties = JSON.parse(schemaJson); }
  catch (e) {
    console.error('Error: schema JSON invalid:', e.message);
    process.exit(1);
  }

  try {
    const db = await notionRequest('/v1/databases', 'POST', {
      parent: { type: 'page_id', page_id: parentPageId },
      title: [{ type: 'text', text: { content: title } }],
      properties
    });

    console.log(JSON.stringify({
      id: db.id,
      url: db.url,
      title,
      parentPageId
    }, null, 2));
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();
