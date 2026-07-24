import * as path from 'path';

export function agentWorkspaceFsPath(
  projectRoot: string,
  agent: { id: string; workspace?: string },
): string {
  if (agent.workspace) {
    if (path.isAbsolute(agent.workspace)) return agent.workspace;
    return path.join(projectRoot, ...agent.workspace.split(/[/\\]/));
  }
  const safe = agent.id.replace(/\//g, '__');
  return path.join(projectRoot, 'ai', 'agents', safe);
}
