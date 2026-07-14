'use strict';

const assert = require('node:assert/strict');
const { describe, it } = require('node:test');
const fs = require('fs');
const path = require('path');
const { aggregateCosts, estimateTokensFromChars } = require('../cost');
const { makeTempProject } = require('../lib/test-fixture');

describe('cost aggregation', () => {
  it('estimateTokensFromChars uses 4 chars/token heuristic', () => {
    assert.equal(estimateTokensFromChars(40), 10);
    assert.equal(estimateTokensFromChars(41), 11);
  });

  it('aggregates fixture activity by task, agent, and model', () => {
    const root = makeTempProject();
    const fixture = fs.readFileSync(
      path.join(__dirname, 'fixtures', 'sample-activity.jsonl'),
      'utf8',
    );
    fs.writeFileSync(path.join(root, 'ai', 'state', 'activity.jsonl'), fixture, 'utf8');

    const agg = aggregateCosts(root);

    assert.ok(agg.byTask.get('T001').events >= 3);
    assert.ok(agg.byAgent.get('dev-T001').tokensIn > 0);
    assert.ok(agg.byModel.get('claude-sonnet'));
    assert.ok(agg.projectTotal.usd > 0);

    const rising = agg.risingTasks.find((r) => r.taskId === 'T001');
    assert.ok(rising, 'expected rising fix-cycle cost for T001');
    assert.equal(rising.usdSeries.length, 2);
    assert.ok(rising.usdSeries[1] > rising.usdSeries[0]);
  });
});
