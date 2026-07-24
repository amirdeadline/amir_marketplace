import { execFile } from 'child_process';
import { promisify } from 'util';
import * as vscode from 'vscode';
import type { StateCli } from './stateCli';
import type { TerminalRegistry } from './terminals';

const execFileAsync = promisify(execFile);

export type HostKind = 'claude' | 'cursor' | 'codex';

export interface HostAvailability {
  claude: boolean;
  cursor: boolean;
  codex: boolean;
}

export class HostCli {
  private availability: HostAvailability = { claude: false, cursor: false, codex: false };

  constructor(
    private readonly terminals: TerminalRegistry,
    private readonly stateCli: () => StateCli | undefined,
  ) {}

  get hosts(): HostAvailability {
    return this.availability;
  }

  async detect(): Promise<HostAvailability> {
    const cfg = vscode.workspace.getConfiguration('amir');
    const checks: [HostKind, string][] = [
      ['claude', cfg.get<string>('hostCli.claude.binary') || 'claude'],
      ['cursor', cfg.get<string>('hostCli.cursor.binary') || 'cursor-agent'],
      ['codex', cfg.get<string>('hostCli.codex.binary') || 'codex'],
    ];
    const next: HostAvailability = { claude: false, cursor: false, codex: false };
    await Promise.all(
      checks.map(async ([kind, bin]) => {
        next[kind] = await this.which(bin);
      }),
    );
    this.availability = next;
    return next;
  }

  private async which(bin: string): Promise<boolean> {
    try {
      if (process.platform === 'win32') {
        await execFileAsync('where', [bin], { windowsHide: true });
      } else {
        await execFileAsync('which', [bin]);
      }
      return true;
    } catch {
      return false;
    }
  }

  defaultHost(): HostKind {
    const d = vscode.workspace.getConfiguration('amir').get<string>('defaultHost') as HostKind;
    return d || 'claude';
  }

  isCursorHost(): boolean {
    const name = (vscode.env.appName || '').toLowerCase();
    return name.includes('cursor');
  }

  buildLaunchCommand(promptPath: string, host?: HostKind): string | undefined {
    const kind = host || this.defaultHost();
    if (!this.availability[kind]) return undefined;
    const cfg = vscode.workspace.getConfiguration('amir');
    const binary = cfg.get<string>(`hostCli.${kind}.binary`) || kind;
    const tmpl = cfg.get<string>(`hostCli.${kind}.argsTemplate`) || '';
    if (tmpl.trim()) {
      const args = tmpl.replace(/\{promptPath\}/g, quote(promptPath));
      return `${quote(binary)} ${args}`.trim();
    }
    // Default: send a readable instruction; user can customize argsTemplate
    return `${quote(binary)} ${quote(promptPath)}`;
  }

  async startAgent(agentId: string, projectRoot: string): Promise<void> {
    const cli = this.stateCli();
    if (!cli?.available) {
      void vscode.window.showErrorMessage('amir tools/state unavailable — cannot generate prompt');
      return;
    }
    const gen = await cli.run('generate-prompt', ['--agent', agentId]);
    if (!gen.ok) {
      void vscode.window.showErrorMessage(`generate-prompt failed: ${gen.error}`);
      return;
    }
    const data = gen.data as { promptPath?: string };
    const promptPath = data?.promptPath || '';
    const launch = this.buildLaunchCommand(promptPath);
    this.terminals.focus(agentId, projectRoot);
    if (!launch) {
      this.terminals.send(
        agentId,
        projectRoot,
        `# amir: prompt ready at ${promptPath} — configure amir.hostCli.* (no host binary detected)`,
        true,
      );
      void vscode.window.showWarningMessage(
        `No host CLI available for ${this.defaultHost()}. Prompt written to ${promptPath}.`,
      );
    } else {
      this.terminals.send(agentId, projectRoot, launch, true);
    }
    await cli.run('set-agent-state', ['--agent', agentId, '--to', 'active']);
  }

  async stopAgent(agentId: string, projectRoot: string): Promise<void> {
    const term = this.terminals.get(agentId);
    if (term) {
      // Graceful: send Ctrl+C equivalent (VS Code sendText with \x03)
      term.sendText('\x03', false);
    }
    const cli = this.stateCli();
    if (cli?.available) {
      await cli.run('set-agent-state', ['--agent', agentId, '--to', 'idle']);
    }
  }
}

function quote(s: string): string {
  if (!/\s/.test(s)) return s;
  if (process.platform === 'win32') {
    return `"${s.replace(/"/g, '\\"')}"`;
  }
  return `'${s.replace(/'/g, `'\\''`)}'`;
}
