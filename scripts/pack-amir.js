#!/usr/bin/env node
/**
 * pack-amir.js — Build a self-contained plugins/amir package for marketplace installs.
 *
 * Claude Code / Cursor / Codex installers copy the plugin directory into a cache.
 * Paths like ../../skills from adapters/ break after that copy. This pack:
 *   - Copies host-agnostic package roots into plugins/amir
 *   - Renames host-agnostic skill specs to skill-specs/*.md
 *   - Merges host skill wrappers into skills/<name>/SKILL.md (Codex+Cursor include /btw)
 *   - Copies Cursor commands/rules and Claude agents/hooks
 *   - Rewrites wrapper paths to resolve inside the packed plugin root
 *
 * Usage (from marketplace root or anywhere):
 *   node scripts/pack-amir.js
 *   node scripts/pack-amir.js --source ../Amir --out plugins/amir
 */

'use strict';

const fs = require('fs');
const path = require('path');

const MARKETPLACE_ROOT = path.resolve(__dirname, '..');
const args = process.argv.slice(2);

function argValue(flag, fallback) {
  const i = args.indexOf(flag);
  if (i >= 0 && args[i + 1]) return path.resolve(args[i + 1]);
  return fallback;
}

const SOURCE = argValue(
  '--source',
  path.resolve(MARKETPLACE_ROOT, '..', 'Amir')
);
const OUT = argValue('--out', path.join(MARKETPLACE_ROOT, 'plugins', 'amir'));

function die(msg) {
  console.error(`[pack-amir] ${msg}`);
  process.exit(1);
}

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
      if (name === 'node_modules' || name === '.git') continue;
      copyRecursive(path.join(src, name), path.join(dest, name));
    }
  } else {
    ensureDir(path.dirname(dest));
    fs.copyFileSync(src, dest);
  }
}

function readText(p) {
  return fs.readFileSync(p, 'utf8');
}

function writeText(p, text) {
  ensureDir(path.dirname(p));
  fs.writeFileSync(p, text, 'utf8');
}

function rewriteWrapper(body) {
  let out = body;
  // Host-agnostic specs live under skill-specs/ in the packed plugin.
  out = out.replace(/skills\/([a-z0-9_]+)\.md/g, 'skill-specs/$1.md');
  out = out.replace(
    /\$\{CLAUDE_PLUGIN_ROOT\}\/\.\.\/\.\.\/skills\//g,
    '${CLAUDE_PLUGIN_ROOT}/skill-specs/'
  );
  out = out.replace(
    /\$\{CLAUDE_PLUGIN_ROOT\}\/\.\.\/\.\.\/tools\//g,
    '${CLAUDE_PLUGIN_ROOT}/tools/'
  );
  out = out.replace(
    /\$\{CLAUDE_PLUGIN_ROOT\}\/\.\.\/\.\.\/core\//g,
    '${CLAUDE_PLUGIN_ROOT}/core/'
  );
  out = out.replace(
    /amir package root is two levels above the Claude Code plugin directory\./g,
    'amir package root is this plugin directory (self-contained marketplace package).'
  );
  out = out.replace(
    /where `<amir-root>` is the directory containing `core\/`, `skills\/`, and `tools\/`\./g,
    'where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).'
  );
  out = out.replace(
    /Resolve amir root: parent of `adapters\/` \(typically `<amir-root>`\)\./g,
    'Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).'
  );
  out = out.replace(
    /in the amir package \(installed alongside this Cursor adapter\)\./g,
    'in this packed amir plugin (`skill-specs/<name>.md`).'
  );
  out = out.replace(
    /Follow the procedure in the host-agnostic amir skill file `skills\//g,
    'Follow the procedure in the host-agnostic amir skill file `skill-specs/'
  );
  return out;
}

