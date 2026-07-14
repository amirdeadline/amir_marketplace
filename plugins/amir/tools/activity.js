#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { validateFile } = require('./lib/validate');
const { statePath, readJson, writeJson } = require('./lib/paths');

const STALE_MS = 5 * 60 * 1000;

function loadActivityLines(projectRoot) {
  const activityPath = statePath(projectRoot, 'activity.jsonl');
  if (!fs.existsSync(activityPath)) return [];
  const content = fs.readFileSync(activityPath, 'utf8').trim();
  if (!content) return [];
  return content.split('\n').map((line, index) => {
    try {
      return JSON.parse(line);
    } catch (err) {
      throw new Error(`Invalid JSON at activity.jsonl line ${index + 1}: ${err.message}`);
    }
  });
}

function appendActivity(projectRoot, event) {
  const validation = validateFile('activity-event.schema.json', event);
  if (!validation.ok) {
    const err = new Error(`activity event validation failed: ${validation.errors.join('; ')}`);
    err.exitCode = 1;
    throw err;
  }

  const activityPath = statePath(projectRoot, 'activity.jsonl');
  fs.mkdirSync(path.dirname(activityPath), { recursive: true });
  fs.appendFileSync(activityPath, `${JSON.stringify(event)}\n`, 'utf8');

  const agentsPath = statePath(projectRoot, 'agents.json');
  if (fs.existsSync(agentsPath)) {
    const agentsData = readJson(agentsPath);
    const agent = agentsData.agents.find((a) => a.id === event.agent_id);
    if (agent) {
      agent.last_heartbeat_ts = event.timestamp;
      writeJson(agentsPath, agentsData);
    }
  }

  return event;
}

function heartbeatCheck(projectRoot, now = Date.now()) {
  const agentsPath = statePath(projectRoot, 'agents.json');
  const agentsData = readJson(agentsPath);
  const activity = loadActivityLines(projectRoot);

  const lastActivityByAgent = new Map();
  for (const evt of activity) {
    lastActivityByAgent.set(evt.agent_id, evt.timestamp);
  }

  const stale = [];
  for (const agent of agentsData.agents) {
    if (agent.state !== 'active') continue;

    const heartbeatTs = agent.last_heartbeat_ts;
    const lastActivityTs = lastActivityByAgent.get(agent.id) || null;
    const heartbeatAge = heartbeatTs ? now - Date.parse(heartbeatTs) : Infinity;
    const activityAge = lastActivityTs ? now - Date.parse(lastActivityTs) : Infinity;
    const oldest = Math.min(heartbeatAge, activityAge);

    if (oldest > STALE_MS) {
      agent.state = 'stale';
      stale.push(agent.id);
    }
  }

  if (stale.length > 0) {
    writeJson(agentsPath, agentsData);
  }

  return stale;
}

function parseFlags(argv) {
  const flags = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--agent') flags.agent = argv[++i];
    else if (arg === '--action') flags.action = argv[++i];
    else if (arg === '--result') flags.result = argv[++i];
    else if (arg === '--task') flags.task = argv[++i];
    else if (arg === '--tokens-in') flags.tokensIn = Number(argv[++i]);
    else if (arg === '--tokens-out') flags.tokensOut = Number(argv[++i]);
    else if (arg === '--model') flags.model = argv[++i];
    else if (arg === '--usd') flags.usd = Number(argv[++i]);
  }
  return flags;
}

function runCli(argv) {
  const [projectRoot, command, ...rest] = argv;
  if (!projectRoot || !command) {
    console.error('Usage: node tools/activity.js <project_root> <append|heartbeat-check> ...');
    process.exit(1);
  }

  try {
    if (command === 'append') {
      const flags = parseFlags(rest);
      const event = appendActivity(projectRoot, {
        timestamp: new Date().toISOString(),
        agent_id: flags.agent,
        action: flags.action,
        result: flags.result ?? '',
        task_id: flags.task ?? null,
        tokens_in: flags.tokensIn ?? null,
        tokens_out: flags.tokensOut ?? null,
        model: flags.model ?? null,
        usd: flags.usd ?? null,
      });
      console.log(JSON.stringify(event));
    } else if (command === 'heartbeat-check') {
      const stale = heartbeatCheck(projectRoot);
      console.log(JSON.stringify({ stale }, null, 2));
    } else {
      console.error(`Unknown command: ${command}`);
      process.exit(1);
    }
  } catch (err) {
    console.error(err.message || String(err));
    process.exit(err.exitCode || 1);
  }
}

if (require.main === module) {
  runCli(process.argv.slice(2));
}

module.exports = {
  appendActivity,
  heartbeatCheck,
  loadActivityLines,
  STALE_MS,
};
