import * as vscode from 'vscode';
import { agentWorkspaceFsPath } from './paths';

export { agentWorkspaceFsPath };

const PREFIX = 'amir: ';

export class TerminalRegistry implements vscode.Disposable {
  private readonly byAgent = new Map<string, vscode.Terminal>();

  constructor(private readonly extensionUri: vscode.Uri) {
    for (const t of vscode.window.terminals) {
      this.tryAssociate(t);
    }
    vscode.window.onDidCloseTerminal((t) => {
      for (const [id, term] of this.byAgent) {
        if (term === t) this.byAgent.delete(id);
      }
    });
  }

  terminalName(agentId: string): string {
    return `${PREFIX}${agentId}`;
  }

  get(agentId: string): vscode.Terminal | undefined {
    const existing = this.byAgent.get(agentId);
    if (existing && !this.isDisposed(existing)) return existing;
    for (const t of vscode.window.terminals) {
      if (t.name === this.terminalName(agentId)) {
        this.byAgent.set(agentId, t);
        return t;
      }
    }
    return undefined;
  }

  getOrCreate(agentId: string, cwd: string, statusColor: 'green' | 'gray' | 'orange' | 'blue' = 'gray'): vscode.Terminal {
    const existing = this.get(agentId);
    if (existing) return existing;
    const iconPath = vscode.Uri.joinPath(this.extensionUri, 'media', `status-${statusColor}.svg`);
    const term = vscode.window.createTerminal({
      name: this.terminalName(agentId),
      cwd,
      iconPath: fsExists(iconPath.fsPath)
        ? iconPath
        : new vscode.ThemeIcon('terminal'),
    });
    this.byAgent.set(agentId, term);
    return term;
  }

  focus(agentId: string, cwd: string): vscode.Terminal {
    const term = this.getOrCreate(agentId, cwd);
    term.show(true);
    return term;
  }

  getOrchestrator(cwd: string): vscode.Terminal {
    return this.focus('1-orchestrator', cwd);
  }

  send(agentId: string, cwd: string, text: string, show = true): void {
    const term = this.getOrCreate(agentId, cwd);
    if (show) term.show(true);
    term.sendText(text, true);
  }

  private tryAssociate(t: vscode.Terminal): void {
    if (t.name.startsWith(PREFIX)) {
      const id = t.name.slice(PREFIX.length);
      this.byAgent.set(id, t);
    }
  }

  private isDisposed(t: vscode.Terminal): boolean {
    try {
      // Accessing name on disposed terminal may throw in some hosts
      void t.name;
      return false;
    } catch {
      return true;
    }
  }

  dispose(): void {
    this.byAgent.clear();
  }
}

function fsExists(p: string): boolean {
  try {
    return require('fs').existsSync(p);
  } catch {
    return false;
  }
}
