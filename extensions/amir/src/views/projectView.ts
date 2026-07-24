import * as path from 'path';
import * as vscode from 'vscode';
import type { StateCli } from '../core/stateCli';
import type { AmirSnapshot, StateStore } from '../core/stateStore';
import type { TerminalRegistry } from '../core/terminals';

export class ProjectViewProvider implements vscode.WebviewViewProvider, vscode.Disposable {
  public static readonly viewType = 'amir.project';
  private view?: vscode.WebviewView;
  private sub?: vscode.Disposable;

  constructor(
    private readonly extensionUri: vscode.Uri,
    private readonly store: StateStore,
    private readonly getCli: () => StateCli | undefined,
    private readonly terminals: TerminalRegistry,
    private readonly runSkill: (skill: string) => void,
  ) {
    this.sub = store.onChange((s) => this.render(s));
  }

  resolveWebviewView(
    webviewView: vscode.WebviewView,
    _ctx: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken,
  ): void {
    this.view = webviewView;
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [vscode.Uri.joinPath(this.extensionUri, 'media')],
    };
    webviewView.webview.onDidReceiveMessage((msg) => void this.onMessage(msg));
    this.render(this.store.current);
  }

  private render(snap: AmirSnapshot | undefined): void {
    if (!this.view) return;
    const webview = this.view.webview;
    const css = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'webview.css'));
    const js = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'project.js'));
    const csp = `default-src 'none'; img-src ${webview.cspSource}; style-src ${webview.cspSource}; script-src ${webview.cspSource};`;

    if (!snap || !snap.isAmirProject) {
      webview.html = `<!DOCTYPE html><html><head>
<meta charset="UTF-8"/><meta http-equiv="Content-Security-Policy" content="${csp}"/>
<link rel="stylesheet" href="${css}"/></head>
<body class="empty">
  <h1 class="project-name">amir</h1>
  <p>No amir project detected in this workspace (<code>ai/state/</code> missing).</p>
  <div class="footer">
    <button data-cmd="createProject">Create amir project here</button>
    <button class="secondary" data-cmd="openDocs">Open documentation</button>
  </div>
  <script src="${js}"></script>
</body></html>`;
      return;
    }

    const st = snap.status;
    const overall = String(st.overall || st.phase || '—');
    const risk = String(st.risk_level || 'low').toLowerCase();
    const progress = (st.progress || {}) as {
      tasks_complete?: number;
      tasks_total?: number;
      percent?: number;
    };
    const complete = progress.tasks_complete ?? 0;
    const total = progress.tasks_total ?? snap.tasks.length;
    const percent =
      progress.percent ?? (total ? Math.round((complete / total) * 100) : 0);
    const currentTask = String(st.current_task || '—');
    const currentTitle =
      snap.tasks.find((t) => t.id === currentTask)?.title || '';
    const dashboard = (st.dashboard || {}) as Record<string, unknown>;
    const phase = String(st.current_phase || st.phase || '—');
    const cycle = String(dashboard.cycle || '');
    const lastQa = String(st.last_qa || dashboard.last_qa || '—');
    const goalAlign = String(st.goal_alignment || dashboard.goal_alignment || '—');
    const nextAction = String(st.next_action || dashboard.next_action || '—');
    const blocker = st.blocker ? String(st.blocker) : '';
    const mutDisabled = this.getCli()?.available
      ? ''
      : ' disabled title="tools/state unavailable — set amir.pluginRoot"';

    const warnings = snap.validationWarnings.length
      ? `<div class="banner">Schema validation warning(s): ${esc(snap.validationWarnings.join(' | '))}
         <button data-cmd="doctor">Run /project_doctor</button></div>`
      : '';

    const approvals = snap.pendingApprovals
      .map(
        (a) => `<div class="approval">
          <div><strong>${esc(a.type)}</strong> · ${esc(a.task || '')}</div>
          <div>${esc(a.summary)}</div>
          <div class="muted">${esc(a.requested_at)}</div>
          <div class="actions">
            <button data-cmd="approve" data-approval="${esc(a.id)}"${mutDisabled}>Approve</button>
            <button class="secondary" data-cmd="reject" data-approval="${esc(a.id)}"${mutDisabled}>Reject</button>
            <button class="secondary" data-cmd="approvalDetails" data-approval="${esc(a.id)}">Details</button>
          </div>
        </div>`,
      )
      .join('') || '<p class="muted">No pending approvals</p>';

    const risks = [...snap.risks]
      .map((r) => r as { severity?: string; id?: string; summary?: string; title?: string })
      .sort((a, b) => severityRank(a.severity) - severityRank(b.severity))
      .map(
        (r) =>
          `<div class="card"><span class="chip risk-${esc((r.severity || 'low').toLowerCase())}">${esc(r.severity || '')}</span> ${esc(r.id || '')} ${esc(r.summary || r.title || JSON.stringify(r))}</div>`,
      )
      .join('') || '<p class="muted">No open risks</p>';

    const goalLines = snap.goalText.split(/\r?\n/).slice(0, 8).join('\n');
    const feed = snap.activity
      .slice()
      .reverse()
      .map(
        (e) => `<div class="feed-item">
          <div class="meta">${esc(e.timestamp)} · <a href="#" data-cmd="focusAgent" data-id="${esc(e.agent_id)}">${esc(e.agent_id)}</a> · ${esc(e.action)}</div>
          <div>${esc(e.result)}</div>
        </div>`,
      )
      .join('') || '<p class="muted">No activity yet</p>';

    const cost =
      snap.estCostUsd !== null ? `est. $${snap.estCostUsd.toFixed(2)}` : 'est. $—';

    webview.html = `<!DOCTYPE html><html><head>
<meta charset="UTF-8"/><meta http-equiv="Content-Security-Policy" content="${csp}"/>
<link rel="stylesheet" href="${css}"/></head><body>
${warnings}
<div class="header">
  <h1 class="project-name">${esc(snap.projectName)}</h1>
  <span class="chip">${esc(overall)}</span>
  <span class="chip risk-${esc(risk)}">${esc(risk)}</span>
</div>

<div class="card">
  <div>Current task: <a href="#" data-cmd="openTask" data-id="${esc(currentTask)}">${esc(currentTask)}</a> ${esc(currentTitle)}</div>
  <div>Phase: ${esc(phase)} ${cycle ? `· cycle ${esc(cycle)}` : ''}</div>
  <div>Last QA: ${esc(String(lastQa))} · Goal alignment: ${esc(String(goalAlign))}</div>
  <div>Next: ${esc(String(nextAction))}</div>
  ${blocker ? `<div class="blocker">Blocker: ${esc(blocker)}</div>` : ''}
</div>

<div class="card">
  <div>Progress: ${complete}/${total} (${percent}%)</div>
  <div class="progress"><span style="width:${percent}%"></span></div>
</div>

<h2>Pending Approvals</h2>
${approvals}

<h2>Open Risks</h2>
${risks}

<h2>Goal Summary</h2>
<pre>${esc(goalLines)}</pre>
<a href="#" data-cmd="openGoal">Open file</a>

<h2>Activity</h2>
${feed}

<div class="footer">
  <button data-cmd="skill" data-id="project_status">/project_status</button>
  <button data-cmd="skill" data-id="project_cost">/project_cost</button>
  <button data-cmd="skill" data-id="project_doctor">/project_doctor</button>
  <button data-cmd="skill" data-id="handoff">/handoff</button>
  <span class="muted">${esc(cost)}</span>
</div>
<script src="${js}"></script>
</body></html>`;
  }

  private async onMessage(msg: {
    command?: string;
    id?: string;
    approvalId?: string;
  }): Promise<void> {
    const snap = this.store.current;
    const root = snap?.projectRoot || '';
    const cli = this.getCli();

    switch (msg.command) {
      case 'createProject':
        await vscode.commands.executeCommand('amir.createProject');
        break;
      case 'openDocs':
        await vscode.commands.executeCommand('amir.openDocs');
        break;
      case 'doctor':
        this.runSkill('project_doctor');
        break;
      case 'skill':
        if (msg.id) this.runSkill(msg.id);
        break;
      case 'openTask':
        if (msg.id) await vscode.commands.executeCommand('amir.openTaskDetail', msg.id);
        break;
      case 'openGoal':
        if (root) {
          const uri = vscode.Uri.file(path.join(root, 'ai', 'project-goal.md'));
          await vscode.window.showTextDocument(uri);
        }
        break;
      case 'focusAgent':
        if (msg.id) await vscode.commands.executeCommand('amir.focusAgentTerminal', msg.id);
        break;
      case 'approvalDetails': {
        const a = snap?.pendingApprovals.find((x) => x.id === msg.approvalId);
        if (a) {
          await vscode.window.showInformationMessage(JSON.stringify(a, null, 2), { modal: true });
        }
        break;
      }
      case 'approve': {
        if (!cli?.available) {
          void vscode.window.showWarningMessage('tools/state unavailable');
          return;
        }
        const a = snap?.pendingApprovals.find((x) => x.id === msg.approvalId);
        if (!a) return;
        const ok = await vscode.window.showInformationMessage(
          `Approve ${a.id}?\n\n${JSON.stringify(a, null, 2)}`,
          { modal: true },
          'Confirm Approve',
        );
        if (ok !== 'Confirm Approve') return;
        const args = ['--approval-id', a.id];
        if (a.type === 'budget_extension') args.push('--grant', 'cycles:+10');
        const r = await cli.run('approve', args);
        if (!r.ok) void vscode.window.showErrorMessage(r.error || 'approve failed');
        else await this.store.reload();
        break;
      }
      case 'reject': {
        if (!cli?.available) {
          void vscode.window.showWarningMessage('tools/state unavailable');
          return;
        }
        const a = snap?.pendingApprovals.find((x) => x.id === msg.approvalId);
        if (!a) return;
        const ok = await vscode.window.showWarningMessage(
          `Reject ${a.id}?\n\n${JSON.stringify(a, null, 2)}`,
          { modal: true },
          'Confirm Reject',
        );
        if (ok !== 'Confirm Reject') return;
        const r = await cli.run('reject', ['--approval-id', a.id]);
        if (!r.ok) void vscode.window.showErrorMessage(r.error || 'reject failed');
        else await this.store.reload();
        break;
      }
      default:
        break;
    }
  }

  dispose(): void {
    this.sub?.dispose();
  }
}

function esc(s: string): string {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function severityRank(s?: string): number {
  switch ((s || '').toUpperCase()) {
    case 'CRITICAL':
      return 0;
    case 'HIGH':
      return 1;
    case 'MEDIUM':
      return 2;
    case 'LOW':
      return 3;
    default:
      return 4;
  }
}
