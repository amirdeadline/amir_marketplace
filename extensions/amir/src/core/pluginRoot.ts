import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

/**
 * Resolve the amir plugin root containing tools/ and schemas/.
 * Order: setting amir.pluginRoot → workspace tools/ → marketplace pack sibling → env.
 */
export function resolvePluginRoot(
  workspaceRoot: string | undefined,
  extensionPath?: string,
): string | undefined {
  const configured = vscode.workspace.getConfiguration('amir').get<string>('pluginRoot')?.trim();
  if (configured && fs.existsSync(path.join(configured, 'tools', 'state.js'))) {
    return configured;
  }

  const env = process.env.AMIR_PLUGIN_ROOT?.trim();
  if (env && fs.existsSync(path.join(env, 'tools', 'state.js'))) {
    return env;
  }

  if (workspaceRoot) {
    const inWorkspace = path.join(workspaceRoot, 'tools', 'state.js');
    if (fs.existsSync(inWorkspace)) {
      return workspaceRoot;
    }
  }

  // extensions/amir → marketplace/plugins/amir
  if (extensionPath) {
    const packed = path.resolve(extensionPath, '..', '..', 'plugins', 'amir');
    if (fs.existsSync(path.join(packed, 'tools', 'state.js'))) {
      return packed;
    }
    // extensions/amir → ../../Amir (dev layout)
    const source = path.resolve(extensionPath, '..', '..', '..', 'Amir');
    if (fs.existsSync(path.join(source, 'tools', 'state.js'))) {
      return source;
    }
  }

  return undefined;
}

export function stateCliPath(pluginRoot: string): string {
  return path.join(pluginRoot, 'tools', 'state.js');
}

export function schemasDir(pluginRoot: string): string {
  return path.join(pluginRoot, 'schemas');
}

export function hasStateCli(pluginRoot: string | undefined): boolean {
  return !!pluginRoot && fs.existsSync(stateCliPath(pluginRoot));
}
