'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { initProject, saveTasks, loadTasks } = require('../state');
const { writeJson } = require('../lib/paths');

function makeTempProject() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'amir-test-'));
  initProject(root);
  return root;
}

function addTask(projectRoot, overrides = {}) {
  const tasksData = loadTasks(projectRoot);
  const task = {
    id: 'T001',
    title: 'Test task',
    goal: 'Goal',
    scope: 'Scope',
    status: 'pending',
    priority: 'P1',
    dependencies: [],
    approval_required: false,
    qa_report_path: null,
    alignment_review_path: null,
    checkpoint_tag: null,
    cycles: { used: 0, budget: 10, extensions_granted: 0 },
    ...overrides,
  };
  tasksData.tasks.push(task);
  saveTasks(projectRoot, tasksData);
  return task;
}

function writeAgents(projectRoot, agents) {
  writeJson(path.join(projectRoot, 'ai', 'state', 'agents.json'), {
    version: 1,
    agents,
  });
}

function appendActivityLine(projectRoot, event) {
  const activityPath = path.join(projectRoot, 'ai', 'state', 'activity.jsonl');
  fs.appendFileSync(activityPath, `${JSON.stringify(event)}\n`, 'utf8');
}

module.exports = {
  makeTempProject,
  addTask,
  writeAgents,
  appendActivityLine,
};
