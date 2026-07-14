#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { validateFile } = require('./lib/validate');
const {
  stateDir,
  statePath,
  readJson,
  writeJson,
  ensureDir,
  viewsDir,
  agentsDir,
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

const DEFAULT_TASKS = {
  version: 1,
  tasks: [],
};

const DEFAULT_STATUS = {
  version: 1,
  phase: 'init',
  dashboard: {},
  pending_approvals: [],
  current_task: null,
  progress: {},
  risks_summary: {},
};

const DEFAULT_AGENTS = {
  version: 1,
  agents: [
    {
      id: '1-orchestrator',
      role: 'orchestrator',
      state: 'active',
      last_heartbeat_ts: null,
      task_id: null,
    },
  ],
};

const DEFAULT_DECISIONS = { version: 1, decisions: [] };
const DEFAULT_RISKS = { version: 1, risks: [] };
const DEFAULT_APPROVALS = { version: 1, approvals: [] };

function isOrchestrator(agentId) {
  return agentId === '1-orchestrator' || agentId.endsWith('orchestrator');
}

function isQaAgent(agentId, agentsData) {
  if (/^qa-/.test(agentId)) return true;
  const agent = (agentsData?.agents || []).find((a) => a.id === agentId);
  return agent?.role === 'verifier';
}

function isDevWorker(agentId) {
  return /^dev-/.test(agentId);
}

function computeBudget(extensionsGranted) {
  return 10 + (extensionsGranted || 0) * 10;
}

function loadTasks(projectRoot) {
  return readJson(statePath(projectRoot, 'tasks.json'), { ...DEFAULT_TASKS, tasks: [] });
}

function saveTasks(projectRoot, tasksData) {
  const validation = validateFile('tasks.schema.json', tasksData);
  if (!validation.ok) {
    throw new Error(`tasks.json validation failed: ${validation.errors.join('; ')}`);
  }
  writeJson(statePath(projectRoot, 'tasks.json'), tasksData);
}

function loadAgents(projectRoot) {
  return readJson(statePath(projectRoot, 'agents.json'), DEFAULT_AGENTS);
}

function loadStatus(projectRoot) {
  return readJson(statePath(projectRoot, 'status.json'), DEFAULT_STATUS);
}

function assertOrchestratorWriter(by, action) {
  if (!isOrchestrator(by)) {
    throw new Error(`${action} requires orchestrator writer (got ${by})`);
  }
}

function findTask(tasksData, taskId) {
  const task = tasksData.tasks.find((t) => t.id === taskId);
  if (!task) {
    throw new Error(`Task not found: ${taskId}`);
  }
  return task;
}

function validateTransition(task, fromStatus, toStatus, options) {
  const { by, agentsData, note, alignmentReview, checkpointTag } = options;
  const errors = [];

  if (!VALID_STATUSES.has(toStatus)) {
    errors.push(`Invalid target status: ${toStatus}`);
    return { ok: false, errors, forcedStatus: null };
  }

  if (fromStatus === toStatus) {
    errors.push(`Task already in status ${toStatus}`);
    return { ok: false, errors, forcedStatus: null };
  }

  let forcedStatus = null;

  if (toStatus === 'cancelled' || (toStatus === 'blocked' && fromStatus !== 'in_progress')) {
    if (!isOrchestrator(by)) {
      errors.push(`Transition to ${toStatus} requires orchestrator`);
    }
    if (!note) {
      errors.push(`Transition to ${toStatus} requires --note reason`);
    }
    return { ok: errors.length === 0, errors, forcedStatus };
  }

  if (fromStatus === 'pending' && toStatus === 'in_progress') {
    if (!isOrchestrator(by)) {
      errors.push('pending → in_progress requires orchestrator');
    }
    return { ok: errors.length === 0, errors, forcedStatus };
  }

  if (fromStatus === 'in_progress') {
    if (toStatus === 'qa_failed' || toStatus === 'qa_passed') {
      if (isDevWorker(by)) {
        errors.push(`Workers (${by}) cannot set ${toStatus}`);
      } else if (!isQaAgent(by, agentsData)) {
        errors.push(`${toStatus} requires QA agent (qa-* or verifier role)`);
      }
      return { ok: errors.length === 0, errors, forcedStatus };
    }
    if (toStatus === 'blocked') {
      return { ok: true, errors, forcedStatus };
    }
  }

  if (fromStatus === 'qa_failed' && toStatus === 'in_progress') {
    const nextUsed = (task.cycles?.used || 0) + 1;
    const extensions = task.cycles?.extensions_granted || 0;
    const budget = computeBudget(extensions);
    if (nextUsed > budget) {
      forcedStatus = 'blocked';
    }
    return { ok: true, errors, forcedStatus };
  }

  if (fromStatus === 'qa_passed' && toStatus === 'complete') {
    if (!isOrchestrator(by)) {
      errors.push('qa_passed → complete requires orchestrator');
    }
    if (!alignmentReview) {
      errors.push('qa_passed → complete requires --alignment-review PATH');
    }
    if (!checkpointTag) {
      errors.push('qa_passed → complete requires --checkpoint-tag TAG');
    }
    return { ok: errors.length === 0, errors, forcedStatus };
  }

  errors.push(`Illegal transition: ${fromStatus} → ${toStatus}`);
  return { ok: false, errors, forcedStatus };
}

function transition(projectRoot, params) {
  const {
    taskId,
    toStatus,
    by,
    note = null,
    qaReport = null,
    alignmentReview = null,
    checkpointTag = null,
  } = params;

  if (!by) {
    throw new Error('Writer identity required (--by or AMIR_AGENT)');
  }

  const tasksData = loadTasks(projectRoot);
  const agentsData = loadAgents(projectRoot);
  const task = findTask(tasksData, taskId);
  const fromStatus = task.status;

  const check = validateTransition(task, fromStatus, toStatus, {
    by,
    agentsData,
    note,
    alignmentReview,
    checkpointTag,
  });

  if (!check.ok) {
    const err = new Error(check.errors.join('; '));
    err.exitCode = 1;
    throw err;
  }

  let finalStatus = check.forcedStatus || toStatus;

  if (fromStatus === 'qa_failed' && toStatus === 'in_progress') {
    task.cycles = task.cycles || { used: 0, budget: 10, extensions_granted: 0 };
    task.cycles.used += 1;
    task.cycles.budget = computeBudget(task.cycles.extensions_granted);
    if (task.cycles.used > task.cycles.budget) {
      finalStatus = 'blocked';
      task.note = note || `Budget exhausted: ${task.cycles.used}/${task.cycles.budget} cycles`;
    }
  }

  task.status = finalStatus;

  if (note) task.note = note;
  if (qaReport) task.qa_report_path = qaReport;
  if (alignmentReview) task.alignment_review_path = alignmentReview;
  if (checkpointTag) task.checkpoint_tag = checkpointTag;

  saveTasks(projectRoot, tasksData);
  return { task, fromStatus, toStatus: finalStatus, forced: !!check.forcedStatus };
}

function initProject(projectRoot) {
  ensureDir(stateDir(projectRoot));
  ensureDir(viewsDir(projectRoot));
  ensureDir(agentsDir(projectRoot));

  const files = [
    ['tasks.json', DEFAULT_TASKS],
    ['status.json', DEFAULT_STATUS],
    ['agents.json', DEFAULT_AGENTS],
    ['decisions.json', DEFAULT_DECISIONS],
    ['risks.json', DEFAULT_RISKS],
    ['approvals.json', DEFAULT_APPROVALS],
  ];

  for (const [name, data] of files) {
    const filePath = statePath(projectRoot, name);
    const schemaName = name.replace('.json', '.schema.json');
    const validation = validateFile(schemaName, data);
    if (!validation.ok) {
      throw new Error(`Default ${name} invalid: ${validation.errors.join('; ')}`);
    }
    writeJson(filePath, data);
  }

  const activityPath = statePath(projectRoot, 'activity.jsonl');
  if (!fs.existsSync(activityPath)) {
    fs.writeFileSync(activityPath, '', 'utf8');
  }

  return { initialized: true, projectRoot };
}

function parseKeyValueArgs(args) {
  const result = {};
  for (const arg of args) {
    if (arg.includes('=')) {
      const idx = arg.indexOf('=');
      result[arg.slice(0, idx)] = arg.slice(idx + 1);
    }
  }
  return result;
}

function parseFlags(argv) {
  const flags = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--task') flags.task = argv[++i];
    else if (arg === '--to') flags.to = argv[++i];
    else if (arg === '--by') flags.by = argv[++i];
    else if (arg === '--note') flags.note = argv[++i];
    else if (arg === '--qa-report') flags.qaReport = argv[++i];
    else if (arg === '--alignment-review') flags.alignmentReview = argv[++i];
    else if (arg === '--checkpoint-tag') flags.checkpointTag = argv[++i];
    else if (arg === '--file') flags.file = argv[++i];
    else if (arg === '--field') flags.field = argv[++i];
    else if (arg === '--value') flags.value = argv[++i];
  }
  return flags;
}

