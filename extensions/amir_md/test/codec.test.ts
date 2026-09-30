import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { parseDocument, serializeDocument, computeChange } from '../src/webview/codec/document';
import { schema } from '../src/webview/codec/schema';
import type { SerializeOptions } from '../src/webview/codec/serialize';

const OPTS: SerializeOptions = { bulletMarker: '-', emphasisMarker: '*', strongMarker: '**' };
const FIX = join(__dirname, 'fixtures');

function roundTrip(text: string): string {
  const { doc, meta } = parseDocument(text, OPTS);
  return serializeDocument(doc, meta);
}

test('mixed fixture round-trips byte for byte', () => {
  const text = readFileSync(join(FIX, 'mixed.md'), 'utf8');
  assert.equal(roundTrip(text), text);
});

test('CRLF text round-trips byte for byte', () => {
  const text = readFileSync(join(FIX, 'mixed.md'), 'utf8').replace(/\r?\n/g, '\r\n');
  assert.equal(roundTrip(text), text);
});

test('edge inputs round-trip', () => {
  for (const text of ['', '\n', '\n\n\n', 'x', '# H', '# H\n', 'a\n\n\n\nb\n\n', '  lead\n', '---\nfront: only\n---\n']) {
    assert.equal(roundTrip(text), text, JSON.stringify(text));
  }
});

test('most blocks are editable, not source blocks', () => {
  const text = readFileSync(join(FIX, 'mixed.md'), 'utf8');
  const { doc, stats } = parseDocument(text, OPTS);
  const kinds = new Set<string>();
  doc.forEach((n) => kinds.add(n.type.name));
  for (const k of ['title', 'subtitle', 'heading', 'paragraph', 'bullet_list', 'ordered_list', 'blockquote', 'code_block', 'horizontal_rule', 'table']) {
    assert.ok(kinds.has(k), `expected a ${k}`);
  }
  // front matter, div, review comment, footnote def + ref def, HTML comment, footnote paragraph
  assert.ok(stats.sourceBlocks <= 8, `too many source blocks: ${stats.sourceBlocks}`);
});

test('editing one paragraph changes only that paragraph', () => {
  const text = readFileSync(join(FIX, 'mixed.md'), 'utf8');
  const { doc, meta } = parseDocument(text, OPTS);
  let target = -1;
  doc.forEach((n, _o, i) => {
    if (target < 0 && n.type.name === 'heading' && n.textContent === 'Lists') target = i;
  });
  assert.ok(target >= 0);
  const old = doc.child(target);
  const edited = old.type.create(old.attrs, schema.text('Lists and tasks'));
  const children: typeof old[] = [];
  doc.forEach((n, _o, i) => children.push(i === target ? edited : n));
  const next = doc.copy(doc.content.replaceChild(target, edited));
  const out = serializeDocument(next, meta);
  const change = computeChange(text, out);
  assert.ok(change);
  assert.equal(text.slice(change!.start, change!.end), '');
  assert.equal(change!.text, ' and tasks');
});

test('computeChange does not split CRLF', () => {
  const c = computeChange('a\r\nb', 'a\r\r\nb');
  assert.ok(c);
  const applied = 'a\r\nb'.slice(0, c!.start) + c!.text + 'a\r\nb'.slice(c!.end);
  assert.equal(applied, 'a\r\r\nb');
});

const MA_GUIDE = 'E:/PC3_Shared/Palo/COE/PRISMA_SDWAN_SnO/.ai/ma/claude/docs/Prisma SD-WAN Maturity Assessment.md';

test('MA guide round-trips byte for byte and opens fast', { skip: !existsSync(MA_GUIDE) }, () => {
  const text = readFileSync(MA_GUIDE, 'utf8');
  const t0 = performance.now();
  const { doc, meta, stats } = parseDocument(text, OPTS);
  const ms = performance.now() - t0;
  assert.equal(serializeDocument(doc, meta), text);
  console.log(`MA guide: ${stats.blocks} blocks, ${stats.sourceBlocks} source blocks, parsed in ${ms.toFixed(0)} ms`);
});
