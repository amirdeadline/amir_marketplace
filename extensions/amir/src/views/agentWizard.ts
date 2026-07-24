import * as vscode from 'vscode';
import type { StateCli } from '../core/stateCli';
import type { StateStore } from '../core/stateStore';

export async function runAddAgentWizard(
  cli: StateCli | undefined,
  store: StateStore,
): Promise<void> {
  if (!cli?.available) {
    void vscode.window.showWarningMessage(
      'amir tools/state missing — Add Agent disabled. Set amir.pluginRoot or install the amir plugin.',
    );
    return;
  }

  const role = await vscode.window.showInputBox({
    title: 'Add Agent — Role',
    prompt: 'Role name (e.g. researcher, worker, verifier)',
    validateInput: (v) => (v.trim() ? undefined : 'Required'),
  });
  if (role === undefined) return;

  const agents = store.current?.agents || [];
  const parentPick = await vscode.window.showQuickPick(
    [
      { label: '(none — top-level)', id: '' },
      ...agents.map((a) => ({ label: a.id, id: a.id })),
    ],
    { title: 'Add Agent — Parent' },
  );
  if (!parentPick) return;

  const responsibility = await vscode.window.showInputBox({
    title: 'Add Agent — Responsibility',
    prompt: 'What should this agent do?',
    validateInput: (v) => (v.trim() ? undefined : 'Required'),
  });
  if (responsibility === undefined) return;

  const modelPick = await vscode.window.showQuickPick(
    [
      { label: 'premium', description: 'Higher capability' },
      { label: 'cheap', description: 'Cost-efficient' },
    ],
    { title: 'Add Agent — Model class' },
  );
  if (!modelPick) return;

  const name = await vscode.window.showInputBox({
    title: 'Add Agent — Name (optional id)',
    prompt: 'Leave empty to auto-assign from role',
  });
  if (name === undefined) return;

  const preview = [
    `Role: ${role}`,
    `Parent: ${parentPick.id || '(none)'}`,
    `Responsibility: ${responsibility}`,
    `Model: ${modelPick.label}`,
    `Name: ${name || '(auto)'}`,
  ].join('\n');

  const confirm = await vscode.window.showInformationMessage(
    `Create agent?\n\n${preview}`,
    { modal: true },
    'Confirm',
  );
  if (confirm !== 'Confirm') return;

  const args = ['--role', role, '--responsibility', responsibility, '--model', modelPick.label];
  if (parentPick.id) args.push('--parent', parentPick.id);
  if (name.trim()) args.push('--name', name.trim());

  const result = await cli.run('add-agent', args);
  if (!result.ok) {
    void vscode.window.showErrorMessage(`add-agent failed: ${result.error}`);
    return;
  }
  void vscode.window.showInformationMessage(`Agent created: ${JSON.stringify(result.data)}`);
  await store.reload();
}

export async function runDeleteAgentWizard(
  agentId: string,
  cli: StateCli | undefined,
  store: StateStore,
): Promise<void> {
  if (!cli?.available) {
    void vscode.window.showWarningMessage('amir tools/state missing — Delete Agent disabled.');
    return;
  }
  const agent = store.current?.agents.find((a) => a.id === agentId);
  if (!agent) {
    void vscode.window.showErrorMessage(`Agent not found: ${agentId}`);
    return;
  }
  if (agent.state === 'active') {
    void vscode.window.showWarningMessage('Stop the agent before deleting.');
    return;
  }

  const typed = await vscode.window.showInputBox({
    title: 'Delete Agent',
    prompt: `Type the agent id to confirm archive (never hard-delete): ${agentId}`,
    validateInput: (v) => (v === agentId ? undefined : `Must type exactly: ${agentId}`),
  });
  if (typed === undefined) return;

  const result = await cli.run('delete-agent', [
    '--agent',
    agentId,
    '--confirm-name',
    typed,
  ]);
  if (!result.ok) {
    void vscode.window.showErrorMessage(`delete-agent failed: ${result.error}`);
    return;
  }
  void vscode.window.showInformationMessage(`Archived ${agentId}`);
  await store.reload();
}
