#!/usr/bin/env node
/**
 * Shared Notion API utilities
 * Used by all notion-enhanced scripts
 * 
 * Security: Only calls api.notion.com. Credentials via NOTION_API_KEY env var.
 */

const https = require('https');

const NOTION_VERSION = '2022-06-28';

function getApiKey() {
  const key = process.env.NOTION_API_KEY;
  if (!key) {
    console.error('Error: NOTION_API_KEY environment variable not set');
    console.error('Set it with: export NOTION_API_KEY="ntn_..."');
    console.error('Or source: source /data/workspace/credentials/notion.env');
    process.exit(1);
  }
  return key;
}

function normalizeId(id) {
  const clean = id.replace(/-/g, '');
  if (clean.length === 32) {
    return `${clean.slice(0,8)}-${clean.slice(8,12)}-${clean.slice(12,16)}-${clean.slice(16,20)}-${clean.slice(20)}`;
  }
  return id;
}

function notionRequest(path, method, data = null) {
  const apiKey = getApiKey();
  return new Promise((resolve, reject) => {
    const requestData = data ? JSON.stringify(data) : null;
    
    const options = {
      hostname: 'api.notion.com',
      port: 443,
      path: path,
      method: method,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json'
      }
    };

    if (requestData) {
      options.headers['Content-Length'] = Buffer.byteLength(requestData);
    }

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(body));
        } else {
          let error;
          try { error = JSON.parse(body); } catch { error = { message: body }; }
          
          if (res.statusCode === 404) {
            reject(new Error(`Not found (404). Make sure the page/database is shared with your integration.`));
          } else if (res.statusCode === 401) {
            reject(new Error('Authentication failed (401). Check your NOTION_API_KEY.'));
          } else if (res.statusCode === 429) {
            reject(new Error('Rate limit exceeded (429). Wait a moment and retry.'));
          } else {
            reject(new Error(`Notion API error (${res.statusCode}): ${error.message || body}`));
          }
        }
      });
    });

    req.on('error', reject);
    if (requestData) req.write(requestData);
    req.end();
  });
}

function extractPropertyValue(property) {
  if (!property) return null;
  switch (property.type) {
    case 'title':
      return property.title.map(t => t.plain_text).join('');
    case 'rich_text':
      return property.rich_text.map(t => t.plain_text).join('');
    case 'number':
      return property.number;
    case 'select':
      return property.select?.name || null;
    case 'multi_select':
      return property.multi_select.map(s => s.name);
    case 'date':
      return property.date ? { start: property.date.start, end: property.date.end } : null;
    case 'checkbox':
      return property.checkbox;
    case 'url':
      return property.url;
    case 'email':
      return property.email;
    case 'phone_number':
      return property.phone_number;
    case 'status':
      return property.status?.name || null;
    case 'relation':
      return property.relation.map(r => r.id);
    case 'formula':
      const f = property.formula;
      return f[f.type];
    case 'rollup':
      const r = property.rollup;
      return r[r.type];
    case 'people':
      return property.people.map(p => p.name || p.id);
    case 'created_time':
      return property.created_time;
    case 'last_edited_time':
      return property.last_edited_time;
    default:
      return property[property.type];
  }
}

// Parse rich text to markdown
function richTextToMarkdown(richText) {
  if (!richText || richText.length === 0) return '';
  return richText.map(rt => {
    let text = rt.plain_text || '';
    const ann = rt.annotations || {};
    if (ann.code) text = `\`${text}\``;
    if (ann.bold) text = `**${text}**`;
    if (ann.italic) text = `*${text}*`;
    if (ann.strikethrough) text = `~~${text}~~`;
    if (rt.href) text = `[${text}](${rt.href})`;
    else if (rt.text?.link) text = `[${text}](${rt.text.link.url})`;
    return text;
  }).join('');
}

