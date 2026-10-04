import { test } from 'node:test';
import assert from 'node:assert/strict';
import { scanHeadings } from '../src/shared/headingsScan';

test('scanHeadings skips fenced code', () => {
  const md = '# Real\n\n```\n# Not a heading\n```\n\n## Also real\n';
  const h = scanHeadings(md);
  assert.deepEqual(h.map((x) => x.text), ['Real', 'Also real']);
});

test('scanHeadings stable keys', () => {
  const md = '# A\n\n# A\n';
  const h = scanHeadings(md);
  assert.equal(h[0].key, '1|A|0');
  assert.equal(h[1].key, '1|A|1');
});
