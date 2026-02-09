#!/usr/bin/env node
/**
 * Update Notion page properties
 * Usage: update-properties.js <page-id> <property-name> <value> [--type TYPE]
 * 
 * Supported types: select, multi_select, checkbox, number, url, email, date, rich_text, status
 * Security: Only calls api.notion.com via notion-utils.js
 */

const { notionRequest, normalizeId } = require('./notion-utils.js');

function buildPropertyValue(type, value) {
  switch (type) {
    case 'select':
      return { select: { name: value } };
    case 'multi_select':
      return { multi_select: value.split(',').map(v => ({ name: v.trim() })) };
    case 'checkbox':
      return { checkbox: value === 'true' || value === '1' };
    case 'number':
      return { number: parseFloat(value) };
    case 'url':
      return { url: value };
    case 'email':
      return { email: value };
    case 'date':
      return { date: { start: value } };
    case 'rich_text':
      return { rich_text: [{ type: 'text', text: { content: value } }] };
    case 'status':
      return { status: { name: value } };
    default:
      console.error(`Unknown type: ${type}. Use: select, multi_select, checkbox, number, url, email, date, rich_text, status`);
      process.exit(1);
  }
}

(async () => {
  const args = process.argv.slice(2);
  
  if (args.length < 3 || args[0] === '--help') {
    console.log('Usage: update-properties.js <page-id> <property-name> <value> [--type TYPE]');
    console.log('Types: select, multi_select, checkbox, number, url, email, date, rich_text, status');
    console.log('Default type: select');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const pageId = args[0];
  const propertyName = args[1];
  const value = args[2];
  let type = 'select';

  for (let i = 3; i < args.length; i++) {
    if (args[i] === '--type' && args[i + 1]) { type = args[i + 1]; i++; }
  }

  try {
    const nid = normalizeId(pageId);
    const properties = { [propertyName]: buildPropertyValue(type, value) };
    
    const result = await notionRequest(`/v1/pages/${nid}`, 'PATCH', { properties });
    console.log(`✅ Updated "${propertyName}" = "${value}" (${type})`);
    console.log(`   Page: ${result.url}`);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();
