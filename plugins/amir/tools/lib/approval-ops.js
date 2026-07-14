'use strict';

const { validateFile } = require('./validate');
const { statePath, readJson, writeJson } = require('./paths');

function computeBudget(extensionsGranted) {
  return 10 + (extensionsGranted || 0) * 10;
}

function appendActivityLine(projectRoot, event) {
  const fs = require('fs');
  const path = require('path');
  const { ensureDir } = require('./paths');
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

function loadApprovals(projectRoot) {
  return readJson(statePath(projectRoot, 'approvals.json'), { version: 1, approvals: [] });
}

function saveApprovals(projectRoot, data) {
  const validation = validateFile('approvals.schema.json', data);
  if (!validation.ok) {
    throw new Error(`approvals.json validation failed: ${validation.errors.join('; ')}`);
  }
  writeJson(statePath(projectRoot, 'approvals.json'), data);
}

function loadStatus(projectRoot) {
  return readJson(statePath(projectRoot, 'status.json'));
}

function saveStatus(projectRoot, data) {
  const validation = validateFile('status.schema.json', data);
  if (!validation.ok) {
    throw new Error(`status.json validation failed: ${validation.errors.join('; ')}`);
  }
  writeJson(statePath(projectRoot, 'status.json'), data);
}

function parseGrant(grant) {
  if (!grant) return null;
  const m = String(grant).match(/^cycles:\+?(\d+)$/i);
  if (!m) throw new Error(`Invalid --grant (expected cycles:+N): ${grant}`);
  return { type: 'cycles', amount: Number(m[1]) };
}

function findPending(statusData, approvalId) {
  const list = statusData.pending_approvals || [];
  const idx = list.findIndex((a) => a.id === approvalId);
  if (idx < 0) throw new Error(`Pending approval not found: ${approvalId}`);
  return { item: list[idx], idx };
}

function applyBudgetGrant(projectRoot, taskId, amount) {
  if (!taskId) return null;
  const tasksPath = statePath(projectRoot, 'tasks.json');
  const tasksData = readJson(tasksPath);
  const task = (tasksData.tasks || []).find((t) => t.id === taskId);
  if (!task) throw new Error(`Task not found for budget grant: ${taskId}`);
  task.cycles = task.cycles || { used: 0, budget: 10, extensions_granted: 0 };
  // amount is cycle budget units; each +10 is one extension per computeBudget formula
  // grant cycles:+10 → +1 extension; cycles:+20 → +2
  const extensionsAdd = Math.max(1, Math.round(amount / 10));
  task.cycles.extensions_granted = (task.cycles.extensions_granted || 0) + extensionsAdd;
  task.cycles.budget = computeBudget(task.cycles.extensions_granted);
  const validation = validateFile('tasks.schema.json', tasksData);
  if (!validation.ok) {
    throw new Error(`tasks.json validation failed: ${validation.errors.join('; ')}`);
  }
  writeJson(tasksPath, tasksData);
  return task;
}

function decideApproval(projectRoot, options) {
  const { approvalId, outcome, grant = null, by = 'human', note = null } = options;
  if (!approvalId) throw new Error(`${outcome} requires --approval-id`);
  if (outcome !== 'approved' && outcome !== 'rejected') {
    throw new Error(`Invalid outcome: ${outcome}`);
  }

  const statusData = loadStatus(projectRoot);
  const { item, idx } = findPending(statusData, approvalId);
  const parsedGrant = outcome === 'approved' ? parseGrant(grant) : null;

  if (outcome === 'approved' && item.type === 'budget_extension' && parsedGrant) {
    applyBudgetGrant(projectRoot, item.task, parsedGrant.amount);
  } else if (outcome === 'approved' && item.type === 'budget_extension' && !parsedGrant) {
    // default +10 cycles
    applyBudgetGrant(projectRoot, item.task, 10);
  }

  statusData.pending_approvals.splice(idx, 1);
  saveStatus(projectRoot, statusData);

  const record = {
    id: item.id,
    type: item.type,
    summary: item.summary,
    requested_at: item.requested_at,
    task: item.task || null,
    justification: item.justification || item.details || null,
    outcome,
    decided_at: new Date().toISOString(),
    decided_by: by,
    grants: parsedGrant
      ? `cycles:+${parsedGrant.amount}`
      : outcome === 'approved' && item.type === 'budget_extension'
        ? 'cycles:+10'
        : null,
    note: note || null,
  };

  const approvalsData = loadApprovals(projectRoot);
  approvalsData.approvals.push(record);
  saveApprovals(projectRoot, approvalsData);

  appendActivityLine(projectRoot, {
    agent_id: by,
    action: 'approval',
    result: `${outcome} ${approvalId}${record.grants ? ` ${record.grants}` : ''}`,
    task_id: item.task || undefined,
  });

  return { record, pending_remaining: statusData.pending_approvals.length };
}

function approveApproval(projectRoot, options) {
  return decideApproval(projectRoot, { ...options, outcome: 'approved' });
}

function rejectApproval(projectRoot, options) {
  return decideApproval(projectRoot, { ...options, outcome: 'rejected' });
}

module.exports = {
  approveApproval,
  rejectApproval,
  decideApproval,
  parseGrant,
};
