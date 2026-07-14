#!/usr/bin/env node
/**
 * pack-amir-asana.js — Build plugins/amir-asana from ../asana/Amir_Asana_Claude.
 *
 * Copies MCP server + skills into a self-contained marketplace plugin, then
 * writes Claude / Cursor / Codex manifests. Optionally junctions .venv and .env
 * from the source tree so local installs keep working credentials + deps.
 *
 * Usage:
 *   node scripts/pack-amir-asana.js
 *   node scripts/pack-amir-asana.js --source ../asana/Amir_Asana_Claude --out plugins/amir-asana
 *   node scripts/pack-amir-asana.js --no-link
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const MARKETPLACE_ROOT = path.resolve(__dirname, '..');
const args = process.argv.slice(2);

function hasFlag(flag) {
  return args.includes(flag);
}

function argValue(flag, fallback) {
  const i = args.indexOf(flag);
  if (i >= 0 && args[i + 1]) return path.resolve(args[i + 1]);
  return fallback;
}

const SOURCE = argValue(
  '--source',
  path.resolve(MARKETPLACE_ROOT, '..', 'asana', 'Amir_Asana_Claude')
);
const OUT = argValue(
  '--out',
  path.join(MARKETPLACE_ROOT, 'plugins', 'amir-asana')
);
const NO_LINK = hasFlag('--no-link');

const SKIP_NAMES = new Set([
  '.git',
  '.venv',
  '.env',
  '.pytest_cache',
  '__pycache__',
  'node_modules',
  '.claude-plugin',
]);

const VERSION = '0.2.0';
const DESCRIPTION =
  'Asana connector (MCP, 17 tools) + task skills: priorities, review, standup, triage, create/edit/complete, report sync.';

function die(msg) {
  console.error(`[pack-amir-asana] ${msg}`);
  process.exit(1);
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function rmrf(p) {
  fs.rmSync(p, { recursive: true, force: true });
}

function writeJson(p, obj) {
  ensureDir(path.dirname(p));
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + '\n', 'utf8');
}

function writeText(p, text) {
  ensureDir(path.dirname(p));
  fs.writeFileSync(p, text, 'utf8');
}

function copyRecursive(src, dest) {
  const st = fs.statSync(src);
  if (st.isDirectory()) {
    ensureDir(dest);
    for (const name of fs.readdirSync(src)) {
      if (SKIP_NAMES.has(name)) continue;
      if (name.endsWith('.pyc')) continue;
      copyRecursive(path.join(src, name), path.join(dest, name));
    }
  } else {
    ensureDir(path.dirname(dest));
    fs.copyFileSync(src, dest);
  }
}

function linkPath(target, linkPathOut) {
  if (!fs.existsSync(target)) {
    console.warn(`[pack-amir-asana] skip link — missing ${target}`);
    return false;
  }
  try {
    if (fs.existsSync(linkPathOut)) fs.rmSync(linkPathOut, { recursive: true, force: true });
  } catch {
    /* ignore */
  }

  if (process.platform === 'win32') {
    const isDir = fs.statSync(target).isDirectory();
    const r = spawnSync(
      'cmd',
      ['/c', 'mklink', ...(isDir ? ['/J'] : []), linkPathOut, target],
      { encoding: 'utf8' }
    );
    if (r.status !== 0) {
      console.warn(
        `[pack-amir-asana] mklink failed for ${linkPathOut}: ${r.stderr || r.stdout}`
      );
      return false;
    }
    return true;
  }

  fs.symlinkSync(target, linkPathOut, fs.statSync(target).isDirectory() ? 'dir' : 'file');
  return true;
}

function writeRunMcp() {
  const js = `#!/usr/bin/env node
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
`;
  writeText(path.join(OUT, 'scripts', 'run-mcp.js'), js);
}

