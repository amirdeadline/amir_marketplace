import * as vscode from 'vscode';
import type { StateCli } from '../core/stateCli';
import type { AmirTask, StateStore } from '../core/stateStore';

export class TaskDetailPanel {
  public static current: TaskDetailPanel | undefined;
  private readonly panel: vscode.WebviewPanel;

  private constructor(
    panel: vscode.WebviewPanel,
    private readonly store: StateStore,
    private readonly getCli: () => StateCli | undefined,
    private taskId: string,
    private readonly extensionUri: vscode.Uri,
  ) {
    this.panel = panel;
    this.panel.onDidDispose(() => {
      if (TaskDetailPanel.current === this) TaskDetailPanel.current = undefined;
    });
    this.panel.webview.onDidReceiveMessage((msg) => void this.onMessage(msg));
    store.onChange(() => this.render());
    this.render();
  }

  static show(
    store: StateStore,
    getCli: () => StateCli | undefined,
    taskId: string,
    extensionUri: vscode.Uri,
  ): void {
    if (TaskDetailPanel.current) {
      TaskDetailPanel.current.taskId = taskId;
      TaskDetailPanel.current.panel.reveal();
      TaskDetailPanel.current.render();
      return;
    }
    const panel = vscode.window.createWebviewPanel(
      'amir.taskDetail',
      `amir ${taskId}`,
      vscode.ViewColumn.Beside,
      {
        enableScripts: true,
        localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')],
      },
    );
    TaskDetailPanel.current = new TaskDetailPanel(panel, store, getCli, taskId, extensionUri);
  }

  private task(): AmirTask | undefined {
    return this.store.current?.tasks.find((t) => t.id === this.taskId);
  }

  private render(): void {
    const task = this.task();
    const css = this.panel.webview.asWebviewUri(
      vscode.Uri.joinPath(this.extensionUri, 'media', 'webview.css'),
    );
    const csp = `default-src 'none'; img-src ${this.panel.webview.cspSource}; style-src ${this.panel.webview.cspSource}; script-src ${this.panel.webview.cspSource};`;
    if (!task) {
      this.panel.webview.html = `<!DOCTYPE html><html><body>Task ${this.taskId} not found</body></html>`;
      return;
    }
    const criteria = renderCriteria(task.acceptance_criteria);
    const history = Array.isArray(task.history)
      ? (task.history as { ts?: string; from?: string; to?: string; by?: string; note?: string }[])
          .map((h) => `<li>${esc(h.ts || '')}: ${esc(h.from || '')} → ${esc(h.to || '')} by ${esc(h.by || '')} ${esc(h.note || '')}</li>`)
          .join('')
      : '';
    const deps = (task.dependencies || [])
      .map((d) => `<a href="#" data-cmd="openTask" data-id="${esc(d)}">${esc(d)}</a>`)
      .join(', ');
    const mut = this.getCli()?.available
      ? ''
      : ' disabled title="tools/state unavailable"';

    this.panel.title = `amir ${task.id}`;
    this.panel.webview.html = `<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"/>
<meta http-equiv="Content-Security-Policy" content="${csp}"/>
<link rel="stylesheet" href="${css}"/>
</head><body>
  <div class="header"><h1 class="project-name">${esc(task.id)} — ${esc(task.title)}</h1>
  <span class="chip">${esc(task.status)}</span></div>
  <div class="card"><strong>Goal</strong><div>${esc(task.goal || '')}</div></div>
  <div class="card"><strong>Scope</strong><div>${esc(task.scope || '')}</div></div>
  <div class="card"><strong>Acceptance criteria</strong><ul class="checklist">${criteria}</ul></div>
  <div class="card"><strong>Definition of done</strong><pre>${esc(stringify(task.definition_of_done))}</pre></div>
  <div class="card"><strong>Allowed files</strong><pre>${esc((task.allowed_files || []).join('\n'))}</pre></div>
  <div class="card"><strong>Forbidden files</strong><pre>${esc((task.forbidden_files || []).join('\n'))}</pre></div>
  <div class="card"><strong>Files likely affected</strong><pre>${esc((task.files_likely_affected || []).join('\n'))}</pre></div>
  <div class="card"><strong>Dependencies</strong><div>${deps || '—'}</div></div>
  <div class="card"><strong>Risk</strong> ${esc(task.risk_level || '—')} · <strong>Milestone</strong> ${esc(task.milestone || '—')}</div>
  <div class="card"><strong>Cycles</strong> ${task.cycles?.used ?? 0}/${task.cycles?.budget ?? 10} (extensions: ${task.cycles?.extensions_granted ?? 0})</div>
  <div class="card"><strong>History</strong><ul>${history || '<li class="muted">—</li>'}</ul></div>
  <div class="footer">
    <button data-cmd="openQa"${task.qa_report_path ? '' : ' disabled'}>Open QA report</button>
    <button data-cmd="openDev">Open dev agent folder</button>
    <button data-cmd="cancel"${mut}>Cancel task</button>
    <button data-cmd="block"${mut}>Block task</button>
    <button data-cmd="acceptRisk"${mut}>Accept remaining risk</button>
    <button data-cmd="reverify"${mut}>Request re-verify</button>
  </div>
  <script src="${this.panel.webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'taskDetail.js'))}"></script>
</body></html>`;
  }

