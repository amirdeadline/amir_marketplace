'use strict';

const assert = require('node:assert/strict');
const { describe, it } = require('node:test');
const path = require('path');
const { appendActivity, heartbeatCheck, STALE_MS } = require('../activity');
const { makeTempProject, writeAgents, appendActivityLine } = require('../lib/test-fixture');
const { readJson } = require('../lib/paths');

describe('activity heartbeat', () => {
  it('append updates agent last_heartbeat_ts', () => {
    const root = makeTempProject();
    writeAgents(root, [
      { id: 'dev-T001', role: 'worker', state: 'active', last_heartbeat_ts: null, task_id: 'T001' },
    ]);

    const ts = '2026-07-14T12:00:00.000Z';
    appendActivity(root, {
      timestamp: ts,
      agent_id: 'dev-T001',
      action: 'fix',
      result: 'ok',
      task_id: 'T001',
      tokens_in: null,
      tokens_out: null,
      model: null,
      usd: null,
    });

    const agents = readJson(path.join(root, 'ai', 'state', 'agents.json'));
    assert.equal(agents.agents[0].last_heartbeat_ts, ts);
  });

  it('heartbeat-check marks stale active agents', () => {
    const root = makeTempProject();
    const oldTs = new Date(Date.now() - STALE_MS - 1000).toISOString();
    writeAgents(root, [
      { id: 'dev-T001', role: 'worker', state: 'active', last_heartbeat_ts: oldTs, task_id: 'T001' },
      { id: 'qa-T001', role: 'verifier', state: 'active', last_heartbeat_ts: oldTs, task_id: 'T001' },
    ]);

    const stale = heartbeatCheck(root, Date.now());
    assert.deepEqual(stale.sort(), ['dev-T001', 'qa-T001']);

    const agents = readJson(path.join(root, 'ai', 'state', 'agents.json'));
    assert.equal(agents.agents[0].state, 'stale');
    assert.equal(agents.agents[1].state, 'stale');
  });

  it('heartbeat-check uses recent activity as alive signal', () => {
    const root = makeTempProject();
    const oldTs = new Date(Date.now() - STALE_MS - 5000).toISOString();
    const recentTs = new Date(Date.now() - 1000).toISOString();

    writeAgents(root, [
      { id: 'dev-T001', role: 'worker', state: 'active', last_heartbeat_ts: oldTs, task_id: 'T001' },
    ]);

    appendActivityLine(root, {
      timestamp: recentTs,
      agent_id: 'dev-T001',
      action: 'heartbeat',
      result: 'alive',
      task_id: 'T001',
      tokens_in: null,
      tokens_out: null,
      model: null,
      usd: null,
    });

    const stale = heartbeatCheck(root, Date.now());
    assert.deepEqual(stale, []);
  });
});
