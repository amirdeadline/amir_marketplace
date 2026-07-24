#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { scanPath } = require('./secrets_scan');
const { loadTasks, computeBudget } = require('./state');
const { loadActivityLines, STALE_MS } = require('./activity');
const { renderProject, renderTasksMd, renderStatusMd } = require('./render');
const {
  statePath,
  agentsDir,
  viewsDir,
  readJson,
} = require('./lib/paths');

const VALID_STATUSES = new Set([
  'pending',
  'in_progress',
  'qa_failed',
  'qa_passed',
  'blocked',
  'complete',
  'cancelled',
]);

function addFinding(findings, severity, check, message, suggested_fix) {
  findings.push({ severity, check, message, suggested_fix });
}

function checkIllegalStatuses(projectRoot, findings) {
  const tasksData = loadTasks(projectRoot);
  for (const task of tasksData.tasks) {
    if (!VALID_STATUSES.has(task.status)) {
      addFinding(
        findings,
        'CRITICAL',
        'illegal_status',
        `Task ${task.id} has illegal status "${task.status}"`,
        'Correct status via orchestrator transition tool',
      );
    }
  }
}

function checkStaleHeartbeats(projectRoot, findings) {
  const agentsData = readJson(statePath(projectRoot, 'agents.json'), { agents: [] });
  const activity = loadActivityLines(projectRoot);
  const now = Date.now();
  const lastActivityByAgent = new Map();
  for (const evt of activity) {
    lastActivityByAgent.set(evt.agent_id, evt.timestamp);
  }

  const tasksData = loadTasks(projectRoot);
  const inProgressTasks = tasksData.tasks.filter((t) => t.status === 'in_progress');

  for (const task of inProgressTasks) {
    const workerId = `dev-${task.id}`;
    const qaId = `qa-${task.id}`;
    for (const agentId of [workerId, qaId]) {
      const agent = agentsData.agents.find((a) => a.id === agentId);
      if (!agent || agent.state !== 'active') continue;
      const heartbeatTs = agent.last_heartbeat_ts;
      const lastActivityTs = lastActivityByAgent.get(agentId) || null;
      const heartbeatAge = heartbeatTs ? now - Date.parse(heartbeatTs) : Infinity;
      const activityAge = lastActivityTs ? now - Date.parse(lastActivityTs) : Infinity;
      if (Math.min(heartbeatAge, activityAge) > STALE_MS) {
        addFinding(
          findings,
          'HIGH',
          'stale_heartbeat',
          `Task ${task.id} in_progress but agent ${agentId} heartbeat/activity older than 5 minutes`,
          'Run activity heartbeat-check or resume agent',
        );
      }
    }
  }
}

function checkMissingQaReports(projectRoot, findings) {
  const tasksData = loadTasks(projectRoot);
  for (const task of tasksData.tasks) {
    if (task.status !== 'qa_passed' && task.status !== 'complete') continue;
    if (!task.qa_report_path || !fs.existsSync(path.resolve(projectRoot, task.qa_report_path))) {
      addFinding(
        findings,
        'HIGH',
        'missing_qa_report',
        `Task ${task.id} (${task.status}) missing QA report at ${task.qa_report_path || '(unset)'}`,
        'Attach QA report path and ensure file exists',
      );
    }
  }
}

function detectCycles(tasks) {
  const graph = new Map();
  for (const task of tasks) {
    graph.set(task.id, task.dependencies || []);
  }

  const cycles = [];
  const visiting = new Set();
  const visited = new Set();
  const stack = [];

  function dfs(node) {
    if (visited.has(node)) return;
    if (visiting.has(node)) {
      const idx = stack.indexOf(node);
      cycles.push(stack.slice(idx).concat(node));
      return;
    }
    visiting.add(node);
    stack.push(node);
    for (const dep of graph.get(node) || []) {
      if (graph.has(dep)) dfs(dep);
    }
    stack.pop();
    visiting.delete(node);
    visited.add(node);
  }

  for (const node of graph.keys()) dfs(node);
  return cycles;
}

function checkCircularDependencies(projectRoot, findings) {
  const tasksData = loadTasks(projectRoot);
  const cycles = detectCycles(tasksData.tasks);
  for (const cycle of cycles) {
    addFinding(
      findings,
      'CRITICAL',
      'circular_dependencies',
      `Circular dependency detected: ${cycle.join(' -> ')}`,
      'Remove or break dependency cycle in tasks.json',
    );
  }
}

function checkOrphanAgents(projectRoot, findings) {
  const agentsData = readJson(statePath(projectRoot, 'agents.json'), { agents: [] });
  const registered = new Set(agentsData.agents.map((a) => a.id));
  const root = agentsDir(projectRoot);
  if (!fs.existsSync(root)) return;

  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    if (!registered.has(entry.name)) {
      addFinding(
        findings,
        'MEDIUM',
        'orphan_agent_workspace',
        `Workspace ai/agents/${entry.name} is not in agents.json registry`,
        'Register agent or remove orphan workspace',
      );
    }
  }
}

