import * as vscode from 'vscode';
import { filterTasks, partitionFinished } from '../core/taskSort';
import type { AmirSnapshot, AmirTask, StateStore } from '../core/stateStore';

export class TaskItem extends vscode.TreeItem {
  constructor(
    public readonly task: AmirTask | null,
    label: string,
    collapsible: vscode.TreeItemCollapsibleState,
  ) {
    super(label, collapsible);
    if (!task) {
      this.contextValue = 'group';
      return;
    }
    this.contextValue = 'task';
    const cycles = task.cycles;
    const used = cycles?.used ?? 0;
    const budget = cycles?.budget ?? 10;
    const over = used >= budget;
    const lock = task.approval_required || task.human_approval_required ? ' 🔒' : '';
    const deps = (task.dependencies || []).length;
    this.description = [
      task.priority || '',
      task.risk_level || '',
      `${used}/${budget}${over ? '!' : ''}`,
      deps ? `deps:${deps}` : '',
    ]
      .filter(Boolean)
      .join(' · ') + lock;
    this.iconPath = statusIcon(task.status);
    this.tooltip = `${task.id}: ${task.title}\n${task.status}`;
    this.command = {
      command: 'amir.openTaskDetail',
      title: 'Open task',
      arguments: [task.id],
    };
  }
}

function statusIcon(status: string): vscode.ThemeIcon {
  switch (status) {
    case 'in_progress':
      return new vscode.ThemeIcon('sync~spin', new vscode.ThemeColor('charts.blue'));
    case 'qa_failed':
      return new vscode.ThemeIcon('error', new vscode.ThemeColor('charts.red'));
    case 'pending':
      return new vscode.ThemeIcon('circle-outline');
    case 'blocked':
      return new vscode.ThemeIcon('warning', new vscode.ThemeColor('charts.orange'));
    case 'qa_passed':
      return new vscode.ThemeIcon('pass', new vscode.ThemeColor('charts.green'));
    case 'complete':
      return new vscode.ThemeIcon('check', new vscode.ThemeColor('charts.green'));
    case 'cancelled':
      return new vscode.ThemeIcon('circle-slash');
    default:
      return new vscode.ThemeIcon('circle-outline');
  }
}

export class TasksTreeProvider implements vscode.TreeDataProvider<TaskItem>, vscode.Disposable {
  private readonly _onDidChange = new vscode.EventEmitter<TaskItem | undefined | null>();
  readonly onDidChangeTreeData = this._onDidChange.event;
  private tasks: AmirTask[] = [];
  private filter: { text?: string; status?: string; milestone?: string } = {};
  private sub: vscode.Disposable | undefined;

  constructor(store: StateStore) {
    this.sub = store.onChange((s) => this.apply(s));
    if (store.current) this.apply(store.current);
  }

  setFilter(f: { text?: string; status?: string; milestone?: string }): void {
    this.filter = f;
    this.refresh();
  }

  refresh(): void {
    this._onDidChange.fire(undefined);
  }

  private apply(snap: AmirSnapshot): void {
    this.tasks = snap.tasks;
    this.refresh();
  }

  getTreeItem(element: TaskItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: TaskItem): TaskItem[] {
    if (element?.task === null && element.label === 'Finished') {
      const { finished } = partitionFinished(filterTasks(this.tasks, this.filter));
      return finished.map(
        (t) => new TaskItem(t, `${t.id}  ${t.title}`, vscode.TreeItemCollapsibleState.None),
      );
    }
    if (element) return [];

    const filtered = filterTasks(this.tasks, this.filter);
    const { active, finished } = partitionFinished(filtered);
    const items = active.map(
      (t) => new TaskItem(t, `${t.id}  ${t.title}`, vscode.TreeItemCollapsibleState.None),
    );
    if (finished.length) {
      items.push(
        new TaskItem(null, 'Finished', vscode.TreeItemCollapsibleState.Collapsed),
      );
    }
    return items;
  }

  dispose(): void {
    this.sub?.dispose();
    this._onDidChange.dispose();
  }
}
