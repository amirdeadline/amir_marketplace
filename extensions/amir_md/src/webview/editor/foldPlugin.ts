// Word-style section folding in the content pane (SRS FR-FOLD).
//
// Fold state lives in plugin state only, never in the document, so folding adds no
// undo step and never changes the file (FR-FOLD-07). Hidden blocks get
// hidden="until-found": they take no space, but the find widget can still match
// text in them, and the browser's `beforematch` event then opens the fold (FR-FOLD-09).

import { EditorState, Plugin, PluginKey, Selection, TextSelection, Transaction } from 'prosemirror-state';
import { Decoration, DecorationSet, EditorView } from 'prosemirror-view';
import type { Node } from 'prosemirror-model';
import { schema } from '../codec/schema';
import { collectHeadings, foldRange, foldsHiding, hiddenChildren } from '../outline';

interface FoldState {
  /** Positions of folded top-level headings. */
  folded: ReadonlySet<number>;
  hidden: boolean[];
  decos: DecorationSet;
}

type FoldMeta =
  | { kind: 'toggle'; pos: number }
  | { kind: 'set'; positions: number[]; folded: boolean }
  | { kind: 'replace'; positions: number[] };

export const foldKey = new PluginKey<FoldState>('amir-fold');

function topIndexOfPos(doc: Node, pos: number): number {
  return doc.resolve(Math.min(pos, doc.content.size)).index(0);
}

function offsets(doc: Node): number[] {
  const out: number[] = [];
  doc.forEach((_n, offset) => out.push(offset));
  return out;
}

function foldedIndices(doc: Node, folded: ReadonlySet<number>): Set<number> {
  const idx = new Set<number>();
  if (!folded.size) return idx;
  doc.forEach((n, offset, index) => {
    if (folded.has(offset) && n.type.name === 'heading') idx.add(index);
  });
  return idx;
}

function caret(isFolded: boolean) {
  return (view: EditorView, getPos: () => number | undefined) => {
    const b = document.createElement('button');
    b.className = 'amd-caret' + (isFolded ? ' amd-caret-folded' : '');
    b.type = 'button';
    b.tabIndex = -1;
    b.contentEditable = 'false';
    b.setAttribute('aria-label', isFolded ? 'Expand section' : 'Collapse section');
    b.setAttribute('aria-expanded', String(!isFolded));
    b.addEventListener('mousedown', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const p = getPos();
      if (p === undefined) return;
      view.dispatch(view.state.tr.setMeta(foldKey, { kind: 'toggle', pos: p - 1 } satisfies FoldMeta));
    });
    return b;
  };
}

function build(doc: Node, folded: ReadonlySet<number>): FoldState {
  const idx = foldedIndices(doc, folded);
  const hidden = hiddenChildren(doc, idx);
  const decos: Decoration[] = [];
  doc.forEach((node, offset, index) => {
    const end = offset + node.nodeSize;
    if (hidden[index]) decos.push(Decoration.node(offset, end, { hidden: 'until-found', class: 'amd-hidden' }));
    if (node.type.name !== 'heading') return;
    const isFolded = idx.has(index);
    decos.push(Decoration.widget(offset + 1, caret(isFolded), {
      side: -1,
      key: isFolded ? 'caret-folded' : 'caret-open',
      ignoreSelection: true,
      stopEvent: () => true,
    }));
    if (isFolded) decos.push(Decoration.node(offset, end, { class: 'amd-folded' }));
  });
  // Keep only positions that still hold a folded heading.
  const clean = new Set<number>();
  doc.forEach((_n, offset, index) => { if (idx.has(index)) clean.add(offset); });
  return { folded: clean, hidden, decos: DecorationSet.create(doc, decos) };
}

function mapFolded(folded: ReadonlySet<number>, tr: Transaction): Set<number> {
  const out = new Set<number>();
  for (const pos of folded) {
    const r = tr.mapping.mapResult(pos, 1);
    if (r.deleted) continue;
    const $p = tr.doc.resolve(r.pos);
    if ($p.depth === 0 && tr.doc.nodeAt(r.pos)?.type.name === 'heading') out.add(r.pos);
  }
  return out;
}

