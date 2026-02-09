#!/usr/bin/env node
/**
 * Monitor Notion page for changes
 * Usage: watch-page.js <page-id> [local-markdown-path]
 * 
 * Stores state in memory/notion-watch-state.json (relative to skill dir)
 * Security: Only calls api.notion.com via notion-utils.js
 */

const fs = require('fs');
const path = require('path');
const { notionRequest, normalizeId, getAllBlocks, blocksToMarkdown } = require('./notion-utils.js');

const STATE_FILE = path.join(__dirname, '..', 'memory', 'notion-watch-state.json');

function loadState() {
  if (!fs.existsSync(STATE_FILE)) return { pages: {} };
  return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
}

function saveState(state) {
  const dir = path.dirname(STATE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
}

async function checkPage(pageId, localPath) {
  const nid = normalizeId(pageId);
  const state = loadState();
  const pageState = state.pages[nid] || {};

  const page = await notionRequest(`/v1/pages/${encodeURIComponent(nid)}`, 'GET');
  const lastEditedTime = page.last_edited_time;
  
  let title = 'Untitled';
  for (const prop of Object.values(page.properties || {})) {
    if (prop.type === 'title' && prop.title?.length) {
      title = prop.title.map(t => t.plain_text).join('');
      break;
    }
  }

  const hasChanges = !pageState.lastEditedTime || 
    new Date(lastEditedTime) > new Date(pageState.lastEditedTime);

  const result = {
    pageId: nid,
    title,
    lastEditedTime,
    hasChanges,
    actions: []
  };

  if (hasChanges) {
    const blocks = await getAllBlocks(nid);
    const notionMarkdown = blocksToMarkdown(blocks);
    result.blockCount = blocks.length;

    if (localPath && fs.existsSync(localPath)) {
      const localMd = fs.readFileSync(localPath, 'utf8');
      result.localDiffers = localMd.trim() !== notionMarkdown.trim();
      if (result.localDiffers) {
        result.actions.push('⚠️ Local markdown differs from Notion version');
      }
    }

    if (pageState.lastEditedTime) {
      result.actions.push(`📝 Edited since ${new Date(pageState.lastEditedTime).toISOString()}`);
    } else {
      result.actions.push('🆕 First time checking this page');
    }

    // Update state
    pageState.lastEditedTime = lastEditedTime;
    pageState.lastChecked = new Date().toISOString();
    pageState.title = title;
    state.pages[nid] = pageState;
    saveState(state);
  } else {
    result.actions.push('✓ No changes since last check');
  }

  return result;
}

(async () => {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log('Usage: watch-page.js <page-id> [local-markdown-path]');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  try {
    const result = await checkPage(args[0], args[1]);
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();