function writeManifests() {
  writeJson(path.join(OUT, '.claude-plugin', 'plugin.json'), {
    name: 'amir-asana',
    version: VERSION,
    description: DESCRIPTION,
    author: { name: 'Amir' },
    mcpServers: {
      'amir-asana': {
        command: 'node',
        args: ['${CLAUDE_PLUGIN_ROOT}/scripts/run-mcp.js'],
      },
    },
  });

  writeJson(path.join(OUT, '.cursor-plugin', 'plugin.json'), {
    name: 'amir-asana',
    version: VERSION,
    description: DESCRIPTION,
    author: { name: 'Amir' },
    keywords: ['asana', 'mcp', 'tasks', 'productivity'],
    skills: './skills/',
    mcpServers: './mcp.json',
  });

  // Cursor resolves local plugins under ~/.cursor/plugins/local/<name>
  writeJson(path.join(OUT, 'mcp.json'), {
    mcpServers: {
      'amir-asana': {
        command: 'node',
        args: [
          '${userHome}/.cursor/plugins/local/amir-asana/scripts/run-mcp.js',
        ],
      },
    },
  });

  writeJson(path.join(OUT, '.codex-plugin', 'plugin.json'), {
    name: 'amir-asana',
    version: VERSION,
    description: DESCRIPTION,
    skills: './skills/',
  });

  writeText(
    path.join(OUT, 'README.md'),
    `# amir-asana

Packed marketplace plugin for the Amir Asana connector (MCP + skills).

Source of truth: \`../../asana/Amir_Asana_Claude\`. Re-pack with:

\`\`\`bash
node scripts/pack-amir-asana.js
\`\`\`

## Setup

1. Ensure the source \`.venv\` exists (or create one in this packed folder):
   \`\`\`powershell
   python -m venv .venv
   .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
   \`\`\`
2. Credentials: \`.env\` with \`ASANA_ACCESS_TOKEN=\` (pack links source \`.env\` when present).
3. Install from **amir-marketplace** (Claude / Cursor / Codex).

## Cursor local

\`\`\`powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\\.cursor\\plugins\\local" | Out-Null
cmd /c mklink /J "%USERPROFILE%\\.cursor\\plugins\\local\\amir-asana" "E:\\PC3_Shared\\Plugins\\amir_marketplace\\plugins\\amir-asana"
\`\`\`

Then Developer: Reload Window.
`
  );
}

function main() {
  if (!fs.existsSync(SOURCE)) die(`source not found: ${SOURCE}`);
  if (!fs.existsSync(path.join(SOURCE, 'src', 'asana_connector', 'server.py'))) {
    die(`server.py missing under ${SOURCE}`);
  }
  if (!fs.existsSync(path.join(SOURCE, 'skills'))) {
    die(`skills/ missing under ${SOURCE}`);
  }

  console.log(`[pack-amir-asana] source: ${SOURCE}`);
  console.log(`[pack-amir-asana] out:    ${OUT}`);

  rmrf(OUT);
  ensureDir(OUT);
  copyRecursive(SOURCE, OUT);
  writeRunMcp();
  writeManifests();

  if (!NO_LINK) {
    const venvLinked = linkPath(path.join(SOURCE, '.venv'), path.join(OUT, '.venv'));
    // File symlinks need elevation on Windows — copy .env instead (gitignored).
    let envCopied = false;
    const envSrc = path.join(SOURCE, '.env');
    const envDest = path.join(OUT, '.env');
    if (fs.existsSync(envSrc)) {
      fs.copyFileSync(envSrc, envDest);
      envCopied = true;
    }
    console.log(
      `[pack-amir-asana] links: .venv=${venvLinked ? 'ok' : 'skipped'} .env=${envCopied ? 'copied' : 'skipped'}`
    );
  }

  const skillCount = fs
    .readdirSync(path.join(OUT, 'skills'))
    .filter((n) => fs.existsSync(path.join(OUT, 'skills', n, 'SKILL.md'))).length;
  console.log(`[pack-amir-asana] done — version ${VERSION}, ${skillCount} skills`);
}

main();
