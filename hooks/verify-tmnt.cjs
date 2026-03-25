/**
 * PLAN-021: Agent-Link HMAC Verification Transform
 * 
 * Gateway hook transform that verifies tmnt-v1 envelope signatures
 * before messages reach the agent session.
 * 
 * - Valid signed messages: passed through with [VERIFIED] prefix
 * - Invalid/unsigned messages: rejected (returns null to drop)
 * - Non-tmnt messages: passed through unchanged (other webhook uses)
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Shared secret location (synced via Syncthing to all agents)
const SECRET_PATH = '/data/shared/credentials/agent-link-token.txt';

// Max message age in seconds (anti-replay)
const MAX_AGE_SECONDS = 300; // 5 minutes

function getSecret() {
  try {
    return fs.readFileSync(SECRET_PATH, 'utf-8').trim();
  } catch {
    return null;
  }
}

function computeHmac(envelope, secret) {
  const from = envelope.from || '';
  const to = envelope.to || '';
  const sentAt = envelope.sent_at || '';
  const msgId = envelope.message_id || '';
  const payload = envelope.payload || {};
  
  // Canonical JSON — must match Python agent_link_signing.py exactly
  const payloadJson = JSON.stringify(payload, Object.keys(payload).sort(), 0)
    .replace(/: /g, ':').replace(/, /g, ',');
  
  // Actually need proper canonical JSON with sorted keys recursively
  const canonicalPayload = canonicalJsonStringify(payload);
  const canonical = `${from}:${to}:${sentAt}:${msgId}:${canonicalPayload}`;
  
  return crypto.createHmac('sha256', secret)
    .update(canonical)
    .digest('hex');
}

function canonicalJsonStringify(obj) {
  if (obj === null || obj === undefined) return 'null';
  if (typeof obj === 'string') return JSON.stringify(obj);
  if (typeof obj === 'number' || typeof obj === 'boolean') return String(obj);
  if (Array.isArray(obj)) {
    return '[' + obj.map(canonicalJsonStringify).join(',') + ']';
  }
  if (typeof obj === 'object') {
    const keys = Object.keys(obj).sort();
    const pairs = keys.map(k => JSON.stringify(k) + ':' + canonicalJsonStringify(obj[k]));
    return '{' + pairs.join(',') + '}';
  }
  return String(obj);
}

/**
 * Transform function called by OpenClaw gateway hooks.
 * 
 * @param {object} ctx - Hook context
 * @param {object} ctx.body - Raw webhook body (parsed JSON)
 * @param {object} ctx.headers - Request headers
 * @returns {object|null} - Transformed message or null to reject
 */
function verifyTmnt(ctx) {
  const body = ctx.body || {};
  
  // Not a tmnt-v1 envelope — pass through unchanged
  if (body.envelope !== 'tmnt-v1') {
    return { text: JSON.stringify(body) };
  }
  
  const secret = getSecret();
  if (!secret) {
    // No secret file = can't verify. Reject for safety.
    console.error('[verify-tmnt] No shared secret found at', SECRET_PATH);
    return null;
  }
  
  // Check signature exists
  const signature = body.signature;
  if (!signature || !signature.startsWith('hmac-sha256:')) {
    console.warn('[verify-tmnt] REJECTED: Missing or invalid signature from', body.from);
    return null;
  }
  
  // Verify HMAC
  const receivedHex = signature.split(':')[1];
  const expectedHex = computeHmac(body, secret);
  
  const receivedBuf = Buffer.from(receivedHex, 'hex');
  const expectedBuf = Buffer.from(expectedHex, 'hex');
  
  if (receivedBuf.length !== expectedBuf.length || !crypto.timingSafeEqual(receivedBuf, expectedBuf)) {
    console.warn('[verify-tmnt] REJECTED: Signature mismatch from', body.from, 'msg:', body.message_id);
    return null;
  }
  
  // Check timestamp freshness (anti-replay)
  const sentAt = body.sent_at;
  if (sentAt) {
    const sentDate = new Date(sentAt);
    const ageSeconds = (Date.now() - sentDate.getTime()) / 1000;
    
    if (ageSeconds < -60) {
      console.warn('[verify-tmnt] REJECTED: Future timestamp from', body.from);
      return null;
    }
    if (ageSeconds > MAX_AGE_SECONDS) {
      console.warn('[verify-tmnt] REJECTED: Message too old (' + Math.round(ageSeconds) + 's) from', body.from);
      return null;
    }
  }
  
  // Signature valid — format the message for the agent
  const from = body.from || 'unknown';
  const type = body.type || 'message';
  const msg = body.payload?.message || JSON.stringify(body.payload);
  
  const text = `[VERIFIED fleet message from ${from}]\nType: ${type}\n\n${msg}`;
  
  return { text };
}

module.exports = verifyTmnt;
