#!/usr/bin/env node
/**
 * Add entry to Notion database
 * Usage: add-to-database.js <database-id> --title "Title" [--props '<json>']
 * 
 * Props JSON maps property names to {type, value} pairs.
 * Example: --props '{"Status":{"type":"select","value":"Draft"},"Tags":{"type":"multi_select","value":"AI,Research"}}'
 * 
 * Security: Only calls api.notion.com via notion-utils.js
 */

const { notionRequest, normalizeId } = require('./notion-utils.js');

function buildProperty(type, value) {
  switch (type) {
    case 'title': return { title: [{ text: { content: value } }] };
    case 'rich_text': return { rich_text: [{ type: 'text', text: { content: value } }] };
    case 'select': return { select: { name: value } };
    case 'multi_select': return { multi_select: value.split(',').map(v => ({ name: v.trim() })) };
    case 'checkbox': return { checkbox: value === 'true' || value === true };
    case 'number': return { number: parseFloat(value) };
    case 'url': return { url: value };
    case 'date': return { date: { start: value } };
    case 'status': return { status: { name: value } };
    default: return { rich_text: [{ type: 'text', text: { content: String(value) } }] };
  }
}

(async () => {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log('Usage: add-to-database.js <database-id> --title "Title" [--props \'<json>\']');
    console.log('Props: {"PropName":{"type":"select","value":"Value"}}');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const databaseId = args[0];
  let title = '', propsJson = '{}';

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--title' && args[i + 1]) { title = args[i + 1]; i++; }
    else if (args[i] === '--props' && args[i + 1]) { propsJson = args[i + 1]; i++; }
  }

  if (!title) {
    console.error('Error: --title is required');
    process.exit(1);
  }

  try {
    const extraProps = JSON.parse(propsJson);
    const properties = {};
    
    // Find the title property name (usually "Name" or first title property)
    // Default to "Name" — will be overridden if DB schema differs
    properties['Name'] = { title: [{ text: { content: title } }] };

    for (const [name, spec] of Object.entries(extraProps)) {
      if (name.toLowerCase() === 'name' || name.toLowerCase() === 'title') {
        // Override the title property with correct name
        properties[name] = { title: [{ text: { content: spec.value || title } }] };
        delete properties['Name'];
      } else {
        properties[name] = buildProperty(spec.type, spec.value);
      }
    }

    const nid = normalizeId(databaseId);
    const result = await notionRequest('/v1/pages', 'POST', {
      parent: { database_id: nid },
      properties
    });

    console.log(`✅ Added "${title}" to database`);
    console.log(`   Page ID: ${result.id}`);
    console.log(`   URL: ${result.url}`);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();
