import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import { ActivityTail, activityPath, type ActivityEvent } from './activityTail';
import { SchemaValidator } from './schemaValidator';

export interface AmirAgent {
  id: string;
  name?: string;
  role: string;
  parent?: string | null;
  workspace?: string;
  model?: string;
  state: string;
  last_heartbeat_ts?: string | null;
  task_id?: string | null;
  current_task?: string | null;
  responsibility?: string;
}

export interface AmirTask {
  id: string;
  title: string;
  goal?: string;
  scope?: string;
  status: string;
  priority?: string;
  order?: number;
  dependencies?: string[];
  approval_required?: boolean;
  human_approval_required?: boolean;
  risk_level?: string;
  milestone?: string;
  cycles?: { used?: number; budget?: number; extensions_granted?: number };
  acceptance_criteria?: unknown;
  definition_of_done?: unknown;
  allowed_files?: string[];
  forbidden_files?: string[];
  files_likely_affected?: string[];
  history?: unknown[];
  qa_report_path?: string | null;
  alignment_review_path?: string | null;
  checkpoint_tag?: string | null;
  dev_agent_folder?: string | null;
  note?: string | null;
  [key: string]: unknown;
}

export interface PendingApproval {
  id: string;
  type: string;
  summary: string;
  requested_at: string;
  task?: string;
  justification?: unknown;
  details?: unknown;
  [key: string]: unknown;
}

export interface AmirSnapshot {
  projectRoot: string;
  projectName: string;
  isAmirProject: boolean;
  tasks: AmirTask[];
  agents: AmirAgent[];
  status: Record<string, unknown>;
  risks: unknown[];
  approvals: unknown[];
  pendingApprovals: PendingApproval[];
  goalText: string;
  activity: ActivityEvent[];
  staleAgentIds: Set<string>;
  validationWarnings: string[];
  estCostUsd: number | null;
}

type Listener = (snap: AmirSnapshot) => void;

const SCHEMA_MAP: Record<string, string> = {
  'tasks.json': 'tasks.schema.json',
  'agents.json': 'agents.schema.json',
  'status.json': 'status.schema.json',
  'risks.json': 'risks.schema.json',
  'approvals.json': 'approvals.schema.json',
};

export class StateStore implements vscode.Disposable {
  private watcher: vscode.FileSystemWatcher | undefined;
  private debounceTimer: NodeJS.Timeout | undefined;
  private readonly listeners = new Set<Listener>();
  private snapshot: AmirSnapshot | undefined;
  private activityTail: ActivityTail | undefined;
  private disposed = false;

  constructor(
    private workspaceRoot: string | undefined,
    private readonly validator: SchemaValidator,
  ) {}

  get current(): AmirSnapshot | undefined {
    return this.snapshot;
  }

  onChange(listener: Listener): vscode.Disposable {
    this.listeners.add(listener);
    return { dispose: () => this.listeners.delete(listener) };
  }

  setWorkspaceRoot(root: string | undefined): void {
    this.workspaceRoot = root;
  }

  startWatching(): void {
    this.stopWatching();
    if (!this.workspaceRoot) return;
    const folder = vscode.Uri.file(this.workspaceRoot);
    const pattern = new vscode.RelativePattern(folder, 'ai/state/**');
    this.watcher = vscode.workspace.createFileSystemWatcher(pattern);
    const bump = () => this.scheduleReload();
    this.watcher.onDidChange(bump);
    this.watcher.onDidCreate(bump);
    this.watcher.onDidDelete(bump);
    void this.reload();
  }

  stopWatching(): void {
    this.watcher?.dispose();
    this.watcher = undefined;
    if (this.debounceTimer) clearTimeout(this.debounceTimer);
  }

