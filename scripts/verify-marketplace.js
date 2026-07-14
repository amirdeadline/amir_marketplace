#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const errors = [];
const REQUIRED = ['amir', 'amir-asana', 'prisma', 'litellm'];

function ok(cond, msg) {
  if (!cond) errors.push(msg);
}

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (e) {
    errors.push(`${p}: ${e.message}`);
    return null;
  }
}

function names(list) {
  return Array.isArray(list) ? list.map((p) => p?.name) : [];
}

const claude = readJson(path.join(ROOT, '.claude-plugin', 'marketplace.json'));
const cursor = readJson(path.join(ROOT, '.cursor-plugin', 'marketplace.json'));
const codex = readJson(path.join(ROOT, '.agents', 'plugins', 'marketplace.json'));

ok(claude?.name === 'amir-marketplace', 'Claude marketplace name');
ok(cursor?.name === 'amir-marketplace', 'Cursor marketplace name');
ok(codex?.name === 'amir-marketplace', 'Codex marketplace name');

for (const n of REQUIRED) {
  ok(names(claude?.plugins).includes(n), `Claude has ${n}`);
  ok(names(cursor?.plugins).includes(n), `Cursor has ${n}`);
  ok(names(codex?.plugins).includes(n), `Codex has ${n}`);
  const pluginDir = path.join(ROOT, 'plugins', n);
  ok(fs.existsSync(pluginDir), `plugins/${n} exists`);
  ok(
    fs.existsSync(path.join(pluginDir, '.claude-plugin', 'plugin.json')),
    `${n} claude plugin.json`
  );
}

ok(
  fs.existsSync(path.join(ROOT, 'plugins', 'prisma', 'skills', 'scm-platform', 'SKILL.md')),
  'prisma scm-platform skill'
);
ok(
  fs.existsSync(
    path.join(ROOT, 'plugins', 'prisma', 'skills', 'scm-platform', 'references', 'index.json')
  ),
  'prisma baked index (run ingest + pack)'
);
ok(
  fs.existsSync(path.join(ROOT, 'plugins', 'litellm', 'bin', 'litellm_mcp.py')),
  'litellm MCP'
);
ok(
  fs.existsSync(path.join(ROOT, 'plugins', 'litellm', 'bin', 'litellm_claude.py')),
  'litellm launcher'
);

if (errors.length) {
  console.error('VERIFY FAIL');
  for (const e of errors) console.error(' -', e);
  process.exit(1);
}
console.log('VERIFY OK — amir-marketplace ready (' + REQUIRED.join(', ') + ')');
