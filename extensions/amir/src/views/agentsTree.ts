import * as vscode from 'vscode';
import type { AmirAgent, AmirSnapshot, StateStore } from '../core/stateStore';

export class AgentItem extends vscode.TreeItem {
  constructor(
    public readonly agent: AmirAgent,
    collapsible: vscode.TreeItemCollapsibleState,
    stale: boolean,
  ) {
    super(agent.id, collapsible);
    this.contextValue = 'agent';
    this.description = `${agent.state}${agent.task_id || agent.current_task ? ` · ${agent.task_id || agent.current_task}` : ''}${agent.model ? ` · ${agent.model}` : ''}`;
    const phase = agent.responsibility || agent.role;
    this.tooltip = stale
      ? `${agent.id}: no heartbeat >5 min`
      : `${agent.id}\n${phase}\nstate=${agent.state}`;
    if (stale) {
      this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('charts.orange'));
    } else if (agent.state === 'active') {
      this.iconPath = new vscode.ThemeIcon('circle-filled', new vscode.ThemeColor('charts.green'));
    } else if (agent.state === 'complete') {
      this.iconPath = new vscode.ThemeIcon('check');
    } else if (agent.state === 'reset') {
      this.iconPath = new vscode.ThemeIcon('debug-restart');
    } else {
      this.iconPath = new vscode.ThemeIcon('circle-outline');
    }
    this.command = {
      command: 'amir.focusAgentTerminal',
      title: 'Focus terminal',
      arguments: [agent.id],
    };
  }
}

export class AgentsTreeProvider implements vscode.TreeDataProvider<AgentItem>, vscode.Disposable {
  private readonly _onDidChange = new vscode.EventEmitter<AgentItem | undefined | null>();
  readonly onDidChangeTreeData = this._onDidChange.event;
  private agents: AmirAgent[] = [];
  private stale = new Set<string>();
  private sub: vscode.Disposable | undefined;

  constructor(store: StateStore) {
    this.sub = store.onChange((s) => this.apply(s));
    if (store.current) this.apply(store.current);
  }

  refresh(): void {
    this._onDidChange.fire(undefined);
  }

  private apply(snap: AmirSnapshot): void {
    this.agents = snap.agents;
    this.stale = snap.staleAgentIds;
    this.refresh();
  }

  getTreeItem(element: AgentItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: AgentItem): AgentItem[] {
    if (!element) {
      const top = this.agents.filter((a) => !a.parent);
      // Also treat ids that are not children of any listed parent as top-level
      const childIds = new Set(
        this.agents.filter((a) => a.parent).map((a) => a.id),
      );
      const orphans = this.agents.filter((a) => !a.parent && !this.isSubId(a.id));
      const tops = this.sortAgents(
        this.agents.filter((a) => {
          if (a.parent) return false;
          // nest qa-* under 3-qa when present even without parent field
          if (/^qa-/.test(a.id) && this.agents.some((x) => x.id === '3-qa')) return false;
          if (/\/sub-/.test(a.id)) return false;
          return true;
        }),
      );
      void childIds;
      void orphans;
      return tops.map(
        (a) =>
          new AgentItem(
            a,
            this.hasChildren(a) ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None,
            this.stale.has(a.id),
          ),
      );
    }
    const kids = this.childrenOf(element.agent);
    return kids.map(
      (a) =>
        new AgentItem(
          a,
          this.hasChildren(a) ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None,
          this.stale.has(a.id),
        ),
    );
  }

  private isSubId(id: string): boolean {
    return id.includes('/sub-');
  }

  private hasChildren(agent: AmirAgent): boolean {
    return this.childrenOf(agent).length > 0;
  }

  private childrenOf(agent: AmirAgent): AmirAgent[] {
    const direct = this.agents.filter((a) => a.parent === agent.id);
    const nested = this.agents.filter(
      (a) => a.id.startsWith(`${agent.id}/sub-`) && a.id !== agent.id,
    );
    const implied =
      agent.id === '3-qa'
        ? this.agents.filter((a) => /^qa-/.test(a.id) && !a.parent)
        : [];
    const map = new Map<string, AmirAgent>();
    for (const a of [...direct, ...nested, ...implied]) map.set(a.id, a);
    return this.sortAgents([...map.values()]);
  }

  private sortAgents(list: AmirAgent[]): AmirAgent[] {
    return [...list].sort((a, b) => a.id.localeCompare(b.id));
  }

  dispose(): void {
    this.sub?.dispose();
    this._onDidChange.dispose();
  }
}
