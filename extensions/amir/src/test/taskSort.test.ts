import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { filterTasks, partitionFinished, sortTasksForTree } from '../core/taskSort';
import type { AmirTask } from '../core/stateStore';

function t(partial: Partial<AmirTask> & { id: string; status: string }): AmirTask {
  return {
    title: partial.title || partial.id,
    ...partial,
  } as AmirTask;
}

describe('taskSort', () => {
  it('orders statuses per §4.3', () => {
    const sorted = sortTasksForTree([
      t({ id: 'T005', status: 'complete' }),
      t({ id: 'T001', status: 'pending', priority: 'P2', order: 2 }),
      t({ id: 'T002', status: 'in_progress' }),
      t({ id: 'T003', status: 'qa_failed' }),
      t({ id: 'T004', status: 'blocked' }),
      t({ id: 'T006', status: 'qa_passed' }),
      t({ id: 'T007', status: 'pending', priority: 'P0', order: 1 }),
      t({ id: 'T008', status: 'cancelled' }),
    ]);
    assert.deepEqual(
      sorted.map((x) => x.id),
      ['T002', 'T003', 'T007', 'T001', 'T004', 'T006', 'T005', 'T008'],
    );
  });

  it('partitions finished group', () => {
    const { active, finished } = partitionFinished([
      t({ id: 'T001', status: 'pending' }),
      t({ id: 'T002', status: 'complete' }),
    ]);
    assert.equal(active.length, 1);
    assert.equal(finished.length, 1);
  });

  it('filters by text and status', () => {
    const tasks = [
      t({ id: 'T001', status: 'pending', title: 'Auth login' }),
      t({ id: 'T002', status: 'blocked', title: 'Payments' }),
    ];
    assert.equal(filterTasks(tasks, { text: 'auth' }).length, 1);
    assert.equal(filterTasks(tasks, { status: 'blocked' })[0].id, 'T002');
  });
});
