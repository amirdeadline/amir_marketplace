// Heading outline shared by the navigation pane and section folding (SRS FR-NAV, FR-FOLD).
// Pure functions over the editor document; no DOM.

import type { Node } from 'prosemirror-model';
import type { NavLevel } from '../shared/messages';

export interface HeadingInfo {
  /** Document position just before the heading node. */
  pos: number;
  level: number;
  text: string;
  /** level|text|occurrence: stable across sessions and edits elsewhere (FR-FOLD-08, FR-NAV-13). */
  key: string;
  /** Index among the document's top-level blocks, or null for headings inside lists or quotes. */
  topIndex: number | null;
}

export function collectHeadings(doc: Node): HeadingInfo[] {
  const out: HeadingInfo[] = [];
  const seen = new Map<string, number>();
  const add = (node: Node, pos: number, topIndex: number | null) => {
    const level: number = node.attrs.level;
    const text = node.textContent.replace(/\s+/g, ' ').trim();
    const base = `${level}|${text}`;
    const n = seen.get(base) ?? 0;
    seen.set(base, n + 1);
    out.push({ pos, level, text, key: `${base}|${n}`, topIndex });
  };
  doc.forEach((child, offset, index) => {
    if (child.type.name === 'heading') {
      add(child, offset, index);
    } else if (!child.isTextblock && !child.isAtom) {
      child.descendants((inner, innerPos) => {
        if (inner.type.name === 'heading') add(inner, offset + 1 + innerPos, null);
        return !inner.isTextblock;
      });
    }
  });
  return out;
}

// ---------------------------------------------------------------- folding

/**
 * Top-level child range [from, to) that folding the heading at `index` hides:
 * everything after it up to the next heading of the same or a higher level (FR-FOLD-04).
 */
export function foldRange(doc: Node, index: number): { from: number; to: number } {
  const level: number = doc.child(index).attrs.level;
  let to = index + 1;
  while (to < doc.childCount) {
    const n = doc.child(to);
    if (n.type.name === 'heading' && n.attrs.level <= level) break;
    to++;
  }
  return { from: index + 1, to };
}

/** For each top-level child, whether a folded heading above it hides it. */
export function hiddenChildren(doc: Node, folded: ReadonlySet<number>): boolean[] {
  const hidden = new Array<boolean>(doc.childCount).fill(false);
  let hideLevel: number | null = null;
  for (let i = 0; i < doc.childCount; i++) {
    const n = doc.child(i);
    const isHeading = n.type.name === 'heading';
    if (hideLevel !== null) {
      if (isHeading && n.attrs.level <= hideLevel) {
        hideLevel = null;
      } else {
        hidden[i] = true;
        continue;
      }
    }
    if (isHeading && folded.has(i)) hideLevel = n.attrs.level;
  }
  return hidden;
}

/** Folded headings (top-level indices) whose sections contain child `index`. */
export function foldsHiding(doc: Node, folded: ReadonlySet<number>, index: number): number[] {
  const out: number[] = [];
  for (const h of folded) {
    if (h >= index) continue;
    const r = foldRange(doc, h);
    if (index >= r.from && index < r.to) out.push(h);
  }
  return out;
}

// ---------------------------------------------------------------- navigation tree

export interface NavEntry {
  key: string;
  level: number;
  text: string;
  pos: number;
  topIndex: number | null;
  parent: NavEntry | null;
  children: NavEntry[];
}

/** Nest headings with a level stack: each is a child of the nearest earlier shallower heading (FR-NAV-01). */
export function buildNavTree(headings: HeadingInfo[]): NavEntry[] {
  const entries: NavEntry[] = [];
  const stack: NavEntry[] = [];
  for (const h of headings) {
    while (stack.length && stack[stack.length - 1].level >= h.level) stack.pop();
    const parent = stack.length ? stack[stack.length - 1] : null;
    const e: NavEntry = { key: h.key, level: h.level, text: h.text, pos: h.pos, topIndex: h.topIndex, parent, children: [] };
    if (parent) parent.children.push(e);
    entries.push(e);
    stack.push(e);
  }
  return entries;
}

export type OpenState = Readonly<Record<string, boolean>>;

/** FR-NAV-16: entries at or above the default level start open. */
export function initialOpen(entries: NavEntry[], defaultExpandLevel: number): OpenState {
  const open: Record<string, boolean> = {};
  for (const e of entries) if (e.children.length) open[e.key] = e.level <= defaultExpandLevel;
  return open;
}

/** Entries that did not exist before get the default; existing ones keep their state (FR-NAV-13). */
export function carryOpen(entries: NavEntry[], previous: OpenState, defaultExpandLevel: number): OpenState {
  const open: Record<string, boolean> = {};
  for (const e of entries) {
    if (!e.children.length) continue;
    open[e.key] = e.key in previous ? previous[e.key] : e.level <= defaultExpandLevel;
  }
  return open;
}

/** Level list + Expand/Collapse semantics (FR-NAV-06 to FR-NAV-08, Appendix A). Returns a new state. */
export function applyLevelAction(entries: NavEntry[], open: OpenState, level: NavLevel, action: 'expand' | 'collapse'): OpenState {
  const next: Record<string, boolean> = { ...open };
  const withKids = entries.filter((e) => e.children.length);
  if (level === 'all') {
    for (const e of withKids) next[e.key] = action === 'expand';
    return next;
  }
  const n = Number(level);
  for (const e of entries) {
    if (e.level !== n) continue;
    if (action === 'collapse') {
      if (e.children.length) next[e.key] = false;
      continue;
    }
    if (e.children.length) next[e.key] = true;
    for (let p = e.parent; p; p = p.parent) next[p.key] = true;
  }
  return next;
}

export function isVisible(e: NavEntry, open: OpenState): boolean {
  for (let p = e.parent; p; p = p.parent) if (!open[p.key]) return false;
  return true;
}

export function withAncestorsOpen(e: NavEntry, open: OpenState): OpenState {
  let changed = false;
  const next: Record<string, boolean> = { ...open };
  for (let p = e.parent; p; p = p.parent) {
    if (!next[p.key]) {
      next[p.key] = true;
      changed = true;
    }
  }
  return changed ? next : open;
}

/** FR-NAV-04: entries matching the filter plus their ancestors. */
export function filterEntries(entries: NavEntry[], query: string): { shown: Set<NavEntry>; matches: number } {
  const q = query.trim().toLowerCase();
  const shown = new Set<NavEntry>();
  let matches = 0;
  for (const e of entries) {
    if (!e.text.toLowerCase().includes(q)) continue;
    matches++;
    for (let p: NavEntry | null = e; p && !shown.has(p); p = p.parent) shown.add(p);
  }
  return { shown, matches };
}

/** The heading whose section contains `pos`: the last heading at or before it. */
export function entryAt(entries: NavEntry[], pos: number): NavEntry | null {
  let best: NavEntry | null = null;
  for (const e of entries) {
    if (e.pos <= pos) best = e;
    else break;
  }
  return best;
}
