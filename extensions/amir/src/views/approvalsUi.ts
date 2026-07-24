import * as vscode from 'vscode';
import type { StateCli } from '../core/stateCli';
import type { AmirSnapshot, PendingApproval, StateStore } from '../core/stateStore';

export class ApprovalsUi implements vscode.Disposable {
  private seen = new Set<string>();
  private lastNotify = new Map<string, number>();
  private sub: vscode.Disposable | undefined;

  constructor(
    private readonly store: StateStore,
    private readonly getCli: () => StateCli | undefined,
  ) {
    this.sub = store.onChange((s) => this.onSnapshot(s));
  }

  private rateOk(key: string): boolean {
    const now = Date.now();
    const last = this.lastNotify.get(key) || 0;
    if (now - last < 30_000) return false;
    this.lastNotify.set(key, now);
    return true;
  }

  private onSnapshot(snap: AmirSnapshot): void {
    if (!snap.isAmirProject) return;

    for (const a of snap.pendingApprovals) {
      if (this.seen.has(a.id)) continue;
      this.seen.add(a.id);
      if (!this.rateOk(`approval:${a.id}`)) continue;
      void this.toastApproval(a);
    }

    if (snap.staleAgentIds.size > 0 && this.rateOk('stale')) {
      const ids = [...snap.staleAgentIds].join(', ');
      void vscode.window.showWarningMessage(`amir: agent(s) stale (no heartbeat >5 min): ${ids}`);
    }

    const overall = String(snap.status.overall || '');
    if (overall === 'complete' && this.rateOk('complete')) {
      void vscode.window.showInformationMessage('amir: project complete');
    }

    for (const t of snap.tasks) {
      if (t.status === 'qa_failed' && this.rateOk(`qa_failed:${t.id}`)) {
        void vscode.window.showWarningMessage(`amir: ${t.id} entered qa_failed`);
      }
      if (t.status === 'blocked' && this.rateOk(`blocked:${t.id}`)) {
        void vscode.window.showWarningMessage(`amir: ${t.id} BLOCKED — ${t.note || 'decision required'}`);
      }
      const used = t.cycles?.used ?? 0;
      const budget = t.cycles?.budget ?? 10;
      if (used >= budget && t.status !== 'complete' && this.rateOk(`budget:${t.id}`)) {
        void vscode.window.showWarningMessage(`amir: ${t.id} budget exhausted (${used}/${budget})`);
      }
    }
  }

  private async toastApproval(a: PendingApproval): Promise<void> {
    const pick = await vscode.window.showInformationMessage(
      `amir pending approval: [${a.type}] ${a.summary}`,
      'Approve',
      'Reject',
      'Open Project',
    );
    if (pick === 'Open Project') {
      await vscode.commands.executeCommand('amir.focusProject');
      return;
    }
    const cli = this.getCli();
    if (!cli?.available) {
      void vscode.window.showErrorMessage('tools/state unavailable');
      return;
    }
    if (pick === 'Approve') {
      const detail = await vscode.window.showInformationMessage(
        `Approve ${a.id}?\n\n${JSON.stringify(a, null, 2)}`,
        { modal: true },
        'Confirm Approve',
      );
      if (detail !== 'Confirm Approve') return;
      const args = ['--approval-id', a.id];
      if (a.type === 'budget_extension') args.push('--grant', 'cycles:+10');
      const r = await cli.run('approve', args);
      if (!r.ok) void vscode.window.showErrorMessage(r.error || 'approve failed');
      else void this.store.reload();
    } else if (pick === 'Reject') {
      const detail = await vscode.window.showWarningMessage(
        `Reject ${a.id}?\n\n${JSON.stringify(a, null, 2)}`,
        { modal: true },
        'Confirm Reject',
      );
      if (detail !== 'Confirm Reject') return;
      const r = await cli.run('reject', ['--approval-id', a.id]);
      if (!r.ok) void vscode.window.showErrorMessage(r.error || 'reject failed');
      else void this.store.reload();
    }
  }

  dispose(): void {
    this.sub?.dispose();
  }
}
