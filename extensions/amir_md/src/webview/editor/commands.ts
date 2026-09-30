// Editing commands behind the toolbar and keyboard shortcuts (SRS FR-EDIT, FR-COLOR, FR-LINK, FR-IMG).

import { Command, EditorState, TextSelection, Transaction } from 'prosemirror-state';
import { Attrs, Mark, MarkType, Node, NodeType, ResolvedPos } from 'prosemirror-model';
import { lift, toggleMark, wrapIn } from 'prosemirror-commands';
import { liftListItem, sinkListItem, wrapInList } from 'prosemirror-schema-list';
import { schema } from '../codec/schema';
import { STYLED_DEFAULTS } from '../codec/serialize';

const N = schema.nodes;
const M = schema.marks;

// ---------------------------------------------------------------- paragraph styles

export type BlockStyle = 'paragraph' | 'title' | 'subtitle' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';

export const BLOCK_STYLES: { value: BlockStyle; label: string }[] = [
  { value: 'paragraph', label: 'Normal text' },
  { value: 'title', label: 'Title' },
  { value: 'subtitle', label: 'Subtitle' },
  { value: 'h1', label: 'Heading 1' },
  { value: 'h2', label: 'Heading 2' },
  { value: 'h3', label: 'Heading 3' },
  { value: 'h4', label: 'Heading 4' },
  { value: 'h5', label: 'Heading 5' },
  { value: 'h6', label: 'Heading 6' },
];

function styleOf(node: Node): BlockStyle | null {
  switch (node.type) {
    case N.paragraph: return 'paragraph';
    case N.title: return 'title';
    case N.subtitle: return 'subtitle';
    case N.heading: return `h${node.attrs.level}` as BlockStyle;
    default: return null;
  }
}

/** Style of the text blocks in the selection, or null when they differ (FR-EDIT-01). */
export function blockStyleAt(state: EditorState): BlockStyle | null {
  const { from, to } = state.selection;
  let style: BlockStyle | null | undefined;
  state.doc.nodesBetween(from, to, (node) => {
    if (!node.isTextblock) return true;
    const s = styleOf(node);
    style = style === undefined ? s : style === s ? s : null;
    return false;
  });
  return style ?? null;
}

export function setBlockStyle(style: BlockStyle): Command {
  const target: { type: NodeType; attrs: (old: Node) => Attrs } =
    style === 'paragraph' ? { type: N.paragraph, attrs: (old) => ({ srcIdx: old.attrs.srcIdx ?? null, align: old.attrs.align ?? null }) }
    : style === 'title' || style === 'subtitle' ? {
        type: N[style],
        attrs: (old) => ({ srcIdx: old.attrs.srcIdx ?? null, styleAttr: old.type === N[style] ? old.attrs.styleAttr : STYLED_DEFAULTS[style] }),
      }
    : { type: N.heading, attrs: (old) => ({ srcIdx: old.attrs.srcIdx ?? null, level: Number(style.slice(1)) }) };
  return (state, dispatch) => {
    const { from, to } = state.selection;
    let applicable = false;
    state.doc.nodesBetween(from, to, (node, pos) => {
      if (applicable) return false;
      if (!node.isTextblock) return true;
      const $pos = state.doc.resolve(pos);
      const index = $pos.index();
      applicable = $pos.parent.canReplaceWith(index, index + 1, target.type);
      return false;
    });
    if (!applicable) return false;
    if (dispatch) dispatch(state.tr.setBlockType(from, to, target.type, target.attrs).scrollIntoView());
    return true;
  };
}

// ---------------------------------------------------------------- character formatting

export function markActive(state: EditorState, type: MarkType): boolean {
  const { from, $from, to, empty } = state.selection;
  if (empty) return !!type.isInSet(state.storedMarks || $from.marks());
  return state.doc.rangeHasMark(from, to, type);
}

export const toggle = {
  strong: toggleMark(M.strong),
  em: toggleMark(M.em),
  underline: toggleMark(M.underline),
  strikethrough: toggleMark(M.strikethrough),
  sup: toggleMark(M.sup),
  sub: toggleMark(M.sub),
  code: toggleMark(M.code),
};

export type StyleAttr = 'color' | 'bg' | 'fontFamily' | 'fontSize';
const EMPTY_STYLE = { color: null, bg: null, fontFamily: null, fontSize: null };

const hasAny = (a: Record<string, unknown>) => Object.values(a).some((v) => v !== null && v !== undefined && v !== '');

