import { spawn } from 'child_process';
import * as path from 'path';
import { stateCliPath } from './pluginRoot';

export interface StateCliResult {
  ok: boolean;
  data?: unknown;
  error?: string;
  stdout: string;
  stderr: string;
  code: number | null;
}

export class StateCli {
  constructor(
    private readonly pluginRoot: string | undefined,
    private readonly projectRoot: string,
  ) {}

  get available(): boolean {
    return !!this.pluginRoot;
  }

  async run(command: string, args: string[] = [], by = 'human'): Promise<StateCliResult> {
    if (!this.pluginRoot) {
      return {
        ok: false,
        error: 'amir tools/state not found — set amir.pluginRoot or install the amir plugin',
        stdout: '',
        stderr: '',
        code: null,
      };
    }

    const script = stateCliPath(this.pluginRoot);
    const fullArgs = [script, this.projectRoot, command, ...args];
    if (!args.includes('--by') && by) {
      fullArgs.push('--by', by);
    }

    return new Promise((resolve) => {
      const child = spawn(process.execPath, fullArgs, {
        cwd: this.projectRoot,
        env: { ...process.env, AMIR_AGENT: by },
        windowsHide: true,
      });
      let stdout = '';
      let stderr = '';
      child.stdout.on('data', (d) => {
        stdout += String(d);
      });
      child.stderr.on('data', (d) => {
        stderr += String(d);
      });
      child.on('error', (err) => {
        resolve({
          ok: false,
          error: err.message,
          stdout,
          stderr,
          code: null,
        });
      });
      child.on('close', (code) => {
        if (code === 0) {
          let data: unknown = stdout;
          try {
            data = JSON.parse(stdout);
          } catch {
            // keep raw
          }
          resolve({ ok: true, data, stdout, stderr, code });
        } else {
          resolve({
            ok: false,
            error: stderr.trim() || stdout.trim() || `exit ${code}`,
            stdout,
            stderr,
            code,
          });
        }
      });
    });
  }

  async runTool(toolFile: string, args: string[] = []): Promise<StateCliResult> {
    if (!this.pluginRoot) {
      return {
        ok: false,
        error: 'amir plugin root missing',
        stdout: '',
        stderr: '',
        code: null,
      };
    }
    const script = path.join(this.pluginRoot, 'tools', toolFile);
    return new Promise((resolve) => {
      const child = spawn(process.execPath, [script, this.projectRoot, ...args], {
        cwd: this.projectRoot,
        windowsHide: true,
      });
      let stdout = '';
      let stderr = '';
      child.stdout.on('data', (d) => {
        stdout += String(d);
      });
      child.stderr.on('data', (d) => {
        stderr += String(d);
      });
      child.on('close', (code) => {
        if (code === 0) {
          let data: unknown = stdout;
          try {
            data = JSON.parse(stdout);
          } catch {
            /* raw */
          }
          resolve({ ok: true, data, stdout, stderr, code });
        } else {
          resolve({
            ok: false,
            error: stderr.trim() || stdout.trim() || `exit ${code}`,
            stdout,
            stderr,
            code,
          });
        }
      });
    });
  }
}
