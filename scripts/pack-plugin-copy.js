#!/usr/bin/env node
/**
 * Generic copy-pack for prisma / litellm source trees into plugins/<name>.
 *
 *   node scripts/pack-plugin-copy.js --name prisma --source ../prisma
 *   node scripts/pack-plugin-copy.js --name litellm --source ../litellm
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const args = process.argv.slice(2);

function argValue(flag, fallback) {
  const i = args.indexOf(flag);
  if (i >= 0 && args[i + 1]) return args[i + 1];
  return fallback;
}

const NAME = argValue('--name', null);
if (!NAME) {
  console.error('Usage: node scripts/pack-plugin-copy.js --name <prisma|litellm> [--source <path>]');
  process.exit(1);
}

const SOURCE = path.resolve(ROOT, argValue('--source', path.join('..', NAME)));
const OUT = path.join(ROOT, 'plugins', NAME);

const SKIP = new Set([
  '.git',
  '.venv',
  '.env',
  '__pycache__',
  '.pytest_cache',
  'node_modules',
]);

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function rmrf(p) {
  fs.rmSync(p, { recursive: true, force: true });
}

function copyRecursive(src, dest) {
  const st = fs.statSync(src);
  if (st.isDirectory()) {
    ensureDir(dest);
    for (const name of fs.readdirSync(src)) {
      if (SKIP.has(name)) continue;
      if (name.endsWith('.pyc')) continue;
      copyRecursive(path.join(src, name), path.join(dest, name));
    }
  } else {
    ensureDir(path.dirname(dest));
    fs.copyFileSync(src, dest);
  }
}

function patchCursorMcp(pluginName) {
  const mcpPath = path.join(OUT, 'mcp.json');
  if (!fs.existsSync(mcpPath)) return;
  const mcp = JSON.parse(fs.readFileSync(mcpPath, 'utf8'));
  for (const [, cfg] of Object.entries(mcp.mcpServers || {})) {
    if (Array.isArray(cfg.args)) {
      cfg.args = cfg.args.map((a) =>
        String(a).includes('CLAUDE_PLUGIN_ROOT')
          ? `\${userHome}/.cursor/plugins/local/${pluginName}/bin/litellm_mcp.py`
          : a
      );
    }
    if (cfg.command === 'python' || cfg.command === 'python.exe') {
      // keep python on PATH for Cursor local
    }
  }
  fs.writeFileSync(mcpPath, JSON.stringify(mcp, null, 2) + '\n');
}

if (!fs.existsSync(SOURCE)) {
  console.error(`[pack-${NAME}] source missing: ${SOURCE}`);
  process.exit(1);
}

console.log(`[pack-${NAME}] ${SOURCE} → ${OUT}`);
rmrf(OUT);
copyRecursive(SOURCE, OUT);
if (NAME === 'litellm') patchCursorMcp(NAME);
console.log(`[pack-${NAME}] done`);
