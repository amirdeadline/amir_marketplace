import type { AmirTask } from './stateStore';

const PRIORITY_ORDER: Record<string, number> = { P0: 0, P1: 1, P2: 2, P3: 3 };

/**
 * Sort per extension build prompt §4.3:
 * in_progress → qa_failed → pending (P0–P3 then order) → blocked → qa_passed
 * → complete/cancelled in Finished group (caller may separate).
 */
export function sortTasksForTree(tasks: AmirTask[]): AmirTask[] {
  const rank = (status: string): number => {
    switch (status) {
      case 'in_progress':
        return 0;
      case 'qa_failed':
        return 1;
      case 'pending':
        return 2;
      case 'blocked':
        return 3;
      case 'qa_passed':
        return 4;
      case 'complete':
        return 5;
      case 'cancelled':
        return 6;
      default:
        return 9;
    }
  };

  return [...tasks].sort((a, b) => {
    const ra = rank(a.status);
    const rb = rank(b.status);
    if (ra !== rb) return ra - rb;
    if (a.status === 'pending' && b.status === 'pending') {
      const pa = PRIORITY_ORDER[a.priority || 'P3'] ?? 9;
      const pb = PRIORITY_ORDER[b.priority || 'P3'] ?? 9;
      if (pa !== pb) return pa - pb;
      const oa = a.order ?? 9999;
      const ob = b.order ?? 9999;
      if (oa !== ob) return oa - ob;
    }
    return a.id.localeCompare(b.id);
  });
}

export function partitionFinished(tasks: AmirTask[]): {
  active: AmirTask[];
  finished: AmirTask[];
} {
  const sorted = sortTasksForTree(tasks);
  return {
    active: sorted.filter((t) => t.status !== 'complete' && t.status !== 'cancelled'),
    finished: sorted.filter((t) => t.status === 'complete' || t.status === 'cancelled'),
  };
}

export function filterTasks(
  tasks: AmirTask[],
  query: { text?: string; status?: string; milestone?: string },
): AmirTask[] {
  const text = (query.text || '').trim().toLowerCase();
  return tasks.filter((t) => {
    if (query.status && t.status !== query.status) return false;
    if (query.milestone && t.milestone !== query.milestone) return false;
    if (!text) return true;
    const hay = `${t.id} ${t.title} ${t.goal || ''} ${t.scope || ''}`.toLowerCase();
    return hay.includes(text);
  });
}
