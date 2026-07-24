import * as fs from 'fs';
import * as path from 'path';

export interface ActivityEvent {
  timestamp: string;
  agent_id: string;
  action: string;
  result: string;
  task_id?: string | null;
  [key: string]: unknown;
}

export interface HeartbeatMap {
  /** agent_id -> last activity/heartbeat Date.ms */
  lastSeen: Map<string, number>;
  staleAgentIds: Set<string>;
}

/**
 * Incremental JSONL tailer. Tracks byte offset; never re-reads prior bytes.
 */
export class ActivityTail {
  private offset = 0;
  private buffer = '';
  private readonly events: ActivityEvent[] = [];
  private readonly lastSeen = new Map<string, number>();
  private readonly maxKeep: number;

  constructor(
    private readonly filePath: string,
    maxKeep = 500,
  ) {
    this.maxKeep = maxKeep;
  }

  getFilePath(): string {
    return this.filePath;
  }

  getOffset(): number {
    return this.offset;
  }

  getRecent(n: number): ActivityEvent[] {
    return this.events.slice(-n);
  }

  getLastForAgent(agentId: string): ActivityEvent | undefined {
    for (let i = this.events.length - 1; i >= 0; i -= 1) {
      if (this.events[i].agent_id === agentId) return this.events[i];
    }
    return undefined;
  }

  /** Read only new bytes since last offset. */
  poll(): ActivityEvent[] {
    if (!fs.existsSync(this.filePath)) {
      this.offset = 0;
      this.buffer = '';
      return [];
    }
    const stat = fs.statSync(this.filePath);
    if (stat.size < this.offset) {
      // Truncated / rotated
      this.offset = 0;
      this.buffer = '';
    }
    if (stat.size === this.offset) return [];

    const fd = fs.openSync(this.filePath, 'r');
    try {
      const length = stat.size - this.offset;
      const buf = Buffer.alloc(length);
      fs.readSync(fd, buf, 0, length, this.offset);
      this.offset = stat.size;
      this.buffer += buf.toString('utf8');
    } finally {
      fs.closeSync(fd);
    }

    const added: ActivityEvent[] = [];
    let nl: number;
    while ((nl = this.buffer.indexOf('\n')) >= 0) {
      const line = this.buffer.slice(0, nl).trim();
      this.buffer = this.buffer.slice(nl + 1);
      if (!line) continue;
      try {
        const raw = JSON.parse(line) as Record<string, unknown>;
        const evt = normalizeEvent(raw);
        if (!evt) continue;
        this.events.push(evt);
        added.push(evt);
        const ts = Date.parse(evt.timestamp);
        if (!Number.isNaN(ts)) {
          this.lastSeen.set(evt.agent_id, ts);
        }
      } catch {
        // skip bad line
      }
    }
    if (this.events.length > this.maxKeep) {
      this.events.splice(0, this.events.length - this.maxKeep);
    }
    return added;
  }

  computeHeartbeats(
    activeAgentIds: string[],
    staleAfterMinutes: number,
    now = Date.now(),
  ): HeartbeatMap {
    const staleMs = staleAfterMinutes * 60 * 1000;
    const staleAgentIds = new Set<string>();
    for (const id of activeAgentIds) {
      const last = this.lastSeen.get(id);
      if (last === undefined || now - last > staleMs) {
        staleAgentIds.add(id);
      }
    }
    return { lastSeen: new Map(this.lastSeen), staleAgentIds };
  }
}

export function normalizeEvent(raw: Record<string, unknown>): ActivityEvent | null {
  const timestamp = String(raw.timestamp ?? raw.ts ?? '');
  const agent_id = String(raw.agent_id ?? raw.agent ?? '');
  const action = String(raw.action ?? '');
  const result = String(raw.result ?? '');
  if (!timestamp || !agent_id || !action) return null;
  return {
    ...raw,
    timestamp,
    agent_id,
    action,
    result,
    task_id: (raw.task_id ?? raw.task ?? null) as string | null,
  };
}

export function activityPath(projectRoot: string): string {
  return path.join(projectRoot, 'ai', 'state', 'activity.jsonl');
}

/** Pure helper for unit tests */
export function isStale(lastSeenMs: number | undefined, staleAfterMinutes: number, now: number): boolean {
  if (lastSeenMs === undefined) return true;
  return now - lastSeenMs > staleAfterMinutes * 60 * 1000;
}
