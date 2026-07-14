#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { loadTasks, loadStatus } = require('./state');
const { viewsDir, ensureDir } = require('./lib/paths');

const PRIORITY_ORDER = { P0: 0, P1: 1, P2: 2 };

function escapeCell(value) {
  if (value === null || value === undefined) return '';
  return String(value).replace(/\|/g, '\\|').replace(/\n/g, ' ');
}

function sortTasks(tasks) {
  return [...tasks].sort((a, b) => {
    const pa = PRIORITY_ORDER[a.priority] ?? 99;
    const pb = PRIORITY_ORDER[b.priority] ?? 99;
    if (pa !== pb) return pa - pb;
    return a.id.localeCompare(b.id);
  });
}

function renderTasksMd(tasksData) {
  const active = sortTasks(
    tasksData.tasks.filter((t) => t.status !== 'complete' && t.status !== 'cancelled'),
  );
  const finished = sortTasks(
    tasksData.tasks.filter((t) => t.status === 'complete' || t.status === 'cancelled'),
  );

  const lines = [
    '# Task Board',
    '',
    '## Active Tasks',
    '',
    '| ID | Title | Goal | Scope | Status | QA Report | Dependencies | Approval Required |',
    '| --- | --- | --- | --- | --- | --- | --- | --- |',
  ];

  for (const task of active) {
    lines.push(
      `| ${escapeCell(task.id)} | ${escapeCell(task.title)} | ${escapeCell(task.goal)} | ${escapeCell(task.scope)} | ${escapeCell(task.status)} | ${escapeCell(task.qa_report_path)} | ${escapeCell((task.dependencies || []).join(', '))} | ${escapeCell(task.approval_required)} |`,
    );
  }

  lines.push('', '## Finished / Cancelled', '');
  lines.push('| ID | Title | Goal | Scope | Status | QA Report | Dependencies | Approval Required |');
  lines.push('| --- | --- | --- | --- | --- | --- | --- | --- |');

  for (const task of finished) {
    lines.push(
      `| ${escapeCell(task.id)} | ${escapeCell(task.title)} | ${escapeCell(task.goal)} | ${escapeCell(task.scope)} | ${escapeCell(task.status)} | ${escapeCell(task.qa_report_path)} | ${escapeCell((task.dependencies || []).join(', '))} | ${escapeCell(task.approval_required)} |`,
    );
  }

  lines.push('');
  return lines.join('\n');
}

function renderStatusMd(statusData, tasksData) {
  const lines = [
    '# Project Status',
    '',
    '## Dashboard',
    '',
    '```json',
    JSON.stringify(statusData.dashboard || {}, null, 2),
    '```',
    '',
    '## Pending Approvals',
    '',
  ];

  const approvals = statusData.pending_approvals || [];
  if (approvals.length === 0) {
    lines.push('_None_');
  } else {
    for (const item of approvals) {
      lines.push(`- ${JSON.stringify(item)}`);
    }
  }

  lines.push('', '## Current Task', '');
  lines.push(statusData.current_task ? `**${statusData.current_task}**` : '_None_');

  const current = tasksData.tasks.find((t) => t.id === statusData.current_task);
  if (current) {
    lines.push(`- Status: ${current.status}`);
    lines.push(`- Priority: ${current.priority}`);
  }

  lines.push('', '## Progress', '', '```json');
  lines.push(JSON.stringify(statusData.progress || {}, null, 2));
  lines.push('```', '', '## Risks Summary', '', '```json');
  lines.push(JSON.stringify(statusData.risks_summary || {}, null, 2));
  lines.push('```', '');

  return lines.join('\n');
}

function renderProject(projectRoot, target = 'all') {
  const tasksData = loadTasks(projectRoot);
  const statusData = loadStatus(projectRoot);
  ensureDir(viewsDir(projectRoot));

  const outputs = {};
  if (target === 'tasks' || target === 'all') {
    outputs.tasks = path.join(viewsDir(projectRoot), 'tasks.md');
    fs.writeFileSync(outputs.tasks, renderTasksMd(tasksData), 'utf8');
  }
  if (target === 'status' || target === 'all') {
    outputs.status = path.join(viewsDir(projectRoot), 'status.md');
    fs.writeFileSync(outputs.status, renderStatusMd(statusData, tasksData), 'utf8');
  }
  return outputs;
}

function runCli(argv) {
  const [projectRoot, target = 'all'] = argv;
  if (!projectRoot) {
    console.error('Usage: node tools/render.js <project_root> [tasks|status|all]');
    process.exit(1);
  }
  if (!['tasks', 'status', 'all'].includes(target)) {
    console.error('Target must be tasks, status, or all');
    process.exit(1);
  }
  const outputs = renderProject(projectRoot, target);
  console.log(JSON.stringify(outputs, null, 2));
}

if (require.main === module) {
  runCli(process.argv.slice(2));
}

module.exports = {
  renderProject,
  renderTasksMd,
  renderStatusMd,
};