function checkSizeEstimates(projectRoot, findings) {
  const tasksData = loadTasks(projectRoot);
  for (const task of tasksData.tasks) {
    const est = task.size_estimate;
    if (!est) continue;
    if (est.files > 5 || est.loc > 300) {
      addFinding(
        findings,
        'HIGH',
        'size_estimate_exceeded',
        `Task ${task.id} size_estimate exceeds caps (files=${est.files}, loc=${est.loc})`,
        'Split task or revise estimate with orchestrator approval',
      );
    }
  }
}

function hasCanaryEvent(activity, taskId) {
  return activity.some((evt) => {
    if (evt.task_id !== taskId) return false;
    const action = String(evt.action || '').toLowerCase();
    const result = String(evt.result || '').toLowerCase();
    return action.includes('start') || result.includes('canary');
  });
}

function checkMissingCanary(projectRoot, findings) {
  const tasksData = loadTasks(projectRoot);
  const activity = loadActivityLines(projectRoot);
  for (const task of tasksData.tasks) {
    if (task.status !== 'in_progress' && task.status !== 'complete') continue;
    if (!hasCanaryEvent(activity, task.id)) {
      addFinding(
        findings,
        'HIGH',
        'missing_canary',
        `Task ${task.id} (${task.status}) has no baseline canary activity event`,
        'Log start/canary activity before progressing task',
      );
    }
  }
}

function checkSecrets(projectRoot, findings) {
  const root = agentsDir(projectRoot);
  if (!fs.existsSync(root)) return;
  const secretFindings = scanPath(root);
  for (const item of secretFindings) {
    addFinding(
      findings,
      'CRITICAL',
      'secrets_in_workspace',
      `${item.path}:${item.line} ${item.type} — ${item.snippet}`,
      'Remove secret and rotate credentials',
    );
  }
}

function checkBudgetOverruns(projectRoot, findings) {
  const tasksData = loadTasks(projectRoot);
  for (const task of tasksData.tasks) {
    const used = task.cycles?.used || 0;
    const extensions = task.cycles?.extensions_granted || 0;
    const budget = computeBudget(extensions);
    if (used > budget) {
      addFinding(
        findings,
        'HIGH',
        'budget_overrun',
        `Task ${task.id} cycles.used (${used}) exceeds budget (${budget}) without sufficient extensions`,
        'Request budget extension or set task blocked',
      );
    }
  }
}

function checkStaleViews(projectRoot, findings) {
  const tasksPath = statePath(projectRoot, 'tasks.json');
  const statusPath = statePath(projectRoot, 'status.json');
  const tasksView = path.join(viewsDir(projectRoot), 'tasks.md');
  const statusView = path.join(viewsDir(projectRoot), 'status.md');

  if (!fs.existsSync(tasksView) && !fs.existsSync(statusView)) return;

  const tasksData = loadTasks(projectRoot);
  const statusData = readJson(statusPath, {});

  if (fs.existsSync(tasksView)) {
    const expected = renderTasksMd(tasksData);
    const actual = fs.readFileSync(tasksView, 'utf8');
    if (actual !== expected) {
      addFinding(
        findings,
        'MEDIUM',
        'stale_tasks_view',
        'ai/views/tasks.md is stale compared to tasks.json',
        'Run: node tools/render.js <project_root> tasks',
      );
    }
  }

  if (fs.existsSync(statusView)) {
    const expected = renderStatusMd(statusData, tasksData);
    const actual = fs.readFileSync(statusView, 'utf8');
    if (actual !== expected) {
      addFinding(
        findings,
        'MEDIUM',
        'stale_status_view',
        'ai/views/status.md is stale compared to status.json',
        'Run: node tools/render.js <project_root> status',
      );
    }
  }
}

function runDoctor(projectRoot) {
  const findings = [];
  checkIllegalStatuses(projectRoot, findings);
  checkStaleHeartbeats(projectRoot, findings);
  checkMissingQaReports(projectRoot, findings);
  checkCircularDependencies(projectRoot, findings);
  checkOrphanAgents(projectRoot, findings);
  checkSizeEstimates(projectRoot, findings);
  checkMissingCanary(projectRoot, findings);
  checkSecrets(projectRoot, findings);
  checkBudgetOverruns(projectRoot, findings);
  checkStaleViews(projectRoot, findings);
  return findings;
}

function runCli(argv) {
  const [projectRoot] = argv;
  if (!projectRoot) {
    console.error('Usage: node tools/doctor.js <project_root>');
    process.exit(1);
  }

  const findings = runDoctor(projectRoot);
  console.log(JSON.stringify(findings, null, 2));

  const fatal = findings.some((f) => f.severity === 'CRITICAL' || f.severity === 'HIGH');
  if (fatal) process.exit(1);
}

if (require.main === module) {
  runCli(process.argv.slice(2));
}

module.exports = {
  runDoctor,
  detectCycles,
  hasCanaryEvent,
};
