import * as path from 'path';
import * as vscode from 'vscode';
import { HostCli } from './core/hostCli';
import { resolvePluginRoot, hasStateCli } from './core/pluginRoot';
import { SchemaValidator } from './core/schemaValidator';
import { StateCli } from './core/stateCli';
import { StateStore } from './core/stateStore';
import { TerminalRegistry, agentWorkspaceFsPath } from './core/terminals';
import { runAddAgentWizard, runDeleteAgentWizard } from './views/agentWizard';
import { AgentsTreeProvider, AgentItem } from './views/agentsTree';
import { ApprovalsUi } from './views/approvalsUi';
import { ProjectViewProvider } from './views/projectView';
import { StatusBarController } from './views/statusBar';
import { TaskDetailPanel } from './views/taskDetailPanel';
import { TasksTreeProvider } from './views/tasksTree';

const SKILLS = [
  'project_create',
  'project_import',
  'project_cleanup',
  'project_status',
  'project_tasks',
  'project_cost',
  'project_watch',
  'project_doctor',
  'design',
  'design_qa',
  'design_agents',
  'build_agents',
  'plan',
  'build_goal',
  'resume_build',
  'handoff',
  'tasks_update',
  'agent_reset',
  'compact',
  'rollback',
  'milestone_retro',
  'docs_sync',
  'document_max',
  'security_scan',
  'git_setup',
  'git_commit',
  'git_push',
  'git_tree',
  'system_skills',
  'system_settings',
  'system_cleanup',
  'user_skills',
  'user_settings',
  'user_cleanup',
];

