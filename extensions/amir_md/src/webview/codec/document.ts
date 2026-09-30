// Whole-document codec: segmentation, fidelity check, block splice (SRS 4.4 and 4.5).
//
// The document text is cut into top-level blocks. For each block we keep its exact
// source text ("body") and the exact text between it and the next block ("gap").
// Editor nodes that were parsed from a block are remembered by identity, so on save
// an untouched node writes back its original body byte for byte. Only nodes the
// user changed are serialized again. A block the editor cannot reproduce exactly
// becomes a source block (raw_block) and is also written back unchanged.
//
// Each parsed block also gets an origin id in its `srcIdx` attribute. An edited
// node keeps the attribute, so the original gap between it and an untouched
// neighbour can still be found through `meta.order`.

import { Node } from 'prosemirror-model';
import { schema } from './schema';
import { createRefMd } from '../../shared/markdownIt';
import { MdEnv, parseBlock, sameContent } from './parse';
import { ESC_MODES, renderBlock, SerializeOptions } from './serialize';
import type { TextChange } from '../../shared/messages';

const refMd = createRefMd();

export interface CodecMeta {
  original: string;
  eol: string;
  prefix: string;
  tail: string;
  bodies: string[];
  gaps: string[];
  nodeIndex: WeakMap<Node, number>;
  order: Map<number, number>;
  cache: WeakMap<Node, string>;
  env: MdEnv;
  opts: SerializeOptions;
}

let nextOrigin = 1;

export interface ParseResult {
  doc: Node;
  meta: CodecMeta;
  stats: { blocks: number; sourceBlocks: number };
}

export function splitLines(text: string): string[] {
  const out: string[] = [];
  const re = /[^\n]*\n|[^\n]+$/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) out.push(m[0]);
  return out;
}

const isBlank = (line: string) => /^[ \t]*\r?\n?$/.test(line);
const eolLen = (line: string) => (line.endsWith('\r\n') ? 2 : line.endsWith('\n') ? 1 : 0);

export function detectEol(text: string): '\n' | '\r\n' {
  const i = text.indexOf('\n');
  return i > 0 && text[i - 1] === '\r' ? '\r\n' : '\n';
}

interface Seg {
  raw: boolean;
  s: number;
  e: number;
}

function segment(text: string, lines: string[]): { segs: Seg[]; env: MdEnv } {
  let fmEnd = 0;
  const first = lines[0]?.replace(/\r?\n$/, '');
  if (first === '---' || first === '+++') {
    const closer = first === '---' ? /^(---|\.\.\.)[ \t]*$/ : /^\+\+\+[ \t]*$/;
    for (let i = 1; i < lines.length; i++) {
      if (closer.test(lines[i].replace(/\r?\n$/, ''))) {
        fmEnd = i + 1;
        break;
      }
    }
  }
  const input = fmEnd ? '\n'.repeat(fmEnd) + lines.slice(fmEnd).join('') : text;
  const env: MdEnv = {};
  const tokens = refMd.parse(input, env);

  const segs: Seg[] = [];
  if (fmEnd) segs.push({ raw: true, s: 0, e: fmEnd });
  let cursor = fmEnd;
  const gapRaw = (from: number, to: number) => {
    let i = from;
    while (i < to) {
      if (isBlank(lines[i])) { i++; continue; }
      let j = i;
      while (j < to && !isBlank(lines[j])) j++;
      segs.push({ raw: true, s: i, e: j });
      i = j;
    }
  };
  for (const t of tokens) {
    if (t.level !== 0 || !t.map || t.nesting === -1) continue;
    const [s, e0] = t.map;
    if (s < cursor) continue;
    gapRaw(cursor, s);
    let e = e0;
    while (e > s && isBlank(lines[e - 1])) e--;
    if (e > s) segs.push({ raw: false, s, e });
    cursor = Math.max(e, s);
  }
  gapRaw(cursor, lines.length);
  return { segs, env };
}

function normHtml(h: string): string {
  return h
    .replace(/<(\/?)b>/g, '<$1strong>')
    .replace(/<(\/?)i>/g, '<$1em>')
    .replace(/<(\/?)(del|strike)>/g, '<$1s>')
    .replace(/<(\/?)ins>/g, '<$1u>')
    .replace(/<br\s*\/?>/g, '<br>')
    .replace(/\s*\/>/g, '>')
    .replace(/style="([^"]*)"/g, (_m, s: string) =>
      `style="${s.split(';').map((x) => x.trim().replace(/\s*:\s*/, ':')).filter(Boolean).join(';')}"`)
    .replace(/\s+/g, ' ')
    .trim();
}

function renderRef(src: string, env: MdEnv): string {
  return normHtml(refMd.render(src, { references: env.references || {} }));
}

/** Serialize a node with the lightest escaping that parses back to the same content. */
export function serializeBlockVerified(node: Node, meta: Pick<CodecMeta, 'env' | 'opts'>): string {
  let out = '';
  for (const mode of ESC_MODES) {
    out = renderBlock(node, meta.opts, mode);
    const back = parseBlock(out, meta.env);
    if (back && sameContent(back, node)) return out;
  }
  return out;
}

function withOrigin(node: Node, origin: number): Node {
  if (!('srcIdx' in node.type.spec.attrs!)) return node;
  return node.type.create({ ...node.attrs, srcIdx: origin }, node.content, node.marks);
}

const toEol = (s: string, eol: string) => (eol === '\n' ? s : s.replace(/\r?\n/g, eol));

