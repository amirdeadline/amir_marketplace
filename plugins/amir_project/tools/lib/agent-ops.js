'use strict';

const fs = require('fs');
const path = require('path');
const { validateFile } = require('./validate');
const {
  agentsDir,
  statePath,
  readJson,
  writeJson,
  ensureDir,
} = require('./paths');

const VALID_AGENT_STATES = new Set([
  'active',
  'idle',
  'complete',
  'stale',
  'reset',
  'inactive',
]);

const DELETABLE_STATES = new Set(['idle', 'complete', 'reset', 'inactive']);

const MODEL_CLASS = {
  premium: 'premium',
  cheap: 'cheap',
};

function isHumanWriter(by) {
  return by === 'human' || by === 'vscode-extension';
}

function appendActivityLine(projectRoot, event) {
  const activityPath = statePath(projectRoot, 'activity.jsonl');
  ensureDir(path.dirname(activityPath));
  const payload = {
    timestamp: event.timestamp || new Date().toISOString(),
    agent_id: event.agent_id,
    action: event.action,
    result: event.result,
  };
  if (event.task_id) payload.task_id = event.task_id;
  const validation = validateFile('activity-event.schema.json', payload);
  if (!validation.ok) {
    throw new Error(`activity event validation failed: ${validation.errors.join('; ')}`);
  }
  fs.appendFileSync(activityPath, `${JSON.stringify(payload)}\n`, 'utf8');
  return payload;
}

function saveAgents(projectRoot, agentsData) {
  const validation = validateFile('agents.schema.json', agentsData);
  if (!validation.ok) {
    throw new Error(`agents.json validation failed: ${validation.errors.join('; ')}`);
  }
  writeJson(statePath(projectRoot, 'agents.json'), agentsData);
}

function loadDecisions(projectRoot) {
  return readJson(statePath(projectRoot, 'decisions.json'), { version: 1, decisions: [] });
}

function saveDecisions(projectRoot, data) {
  writeJson(statePath(projectRoot, 'decisions.json'), data);
}

function slugify(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 32);
}

