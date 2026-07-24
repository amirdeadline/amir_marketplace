import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Grep gate: extension src must not write ai/state JSON directly.
 */
describe('single-writer guard', () => {
  it('has no direct write patterns to ai/state in src', () => {
    const srcRoot = path.join(__dirname, '..');
    const offenders: string[] = [];
    const walk = (dir: string): void => {
      for (const name of fs.readdirSync(dir)) {
        const full = path.join(dir, name);
        const st = fs.statSync(full);
        if (st.isDirectory()) {
          if (name === 'test') continue;
          walk(full);
          continue;
        }
        if (!/\.(ts|js)$/.test(name)) continue;
        const body = fs.readFileSync(full, 'utf8');
        if (/writeFileSync\([^)]*ai[/\\]state/.test(body)) {
          offenders.push(full);
        }
        if (/writeJson\([^)]*state/.test(body)) {
          offenders.push(full);
        }
        if (/ai\/state\/.*\.json['"].*write/i.test(body)) {
          offenders.push(full);
        }
      }
    };
    walk(srcRoot);
    assert.deepEqual(offenders, []);
  });
});
