#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const SKIP_DIRS = new Set(['node_modules', '.git', '.svn', '.hg']);
const TEXT_EXTENSIONS = new Set([
  '.txt', '.md', '.json', '.js', '.ts', '.jsx', '.tsx', '.py', '.rb', '.go',
  '.java', '.cs', '.yaml', '.yml', '.xml', '.html', '.css', '.scss', '.env',
  '.sh', '.ps1', '.toml', '.ini', '.cfg', '.conf', '.sql', '.graphql',
]);

const PATTERNS = [
  { type: 'aws_access_key', regex: /AKIA[0-9A-Z]{16}/g },
  { type: 'github_token', regex: /gh[pousr]_[A-Za-z0-9_]{20,}/g },
  { type: 'slack_token', regex: /xox[baprs]-[0-9A-Za-z-]{10,}/g },
  { type: 'private_key_block', regex: /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/g },
  {
    type: 'high_entropy',
    regex: /(?:^|[^A-Za-z0-9+/=])([A-Za-z0-9+/]{32,}={0,2})(?:[^A-Za-z0-9+/=]|$)/g,
  },
];

function isBinaryBuffer(buf) {
  const sample = buf.slice(0, Math.min(buf.length, 8000));
  for (const byte of sample) {
    if (byte === 0) return true;
  }
  return false;
}

function shouldScanFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (!ext) return true;
  return TEXT_EXTENSIONS.has(ext);
}

function maskSnippet(value) {
  if (value.length <= 8) return '***';
  return `${value.slice(0, 4)}...${value.slice(-4)}`;
}

function scanContent(content, filePath) {
  const findings = [];
  const lines = content.split('\n');

  for (let lineNo = 0; lineNo < lines.length; lineNo += 1) {
    const line = lines[lineNo];
    for (const pattern of PATTERNS) {
      pattern.regex.lastIndex = 0;
      let match;
      while ((match = pattern.regex.exec(line)) !== null) {
        const raw = pattern.type === 'high_entropy' ? match[1] : match[0];
        if (pattern.type === 'high_entropy') {
          const unique = new Set(raw.replace(/=+$/, ''));
          if (unique.size < 10) continue;
          if (/^(.)\1+$/.test(raw)) continue;
        }
        findings.push({
          path: filePath,
          line: lineNo + 1,
          type: pattern.type,
          snippet: maskSnippet(raw.trim()),
        });
      }
    }
  }

  return findings;
}

function scanPath(targetPath) {
  const resolved = path.resolve(targetPath);
  const findings = [];

  function walk(currentPath) {
    const stat = fs.statSync(currentPath);
    if (stat.isDirectory()) {
      for (const entry of fs.readdirSync(currentPath, { withFileTypes: true })) {
        if (SKIP_DIRS.has(entry.name)) continue;
        walk(path.join(currentPath, entry.name));
      }
      return;
    }

    if (!shouldScanFile(currentPath)) return;
    const buf = fs.readFileSync(currentPath);
    if (isBinaryBuffer(buf)) return;
    const content = buf.toString('utf8');
    findings.push(...scanContent(content, currentPath));
  }

  walk(resolved);
  return findings;
}

function runCli(argv) {
  const [targetPath] = argv;
  if (!targetPath) {
    console.error('Usage: node tools/secrets_scan.js <path>');
    process.exit(1);
  }

  const findings = scanPath(targetPath);
  if (findings.length > 0) {
    for (const item of findings) {
      console.error(`${item.path}:${item.line} [${item.type}] ${item.snippet}`);
    }
    process.exit(1);
  }

  console.log('No secrets detected');
}

if (require.main === module) {
  runCli(process.argv.slice(2));
}

module.exports = {
  scanPath,
  scanContent,
};