export function activate(context: vscode.ExtensionContext): void {
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  const pluginRoot = resolvePluginRoot(workspaceRoot, context.extensionPath);
  const validator = new SchemaValidator();
  validator.setPluginRoot(pluginRoot);

  const store = new StateStore(workspaceRoot, validator);
  const terminals = new TerminalRegistry(context.extensionUri);

  const getCli = (): StateCli | undefined => {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!root) return undefined;
    const pr = resolvePluginRoot(root, context.extensionPath);
    validator.setPluginRoot(pr);
    if (!hasStateCli(pr)) return undefined;
    return new StateCli(pr, root);
  };

  const hostCli = new HostCli(terminals, getCli);
  void hostCli.detect().then((hosts) => {
    const usable = Object.entries(hosts)
      .filter(([, ok]) => ok)
      .map(([k]) => k);
    if (usable.length === 0) {
      console.warn('[amir] No host CLIs detected (claude/cursor-agent/codex)');
    }
  });

  const runSkill = (skill: string): void => {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!root) {
      void vscode.window.showWarningMessage('Open a workspace folder first');
      return;
    }
    terminals.getOrchestrator(root);
    terminals.send('1-orchestrator', root, `/${skill}`, true);
  };

  const projectProvider = new ProjectViewProvider(
    context.extensionUri,
    store,
    getCli,
    terminals,
    runSkill,
  );
  const agentsProvider = new AgentsTreeProvider(store);
  const tasksProvider = new TasksTreeProvider(store);

  context.subscriptions.push(
    store,
    terminals,
    projectProvider,
    agentsProvider,
    tasksProvider,
    new StatusBarController(store),
    new ApprovalsUi(store, getCli),
    vscode.window.registerWebviewViewProvider(ProjectViewProvider.viewType, projectProvider),
    vscode.window.createTreeView('amir.agents', {
      treeDataProvider: agentsProvider,
      showCollapseAll: true,
    }),
    vscode.window.createTreeView('amir.tasks', {
      treeDataProvider: tasksProvider,
      showCollapseAll: true,
    }),
  );

  store.startWatching();

  // Refresh est. cost periodically via tools/cost.js (markdown report)
  const refreshCost = async (): Promise<void> => {
    const cli = getCli();
    const snap = store.current;
    if (!cli?.available || !snap?.isAmirProject) return;
    const r = await cli.runTool('cost.js');
    if (!r.ok) return;
    const m = r.stdout.match(/USD \(est\)[\s\S]*?\|[^|]*\|[^|]*\|\s*\$([0-9.]+)\s*\|/);
    if (m) {
      snap.estCostUsd = Number(m[1]);
    }
  };
  void refreshCost();
  const costTimer = setInterval(() => {
    void refreshCost();
  }, 60_000);
  context.subscriptions.push({ dispose: () => clearInterval(costTimer) });

  const regs = [
    vscode.commands.registerCommand('amir.focusProject', () =>
      vscode.commands.executeCommand('amir.project.focus'),
    ),
    vscode.commands.registerCommand('amir.focusAgents', () =>
      vscode.commands.executeCommand('amir.agents.focus'),
    ),
    vscode.commands.registerCommand('amir.focusTasks', () =>
      vscode.commands.executeCommand('amir.tasks.focus'),
    ),
    vscode.commands.registerCommand('amir.refresh', () => store.reload()),
    vscode.commands.registerCommand('amir.focusAgentTerminal', (agentId: string) => {
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!root || !agentId) return;
      terminals.focus(agentId, root);
    }),
    vscode.commands.registerCommand('amir.startAgent', async (item?: AgentItem) => {
      const id = item?.agent.id;
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!id || !root) return;
      await hostCli.startAgent(id, root);
      await store.reload();
    }),
    vscode.commands.registerCommand('amir.stopAgent', async (item?: AgentItem) => {
      const id = item?.agent.id;
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!id || !root) return;
      await hostCli.stopAgent(id, root);
      await store.reload();
    }),
    vscode.commands.registerCommand('amir.resetAgent', async (item?: AgentItem) => {
      const id = item?.agent.id;
      if (!id) return;
      const ok = await vscode.window.showWarningMessage(
        `Reset agent ${id}? Workspace will be archived.`,
        { modal: true },
        'Reset',
      );
      if (ok !== 'Reset') return;
      const cli = getCli();
      if (!cli?.available) {
        void vscode.window.showWarningMessage('tools/state unavailable');
        return;
      }
      const r = await cli.run('reset-agent', ['--agent', id]);
      if (!r.ok) void vscode.window.showErrorMessage(r.error || 'reset failed');
      else await store.reload();
    }),
    vscode.commands.registerCommand('amir.openAgentWorkspace', async (item?: AgentItem) => {
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!item?.agent || !root) return;
      const p = agentWorkspaceFsPath(root, item.agent);
      await vscode.commands.executeCommand('revealFileInOS', vscode.Uri.file(p));
    }),
    vscode.commands.registerCommand('amir.openAgentNotes', async (item?: AgentItem) => {
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!item?.agent || !root) return;
      const p = path.join(agentWorkspaceFsPath(root, item.agent), 'notes.md');
      await vscode.window.showTextDocument(vscode.Uri.file(p));
    }),
    vscode.commands.registerCommand('amir.viewLastActivity', async (item?: AgentItem) => {
      const id = item?.agent.id;
      if (!id || !store.current) return;
      const evt = store.current.activity.find((a) => a.agent_id === id);
      // Prefer most recent - activity is last 30 chronological
      const all = [...store.current.activity].reverse().find((a) => a.agent_id === id);
      const e = all || evt;
      void vscode.window.showInformationMessage(
        e ? JSON.stringify(e, null, 2) : `No recent activity for ${id}`,
        { modal: true },
      );
    }),
    vscode.commands.registerCommand('amir.addAgent', () => runAddAgentWizard(getCli(), store)),
    vscode.commands.registerCommand('amir.deleteAgent', (item?: AgentItem) => {
      if (!item?.agent) return;
      return runDeleteAgentWizard(item.agent.id, getCli(), store);
    }),
    vscode.commands.registerCommand('amir.startAll', async () => {
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!root || !store.current) return;
      const stagger =
        vscode.workspace.getConfiguration('amir').get<number>('startAll.staggerMs') ?? 2000;
      const agents = store.current.agents
        .filter((a) => !a.parent && !a.id.includes('/sub-'))
        .sort((a, b) => a.id.localeCompare(b.id));
      const ordered = [
        ...agents.filter((a) => a.id === '1-orchestrator'),
        ...agents.filter((a) => a.id !== '1-orchestrator'),
      ];
      for (let i = 0; i < ordered.length; i += 1) {
        await hostCli.startAgent(ordered[i].id, root);
        if (i < ordered.length - 1) {
          await sleep(stagger);
        }
      }
      await store.reload();
    }),
    vscode.commands.registerCommand('amir.stopAll', async () => {
      const ok = await vscode.window.showWarningMessage(
        'Stop all agents?',
        { modal: true },
        'Stop All',
      );
      if (ok !== 'Stop All') return;
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!root || !store.current) return;
      for (const a of store.current.agents) {
        await hostCli.stopAgent(a.id, root);
      }
      await store.reload();
    }),
    vscode.commands.registerCommand('amir.openTaskDetail', (taskId: string) => {
      if (!taskId) return;
      TaskDetailPanel.show(store, getCli, taskId, context.extensionUri);
    }),
    vscode.commands.registerCommand('amir.filterTasks', async () => {
      const text = await vscode.window.showInputBox({
        prompt: 'Filter tasks by text (id/title/goal)',
      });
      if (text === undefined) return;
      const status = await vscode.window.showQuickPick(
        [
          { label: '(any status)', value: '' },
          ...['pending', 'in_progress', 'qa_failed', 'blocked', 'qa_passed', 'complete', 'cancelled'].map(
            (s) => ({ label: s, value: s }),
          ),
        ],
        { title: 'Filter by status' },
      );
      const milestone = await vscode.window.showInputBox({ prompt: 'Milestone (optional)' });
      tasksProvider.setFilter({
        text: text || undefined,
        status: status?.value || undefined,
        milestone: milestone || undefined,
      });
    }),
    vscode.commands.registerCommand('amir.createProject', () => runSkill('project_create')),
    vscode.commands.registerCommand('amir.runProjectDoctor', () => runSkill('project_doctor')),
    vscode.commands.registerCommand('amir.openDocs', async () => {
      const pr = resolvePluginRoot(
        vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
        context.extensionPath,
      );
      if (pr) {
        const readme = vscode.Uri.file(path.join(pr, 'README.md'));
        await vscode.window.showTextDocument(readme);
      } else {
        void vscode.window.showInformationMessage(
          'amir docs: install the amir plugin or set amir.pluginRoot',
        );
      }
    }),
  ];

  for (const skill of SKILLS) {
    regs.push(
      vscode.commands.registerCommand(`amir.${skill}`, () => runSkill(skill)),
    );
  }

  if (hostCli.isCursorHost()) {
    regs.push(vscode.commands.registerCommand('amir.btw', () => runSkill('btw')));
  } else {
    regs.push(
      vscode.commands.registerCommand('amir.btw', () => {
        void vscode.window.showWarningMessage(
          '**/btw** is registered only under Cursor (amir adapter rule).',
        );
      }),
    );
  }

  context.subscriptions.push(...regs);

  context.subscriptions.push(
    vscode.workspace.onDidChangeWorkspaceFolders(() => {
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      store.setWorkspaceRoot(root);
      validator.setPluginRoot(resolvePluginRoot(root, context.extensionPath));
      store.startWatching();
    }),
  );

  if (!hasStateCli(pluginRoot)) {
    void vscode.window.setStatusBarMessage(
      'amir: tools/state not found — mutation UI disabled (set amir.pluginRoot)',
      8000,
    );
  }
}

export function deactivate(): void {
  /* disposables handled by context */
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}
