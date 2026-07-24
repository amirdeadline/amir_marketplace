import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import * as fs from 'fs';
import * as path from 'path';
import { sortTasksForTree } from '../core/taskSort';
import type { AmirTask } from '../core/stateStore';

describe('fixture amir project', () => {
  const fixture = path.join(__dirname, 'fixtures', 'amir-project');

  it('loads Windows-style workspace paths from agents.json', () => {
    const agents = JSON.parse(
      fs.readFileSync(path.join(fixture, 'ai', 'state', 'agents.json'), 'utf8'),
    ) as { agents: { id: string; workspace?: string }[] };
    const orch = agents.agents.find((a) => a.id === '1-orchestrator');
    assert.ok(orch?.workspace?.startsWith('E:\\'));
  });

  it('sorts fixture tasks with in_progress first', () => {
    const data = JSON.parse(
      fs.readFileSync(path.join(fixture, 'ai', 'state', 'tasks.json'), 'utf8'),
    ) as { tasks: AmirTask[] };
    const sorted = sortTasksForTree(data.tasks);
    assert.equal(sorted[0].id, 'T001');
    assert.equal(sorted[0].status, 'in_progress');
    assert.ok(sorted.some((t) => t.status === 'complete'));
  });

  it('has pending approval in status.json', () => {
    const status = JSON.parse(
      fs.readFileSync(path.join(fixture, 'ai', 'state', 'status.json'), 'utf8'),
    ) as { pending_approvals: unknown[] };
    assert.equal(status.pending_approvals.length, 1);
  });
});
