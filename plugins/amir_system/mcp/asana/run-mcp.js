#!/usr/bin/env node
'use strict';
/**
 * Bootstrap launcher for the amir_system Asana MCP stdio server.
 *
 * 1. Loads %USERPROFILE%\.amir\secrets\asana.env (KEY=VALUE lines) into the
 *    child environment WITHOUT overriding variables already set at OS level.
 *    Secret values are never logged or printed.
 * 2. Picks a Python interpreter: local .venv first, then system python.
 * 3. Spawns src/asana_connector/server.py over stdio.
 *
 * Token variable: ASANA_ACCESS_TOKEN (verified against the connector source,
 * src/asana_connector/config.py).
 */
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const MCP_ROOT = path.resolve(__dirname);
const SERVER = path.join(MCP_ROOT, 'src', 'asana_connector', 'server.py');
const SECRETS_ENV = path.join(os.homedir(), '.amir', 'secrets', 'asana.env');

function exists(p) {
  try { return fs.existsSync(p); } catch { return false; }
}

/** Parse a simple KEY=VALUE env file. Never logs values. */
function loadEnvFile(filePath, env) {
  if (!exists(filePath)) {
    // Not fatal: the server itself reports a readable missing-token message.
    console.error(`[amir asana-mcp] Note: secrets file not found: ${filePath}`);
    return env;
  }
  const merged = { ...env };
  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);
  for (const raw of lines) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq <= 0) continue;
    const key = line.slice(0, eq).trim();
    const value = line.slice(eq + 1).trim().replace(/^["']|["']$/g, '');
    // OS-level environment always wins; the file only fills gaps.
    if (!(key in merged) || !merged[key]) {
      merged[key] = value;
    }
  }
  return merged;
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
  venvPython(path.join(MCP_ROOT, '.venv')),
  process.platform === 'win32' ? 'python.exe' : 'python3',
  'python',
].filter(Boolean);

const python = candidates.find((c) => (c.includes(path.sep) ? exists(c) : true));
if (!python) {
  console.error(
    '[amir asana-mcp] No Python interpreter found. Install Python 3.12+ or create ' +
    `a venv at ${path.join(MCP_ROOT, '.venv')} and pip install -r requirements.txt`
  );
  process.exit(1);
}
if (!exists(SERVER)) {
  console.error('[amir asana-mcp] Missing server.py at', SERVER);
  process.exit(1);
}

const childEnv = loadEnvFile(SECRETS_ENV, process.env);

const child = spawn(python, [SERVER], {
  stdio: 'inherit',
  cwd: MCP_ROOT,
  env: childEnv,
});
child.on('error', (err) => {
  console.error(`[amir asana-mcp] Failed to start Python (${python}): ${err.message}`);
  process.exit(1);
});
child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code === null || code === undefined ? 1 : code);
});
