'use strict';
/**
 * Merge palo workspace .env into process.env without overriding values already set.
 * Never logs secret values.
 */
const fs = require('fs');
const os = require('os');
const path = require('path');

function workspacesRoot() {
  const fromEnv = (process.env.WORKSPACES_ROOT || '').trim();
  if (fromEnv) return fromEnv;
  if (process.platform === 'win32') return 'E:\\PC3_Shared\\workspaces';
  return path.join(os.homedir(), 'workspaces');
}

function paloEnvPath() {
  return path.join(workspacesRoot(), 'virtual_envs', 'palo', '.env');
}

function parseEnvFile(filePath) {
  const out = {};
  if (!fs.existsSync(filePath)) return out;
  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);
  for (const raw of lines) {
    const line = raw.trim();
    if (!line || line.startsWith('#') || !line.includes('=')) continue;
    let body = line;
    if (body.toLowerCase().startsWith('export ')) body = body.slice(7).trim();
    const eq = body.indexOf('=');
    const key = body.slice(0, eq).trim();
    let value = body.slice(eq + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (key) out[key] = value;
  }
  return out;
}

/** @param {NodeJS.ProcessEnv} base */
function mergePaloEnv(base) {
  const merged = { ...base };
  const file = paloEnvPath();
  const fromFile = parseEnvFile(file);
  for (const [key, value] of Object.entries(fromFile)) {
    if (!(key in merged) || !merged[key]) merged[key] = value;
  }
  return merged;
}

module.exports = { mergePaloEnv, paloEnvPath, workspacesRoot };
