'use strict';
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { mergePaloEnv, paloEnvPath, workspacesRoot } = require('./load_palo_env');

function exists(p) {
  try {
    return fs.existsSync(p);
  } catch {
    return false;
  }
}

function venvPython(root) {
  if (process.platform === 'win32') {
    const p = path.join(root, '.venv', 'Scripts', 'python.exe');
    return exists(p) ? p : null;
  }
  const p = path.join(root, '.venv', 'bin', 'python');
  return exists(p) ? p : null;
}

function paloVenvPython() {
  return venvPython(path.join(workspacesRoot(), 'virtual_envs', 'palo'));
}

/** True if this interpreter can run our FastMCP (mcp 1.x) servers. */
function pythonSupportsFastMcp(exe) {
  if (!exe) return false;
  const probe = spawnSync(
    exe,
    ['-c', 'from mcp.server.fastmcp import FastMCP'],
    { encoding: 'utf8', timeout: 15000, windowsHide: true },
  );
  return probe.status === 0;
}

function pickPython(mcpRoot, label) {
  const candidates = [
    paloVenvPython(),
    venvPython(mcpRoot),
    process.platform === 'win32' ? 'python.exe' : 'python3',
    'python',
  ].filter(Boolean);

  const seen = new Set();
  for (const c of candidates) {
    const key = c.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    if (c.includes(path.sep) && !exists(c)) continue;
    if (pythonSupportsFastMcp(c)) return c;
  }
  console.error(
    `[${label}] No Python with mcp 1.x (FastMCP). Run in palo venv:\n` +
      `  pip install "mcp>=1.2.0,<2.0.0" httpx python-dotenv`,
  );
  process.exit(1);
}

/**
 * @param {string} mcpRoot directory containing run-mcp.js
 * @param {string} serverRel e.g. src/server.py
 * @param {string} label log prefix
 */
function spawnServer(mcpRoot, serverRel, label) {
  const server = path.join(mcpRoot, serverRel);
  if (!exists(server)) {
    console.error(`[${label}] Missing`, server);
    process.exit(1);
  }
  const python = pickPython(mcpRoot, label);
  const childEnv = mergePaloEnv(process.env);
  if (!exists(paloEnvPath())) {
    console.error(`[${label}] Note: palo .env not found at ${paloEnvPath()} — using OS env only`);
  }
  const child = spawn(python, [server], {
    stdio: 'inherit',
    cwd: mcpRoot,
    env: childEnv,
    windowsHide: true,
  });
  child.on('error', (err) => {
    console.error(`[${label}] Failed to start Python (${python}): ${err.message}`);
    process.exit(1);
  });
  child.on('exit', (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    process.exit(code === null || code === undefined ? 1 : code);
  });
}

module.exports = { spawnServer };