function updateStatus(projectRoot, updates, by) {
  assertOrchestratorWriter(by, 'update-status');
  const statusData = loadStatus(projectRoot);
  Object.assign(statusData, updates);
  const validation = validateFile('status.schema.json', statusData);
  if (!validation.ok) {
    throw new Error(`status.json validation failed: ${validation.errors.join('; ')}`);
  }
  writeJson(statePath(projectRoot, 'status.json'), statusData);
  return statusData;
}

function setTaskField(projectRoot, taskId, field, value, by) {
  assertOrchestratorWriter(by, 'set-task-field');
  if (field === 'status') {
    throw new Error('Use transition for status changes');
  }
  const tasksData = loadTasks(projectRoot);
  const task = findTask(tasksData, taskId);
  task[field] = value;
  saveTasks(projectRoot, tasksData);
  return task;
}

function runCli(argv) {
  const [projectRoot, command, ...rest] = argv;
  if (!projectRoot || !command) {
    console.error('Usage: node tools/state.js <project_root> <command> ...');
    process.exit(1);
  }

  const flags = parseFlags(rest);
  const writer = flags.by || process.env.AMIR_AGENT;

  try {
    switch (command) {
      case 'init': {
        const result = initProject(projectRoot);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      case 'get-tasks': {
        console.log(JSON.stringify(loadTasks(projectRoot), null, 2));
        break;
      }
      case 'get-status': {
        console.log(JSON.stringify(loadStatus(projectRoot), null, 2));
        break;
      }
      case 'get-agents': {
        console.log(JSON.stringify(loadAgents(projectRoot), null, 2));
        break;
      }
      case 'transition': {
        const result = transition(projectRoot, {
          taskId: flags.task,
          toStatus: flags.to,
          by: writer,
          note: flags.note || null,
          qaReport: flags.qaReport || null,
          alignmentReview: flags.alignmentReview || null,
          checkpointTag: flags.checkpointTag || null,
        });
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      case 'update-status': {
        let updates = {};
        if (flags.file) {
          updates = readJson(path.resolve(projectRoot, flags.file));
        } else {
          updates = parseKeyValueArgs(rest.filter((a) => !a.startsWith('--')));
        }
        const result = updateStatus(projectRoot, updates, writer);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      case 'set-task-field': {
        if (!flags.task || !flags.field) {
          throw new Error('set-task-field requires --task and --field');
        }
        let value = flags.value;
        if (value === undefined) {
          const raw = rest.find((a) => a.startsWith('--value='));
          value = raw ? raw.slice('--value='.length) : null;
        }
        if (value === 'true') value = true;
        else if (value === 'false') value = false;
        else if (value !== null && value !== undefined && !Number.isNaN(Number(value)) && /^-?\d+(\.\d+)?$/.test(String(value))) {
          value = Number(value);
        } else if (typeof value === 'string' && (value.startsWith('{') || value.startsWith('['))) {
          value = JSON.parse(value);
        }
        const result = setTaskField(projectRoot, flags.task, flags.field, value, writer);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      default:
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
  transition,
  initProject,
  loadTasks,
  saveTasks,
  validateTransition,
  loadAgents,
  loadStatus,
  isOrchestrator,
  isQaAgent,
  isDevWorker,
  computeBudget,
  setTaskField,
  updateStatus,
};
