import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import * as path from 'path';
import { agentWorkspaceFsPath } from '../core/paths';

describe('windows paths', () => {
  it('joins relative workspace with project root', () => {
    const root = 'E:\\PC3_Shared\\Projects\\demo';
    const p = agentWorkspaceFsPath(root, {
      id: 'dev-T001',
      workspace: 'ai/agents/dev-T001',
    });
    assert.equal(p, path.join(root, 'ai', 'agents', 'dev-T001'));
  });

  it('keeps absolute Windows workspace paths', () => {
    const abs = 'E:\\proj\\ai\\agents\\1-orchestrator';
    const p = agentWorkspaceFsPath('C:\\other', {
      id: '1-orchestrator',
      workspace: abs,
    });
    assert.equal(p, abs);
  });

  it('sanitizes nested agent ids for default folder', () => {
    const root = 'E:\\root';
    const p = agentWorkspaceFsPath(root, { id: '3-qa/sub-lint' });
    assert.equal(p, path.join(root, 'ai', 'agents', '3-qa__sub-lint'));
  });
});
