'use strict';

const assert = require('node:assert/strict');
const { describe, it } = require('node:test');
const fs = require('fs');
const path = require('path');
const {
  addAgent,
  deleteAgent,
  setAgentState,
  resetAgent,
  generatePrompt,
  approveApproval,
  rejectApproval,
  loadAgents,
  loadStatus,
  transition,
} = require('../state');
const { makeTempProject, addTask, writeAgents } = require('../lib/test-fixture');
const { writeJson, statePath, readJson } = require('../lib/paths');

describe('agent ops', () => {
  it('add-agent scaffolds workspace and registry', () => {
    const root = makeTempProject();
    const result = addAgent(root, {
      role: 'researcher',
      responsibility: 'scout APIs',
      model: 'cheap',
      name: 'api-scout',
      by: 'human',
    });
    assert.equal(result.agent.id, 'api-scout');
    assert.ok(fs.existsSync(path.join(root, 'ai', 'agents', 'api-scout', 'prompt.md')));
    assert.ok(fs.existsSync(path.join(root, 'ai', 'views', 'agents.md')));
    const agents = loadAgents(root);
    assert.ok(agents.agents.some((a) => a.id === 'api-scout'));
  });

  it('add-agent with parent uses sub- id', () => {
    const root = makeTempProject();
    writeAgents(root, [
      { id: '1-orchestrator', role: 'orchestrator', state: 'active', last_heartbeat_ts: null, task_id: null },
      { id: '3-qa', role: 'qa', state: 'idle', last_heartbeat_ts: null, task_id: null },
    ]);
    const result = addAgent(root, {
      role: 'helper',
      parent: '3-qa',
      name: 'lint',
      by: 'human',
    });
    assert.equal(result.agent.id, '3-qa/sub-lint');
    assert.ok(fs.existsSync(path.join(root, 'ai', 'agents', '3-qa__sub-lint', 'prompt.md')));
  });

  it('delete-agent archives and requires typed name', () => {
    const root = makeTempProject();
    addAgent(root, { role: 'temp', name: 'temp-agent', by: 'human' });
    setAgentState(root, { agentId: 'temp-agent', to: 'idle', by: 'human' });
    assert.throws(
      () => deleteAgent(root, { agentId: 'temp-agent', confirmName: 'wrong', by: 'human' }),
      /confirmation/,
    );
    const result = deleteAgent(root, {
      agentId: 'temp-agent',
      confirmName: 'temp-agent',
      by: 'human',
    });
    assert.ok(result.archivePath.includes('_archive'));
    assert.ok(fs.existsSync(path.join(root, result.archivePath)));
    assert.ok(!loadAgents(root).agents.some((a) => a.id === 'temp-agent'));
  });

  it('delete-agent rejects active agents', () => {
    const root = makeTempProject();
    addAgent(root, { role: 'busy', name: 'busy-one', by: 'human' });
    setAgentState(root, { agentId: 'busy-one', to: 'active', by: 'human' });
    assert.throws(
      () =>
        deleteAgent(root, {
          agentId: 'busy-one',
          confirmName: 'busy-one',
          by: 'human',
        }),
      /stop first/,
    );
  });

  it('reset-agent archives then rescaffolds', () => {
    const root = makeTempProject();
    addAgent(root, { role: 'worker', name: 'dev-T099', by: 'human' });
    fs.writeFileSync(path.join(root, 'ai', 'agents', 'dev-T099', 'notes.md'), 'old notes');
    const result = resetAgent(root, { agentId: 'dev-T099', by: 'human', reason: 'stale' });
    assert.ok(result.archivePath.includes('reset'));
    assert.ok(fs.existsSync(path.join(root, 'ai', 'agents', 'dev-T099', 'prompt.md')));
  });

  it('generate-prompt writes prompt.md', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'in_progress' });
    writeAgents(root, [
      {
        id: 'dev-T001',
        role: 'worker',
        state: 'idle',
        task_id: 'T001',
        last_heartbeat_ts: null,
      },
    ]);
    const result = generatePrompt(root, { agentId: 'dev-T001' });
    assert.ok(result.promptPath.endsWith('prompt.md'));
    const body = fs.readFileSync(path.join(root, result.promptPath), 'utf8');
    assert.match(body, /T001/);
  });

  it('handles Windows-style workspace paths in registry', () => {
    const root = makeTempProject();
    writeAgents(root, [
      {
        id: '1-orchestrator',
        role: 'orchestrator',
        state: 'active',
        workspace: 'E:\\proj\\.ai\\agents\\1-orchestrator',
        last_heartbeat_ts: null,
        task_id: null,
      },
    ]);
    const agents = loadAgents(root);
    assert.equal(agents.agents[0].workspace, 'E:\\proj\\.ai\\agents\\1-orchestrator');
    const result = setAgentState(root, {
      agentId: '1-orchestrator',
      to: 'idle',
      by: 'human',
    });
    assert.equal(result.to, 'idle');
  });
});

describe('approval ops', () => {
  it('approve moves pending to approvals and grants cycles', () => {
    const root = makeTempProject();
    addTask(root, {
      id: 'T001',
      status: 'blocked',
      cycles: { used: 10, budget: 10, extensions_granted: 0 },
    });
    const status = loadStatus(root);
    status.pending_approvals = [
      {
        id: 'appr-1',
        type: 'budget_extension',
        summary: 'Need more cycles',
        requested_at: new Date().toISOString(),
        task: 'T001',
        justification: '1) scope 2) risk 3) cost 4) alt',
      },
    ];
    writeJson(statePath(root, 'status.json'), status);

    const result = approveApproval(root, {
      approvalId: 'appr-1',
      grant: 'cycles:+10',
      by: 'human',
    });
    assert.equal(result.record.outcome, 'approved');
    assert.equal(loadStatus(root).pending_approvals.length, 0);
    const approvals = readJson(statePath(root, 'approvals.json'));
    assert.equal(approvals.approvals.length, 1);
    const tasks = readJson(statePath(root, 'tasks.json'));
    assert.equal(tasks.tasks[0].cycles.extensions_granted, 1);
    assert.equal(tasks.tasks[0].cycles.budget, 20);
  });

  it('reject records outcome without grant', () => {
    const root = makeTempProject();
    const status = loadStatus(root);
    status.pending_approvals = [
      {
        id: 'appr-2',
        type: 'architecture',
        summary: 'Swap DB',
        requested_at: new Date().toISOString(),
      },
    ];
    writeJson(statePath(root, 'status.json'), status);
    const result = rejectApproval(root, { approvalId: 'appr-2', by: 'human', note: 'no' });
    assert.equal(result.record.outcome, 'rejected');
  });
});

describe('human writer transitions', () => {
  it('allows human to cancel a task', () => {
    const root = makeTempProject();
    addTask(root, { id: 'T001', status: 'pending' });
    const result = transition(root, {
      taskId: 'T001',
      toStatus: 'cancelled',
      by: 'human',
      note: 'no longer needed',
    });
    assert.equal(result.toStatus, 'cancelled');
  });
});