  scheduleReload(): void {
    const ms = vscode.workspace.getConfiguration('amir').get<number>('watchDebounceMs') ?? 250;
    if (this.debounceTimer) clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      void this.reload();
    }, ms);
  }

  async reload(): Promise<AmirSnapshot> {
    const snap = this.loadSnapshot();
    this.snapshot = snap;
    for (const l of this.listeners) {
      try {
        l(snap);
      } catch {
        /* ignore listener errors */
      }
    }
    return snap;
  }

  private loadSnapshot(): AmirSnapshot {
    const root = this.workspaceRoot;
    const empty: AmirSnapshot = {
      projectRoot: root || '',
      projectName: root ? path.basename(root) : '',
      isAmirProject: false,
      tasks: [],
      agents: [],
      status: {},
      risks: [],
      approvals: [],
      pendingApprovals: [],
      goalText: '',
      activity: [],
      staleAgentIds: new Set(),
      validationWarnings: [],
      estCostUsd: null,
    };
    if (!root) return empty;

    const stateDir = path.join(root, 'ai', 'state');
    if (!fs.existsSync(stateDir)) return empty;

    const warnings: string[] = [];
    const readJson = (name: string): unknown => {
      const p = path.join(stateDir, name);
      if (!fs.existsSync(p)) return null;
      try {
        const data = JSON.parse(fs.readFileSync(p, 'utf8')) as unknown;
        const schema = SCHEMA_MAP[name];
        if (schema) {
          const v = this.validator.validate(schema, data);
          if (!v.ok) {
            warnings.push(`${name}: ${v.errors.join('; ')}`);
          }
        }
        return data;
      } catch (err) {
        warnings.push(`${name}: ${err instanceof Error ? err.message : String(err)}`);
        return null;
      }
    };

    const tasksData = readJson('tasks.json') as { tasks?: AmirTask[] } | null;
    const agentsData = readJson('agents.json') as { agents?: AmirAgent[] } | null;
    const statusData = (readJson('status.json') as Record<string, unknown> | null) || {};
    const risksData = readJson('risks.json') as { risks?: unknown[] } | null;
    const approvalsData = readJson('approvals.json') as { approvals?: unknown[] } | null;

    const goalPath = path.join(root, 'ai', 'project-goal.md');
    let goalText = '';
    if (fs.existsSync(goalPath)) {
      try {
        goalText = fs.readFileSync(goalPath, 'utf8');
      } catch {
        /* ignore */
      }
    }

    const actPath = activityPath(root);
    if (!this.activityTail || this.activityTail.getFilePath() !== actPath) {
      this.activityTail = new ActivityTail(actPath);
    }
    this.activityTail.poll();

    const agents = agentsData?.agents || [];
    const staleMinutes =
      vscode.workspace.getConfiguration('amir').get<number>('staleAfterMinutes') ?? 5;
    const activeIds = agents.filter((a) => a.state === 'active').map((a) => a.id);
    // Also consider last_heartbeat_ts from registry
    for (const a of agents) {
      if (a.last_heartbeat_ts) {
        const ts = Date.parse(a.last_heartbeat_ts);
        if (!Number.isNaN(ts)) {
          // activityTail lastSeen is private; poll already updated from file.
          // Merge heartbeat into stale calc via temporary map:
        }
      }
    }
    const hb = this.activityTail.computeHeartbeats(activeIds, staleMinutes);
    for (const a of agents) {
      if (a.state !== 'active') continue;
      if (a.last_heartbeat_ts) {
        const ts = Date.parse(a.last_heartbeat_ts);
        const last = hb.lastSeen.get(a.id);
        const best = Math.max(last ?? 0, Number.isNaN(ts) ? 0 : ts);
        if (best && Date.now() - best <= staleMinutes * 60 * 1000) {
          hb.staleAgentIds.delete(a.id);
        }
      }
    }

    return {
      projectRoot: root,
      projectName: path.basename(root),
      isAmirProject: true,
      tasks: tasksData?.tasks || [],
      agents,
      status: statusData,
      risks: risksData?.risks || [],
      approvals: approvalsData?.approvals || [],
      pendingApprovals: (statusData.pending_approvals as PendingApproval[]) || [],
      goalText,
      activity: this.activityTail.getRecent(30),
      staleAgentIds: hb.staleAgentIds,
      validationWarnings: warnings,
      estCostUsd: null,
    };
  }

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.stopWatching();
    this.listeners.clear();
  }
}