function applyMeta(folded: ReadonlySet<number>, meta: FoldMeta): Set<number> {
  const next = new Set(folded);
  switch (meta.kind) {
    case 'toggle':
      if (next.has(meta.pos)) next.delete(meta.pos);
      else next.add(meta.pos);
      break;
    case 'set':
      for (const p of meta.positions) {
        if (meta.folded) next.add(p);
        else next.delete(p);
      }
      break;
    case 'replace':
      return new Set(meta.positions);
  }
  return next;
}

// ---------------------------------------------------------------- queries and commands

export function foldState(state: EditorState): FoldState {
  return foldKey.getState(state)!;
}

export function isFoldedAt(state: EditorState, headingPos: number): boolean {
  return foldState(state).folded.has(headingPos);
}

/** Transaction that opens every fold hiding top-level child `index`, or null if it is visible. */
export function revealIndex(state: EditorState, index: number): Transaction | null {
  const st = foldState(state);
  if (!st.hidden[index]) return null;
  const doc = state.doc;
  const offs = offsets(doc);
  const hiding = foldsHiding(doc, foldedIndices(doc, st.folded), index);
  return state.tr.setMeta(foldKey, { kind: 'set', positions: hiding.map((i) => offs[i]), folded: false } satisfies FoldMeta);
}

export function revealPos(state: EditorState, pos: number): Transaction | null {
  return revealIndex(state, topIndexOfPos(state.doc, pos));
}

export function setAllFolds(state: EditorState, fold: boolean): Transaction {
  const positions: number[] = [];
  if (fold) {
    state.doc.forEach((n, offset, index) => {
      if (n.type.name === 'heading' && foldRange(state.doc, index).to > index + 1) positions.push(offset);
    });
  }
  return state.tr.setMeta(foldKey, { kind: 'replace', positions } satisfies FoldMeta);
}

/** FR-FOLD-12: fold or open the section that contains the cursor. */
export function foldAtCursor(fold: boolean) {
  return (state: EditorState, dispatch?: (tr: Transaction) => void): boolean => {
    const idx = topIndexOfPos(state.doc, state.selection.head);
    let h = -1;
    for (let i = idx; i >= 0; i--) {
      if (state.doc.child(i).type.name === 'heading') { h = i; break; }
    }
    if (h < 0) return false;
    if (dispatch) dispatch(state.tr.setMeta(foldKey, { kind: 'set', positions: [offsets(state.doc)[h]], folded: fold } satisfies FoldMeta));
    return true;
  };
}

/** Fold keys (level|text|occurrence) for saving view state (FR-FOLD-08). */
export function foldKeys(state: EditorState): string[] {
  const st = foldState(state);
  return collectHeadings(state.doc).filter((h) => h.topIndex !== null && st.folded.has(h.pos)).map((h) => h.key);
}

export function applyFoldKeys(state: EditorState, keys: readonly string[]): Transaction {
  const want = new Set(keys);
  const positions = collectHeadings(state.doc).filter((h) => h.topIndex !== null && want.has(h.key)).map((h) => h.pos);
  return state.tr.setMeta(foldKey, { kind: 'replace', positions } satisfies FoldMeta);
}

// ---------------------------------------------------------------- keys

function nextVisible(hidden: boolean[], from: number, step: 1 | -1): number {
  for (let i = from; i >= 0 && i < hidden.length; i += step) if (!hidden[i]) return i;
  return -1;
}

function handleArrows(view: EditorView, e: KeyboardEvent, st: FoldState): boolean {
  const { state } = view;
  const sel = state.selection;
  if (!sel.empty || !(sel instanceof TextSelection)) return false;
  const $h = sel.$head;
  if ($h.depth !== 1) return false;
  const idx = $h.index(0);
  const forward = e.key === 'ArrowDown' || e.key === 'ArrowRight';
  const atEdge = e.key === 'ArrowRight' ? $h.parentOffset === $h.parent.content.size
    : e.key === 'ArrowLeft' ? $h.parentOffset === 0
    : view.endOfTextblock(forward ? 'down' : 'up');
  if (!atEdge) return false;
  const neighbour = idx + (forward ? 1 : -1);
  if (neighbour < 0 || neighbour >= st.hidden.length || !st.hidden[neighbour]) return false;
  const j = nextVisible(st.hidden, neighbour, forward ? 1 : -1);
  if (j < 0) return true; // nothing visible that way; stay put
  const offs = offsets(state.doc);
  const target = forward ? offs[j] : offs[j] + state.doc.child(j).nodeSize;
  const next = Selection.near(state.doc.resolve(target), forward ? 1 : -1);
  view.dispatch(state.tr.setSelection(next).scrollIntoView());
  return true;
}

