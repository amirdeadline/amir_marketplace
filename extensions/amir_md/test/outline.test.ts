import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseDocument } from '../src/webview/codec/document';
import {
  applyLevelAction, buildNavTree, carryOpen, collectHeadings, filterEntries, foldRange, foldsHiding,
  hiddenChildren, initialOpen, isVisible,
} from '../src/webview/outline';
import { slugger } from '../src/shared/slug';

const OPTS = { bulletMarker: '-', emphasisMarker: '*', strongMarker: '**' };
const doc = (md: string) => parseDocument(md, OPTS).doc;

// SRS Appendix B
const B = '# A\n\ntext a\n\n## A1\n\ntext a1\n\n### A1a\n\ntext a1a\n\n## A2\n\ntext a2\n\n# B\n\ntext b\n';

function texts(d: ReturnType<typeof doc>, from: number, to: number): string[] {
  const out: string[] = [];
  for (let i = from; i < to; i++) out.push(d.child(i).textContent);
  return out;
}

test('fold ranges follow Appendix B', () => {
  const d = doc(B);
  const idx = (t: string) => { let k = -1; d.forEach((n, _o, i) => { if (n.textContent === t) k = i; }); return k; };
  const r = (t: string) => { const x = foldRange(d, idx(t)); return texts(d, x.from, x.to); };
  assert.deepEqual(r('A'), ['text a', 'A1', 'text a1', 'A1a', 'text a1a', 'A2', 'text a2']);
  assert.deepEqual(r('A1'), ['text a1', 'A1a', 'text a1a']);
  assert.deepEqual(r('A1a'), ['text a1a']);
  assert.deepEqual(r('A2'), ['text a2']);
  assert.deepEqual(r('B'), ['text b']);
});

test('nested folds keep their own state (FR-FOLD-05)', () => {
  const d = doc(B);
  // fold A1 (index 2) and A (index 0), then unfold A
  const both = hiddenChildren(d, new Set([0, 2]));
  assert.deepEqual(both.map((h, i) => (h ? i : -1)).filter((i) => i >= 0), [1, 2, 3, 4, 5, 6, 7]);
  const inner = hiddenChildren(d, new Set([2]));
  assert.deepEqual(inner.map((h, i) => (h ? i : -1)).filter((i) => i >= 0), [3, 4, 5]);
  assert.deepEqual(foldsHiding(d, new Set([0, 2]), 4).sort(), [0, 2]);
});

// SRS Appendix A: 1 > 1.1 > 1.1.1, 1.2 > 1.2.1 ; 2 > 2.1 > 2.1.1
const A = '# 1\n## 1.1\n### 1.1.1\n## 1.2\n### 1.2.1\n# 2\n## 2.1\n### 2.1.1\n';

test('nav tree nests by level and skips levels to the nearest shallower heading', () => {
  const e = buildNavTree(collectHeadings(doc('# a\n#### b\n## c\n')));
  assert.equal(e[1].parent, e[0]);
  assert.equal(e[2].parent, e[0]);
});

test('level list actions follow Appendix A', () => {
  const e = buildNavTree(collectHeadings(doc(A)));
  const key = (t: string) => e.find((x) => x.text === t)!.key;
  let open = initialOpen(e, 2);
  assert.equal(open[key('1')], true);
  assert.equal(open[key('1.1')], true);

  open = applyLevelAction(e, open, 'all', 'collapse');
  assert.ok(Object.values(open).every((v) => v === false));

  open = applyLevelAction(e, open, '2', 'expand');
  for (const t of ['1', '2', '1.1', '1.2', '2.1']) assert.equal(open[key(t)], true, t);
  assert.ok(isVisible(e.find((x) => x.text === '2.1.1')!, open));

  open = applyLevelAction(e, open, '1', 'collapse');
  assert.equal(open[key('1')], false);
  assert.equal(open[key('1.1')], true, 'other levels keep their state');

  open = applyLevelAction(e, open, 'all', 'expand');
  assert.ok(Object.values(open).every((v) => v === true));
});

test('expansion state survives a rebuild by key', () => {
  const e1 = buildNavTree(collectHeadings(doc(A)));
  const open = applyLevelAction(e1, initialOpen(e1, 1), 'all', 'collapse');
  const e2 = buildNavTree(collectHeadings(doc(A + '# 3\n## 3.1\n')));
  const carried = carryOpen(e2, open, 1);
  assert.equal(carried[e2.find((x) => x.text === '1')!.key], false);
  assert.equal(carried[e2.find((x) => x.text === '3')!.key], true, 'new entry gets the default');
});

test('filter shows matches and their ancestors', () => {
  const e = buildNavTree(collectHeadings(doc(A)));
  const { shown, matches } = filterEntries(e, '2.1.');
  assert.equal(matches, 1);
  assert.deepEqual([...shown].map((x) => x.text).sort(), ['2', '2.1', '2.1.1']);
  assert.equal(filterEntries(e, 'NOPE').matches, 0);
});

test('heading keys count repeated headings', () => {
  const h = collectHeadings(doc('## Notes\n\n## Notes\n\n### Notes\n'));
  assert.deepEqual(h.map((x) => x.key), ['2|Notes|0', '2|Notes|1', '3|Notes|0']);
});

test('GitHub slugs', () => {
  const s = slugger();
  assert.equal(s('1.1.1. IdP federation: SCM'), '111-idp-federation-scm');
  assert.equal(s('Notes'), 'notes');
  assert.equal(s('Notes'), 'notes-1');
});
