import * as vscode from 'vscode';
import type { StateStore, AmirSnapshot } from '../core/stateStore';

export class StatusBarController implements vscode.Disposable {
  private readonly item: vscode.StatusBarItem;
  private sub: vscode.Disposable | undefined;

  constructor(private readonly store: StateStore) {
    this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 50);
    this.item.command = 'amir.focusProject';
    this.sub = store.onChange((s) => this.render(s));
    if (store.current) this.render(store.current);
  }

  private render(snap: AmirSnapshot): void {
    if (!snap.isAmirProject) {
      this.item.hide();
      return;
    }
    const phase = String(snap.status.phase || snap.status.current_phase || '—');
    const task = String(snap.status.current_task || '—');
    const cost =
      snap.estCostUsd !== null && snap.estCostUsd !== undefined
        ? `$${snap.estCostUsd.toFixed(2)}`
        : '$—';
    this.item.text = `amir: ${phase} | ${task} | ${cost}`;
    const warn =
      snap.pendingApprovals.length > 0 || snap.staleAgentIds.size > 0;
    this.item.backgroundColor = warn
      ? new vscode.ThemeColor('statusBarItem.warningBackground')
      : undefined;
    this.item.tooltip = warn
      ? 'Pending approvals or stale agents — click for Project tab'
      : 'Open amir Project tab';
    this.item.show();
  }

  dispose(): void {
    this.sub?.dispose();
    this.item.dispose();
  }
}