/** FR-FOLD-11: Enter at the end of a folded heading adds a paragraph after the hidden section. */
function handleEnter(view: EditorView, st: FoldState): boolean {
  const { state } = view;
  const sel = state.selection;
  if (!sel.empty) return false;
  const $h = sel.$head;
  if ($h.depth !== 1 || $h.parent.type.name !== 'heading' || $h.parentOffset !== $h.parent.content.size) return false;
  const idx = $h.index(0);
  const offs = offsets(state.doc);
  if (!st.folded.has(offs[idx])) return false;
  const { to } = foldRange(state.doc, idx);
  const insertAt = to < state.doc.childCount ? offs[to] : state.doc.content.size;
  const tr = state.tr.insert(insertAt, schema.nodes.paragraph.create());
  tr.setSelection(TextSelection.create(tr.doc, insertAt + 1)).scrollIntoView();
  view.dispatch(tr);
  return true;
}

/** FR-FOLD-11: deleting a selection that includes a folded heading also deletes its hidden content. */
function handleDelete(view: EditorView, st: FoldState, onStatus: (msg: string) => void): boolean {
  const { state } = view;
  const sel = state.selection;
  if (sel.empty || !st.folded.size) return false;
  const doc = state.doc;
  const a = topIndexOfPos(doc, sel.from);
  const b = topIndexOfPos(doc, sel.to);
  const idx = foldedIndices(doc, st.folded);
  const offs = offsets(doc);
  let end = b;
  for (let i = a; i <= Math.min(b, doc.childCount - 1); i++) {
    if (idx.has(i) && sel.from <= offs[i]) end = Math.max(end, foldRange(doc, i).to - 1);
  }
  if (end === b) return false;
  const to = offs[end] + doc.child(end).nodeSize;
  view.dispatch(state.tr.delete(sel.from, to).scrollIntoView());
  const blocks = end - a + 1;
  onStatus(`Deleted ${blocks} block${blocks === 1 ? '' : 's'}, including folded content.`);
  return true;
}

// ---------------------------------------------------------------- plugin

export function foldPlugin(onStatus: (msg: string) => void): Plugin<FoldState> {
  return new Plugin<FoldState>({
    key: foldKey,
    state: {
      init: (_config, state) => build(state.doc, new Set()),
      apply(tr, value) {
        const meta = tr.getMeta(foldKey) as FoldMeta | undefined;
        if (!tr.docChanged && !meta) return value;
        let folded: ReadonlySet<number> = tr.docChanged ? mapFolded(value.folded, tr) : value.folded;
        if (meta) folded = applyMeta(folded, meta);
        return build(tr.doc, folded);
      },
    },
    props: {
      decorations: (state) => foldKey.getState(state)!.decos,
      handleKeyDown(view, e) {
        const st = foldKey.getState(view.state)!;
        if (e.ctrlKey || e.metaKey || e.altKey) return false;
        if (e.key === 'Enter' && !e.shiftKey) return handleEnter(view, st);
        if ((e.key === 'Backspace' || e.key === 'Delete') && !e.shiftKey) return handleDelete(view, st, onStatus);
        if (!e.shiftKey && e.key.startsWith('Arrow') && st.folded.size) return handleArrows(view, e, st);
        return false;
      },
    },
    // FR-FOLD-09: a selection that lands in hidden content opens the folds around it.
    appendTransaction(trs, _old, state) {
      if (!trs.some((t) => t.selectionSet) || trs.some((t) => t.getMeta('amir-external'))) return null;
      const st = foldKey.getState(state)!;
      if (!st.folded.size) return null;
      return revealPos(state, state.selection.head);
    },
    view(view) {
      const onBeforeMatch = (e: Event) => {
        const el = e.target as HTMLElement;
        const pos = view.posAtDOM(el, 0);
        const tr = revealPos(view.state, pos);
        if (tr) view.dispatch(tr);
      };
      view.dom.addEventListener('beforematch', onBeforeMatch);
      return { destroy: () => view.dom.removeEventListener('beforematch', onBeforeMatch) };
    },
  });
}
