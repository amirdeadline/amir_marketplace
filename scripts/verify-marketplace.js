#!/usr/bin/env node
/**
 * verify-marketplace.js — sanity-check marketplace manifests + packed plugins.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const errors = [];

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

function hasPlugin(list, name) {
  return Array.isArray(list) && list.some((p) => p?.name === name);
}

const claude = readJson(path.join(ROOT, '.claude-plugin', 'marketplace.json'));
const cursor = readJson(path.join(ROOT, '.cursor-plugin', 'marketplace.json'));
const codex = readJson(path.join(ROOT, '.agents', 'plugins', 'marketplace.json'));
const hosts = readJson(path.join(ROOT, 'catalog', 'hosts.json'));

ok(claude && claude.name === 'amir-marketplace', 'Claude marketplace name');
ok(hasPlugin(claude?.plugins, 'amir'), 'Claude has amir');
ok(hasPlugin(claude?.plugins, 'amir-asana'), 'Claude has amir-asana');
ok(cursor && cursor.name === 'amir-marketplace', 'Cursor marketplace name');
ok(hasPlugin(cursor?.plugins, 'amir'), 'Cursor has amir');
ok(hasPlugin(cursor?.plugins, 'amir-asana'), 'Cursor has amir-asana');
ok(codex && codex.name === 'amir-marketplace', 'Codex marketplace name');
ok(hasPlugin(codex?.plugins, 'amir'), 'Codex has amir');
ok(hasPlugin(codex?.plugins, 'amir-asana'), 'Codex has amir-asana');
ok(hosts && Array.isArray(hosts.hosts) && hosts.hosts.length >= 4, 'hosts.json covers 4+ hosts');
ok(hosts && Array.isArray(hosts.plugins) && hosts.plugins.length >= 2, 'hosts.json lists 2+ plugins');

const amir = path.join(ROOT, 'plugins', 'amir');
ok(fs.existsSync(amir), 'plugins/amir exists (run pack-amir.js)');
ok(
  fs.existsSync(path.join(amir, '.claude-plugin', 'plugin.json')),
  'amir claude plugin.json'
);
ok(
  fs.existsSync(path.join(amir, '.cursor-plugin', 'plugin.json')),
  'amir cursor plugin.json'
);
ok(
  fs.existsSync(path.join(amir, '.codex-plugin', 'plugin.json')),
  'amir codex plugin.json'
);
ok(fs.existsSync(path.join(amir, 'tools', 'state.js')), 'tools/state.js');
ok(
  fs.existsSync(path.join(amir, 'skill-specs', 'project_create.md')),
  'skill-specs'
);
ok(
  fs.existsSync(path.join(amir, 'skills', 'btw', 'SKILL.md')),
  'btw skill (Cursor/Codex)'
);
ok(
  fs.existsSync(path.join(amir, 'commands', 'btw.md')),
  'btw command (Cursor)'
);

const asana = path.join(ROOT, 'plugins', 'amir-asana');
ok(fs.existsSync(asana), 'plugins/amir-asana exists (run pack-amir-asana.js)');
ok(
  fs.existsSync(path.join(asana, '.claude-plugin', 'plugin.json')),
  'amir-asana claude plugin.json'
);
ok(
  fs.existsSync(path.join(asana, '.cursor-plugin', 'plugin.json')),
  'amir-asana cursor plugin.json'
);
ok(
  fs.existsSync(path.join(asana, '.codex-plugin', 'plugin.json')),
  'amir-asana codex plugin.json'
);
ok(fs.existsSync(path.join(asana, 'mcp.json')), 'amir-asana mcp.json');
ok(
  fs.existsSync(path.join(asana, 'scripts', 'run-mcp.js')),
  'amir-asana run-mcp.js'
);
ok(
  fs.existsSync(path.join(asana, 'src', 'asana_connector', 'server.py')),
  'amir-asana server.py'
);
ok(
  fs.existsSync(path.join(asana, 'skills', 'asana-priorities-today', 'SKILL.md')),
  'amir-asana skills'
);

const claudeHost = hosts?.hosts?.find((h) => h.id === 'claude-code');
ok(claudeHost && claudeHost.supports?.btw === false, 'Claude btw intentionally false');

if (errors.length) {
  console.error('VERIFY FAIL');
  for (const e of errors) console.error(' -', e);
  process.exit(1);
}
console.log('VERIFY OK — amir-marketplace ready (amir + amir-asana)');