/** Text style at the cursor, or of the first text in the selection. */
export function textStyleAt(state: EditorState): Record<StyleAttr, string | null> {
  const { $from, empty, from, to } = state.selection;
  let mark = M.textStyle.isInSet(empty ? state.storedMarks || $from.marks() : []);
  if (!empty) {
    state.doc.nodesBetween(from, to, (node) => {
      if (mark || !node.isText) return !mark;
      mark = M.textStyle.isInSet(node.marks);
      return false;
    });
  }
  return { ...EMPTY_STYLE, ...(mark?.attrs ?? {}) } as Record<StyleAttr, string | null>;
}

/** Set one text style property on the selection; null removes it (FR-EDIT-02, 03, FR-COLOR). */
export function setTextStyle(attr: StyleAttr, value: string | null): Command {
  return (state, dispatch) => {
    const type = M.textStyle;
    const { empty, $from, ranges } = state.selection;
    if (empty) {
      const cur = type.isInSet(state.storedMarks || $from.marks());
      const attrs = { ...EMPTY_STYLE, ...(cur?.attrs ?? {}), [attr]: value };
      let tr = state.tr.removeStoredMark(type);
      if (hasAny(attrs)) tr = tr.addStoredMark(type.create(attrs));
      if (dispatch) dispatch(tr);
      return true;
    }
    const tr = state.tr;
    for (const r of ranges) {
      const from = r.$from.pos;
      const to = r.$to.pos;
      state.doc.nodesBetween(from, to, (node, pos, parent) => {
        if (!node.isText || !parent || !parent.type.allowsMarkType(type)) return true;
        const s = Math.max(pos, from);
        const e = Math.min(pos + node.nodeSize, to);
        const cur = type.isInSet(node.marks);
        const attrs = { ...EMPTY_STYLE, ...(cur?.attrs ?? {}), [attr]: value };
        tr.removeMark(s, e, type);
        if (hasAny(attrs)) tr.addMark(s, e, type.create(attrs));
        return false;
      });
    }
    if (dispatch) dispatch(tr.scrollIntoView());
    return true;
  };
}

const CLEARABLE = [M.strong, M.em, M.underline, M.strikethrough, M.sup, M.sub, M.code, M.textStyle];

/** FR-EDIT-05: remove character formatting, keep links and paragraph styles. */
export const clearFormatting: Command = (state, dispatch) => {
  const { empty, ranges } = state.selection;
  let tr = state.tr;
  if (empty) {
    for (const t of CLEARABLE) tr = tr.removeStoredMark(t);
  } else {
    for (const r of ranges) for (const t of CLEARABLE) tr.removeMark(r.$from.pos, r.$to.pos, t);
  }
  if (dispatch) dispatch(tr);
  return true;
};

/** FR-COLOR-03: #rgb and #rrggbb become #RRGGBB; anything else is returned unchanged. */
export function normalizeHex(value: string): string {
  const v = value.trim();
  const m3 = /^#?([0-9a-f])([0-9a-f])([0-9a-f])$/i.exec(v);
  if (m3) return `#${m3[1]}${m3[1]}${m3[2]}${m3[2]}${m3[3]}${m3[3]}`.toUpperCase();
  const m6 = /^#?([0-9a-f]{6})$/i.exec(v);
  if (m6) return `#${m6[1]}`.toUpperCase();
  return v;
}

// ---------------------------------------------------------------- lists, quotes, code, rules, alignment

function listAround($pos: ResolvedPos): { node: Node; pos: number; depth: number } | null {
  for (let d = $pos.depth; d > 0; d--) {
    const n = $pos.node(d);
    if (n.type === N.bullet_list || n.type === N.ordered_list) return { node: n, pos: $pos.before(d), depth: d };
  }
  return null;
}

export type ListKind = 'bullet' | 'ordered' | 'task';

function kindOf(list: Node): ListKind {
  if (list.type === N.ordered_list) return 'ordered';
  let task = false;
  list.forEach((item) => { if (item.attrs.checked !== null) task = true; });
  return task ? 'task' : 'bullet';
}

export function listKindAt(state: EditorState): ListKind | null {
  const l = listAround(state.selection.$from);
  return l ? kindOf(l.node) : null;
}