export function parseDocument(text: string, opts: SerializeOptions): ParseResult {
  const lines = splitLines(text);
  const eol = detectEol(text);
  const { segs, env } = segment(text, lines);

  const lineStart: number[] = [0];
  for (const l of lines) lineStart.push(lineStart[lineStart.length - 1] + l.length);

  const meta: CodecMeta = {
    original: text,
    eol,
    prefix: '',
    tail: '',
    bodies: [],
    gaps: [],
    nodeIndex: new WeakMap(),
    order: new Map(),
    cache: new WeakMap(),
    env,
    opts,
  };

  const nodes: Node[] = [];
  let sourceBlocks = 0;
  let prevEnd = 0;
  segs.forEach((seg, k) => {
    const start = lineStart[seg.s];
    const end = lineStart[seg.e] - eolLen(lines[seg.e - 1]);
    const body = text.slice(start, end);
    if (k === 0) meta.prefix = text.slice(0, start);
    else meta.gaps.push(text.slice(prevEnd, start));
    prevEnd = end;
    meta.bodies.push(body);

    let node: Node | null = null;
    if (!seg.raw) {
      const parsed = parseBlock(body, env);
      if (parsed) {
        const ser = serializeBlockVerified(parsed, meta);
        if (renderRef(body, env) === renderRef(ser, env)) node = parsed;
      }
    }
    const origin = nextOrigin++;
    if (!node) {
      node = schema.nodes.raw_block.create({ text: body.replace(/\r\n/g, '\n'), srcIdx: origin });
      sourceBlocks++;
    } else {
      node = withOrigin(node, origin);
    }
    meta.nodeIndex.set(node, k);
    meta.order.set(origin, k);
    nodes.push(node);
  });
  if (segs.length) meta.tail = text.slice(prevEnd);
  else meta.prefix = text;

  const doc = schema.node('doc', null, nodes.length ? nodes : [schema.nodes.paragraph.create()]);
  return { doc, meta, stats: { blocks: nodes.length, sourceBlocks } };
}

export function serializeDocument(doc: Node, meta: CodecMeta): string {
  if (!meta.bodies.length && doc.childCount === 1 && doc.firstChild!.type.name === 'paragraph' && doc.firstChild!.content.size === 0) {
    return meta.original;
  }
  const parts: string[] = [meta.prefix];
  const n = doc.childCount;
  let prevIdx: number | undefined;
  for (let i = 0; i < n; i++) {
    const node = doc.child(i);
    const k = meta.nodeIndex.get(node);
    const idx = k ?? (node.attrs.srcIdx != null ? meta.order.get(node.attrs.srcIdx) : undefined);
    if (i > 0) parts.push(prevIdx !== undefined && idx === prevIdx + 1 ? meta.gaps[prevIdx] : meta.eol + meta.eol);
    if (k !== undefined) {
      parts.push(meta.bodies[k]);
    } else {
      let c = meta.cache.get(node);
      if (c === undefined) {
        c = toEol(serializeBlockVerified(node, meta), meta.eol);
        meta.cache.set(node, c);
      }
      parts.push(c);
    }
    prevIdx = idx;
  }
  parts.push(meta.bodies.length ? meta.tail : meta.eol);
  return parts.join('');
}

export interface Reconciled {
  /** Replace top-level children [fromChild, toChild) of the old document with `nodes`. */
  fromChild: number;
  toChild: number;
  nodes: Node[];
  meta: CodecMeta;
  stats: ParseResult['stats'];
}

/**
 * Bring an open editor document in line with new text (an external change or a
 * rebase). Unchanged leading and trailing blocks keep their node identity, so the
 * view does not redraw them and their source text stays exact.
 */
export function reconcile(oldDoc: Node, newText: string, opts: SerializeOptions): Reconciled {
  const { doc: next, meta, stats } = parseDocument(newText, opts);
  const oldN = oldDoc.childCount;
  const newN = next.childCount;
  let p = 0;
  while (p < oldN && p < newN && sameContent(oldDoc.child(p), next.child(p))) p++;
  let s = 0;
  while (s < oldN - p && s < newN - p && sameContent(oldDoc.child(oldN - 1 - s), next.child(newN - 1 - s))) s++;
  const keep = (oldNode: Node, k: number) => {
    meta.nodeIndex.set(oldNode, k);
    if (oldNode.attrs.srcIdx != null) meta.order.set(oldNode.attrs.srcIdx, k);
  };
  for (let i = 0; i < p; i++) keep(oldDoc.child(i), i);
  for (let j = 0; j < s; j++) keep(oldDoc.child(oldN - 1 - j), newN - 1 - j);
  const nodes: Node[] = [];
  for (let i = p; i < newN - s; i++) nodes.push(next.child(i));
  return { fromChild: p, toChild: oldN - s, nodes, meta, stats };
}

/** One range replacement turning oldText into newText, or null when equal. */
export function computeChange(oldText: string, newText: string): TextChange | null {
  if (oldText === newText) return null;
  let p = 0;
  const max = Math.min(oldText.length, newText.length);
  while (p < max && oldText.charCodeAt(p) === newText.charCodeAt(p)) p++;
  let s = 0;
  while (s < max - p && oldText.charCodeAt(oldText.length - 1 - s) === newText.charCodeAt(newText.length - 1 - s)) s++;
  // never split a CRLF pair or a surrogate pair
  const splits = (t: string, i: number) =>
    i > 0 && i < t.length && ((t[i - 1] === '\r' && t[i] === '\n') || (/[\uD800-\uDBFF]/.test(t[i - 1]) && /[\uDC00-\uDFFF]/.test(t[i])));
  while (p > 0 && (splits(oldText, p) || splits(newText, p))) p--;
  while (s > 0 && (splits(oldText, oldText.length - s) || splits(newText, newText.length - s))) s--;
  return { start: p, end: oldText.length - s, text: newText.slice(p, newText.length - s) };
}
