'use strict';

const assert = require('node:assert/strict');
const { describe, it } = require('node:test');
const fs = require('fs');
const path = require('path');
const {
  transition,
  validateTransition,
  initProject,
  loadTasks,
  computeBudget,
} = require('../state');
const { makeTempProject, addTask, writeAgents } = require('../lib/test-fixture');

describe('state transitions', () => {
  it('allows orchestrator pending to in_progress', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'pending' });
    const result = transition(root, {
      taskId: 'T001',
      toStatus: 'in_progress',
      by: '1-orchestrator',
    });
    assert.equal(result.toStatus, 'in_progress');
  });

  it('rejects non-orchestrator pending to in_progress', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'pending' });
    assert.throws(
      () => transition(root, { taskId: 'T001', toStatus: 'in_progress', by: 'dev-T001' }),
      /orchestrator/,
    );
  });

  it('allows qa agent to set qa_passed', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'in_progress' });
    writeAgents(root, [
      { id: 'qa-T001', role: 'verifier', state: 'active', last_heartbeat_ts: null, task_id: 'T001' },
    ]);
    const result = transition(root, {
      taskId: 'T001',
      toStatus: 'qa_passed',
      by: 'qa-T001',
      qaReport: 'ai/agents/qa-T001/qa-report.md',
    });
    assert.equal(result.toStatus, 'qa_passed');
  });

  it('rejects worker setting qa_passed', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'in_progress' });
    assert.throws(
      () => transition(root, { taskId: 'T001', toStatus: 'qa_passed', by: 'dev-T001' }),
      /cannot set qa_passed/,
    );
  });

  it('rejects qa_passed to complete without checkpoint and alignment review', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'qa_passed' });
    assert.throws(
      () => transition(root, { taskId: 'T001', toStatus: 'complete', by: '1-orchestrator' }),
      /alignment-review/,
    );
  });

  it('allows qa_passed to complete with required artifacts', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'qa_passed' });
    const alignPath = 'ai/agents/qa-T001/alignment.md';
    fs.mkdirSync(path.dirname(path.join(root, alignPath)), { recursive: true });
    fs.writeFileSync(path.join(root, alignPath), 'PASS');

    const result = transition(root, {
      taskId: 'T001',
      toStatus: 'complete',
      by: '1-orchestrator',
      alignmentReview: alignPath,
      checkpointTag: 'checkpoint-T001',
    });
    assert.equal(result.toStatus, 'complete');
    const tasks = loadTasks(root);
    assert.equal(tasks.tasks[0].checkpoint_tag, 'checkpoint-T001');
  });

  it('forces blocked when budget exceeded on qa_failed to in_progress', () => {
    const root = makeTempProject();
    addTask(root, {
      id: 'T001',
      status: 'qa_failed',
      cycles: { used: 10, budget: 10, extensions_granted: 0 },
    });

    const result = transition(root, {
      taskId: 'T001',
      toStatus: 'in_progress',
      by: '1-orchestrator',
    });

    assert.equal(result.toStatus, 'blocked');
    const tasks = loadTasks(root);
    assert.equal(tasks.tasks[0].cycles.used, 11);
  });

  it('increments cycles on qa_failed to in_progress within budget', () => {
    const root = makeTempProject();
    addTask(root, {
      id: 'T001',
      status: 'qa_failed',
      cycles: { used: 2, budget: 10, extensions_granted: 0 },
    });

    const result = transition(root, {
      taskId: 'T001',
      toStatus: 'in_progress',
      by: '1-orchestrator',
    });

    assert.equal(result.toStatus, 'in_progress');
    const tasks = loadTasks(root);
    assert.equal(tasks.tasks[0].cycles.used, 3);
  });

  it('rejects wrong writer for orchestrator-only cancelled transition', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'pending' });
    assert.throws(
      () => transition(root, { taskId: 'T001', toStatus: 'cancelled', by: 'dev-T001', note: 'stop' }),
      /orchestrator/,
    );
  });

  it('validateTransition exposes budget math', () => {
    const task = {
      cycles: { used: 10, budget: 10, extensions_granted: 0 },
      status: 'qa_failed',
    };
    const check = validateTransition(task, 'qa_failed', 'in_progress', { by: '1-orchestrator' });
    assert.equal(check.ok, true);
    assert.equal(check.forcedStatus, 'blocked');
    assert.equal(computeBudget(1), 20);
  });

  it('init creates valid skeleton state', () => {
    const root = makeTempProject();
    const tasks = loadTasks(root);
    assert.equal(tasks.version, 1);
    assert.ok(fs.existsSync(path.join(root, 'ai', 'state', 'activity.jsonl')));
  });
});