  private async onMessage(msg: { command?: string; id?: string }): Promise<void> {
    const task = this.task();
    if (!task) return;
    const cli = this.getCli();
    const root = this.store.current?.projectRoot || '';

    if (msg.command === 'openTask' && msg.id) {
      TaskDetailPanel.show(this.store, this.getCli, msg.id, this.extensionUri);
      return;
    }
    if (msg.command === 'openQa' && task.qa_report_path) {
      const uri = vscode.Uri.file(joinRoot(root, task.qa_report_path));
      await vscode.window.showTextDocument(uri);
      return;
    }
    if (msg.command === 'openDev') {
      const folder = task.dev_agent_folder || `ai/agents/dev-${task.id}`;
      const uri = vscode.Uri.file(joinRoot(root, folder));
      await vscode.commands.executeCommand('revealFileInOS', uri);
      return;
    }
    if (!cli?.available) {
      void vscode.window.showWarningMessage('tools/state unavailable');
      return;
    }
    if (msg.command === 'cancel') {
      const ok = await vscode.window.showWarningMessage(`Cancel ${task.id}?`, { modal: true }, 'Cancel task');
      if (ok !== 'Cancel task') return;
      const r = await cli.run('transition', [
        '--task', task.id, '--to', 'cancelled', '--note', 'Cancelled from amir cockpit',
      ]);
      if (!r.ok) void vscode.window.showErrorMessage(r.error || 'failed');
      else await this.store.reload();
    }
    if (msg.command === 'block') {
      const note = await vscode.window.showInputBox({ prompt: 'Block reason (required)', validateInput: (v) => (v.trim() ? undefined : 'Required') });
      if (!note) return;
      const r = await cli.run('transition', ['--task', task.id, '--to', 'blocked', '--note', note]);
      if (!r.ok) void vscode.window.showErrorMessage(r.error || 'failed');
      else await this.store.reload();
    }
    if (msg.command === 'acceptRisk') {
      const ok = await vscode.window.showInformationMessage(
        `Accept remaining risk for ${task.id}?`,
        { modal: true },
        'Accept',
      );
      if (ok !== 'Accept') return;
      await cli.run('set-task-field', [
        '--task', task.id, '--field', 'note', '--value', 'human accepted remaining risk',
      ]);
      await this.store.reload();
    }
    if (msg.command === 'reverify') {
      if (task.status !== 'qa_passed' && task.status !== 'complete') {
        void vscode.window.showWarningMessage('Re-verify only from qa_passed/complete context');
        return;
      }
      await cli.run('set-task-field', [
        '--task', task.id, '--field', 'note', '--value', 'needs_reverify',
      ]);
      await this.store.reload();
    }
  }
}

function joinRoot(root: string, rel: string): string {
  const path = require('path') as typeof import('path');
  if (path.isAbsolute(rel)) return rel;
  return path.join(root, ...rel.split(/[/\\]/));
}

function esc(s: string): string {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function stringify(v: unknown): string {
  if (v === null || v === undefined) return '';
  if (typeof v === 'string') return v;
  return JSON.stringify(v, null, 2);
}

function renderCriteria(c: unknown): string {
  if (!c) return '<li class="muted">—</li>';
  if (Array.isArray(c)) {
    return c
      .map((item) => {
        if (typeof item === 'string') return `<li>${esc(item)}</li>`;
        if (item && typeof item === 'object') {
          const o = item as { text?: string; done?: boolean };
          return `<li class="${o.done ? 'done' : ''}">${esc(o.text || JSON.stringify(item))}</li>`;
        }
        return `<li>${esc(String(item))}</li>`;
      })
      .join('');
  }
  return `<li>${esc(stringify(c))}</li>`;
}