// Parse markdown text to Notion rich_text
function parseRichText(text) {
  const richText = [];
  const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|\[.*?\]\(.*?\)|\`.*?\`)/);
  
  for (let part of parts) {
    if (!part) continue;
    if (part.startsWith('**') && part.endsWith('**')) {
      richText.push({ type: 'text', text: { content: part.slice(2, -2) }, annotations: { bold: true } });
    } else if (part.startsWith('`') && part.endsWith('`')) {
      richText.push({ type: 'text', text: { content: part.slice(1, -1) }, annotations: { code: true } });
    } else if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
      richText.push({ type: 'text', text: { content: part.slice(1, -1) }, annotations: { italic: true } });
    } else if (part.match(/\[(.*?)\]\((.*?)\)/)) {
      const match = part.match(/\[(.*?)\]\((.*?)\)/);
      richText.push({ type: 'text', text: { content: match[1], link: { url: match[2] } } });
    } else {
      richText.push({ type: 'text', text: { content: part } });
    }
  }
  return richText.length > 0 ? richText : [{ type: 'text', text: { content: text } }];
}

// Fetch all blocks with pagination
async function getAllBlocks(blockId) {
  const nid = normalizeId(blockId);
  let allBlocks = [];
  let cursor = null;
  do {
    const path = `/v1/blocks/${encodeURIComponent(nid)}/children${cursor ? `?start_cursor=${encodeURIComponent(cursor)}` : ''}`;
    const response = await notionRequest(path, 'GET');
    allBlocks = allBlocks.concat(response.results);
    cursor = response.has_more ? response.next_cursor : null;
  } while (cursor);
  return allBlocks;
}

// Convert blocks to markdown
function blocksToMarkdown(blocks) {
  const lines = [];
  for (const block of blocks) {
    const type = block.type;
    const content = block[type];
    if (!content) continue;
    
    switch (type) {
      case 'heading_1':
        lines.push(`# ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'heading_2':
        lines.push(`## ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'heading_3':
        lines.push(`### ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'paragraph':
        lines.push(richTextToMarkdown(content.rich_text));
        break;
      case 'bulleted_list_item':
        lines.push(`- ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'numbered_list_item':
        lines.push(`1. ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'to_do':
        const checked = content.checked ? 'x' : ' ';
        lines.push(`- [${checked}] ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'toggle':
        lines.push(`<details><summary>${richTextToMarkdown(content.rich_text)}</summary></details>`);
        break;
      case 'code':
        const lang = content.language || '';
        lines.push(`\`\`\`${lang}`);
        lines.push(richTextToMarkdown(content.rich_text));
        lines.push('```');
        break;
      case 'quote':
        lines.push(`> ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'callout':
        const icon = content.icon?.emoji || '💡';
        lines.push(`> ${icon} ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'divider':
        lines.push('---');
        break;
      case 'table_of_contents':
        lines.push('[TOC]');
        break;
      case 'child_database':
        lines.push(`📊 *Database: ${content.title}*`);
        break;
      case 'child_page':
        lines.push(`📄 *Page: ${content.title}*`);
        break;
      case 'bookmark':
        lines.push(`🔗 [${content.caption?.length ? richTextToMarkdown(content.caption) : content.url}](${content.url})`);
        break;
      case 'image':
        const imgUrl = content.file?.url || content.external?.url || '';
        lines.push(`![image](${imgUrl})`);
        break;
      default:
        // Skip unsupported block types silently
        break;
    }
    lines.push('');
  }
  return lines.join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

// Parse markdown into Notion blocks
function parseMarkdown(markdown) {
  const lines = markdown.split('\n');
  const blocks = [];
  let currentParagraph = [];
  let inCodeBlock = false;
  let codeLanguage = '';
  let codeContent = [];

  const flushParagraph = () => {
    if (currentParagraph.length > 0) {
      const text = currentParagraph.join('\n').trim();
      if (text) {
        blocks.push({ type: 'paragraph', paragraph: { rich_text: parseRichText(text) } });
      }
      currentParagraph = [];
    }
  };

  for (let line of lines) {
    if (line.startsWith('```')) {
      if (!inCodeBlock) {
        flushParagraph();
        inCodeBlock = true;
        codeLanguage = line.slice(3).trim() || 'plain text';
        codeContent = [];
      } else {
        blocks.push({
          type: 'code',
          code: { language: codeLanguage, rich_text: [{ type: 'text', text: { content: codeContent.join('\n') } }] }
        });
        inCodeBlock = false;
      }
      continue;
    }
    if (inCodeBlock) { codeContent.push(line); continue; }

    if (line.match(/^#{1,3}\s+/)) {
      flushParagraph();
      const level = line.match(/^#+/)[0].length;
      const text = line.replace(/^#+\s+/, '').trim();
      const key = level === 1 ? 'heading_1' : level === 2 ? 'heading_2' : 'heading_3';
      blocks.push({ type: key, [key]: { rich_text: parseRichText(text) } });
      continue;
    }
    if (line.match(/^---+$/)) { flushParagraph(); blocks.push({ type: 'divider', divider: {} }); continue; }
    if (line.match(/^[-*]\s+/)) {
      flushParagraph();
      blocks.push({ type: 'bulleted_list_item', bulleted_list_item: { rich_text: parseRichText(line.replace(/^[-*]\s+/, '').trim()) } });
      continue;
    }
    if (line.match(/^\d+\.\s+/)) {
      flushParagraph();
      blocks.push({ type: 'numbered_list_item', numbered_list_item: { rich_text: parseRichText(line.replace(/^\d+\.\s+/, '').trim()) } });
      continue;
    }
    if (line.match(/^>\s+/)) {
      flushParagraph();
      blocks.push({ type: 'quote', quote: { rich_text: parseRichText(line.replace(/^>\s+/, '').trim()) } });
      continue;
    }
    if (line.trim() === '') { flushParagraph(); continue; }
    currentParagraph.push(line);
  }
  flushParagraph();
  return blocks;
}

module.exports = {
  notionRequest,
  normalizeId,
  getApiKey,
  extractPropertyValue,
  richTextToMarkdown,
  parseRichText,
  getAllBlocks,
  blocksToMarkdown,
  parseMarkdown,
  NOTION_VERSION
};
