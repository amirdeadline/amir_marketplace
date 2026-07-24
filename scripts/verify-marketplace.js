#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const errors = [];

const REQUIRED = [
  'amir',
  'amir-asana',
  'amir-prisma',
  'amir-litellm',
  'amir-paloalto',
  'amir-aws',
  'amir-azure',
  'amir-terraform',
  'amir-docker',
  'amir-splunk',
  'amir-elastic',
  'amir-sentinel',
  'amir-qradar',
  'amir-cortex-xdr',
  'amir-ssh',
  'amir-nmap',
  'amir-wireshark',
];

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
  ok(n === 'amir' || n.startsWith('amir-'), `${n} starts with amir`);
  const pluginDir = path.join(ROOT, 'plugins', n);
  ok(fs.existsSync(pluginDir), `plugins/${n} exists`);
  const pj = readJson(path.join(pluginDir, '.claude-plugin', 'plugin.json'));
  ok(pj?.name === n, `${n} plugin.json name matches`);
}

// Sample: core amir command uses /amir:
const plan = path.join(ROOT, 'plugins', 'amir', 'commands', 'plan.md');
if (fs.existsSync(plan)) {
  const t = fs.readFileSync(plan, 'utf8');
  ok(t.includes('/amir:plan') || t.includes('name: amir:plan'), 'amir plan slash is /amir:plan');
}

if (errors.length) {
  console.error('VERIFY FAIL');
  for (const e of errors) console.error(' -', e);
  process.exit(1);
}
console.log('VERIFY OK — ' + REQUIRED.length + ' amir* plugins');
