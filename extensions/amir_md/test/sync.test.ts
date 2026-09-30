import { test } from 'node:test';
import assert from 'node:assert/strict';
import { EditorState } from 'prosemirror-state';
import { parseDocument, reconcile, CodecMeta } from '../src/webview/codec/document';
import { DocSync, replay } from '../src/webview/sync';
import type { WebviewToHost } from '../src/shared/messages';
import { schema } from '../src/webview/codec/schema';

const OPTS = { bulletMarker: '-', emphasisMarker: '*', strongMarker: '**' };

// A tiny stand-in for the webview: an editor state, codec meta, and a fake host.
function harness(text: string) {
  const parsed = parseDocument(text, OPTS);
  let state = EditorState.create({ doc: parsed.doc });
  let meta: CodecMeta = parsed.meta;
  let hostText = text;
  let hostVersion = 1;
  const sent: WebviewToHost[] = [];
  const notes: string[] = [];
  const sync = new DocSync({
    post: (m) => sent.push(m),
    doc: () => state.doc,
    meta: () => meta,
    load: (t) => {
      const r = reconcile(state.doc, t, OPTS);
      let from = 0;
      for (let i = 0; i < r.fromChild; i++) from += state.doc.child(i).nodeSize;
      let to = from;
      for (let i = r.fromChild; i < r.toChild; i++) to += state.doc.child(i).nodeSize;
      state = state.apply(state.tr.replaceWith(from, to, r.nodes));
      meta = r.meta;
    },
    notify: (n) => notes.push(n),
    debounceMs: 0,
  }, text, 1);
  const editParagraph = (index: number, newText: string) => {
    let pos = 0;
    for (let i = 0; i < index; i++) pos += state.doc.child(i).nodeSize;
    const node = state.doc.child(index);
    state = state.apply(state.tr.replaceWith(pos, pos + node.nodeSize, node.type.create(node.attrs, schema.text(newText))));
  };
  // host applies the last edit if versions match
  const hostHandle = () => {
    const m = sent.shift();
    if (!m || m.type !== 'edit') return;
    if (m.baseVersion !== hostVersion) {
      sync.editResult(false, hostVersion, hostText);
      return;
    }
    for (const c of m.changes) hostText = hostText.slice(0, c.start) + c.text + hostText.slice(c.end);
    hostVersion++;
    sync.editResult(true, hostVersion);
  };
  const hostExternal = (t: string) => { hostText = t; hostVersion++; };
  return {
    sync, sent, notes, editParagraph, hostHandle, hostExternal,
    get host() { return hostText; }, get hostVersion() { return hostVersion; },
    get editorText() { return sync.current(); },
  };
}

const TEXT = 'Alpha\n\nBravo\n\nCharlie\n';

test('a local edit reaches the host as one small change', () => {
  const h = harness(TEXT);
  h.editParagraph(1, 'Bravo two');
  h.sync.flush();
  assert.equal(h.sent.length, 1);
  const m = h.sent[0];
  assert.ok(m.type === 'edit');
  assert.deepEqual(m.changes, [{ start: 12, end: 12, text: ' two' }]);
  h.hostHandle();
  assert.equal(h.host, 'Alpha\n\nBravo two\n\nCharlie\n');
});

test('a rejected edit is replayed when the outside change is elsewhere', () => {
  const h = harness(TEXT);
  h.hostExternal('Alpha\n\nBravo\n\nCharlie and Delta\n');
  h.editParagraph(0, 'Alpha one');
  h.sync.flush();
  h.hostHandle(); // rejected: version moved
  assert.equal(h.editorText, 'Alpha one\n\nBravo\n\nCharlie and Delta\n');
  h.hostHandle(); // replayed edit
  assert.equal(h.host, 'Alpha one\n\nBravo\n\nCharlie and Delta\n');
  assert.equal(h.notes.length, 0);
});

test('a conflicting edit reloads from the file and tells the user', () => {
  const h = harness(TEXT);
  h.hostExternal('Alpha\n\nBravo changed outside\n\nCharlie\n');
  h.editParagraph(1, 'Bravo changed inside');
  h.sync.flush();
  h.hostHandle();
  assert.equal(h.editorText, 'Alpha\n\nBravo changed outside\n\nCharlie\n');
  assert.equal(h.notes.length, 1);
});

test('an outside change with no local edits reloads only the changed block', () => {
  const h = harness(TEXT);
  h.sync.external('Alpha\n\nBravo\n\nCharlie!\n', 2);
  assert.equal(h.editorText, 'Alpha\n\nBravo\n\nCharlie!\n');
  assert.equal(h.sent.length, 0);
});

test('replay shifts a later change by the earlier one', () => {
  // base "abc": ours replaces "b" with "B", theirs inserts "XX" at the start
  assert.equal(replay('XXabc', { start: 1, end: 2, text: 'B' }, { start: 0, end: 0, text: 'XX' }), 'XXaBc');
  // ours before theirs: no shift
  assert.equal(replay('abcYY', { start: 0, end: 1, text: 'A' }, { start: 3, end: 3, text: 'YY' }), 'AbcYY');
});