function agentWorkspacePath(projectRoot, agentId) {
  // Flat convention: ai/agents/<id with / replaced by __>
  const safe = agentId.replace(/\//g, '__');
  return path.join(agentsDir(projectRoot), safe);
}

function resolvePluginRoot() {
  return path.join(__dirname, '..', '..');
}

function fillTemplate(template, vars) {
  return template.replace(/\{\{(\w+)\}\}/g, (_, key) => {
    const v = vars[key];
    return v === undefined || v === null ? '' : String(v);
  });
}

function scaffoldAgentWorkspace(projectRoot, agent, responsibility) {
  const ws = agentWorkspacePath(projectRoot, agent.id);
  ensureDir(ws);
  ensureDir(path.join(ws, 'logs'));

  const notesPath = path.join(ws, 'notes.md');
  if (!fs.existsSync(notesPath)) {
    fs.writeFileSync(
      notesPath,
      `# Notes — ${agent.id}\n\n## Responsibility\n\n${responsibility || agent.role}\n\n## Scratch\n\n`,
      'utf8',
    );
  }

  const promptPath = path.join(ws, 'prompt.md');
  if (!fs.existsSync(promptPath) || fs.readFileSync(promptPath, 'utf8').trim() === '') {
    fs.writeFileSync(
      promptPath,
      [
        `# Agent Prompt — ${agent.id}`,
        '',
        `> **Role:** ${agent.role}`,
        `> **State:** ${agent.state}`,
        `> **Model:** ${agent.model || 'unspecified'}`,
        '',
        '## Responsibility',
        '',
        responsibility || agent.role,
        '',
        '## Fresh context',
        '',
        'This prompt is regenerated from project JSON state. Do not rely on prior chat.',
        '',
      ].join('\n'),
      'utf8',
    );
  }

  agent.workspace = path.relative(projectRoot, ws).split(path.sep).join('/');
  return ws;
}

function sanitizeId(value) {
  // Preserve case for task-style ids (dev-T001); only strip illegal chars
  const cleaned = String(value || '')
    .trim()
    .replace(/[^A-Za-z0-9/_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
  if (!cleaned || cleaned.length > 64) return '';
  return cleaned;
}

function assignAgentId(agents, { role, parent, name }) {
  if (name) {
    const base = sanitizeId(name) || slugify(name);
    const id = parent ? `${parent}/sub-${slugify(name)}` : base;
    if (!id) throw new Error('Invalid agent name');
    if (agents.some((a) => a.id === id)) {
      throw new Error(`Agent id already exists: ${id}`);
    }
    return id;
  }

  const roleSlug = slugify(role);
  if (!roleSlug) throw new Error('--role is required');

  const fixed = {
    orchestrator: '1-orchestrator',
    architect: '2-architect',
    qa: '3-qa',
    security: '4-security',
  };
  if (fixed[roleSlug] && !agents.some((a) => a.id === fixed[roleSlug])) {
    return fixed[roleSlug];
  }

  if (parent) {
    let n = 1;
    let id;
    do {
      id = `${parent}/sub-${roleSlug}${n > 1 ? `-${n}` : ''}`;
      n += 1;
    } while (agents.some((a) => a.id === id));
    return id;
  }

  // Custom top-level or worker-style roles
  let base = roleSlug;
  if (roleSlug.startsWith('dev-') || roleSlug.startsWith('qa-') || roleSlug.startsWith('doc-')) {
    base = roleSlug;
  }
  let id = base;
  let n = 2;
  while (agents.some((a) => a.id === id)) {
    id = `${base}-${n}`;
    n += 1;
  }
  return id;
}

function resolveModel(modelClass) {
  if (!modelClass) return 'premium';
  const key = String(modelClass).toLowerCase();
  if (!MODEL_CLASS[key]) {
    throw new Error(`--model must be premium or cheap (got ${modelClass})`);
  }
  return MODEL_CLASS[key];
}

function renderAgentsView(projectRoot, agentsData) {
  const viewsDir = path.join(projectRoot, 'ai', 'views');
  ensureDir(viewsDir);
  const lines = [
    '# Agent Registry',
    '',
    '| Id | Role | State | Task | Model | Workspace |',
    '| --- | --- | --- | --- | --- | --- |',
  ];
  for (const a of agentsData.agents) {
    lines.push(
      `| ${a.id} | ${a.role} | ${a.state} | ${a.task_id || a.current_task || ''} | ${a.model || ''} | ${a.workspace || ''} |`,
    );
  }
  lines.push('');
  const out = path.join(viewsDir, 'agents.md');
  fs.writeFileSync(out, lines.join('\n'), 'utf8');
  return out;
}

function addAgent(projectRoot, options) {
  const {
    role,
    parent = null,
    responsibility = '',
    model = 'premium',
    name = null,
    by = 'human',
  } = options;

  if (!role) throw new Error('add-agent requires --role');
  if (parent) {
    const agentsData = readJson(statePath(projectRoot, 'agents.json'));
    if (!agentsData.agents.some((a) => a.id === parent)) {
      throw new Error(`Parent agent not found: ${parent}`);
    }
  }

  const agentsData = readJson(statePath(projectRoot, 'agents.json'), { version: 1, agents: [] });
  const id = assignAgentId(agentsData.agents, { role, parent, name });
  const now = new Date().toISOString();
  const agent = {
    id,
    name: name || id,
    role: slugify(role) || role,
    parent: parent || null,
    model: resolveModel(model),
    created_at: now,
    state: 'idle',
    last_heartbeat_ts: null,
    task_id: null,
    current_task: null,
    responsibility: responsibility || '',
  };

  scaffoldAgentWorkspace(projectRoot, agent, responsibility);
  agentsData.version = agentsData.version || 1;
  agentsData.agents.push(agent);
  saveAgents(projectRoot, agentsData);
  const viewPath = renderAgentsView(projectRoot, agentsData);

  appendActivityLine(projectRoot, {
    agent_id: by,
    action: 'message',
    result: `add-agent ${id}`,
  });

  return { agent, viewPath };
}

function archiveWorkspace(projectRoot, agentId, suffix) {
  const ws = agentWorkspacePath(projectRoot, agentId);
  const archiveRoot = path.join(agentsDir(projectRoot), '_archive');
  ensureDir(archiveRoot);
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const dest = path.join(archiveRoot, `${agentId.replace(/\//g, '__')}-${suffix}-${stamp}`);
  if (fs.existsSync(ws)) {
    fs.cpSync(ws, dest, { recursive: true });
    fs.rmSync(ws, { recursive: true, force: true });
  } else {
    ensureDir(dest);
  }
  return path.relative(projectRoot, dest).split(path.sep).join('/');
}

function deleteAgent(projectRoot, options) {
  const { agentId, confirmName, by = 'human' } = options;
  if (!agentId) throw new Error('delete-agent requires --agent');
  if (confirmName !== agentId) {
    throw new Error(`Typed confirmation mismatch: expected ${agentId}`);
  }

  const agentsData = readJson(statePath(projectRoot, 'agents.json'));
  const idx = agentsData.agents.findIndex((a) => a.id === agentId);
  if (idx < 0) throw new Error(`Agent not found: ${agentId}`);
  const agent = agentsData.agents[idx];
  if (!DELETABLE_STATES.has(agent.state)) {
    throw new Error(`Agent ${agentId} is ${agent.state}; stop first (only idle/complete/reset/inactive deletable)`);
  }

  const archivePath = archiveWorkspace(projectRoot, agentId, 'deleted');
  agentsData.agents.splice(idx, 1);
  saveAgents(projectRoot, agentsData);
  const viewPath = renderAgentsView(projectRoot, agentsData);

  const decisions = loadDecisions(projectRoot);
  decisions.decisions.push({
    id: `del-${agentId}-${Date.now()}`,
    ts: new Date().toISOString(),
    by,
    summary: `Deleted agent ${agentId}; archived to ${archivePath}`,
  });
  saveDecisions(projectRoot, decisions);

  appendActivityLine(projectRoot, {
    agent_id: by,
    action: 'message',
    result: `delete-agent ${agentId} archive=${archivePath}`,
  });

  return { agentId, archivePath, viewPath };
}

function setAgentState(projectRoot, options) {
  const { agentId, to, by = 'human' } = options;
  if (!agentId) throw new Error('set-agent-state requires --agent');
  if (!VALID_AGENT_STATES.has(to)) {
    throw new Error(`Invalid agent state: ${to}`);
  }
  const agentsData = readJson(statePath(projectRoot, 'agents.json'));
  const agent = agentsData.agents.find((a) => a.id === agentId);
  if (!agent) throw new Error(`Agent not found: ${agentId}`);
  const from = agent.state;
  agent.state = to;
  if (to === 'active') {
    agent.last_heartbeat_ts = new Date().toISOString();
  }
  saveAgents(projectRoot, agentsData);
  appendActivityLine(projectRoot, {
    agent_id: agentId,
    action: to === 'active' ? 'start' : 'message',
    result: `set-agent-state ${from}→${to} by ${by}`,
  });
  return { agent, from, to };
}

function resetAgent(projectRoot, options) {
  const { agentId, by = 'human', reason = '' } = options;
  if (!agentId) throw new Error('reset-agent requires --agent');
  const agentsData = readJson(statePath(projectRoot, 'agents.json'));
  const agent = agentsData.agents.find((a) => a.id === agentId);
  if (!agent) throw new Error(`Agent not found: ${agentId}`);

  const archivePath = archiveWorkspace(projectRoot, agentId, 'reset');
  agent.state = 'idle';
  agent.last_heartbeat_ts = null;
  scaffoldAgentWorkspace(projectRoot, agent, agent.responsibility || agent.role);
  saveAgents(projectRoot, agentsData);
  renderAgentsView(projectRoot, agentsData);

  appendActivityLine(projectRoot, {
    agent_id: agentId,
    action: 'message',
    result: `reset-agent archive=${archivePath}${reason ? ` reason=${reason}` : ''}`,
  });

  return { agent, archivePath };
}

function generatePrompt(projectRoot, options) {
  const { agentId } = options;
  if (!agentId) throw new Error('generate-prompt requires --agent');

  const agentsData = readJson(statePath(projectRoot, 'agents.json'));
  const agent = agentsData.agents.find((a) => a.id === agentId);
  if (!agent) throw new Error(`Agent not found: ${agentId}`);

  const tasksData = readJson(statePath(projectRoot, 'tasks.json'), { version: 1, tasks: [] });
  const statusData = readJson(statePath(projectRoot, 'status.json'), {});
  const taskId = agent.task_id || agent.current_task || statusData.current_task;
  const task = (tasksData.tasks || []).find((t) => t.id === taskId) || null;

  const pluginRoot = resolvePluginRoot();
  let templateName = 'fix-prompt.md.tmpl';
  if (agent.role === 'verifier' || /^qa-/.test(agent.id)) {
    templateName = 'verifier-prompt.md.tmpl';
  } else if (/^dev-/.test(agent.id) || agent.role === 'worker') {
    templateName = 'worker-prompt.md.tmpl';
  }

  const templatePath = path.join(pluginRoot, 'templates', templateName);
  let body;
  if (fs.existsSync(templatePath) && task) {
    const tmpl = fs.readFileSync(templatePath, 'utf8');
    body = fillTemplate(tmpl, {
      TASK_ID: task.id,
      TASK_TITLE: task.title || '',
      TASK_GOAL: task.goal || '',
      TASK_SCOPE: task.scope || '',
      TASK_STATUS: task.status || '',
      TASK_PRIORITY: task.priority || '',
      TASK_DEPENDENCIES: (task.dependencies || []).join(', '),
      TASK_APPROVAL_REQUIRED: String(!!task.approval_required),
      CHECKPOINT_TAG: task.checkpoint_tag || '',
      TASK_NOTE: task.note || '',
      GOAL_SUMMARY: '',
      APPROVED_DECISIONS: '',
      GENERATED_AT: new Date().toISOString(),
      PHASE: statusData.phase || statusData.current_phase || '',
      CYCLE_USED: String(task.cycles?.used ?? 0),
      CYCLE_BUDGET: String(task.cycles?.budget ?? 10),
    });
  } else {
    body = [
      `# Agent Prompt — ${agent.id}`,
      '',
      `> **Generated:** ${new Date().toISOString()}`,
      `> **Role:** ${agent.role}`,
      `> **Model:** ${agent.model || 'unspecified'}`,
      '',
      '## Responsibility',
      '',
      agent.responsibility || agent.role,
      '',
      task
        ? `## Current Task\n\n- ${task.id}: ${task.title}\n- Goal: ${task.goal}\n- Scope: ${task.scope}\n`
        : '## Current Task\n\n_None assigned — await orchestrator._\n',
      '',
      'Fresh context: regenerated from JSON state. Do not reuse prior thread.',
      '',
    ].join('\n');
  }

  const ws = scaffoldAgentWorkspace(projectRoot, agent, agent.responsibility);
  const promptPath = path.join(ws, 'prompt.md');
  fs.writeFileSync(promptPath, body, 'utf8');
  agent.workspace = path.relative(projectRoot, ws).split(path.sep).join('/');
  saveAgents(projectRoot, agentsData);

  appendActivityLine(projectRoot, {
    agent_id: agentId,
    action: 'start',
    result: `generate-prompt ${path.relative(projectRoot, promptPath).split(path.sep).join('/')}`,
    task_id: taskId || undefined,
  });

  return {
    agentId,
    promptPath: path.relative(projectRoot, promptPath).split(path.sep).join('/'),
    absolutePath: promptPath,
  };
}

module.exports = {
  isHumanWriter,
  addAgent,
  deleteAgent,
  setAgentState,
  resetAgent,
  generatePrompt,
  scaffoldAgentWorkspace,
  agentWorkspacePath,
  renderAgentsView,
  saveAgents,
  VALID_AGENT_STATES,
  DELETABLE_STATES,
};
