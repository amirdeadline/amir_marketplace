import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { ActivityTail, isStale } from '../core/activityTail';

describe('activityTail', () => {
  it('computes stale heartbeats', () => {
    const now = Date.parse('2026-07-14T12:00:00.000Z');
    assert.equal(isStale(undefined, 5, now), true);
    assert.equal(isStale(now - 4 * 60 * 1000, 5, now), false);
    assert.equal(isStale(now - 6 * 60 * 1000, 5, now), true);
  });

  it('tails incrementally by byte offset (no full re-read)', () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'amir-tail-'));
    const file = path.join(dir, 'activity.jsonl');
    fs.writeFileSync(file, '');

    const tail = new ActivityTail(file, 100);
    assert.equal(tail.getOffset(), 0);

    const line1 =
      JSON.stringify({
        timestamp: '2026-07-14T10:00:00.000Z',
        agent_id: '1-orchestrator',
        action: 'heartbeat',
        result: 'ok',
      }) + '\n';
    fs.appendFileSync(file, line1);
    const first = tail.poll();
    assert.equal(first.length, 1);
    const afterFirst = tail.getOffset();
    assert.equal(afterFirst, Buffer.byteLength(line1));

    // Append more without resetting offset
    const line2 =
      JSON.stringify({
        timestamp: '2026-07-14T10:01:00.000Z',
        agent_id: 'dev-T001',
        action: 'message',
        result: 'working',
      }) + '\n';
    fs.appendFileSync(file, line2);
    const second = tail.poll();
    assert.equal(second.length, 1);
    assert.equal(second[0].agent_id, 'dev-T001');
    assert.equal(tail.getOffset(), afterFirst + Buffer.byteLength(line2));

    // Empty poll at EOF
    assert.equal(tail.poll().length, 0);
    assert.equal(tail.getOffset(), afterFirst + Buffer.byteLength(line2));
  });

  it('handles large JSONL without resetting offset (50MB smoke)', () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'amir-tail-big-'));
    const file = path.join(dir, 'activity.jsonl');
    const line =
      JSON.stringify({
        timestamp: '2026-07-14T09:00:00.000Z',
        agent_id: 'filler',
        action: 'message',
        result: 'x'.repeat(200),
      }) + '\n';
    const targetBytes = 50 * 1024 * 1024;
    const fd = fs.openSync(file, 'w');
    let written = 0;
    const buf = Buffer.from(line);
    while (written < targetBytes) {
      fs.writeSync(fd, buf);
      written += buf.length;
    }
    fs.closeSync(fd);

    const tail = new ActivityTail(file, 50);
    const added = tail.poll();
    assert.ok(added.length > 0);
    const mid = tail.getOffset();
    assert.ok(mid >= targetBytes);

    const extra =
      JSON.stringify({
        timestamp: '2026-07-14T11:00:00.000Z',
        agent_id: 'marker',
        action: 'heartbeat',
        result: 'tail-ok',
      }) + '\n';
    fs.appendFileSync(file, extra);
    const more = tail.poll();
    assert.equal(more.length, 1);
    assert.equal(more[0].agent_id, 'marker');
    assert.equal(tail.getOffset(), mid + Buffer.byteLength(extra));
  });
});
