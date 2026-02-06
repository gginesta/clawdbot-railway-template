#!/usr/bin/env bun
/**
 * Add displaced Pokemon to later phases in Notion
 */

const { Client } = require('@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_API_KEY });

// Phase 1 table: 2fe39dd6-9afd-8117-9955-fbfd60cdf149
// Phase 2 table: 2fe39dd6-9afd-815e-a810-fa4a98a5c704

async function addRow(tableId, cells) {
  const tableCells = cells.map(text => [
    { type: 'text', text: { content: text } }
  ]);
  
  await notion.blocks.children.append({
    block_id: tableId,
    children: [{
      type: 'table_row',
      table_row: { cells: tableCells }
    }]
  });
  console.log(`✅ Added row to table`);
}

async function main() {
  // Add Alakazam to Phase 1
  console.log('Adding Alakazam 🥄 to Phase 1...');
  await addRow('2fe39dd6-9afd-8117-9955-fbfd60cdf149', [
    'Strategist',
    'Alakazam 🥄',
    'Claude Sonnet',
    'IQ of 5000. Long-term planning, complex multi-step decisions.',
    'Strategy docs, decision frameworks, trade-off analysis'
  ]);

  // Add Machamp to Phase 2
  console.log('Adding Machamp 💪 to Phase 2...');
  await addRow('2fe39dd6-9afd-815e-a810-fa4a98a5c704', [
    'Batch Processor',
    'Machamp 💪',
    'GPT-5.2',
    'Four arms for parallel work. Bulk operations at scale.',
    'Mass updates, data migrations, parallel task execution'
  ]);

  // Add Eevee to Phase 2
  console.log('Adding Eevee 🔎 to Phase 2...');
  await addRow('2fe39dd6-9afd-815e-a810-fa4a98a5c704', [
    'Flex / Generalist',
    'Eevee 🔎',
    'Gemini Flash',
    'Adapts to any domain. Can evolve into specialist when needed.',
    'Overflow tasks, cross-domain work, backup for any role'
  ]);

  console.log('\n🎉 All displaced Pokemon added to later phases!');
}

main().catch(e => {
  console.error('Error:', e.message);
  process.exit(1);
});
