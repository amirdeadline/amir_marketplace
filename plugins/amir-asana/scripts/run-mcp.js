#!/usr/bin/env node
'use strict';
/**
 * Cross-host launcher for the amir-asana MCP stdio server.
 * Resolves plugin root from this script location; prefers local .venv, then
 * sibling source tree ../asana/Amir_Asana_Claude/.venv, then system python.
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const PLUGIN_ROOT = path.resolve(__dirname, '..');
const SERVER = path.join(PLUGIN_ROOT, 'src', 'asana_connector', 'server.py');
const SOURCE_VENV = path.resolve(PLUGIN_ROOT, '..', '..', 'asana', 'Amir_Asana_Claude', '.venv');

function exists(p) {
  try { return fs.existsSync(p); } catch { return false; }
}

function venvPython(root) {
  if (process.platform === 'win32') {
    const p = path.join(root, 'Scripts', 'python.exe');
    return exists(p) ? p : null;
  }
  const p = path.join(root, 'bin', 'python');
  return exists(p) ? p : null;
}

const candidates = [
  venvPython(path.join(PLUGIN_ROOT, '.venv')),
  venvPython(SOURCE_VENV),
  process.platform === 'win32' ? 'python.exe' : 'python3',
  'python',
].filter(Boolean);

const python = candidates.find((c) => c.includes(path.sep) ? exists(c) : true);
if (!python) {
  console.error('[amir-asana] No Python interpreter found. Create .venv and pip install -r requirements.txt');
  process.exit(1);
}
if (!exists(SERVER)) {
  console.error('[amir-asana] Missing server.py at', SERVER);
  process.exit(1);
}

const child = spawn(python, [SERVER], {
  stdio: 'inherit',
  cwd: PLUGIN_ROOT,
  env: process.env,
});
child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code ?? 1);
});
