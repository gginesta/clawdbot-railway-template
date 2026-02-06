#!/usr/bin/env bun
/**
 * Update Pokemon Squad Phase 0 table with OG starters
 */

const { Client } = require('@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_API_KEY });

const updates = [
  {
    id: '2fe39dd6-9afd-817b-88e0-f6415e6c3fab', // Spec Writer row
    cells: [
      'Spec Writer',
      'Squirtle 🐢',
      'GPT-5.2 (high thinking)',
      'Water flows and adapts. Shapes ideas into structured specs.',
      'Project specs, integration plans, architecture docs, roadmaps'
    ]
  },
  {
    id: '2fe39dd6-9afd-8111-b303-efef5f362f7a', // Builder row
    cells: [
      'Builder',
      'Charmander 🔥',
      'GPT-5.2 (high thinking)',
      'Fire energy, makes things happen. Builds what specs define.',
      'Scripts, skills, tools, automation code, deployment configs'
    ]
  },
  {
    id: '2fe39dd6-9afd-8133-ba66-cf0d72690c3e', // Researcher row
    cells: [
      'Researcher',
      'Bulbasaur 🌱',
      'Gemini Flash',
      'Grows knowledge from seeds. Patient, thorough intel gathering.',
      'Web research, trend analysis, API docs, competitive intel'
    ]
  }
];

async function updateRow(rowId, cells) {
  const tableCells = cells.map(text => [
    { type: 'text', text: { content: text } }
  ]);
  
  await notion.blocks.update({
    block_id: rowId,
    table_row: { cells: tableCells }
  });
  console.log(`✅ Updated row ${rowId}`);
}

async function main() {
  for (const row of updates) {
    await updateRow(row.id, row.cells);
  }
  console.log('\n🎉 Phase 0 table updated with OG starters!');
}

main().catch(e => {
  console.error('Error:', e.message);
  process.exit(1);
});