function mergeSkillDir(srcSkillsDir) {
  if (!fs.existsSync(srcSkillsDir)) return;
  for (const name of fs.readdirSync(srcSkillsDir)) {
    const src = path.join(srcSkillsDir, name);
    if (!fs.statSync(src).isDirectory()) continue;
    const skillMd = path.join(src, 'SKILL.md');
    if (!fs.existsSync(skillMd)) continue;
    const destDir = path.join(OUT, 'skills', name);
    ensureDir(destDir);
    const rewritten = rewriteWrapper(readText(skillMd));
    writeText(path.join(destDir, 'SKILL.md'), rewritten);
  }
}

function pack() {
  if (!fs.existsSync(SOURCE)) die(`Source not found: ${SOURCE}`);
  const versionPath = path.join(SOURCE, 'VERSION');
  if (!fs.existsSync(versionPath)) die(`Missing VERSION in ${SOURCE}`);

  console.log(`[pack-amir] source: ${SOURCE}`);
  console.log(`[pack-amir] out:    ${OUT}`);

  rmrf(OUT);
  ensureDir(OUT);

  // Shared package roots
  for (const dir of ['core', 'schemas', 'templates', 'tools']) {
    const src = path.join(SOURCE, dir);
    if (!fs.existsSync(src)) die(`Missing ${dir}/ in source`);
    copyRecursive(src, path.join(OUT, dir));
  }

  // Host-agnostic skill specs → skill-specs/
  const skillsSrc = path.join(SOURCE, 'skills');
  ensureDir(path.join(OUT, 'skill-specs'));
  for (const name of fs.readdirSync(skillsSrc)) {
    if (!name.endsWith('.md')) continue;
    fs.copyFileSync(
      path.join(skillsSrc, name),
      path.join(OUT, 'skill-specs', name)
    );
  }

  // Copy VERSION + README excerpt + capabilities
  fs.copyFileSync(versionPath, path.join(OUT, 'VERSION'));
  fs.copyFileSync(
    path.join(SOURCE, 'adapters', 'capabilities.md'),
    path.join(OUT, 'capabilities.md')
  );

  // Claude agents + hooks
  const claude = path.join(SOURCE, 'adapters', 'claude-code');
  copyRecursive(path.join(claude, 'agents'), path.join(OUT, 'agents'));
  copyRecursive(path.join(claude, 'hooks'), path.join(OUT, 'hooks'));
  if (fs.existsSync(path.join(claude, 'bin'))) {
    copyRecursive(path.join(claude, 'bin'), path.join(OUT, 'bin'));
  }

  // Cursor commands + rules (merge hooks if cursor has more — keep Claude hooks as base)
  const cursor = path.join(SOURCE, 'adapters', 'cursor');
  copyRecursive(path.join(cursor, 'commands'), path.join(OUT, 'commands'));
  copyRecursive(path.join(cursor, 'rules'), path.join(OUT, 'rules'));
  // Also rewrite command files that reference skills/*.md
  for (const name of fs.readdirSync(path.join(OUT, 'commands'))) {
    const p = path.join(OUT, 'commands', name);
    if (!name.endsWith('.md')) continue;
    writeText(p, rewriteWrapper(readText(p)));
  }
  // Rewrite cursor rule paths
  const rulePath = path.join(OUT, 'rules', 'amir-core.mdc');
  if (fs.existsSync(rulePath)) {
    writeText(rulePath, rewriteWrapper(readText(rulePath)));
  }

  // Codex AGENTS.md + sample config
  const codex = path.join(SOURCE, 'adapters', 'codex');
  fs.copyFileSync(path.join(codex, 'AGENTS.md'), path.join(OUT, 'AGENTS.md'));
  if (fs.existsSync(path.join(codex, '.codex'))) {
    copyRecursive(path.join(codex, '.codex'), path.join(OUT, '.codex'));
  }
  // Soften AGENTS.md path refs for packed layout
  {
    let agents = readText(path.join(OUT, 'AGENTS.md'));
    agents = agents.replace(/\.agents\/skills\//g, 'skills/');
    agents = agents.replace(/skills\/([a-z0-9_]+)\.md/g, 'skill-specs/$1.md');
    writeText(path.join(OUT, 'AGENTS.md'), agents);
  }

  // Merge skill wrappers: Claude → Cursor → Codex (later hosts can add btw, etc.)
  mergeSkillDir(path.join(claude, 'skills'));
  mergeSkillDir(path.join(cursor, 'skills'));
  mergeSkillDir(path.join(codex, '.agents', 'skills'));

  // Claude Code must not treat /btw as a supported amir feature.
  // Keep the skill file for Cursor/Codex discovery, but gate Claude Code out.
  const btwSkill = path.join(OUT, 'skills', 'btw', 'SKILL.md');
  if (fs.existsSync(btwSkill)) {
    let body = readText(btwSkill);
    if (!body.includes('CLAUDE CODE GATE')) {
      body = body.replace(
        '# btw\n',
        `# btw

## CLAUDE CODE GATE

If the host is **Claude Code**, refuse this skill. amir intentionally does **not**
register \`/btw\` there (no true zero-pollution ephemeral session). Tell the user
to ask in a normal chat or switch to Cursor/Codex for \`/btw\`.

`
      );
      writeText(btwSkill, body);
    }
  }

  // Host manifests
  writeText(
    path.join(OUT, '.claude-plugin', 'plugin.json'),
    JSON.stringify(
      {
        name: 'amir',
        description:
          'Portable multi-agent project-execution harness: context engineering, JSON state, QA loops, cost control, and human visibility.',
        version: readText(versionPath).trim(),
        author: { name: 'amir' },
        keywords: [
          'multi-agent',
          'orchestrator',
          'qa',
          'project-management',
          'budget'
        ]
      },
      null,
      2
    ) + '\n'
  );

  writeText(
    path.join(OUT, '.cursor-plugin', 'plugin.json'),
    JSON.stringify(
      {
        name: 'amir',
        version: readText(versionPath).trim(),
        description:
          'Portable multi-agent project-execution harness for Cursor: commands, rules, skills, and hooks.',
        author: { name: 'amir' },
        keywords: ['multi-agent', 'qa', 'orchestrator', 'project-management'],
        skills: './skills/',
        commands: './commands/',
        rules: './rules/',
        hooks: './hooks/hooks.json',
        agents: './agents/'
      },
      null,
      2
    ) + '\n'
  );

  writeText(
    path.join(OUT, '.codex-plugin', 'plugin.json'),
    JSON.stringify(
      {
        name: 'amir',
        version: readText(versionPath).trim(),
        description:
          'Portable multi-agent project-execution harness for Codex: skills, AGENTS.md guidance, JSON state tools.',
        skills: './skills/'
      },
      null,
      2
    ) + '\n'
  );

  writeText(
    path.join(OUT, 'README.md'),
    `# amir (marketplace package)

Self-contained amir plugin built by \`scripts/pack-amir.js\` for Claude Code, Cursor, and Codex marketplace installs.

| Path | Role |
|------|------|
| \`core/\` | Process rules (single source) |
| \`skill-specs/\` | Host-agnostic skill definitions |
| \`skills/\` | Host wrappers (\`SKILL.md\`) |
| \`tools/\` | Node.js CLI (state, render, activity, cost, doctor, secrets_scan) |
| \`commands/\` | Cursor slash commands (includes \`/btw\`) |
| \`agents/\` | Claude Code agent defs |
| \`rules/\` | Cursor always-on rules |
| \`schemas/\`, \`templates/\` | State schemas + prompt templates |

**Source of truth for development:** \`../Amir\` (sibling repo). Re-run \`node scripts/pack-amir.js\` after changing the source.

Requires **Node.js >= 18**.

See \`capabilities.md\` for host degrade paths. Claude Code does **not** register \`/btw\`.
`
  );

  // Count skills
  const skillDirs = fs
    .readdirSync(path.join(OUT, 'skills'))
    .filter((n) =>
      fs.existsSync(path.join(OUT, 'skills', n, 'SKILL.md'))
    );
  const specs = fs
    .readdirSync(path.join(OUT, 'skill-specs'))
    .filter((n) => n.endsWith('.md'));

  console.log(
    `[pack-amir] packed ${skillDirs.length} skill wrappers, ${specs.length} skill-specs`
  );
  console.log('[pack-amir] done');
}

pack();