function setItemsChecked(tr: Transaction, listPos: number, checked: boolean | null): void {
  const list = tr.doc.nodeAt(listPos);
  if (!list) return;
  list.forEach((item, offset) => {
    const p = listPos + 1 + offset;
    const want = checked === null ? null : item.attrs.checked ?? checked;
    if (item.attrs.checked !== want) tr.setNodeMarkup(p, undefined, { ...item.attrs, checked: want });
  });
}

/** Bulleted, numbered, and checkbox lists: apply, switch kind, or remove (FR-EDIT-06). */
export function toggleList(kind: ListKind): Command {
  return (state, dispatch) => {
    const around = listAround(state.selection.$from);
    const type = kind === 'ordered' ? N.ordered_list : N.bullet_list;
    if (around) {
      if (kindOf(around.node) === kind) return liftListItem(N.list_item)(state, dispatch);
      if (!dispatch) return true;
      const tr = state.tr;
      const attrs = type === N.ordered_list
        ? { srcIdx: around.node.attrs.srcIdx ?? null, order: 1, tight: around.node.attrs.tight }
        : { srcIdx: around.node.attrs.srcIdx ?? null, tight: around.node.attrs.tight, bullet: null };
      tr.setNodeMarkup(around.pos, type, attrs);
      setItemsChecked(tr, around.pos, kind === 'task' ? false : null);
      dispatch(tr);
      return true;
    }
    const attrs = type === N.bullet_list ? { bullet: null, tight: true } : { order: 1, tight: true };
    let wrapped: Transaction | null = null;
    if (!wrapInList(type, attrs)(state, (tr) => { wrapped = tr; })) return false;
    if (!dispatch) return true;
    const tr = wrapped as unknown as Transaction;
    if (kind === 'task') {
      const l = listAround(tr.doc.resolve(tr.mapping.map(state.selection.from)));
      if (l) setItemsChecked(tr, l.pos, false);
    }
    dispatch(tr);
    return true;
  };
}

export const indentList: Command = sinkListItem(N.list_item);
export const outdentList: Command = liftListItem(N.list_item);

export function inBlockquote(state: EditorState): boolean {
  const $f = state.selection.$from;
  for (let d = $f.depth; d > 0; d--) if ($f.node(d).type === N.blockquote) return true;
  return false;
}

export const toggleBlockquote: Command = (state, dispatch) =>
  inBlockquote(state) ? lift(state, dispatch) : wrapIn(N.blockquote)(state, dispatch);

export function toggleCodeBlock(language = ''): Command {
  return (state, dispatch) => {
    const { $from, from, to } = state.selection;
    if ($from.parent.type === N.code_block) {
      if (dispatch) dispatch(state.tr.setBlockType(from, to, N.paragraph, (old) => ({ srcIdx: old.attrs.srcIdx ?? null })));
      return true;
    }
    if (!$from.parent.isTextblock) return false;
    if (dispatch) dispatch(state.tr.setBlockType(from, to, N.code_block, (old) => ({ srcIdx: old.attrs.srcIdx ?? null, params: language })));
    return true;
  };
}

export const insertRule: Command = (state, dispatch) => {
  if (dispatch) dispatch(state.tr.replaceSelectionWith(N.horizontal_rule.create()).scrollIntoView());
  return true;
};

export function insertTable(rows: number, cols: number): Command {
  return (state, dispatch) => {
    const cell = (type: NodeType) => type.create(null, N.paragraph.create());
    const header = N.table_row.create(null, Array.from({ length: cols }, () => cell(N.table_header)));
    const body = Array.from({ length: Math.max(0, rows - 1) }, () =>
      N.table_row.create(null, Array.from({ length: cols }, () => cell(N.table_cell))));
    const table = N.table.create(null, [header, ...body]);
    if (!dispatch) return true;
    const tr = state.tr.replaceSelectionWith(table);
    // put the cursor in the first header cell
    const start = tr.selection.from;
    let found = -1;
    tr.doc.nodesBetween(Math.max(0, start - table.nodeSize - 2), Math.min(tr.doc.content.size, start + 2), (n, pos) => {
      if (found < 0 && n.type === N.table_header) found = pos;
      return found < 0;
    });
    if (found >= 0) tr.setSelection(TextSelection.near(tr.doc.resolve(found + 2)));
    dispatch(tr.scrollIntoView());
    return true;
  };
}

export type Align = 'left' | 'center' | 'right' | null;

export function alignAt(state: EditorState): Align {
  const p = state.selection.$from.parent;
  return p.type === N.paragraph ? p.attrs.align : null;
}

