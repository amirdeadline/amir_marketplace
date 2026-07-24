'use strict';

const fs = require('fs');
const path = require('path');

function aiRoot(projectRoot) {
  return path.join(projectRoot, 'ai');
}

function stateDir(projectRoot) {
  return path.join(aiRoot(projectRoot), 'state');
}

function viewsDir(projectRoot) {
  return path.join(aiRoot(projectRoot), 'views');
}

function agentsDir(projectRoot) {
  return path.join(aiRoot(projectRoot), 'agents');
}

function statePath(projectRoot, name) {
  return path.join(stateDir(projectRoot), name);
}

function readJson(filePath, fallback = null) {
  if (!fs.existsSync(filePath)) {
    if (fallback !== null) return fallback;
    throw new Error(`File not found: ${filePath}`);
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

module.exports = {
  aiRoot,
  stateDir,
  viewsDir,
  agentsDir,
  statePath,
  readJson,
  writeJson,
  ensureDir,
};