export function setAlign(align: Align): Command {
  return (state, dispatch) => {
    const { from, to } = state.selection;
    const tr = state.tr;
    state.doc.nodesBetween(from, to, (node, pos) => {
      if (node.type === N.paragraph && node.attrs.align !== align) tr.setNodeMarkup(pos, undefined, { ...node.attrs, align });
      return !node.isTextblock;
    });
    if (!tr.docChanged) return false;
    if (dispatch) dispatch(tr);
    return true;
  };
}

// ---------------------------------------------------------------- links

export interface LinkInfo { from: number; to: number; href: string; title: string | null; text: string }

function markExtent($pos: ResolvedPos, type: MarkType): { from: number; to: number; mark: Mark } | null {
  const parent = $pos.parent;
  const start = $pos.start();
  const spans: { from: number; to: number; mark: Mark | undefined }[] = [];
  parent.forEach((child, offset) => {
    spans.push({ from: start + offset, to: start + offset + child.nodeSize, mark: type.isInSet(child.marks) ?? undefined });
  });
  const hit = spans.findIndex((s) => s.mark && $pos.pos >= s.from && $pos.pos <= s.to);
  if (hit < 0) return null;
  const mark = spans[hit].mark!;
  let a = hit;
  let b = hit;
  while (a > 0 && spans[a - 1].mark && spans[a - 1].mark!.eq(mark)) a--;
  while (b < spans.length - 1 && spans[b + 1].mark && spans[b + 1].mark!.eq(mark)) b++;
  return { from: spans[a].from, to: spans[b].to, mark };
}

export function linkAt(state: EditorState): LinkInfo | null {
  const { $from, $to, empty } = state.selection;
  const ext = markExtent($from, M.link);
  if (!ext) return null;
  if (!empty && ($to.pos > ext.to || $from.pos < ext.from)) return null;
  return { from: ext.from, to: ext.to, href: ext.mark.attrs.href, title: ext.mark.attrs.title, text: state.doc.textBetween(ext.from, ext.to) };
}

/** FR-LINK-01: set or replace the link on the selection (or the link at the cursor). */
export function setLink(href: string, title: string | null, text: string): Command {
  return (state, dispatch) => {
    if (!href) return false;
    const mark = M.link.create({ href, title: title || null });
    const existing = linkAt(state);
    const { from, to, empty } = state.selection;
    const range = existing ?? { from, to };
    if (!dispatch) return true;
    const tr = state.tr;
    const currentText = state.doc.textBetween(range.from, range.to);
    const wantText = text || currentText || href;
    if (range.from === range.to || wantText !== currentText) {
      const marks = (empty ? state.storedMarks || state.selection.$from.marks() : []).filter((m) => m.type !== M.link);
      tr.replaceWith(range.from, range.to, schema.text(wantText, [...marks, mark]));
      tr.setSelection(TextSelection.create(tr.doc, range.from + wantText.length));
    } else {
      tr.removeMark(range.from, range.to, M.link).addMark(range.from, range.to, mark);
    }
    dispatch(tr.scrollIntoView());
    return true;
  };
}

export const removeLink: Command = (state, dispatch) => {
  const l = linkAt(state);
  const { from, to } = state.selection;
  const range = l ?? { from, to };
  if (range.from === range.to) return false;
  if (dispatch) dispatch(state.tr.removeMark(range.from, range.to, M.link));
  return true;
};

// ---------------------------------------------------------------- images

export function insertImage(src: string, alt: string | null, title: string | null = null): Command {
  return (state, dispatch) => {
    if (dispatch) dispatch(state.tr.replaceSelectionWith(N.image.create({ src, alt: alt || null, title })).scrollIntoView());
    return true;
  };
}

export function updateNodeAttrs(pos: number, attrs: Record<string, unknown>): Command {
  return (state, dispatch) => {
    const node = state.doc.nodeAt(pos);
    if (!node) return false;
    if (dispatch) dispatch(state.tr.setNodeMarkup(pos, undefined, { ...node.attrs, ...attrs }));
    return true;
  };
}

// ---------------------------------------------------------------- tasks

/** Toggle a checkbox list item's state at `pos` (the list item position). */
export function toggleTask(pos: number): Command {
  return (state, dispatch) => {
    const item = state.doc.nodeAt(pos);
    if (!item || item.type !== N.list_item || item.attrs.checked === null) return false;
    if (dispatch) dispatch(state.tr.setNodeMarkup(pos, undefined, { ...item.attrs, checked: !item.attrs.checked }));
    return true;
  };
}
