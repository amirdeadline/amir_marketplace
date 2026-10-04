// Navigation pane: heading tree, filter, level list with Expand and Collapse,
// current-section tracking, and WAI-ARIA tree keyboard support (SRS FR-NAV).
// Ported from the MA guide navigator (build_navigator.py).

import type { NavLevel } from '../../shared/messages';
import {
  applyLevelAction, buildNavTree, carryOpen, filterEntries, HeadingInfo, isVisible, NavEntry, OpenState, withAncestorsOpen,
} from '../outline';
import { h } from './dom';

export interface NavDeps {
  navigate(entry: NavEntry): void;
  stateChanged(): void;
  defaultExpandLevel(): number;
}

const LEVELS: { value: NavLevel; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: '1', label: 'Heading 1' },
  { value: '2', label: 'Heading 2' },
  { value: '3', label: 'Heading 3' },
  { value: '4', label: 'Heading 4' },
  { value: '5', label: 'Heading 5' },
];

export class NavPane {
  el: HTMLElement;
  private tree: HTMLUListElement;
  private filter: HTMLInputElement;
  private levelSel: HTMLSelectElement;
  private count: HTMLElement;
  private entries: NavEntry[] = [];
  private items = new Map<NavEntry, HTMLLIElement>();
  private open: OpenState = {};
  private savedOpen: OpenState | null = null;
  private currentKey: string | null = null;
  private focusedKey: string | null = null;
  private initialised = false;

  constructor(private deps: NavDeps) {
    this.filter = h('input', { type: 'search', class: 'amd-nav-filter', placeholder: 'Filter headings', 'aria-label': 'Filter headings', spellcheck: 'false' });
    this.levelSel = h('select', { class: 'amd-nav-level', 'aria-label': 'Heading level for Expand and Collapse', title: 'Heading level for Expand and Collapse' });
    for (const l of LEVELS) this.levelSel.append(h('option', { value: l.value }, l.label));
    const expand = h('button', { type: 'button', onclick: () => this.levelAction('expand') }, 'Expand');
    const collapse = h('button', { type: 'button', onclick: () => this.levelAction('collapse') }, 'Collapse');
    this.levelSel.addEventListener('change', () => this.deps.stateChanged());
    this.count = h('div', { class: 'amd-nav-count', 'aria-live': 'polite' });
    this.tree = h('ul', { class: 'amd-nav-tree', role: 'tree', 'aria-label': 'Headings' });
    this.el = h('nav', { class: 'amd-nav', 'aria-label': 'Navigation pane' },
      h('div', { class: 'amd-nav-tools' },
        this.filter,
        h('div', { class: 'amd-nav-row' }, this.levelSel, expand, collapse),
        this.count),
      this.tree);
    this.filter.addEventListener('input', () => this.applyFilter());
    this.tree.addEventListener('click', (e) => this.onClick(e));
    this.tree.addEventListener('keydown', (e) => this.onKey(e));
  }

  // ---------------------------------------------------------------- state

  get level(): NavLevel { return this.levelSel.value as NavLevel; }
  set level(v: NavLevel) { if (LEVELS.some((l) => l.value === v)) this.levelSel.value = v; }
  get openState(): OpenState { return this.savedOpen ?? this.open; }

  restore(open: OpenState | null, level: NavLevel | null): void {
    if (open) {
      this.open = open;
      this.initialised = true;
    }
    if (level) this.level = level;
  }

  private domCap = 10_000;

  setDomCap(cap: number): void {
    this.domCap = Math.max(200, cap);
  }

  setHeadings(headings: HeadingInfo[]): void {
    this.entries = buildNavTree(headings);
    this.open = this.initialised
      ? carryOpen(this.entries, this.open, this.deps.defaultExpandLevel())
      : carryOpen(this.entries, {}, this.deps.defaultExpandLevel());
    this.initialised = true;
    this.renderChunked();
    if (this.filter.value.trim()) this.applyFilter();
  }

  // ---------------------------------------------------------------- rendering

  private renderChunked(): void {
    this.items.clear();
    this.tree.textContent = '';
    const cap = this.domCap;
    const toRender = this.entries.length > cap ? this.entries.slice(0, cap) : this.entries;
    const groups = new Map<NavEntry, HTMLUListElement>();
    const CHUNK = 80;
    let i = 0;
    const step = () => {
      const end = Math.min(i + CHUNK, toRender.length);
      for (; i < end; i++) this.appendEntry(toRender[i], groups);
      if (i < toRender.length) {
        requestAnimationFrame(step);
        return;
      }
      this.finishRender(toRender);
    };
    if (!toRender.length) this.finishRender(toRender);
    else requestAnimationFrame(step);
  }

  private appendEntry(e: NavEntry, groups: Map<NavEntry, HTMLUListElement>): void {
    const li = h('li', { role: 'treeitem', 'aria-level': String(e.level), tabindex: '-1' });
    const row = h('div', { class: 'amd-nav-row-item', style: `padding-left:${(this.depth(e)) * 14 + 4}px` },
      h('span', { class: 'amd-tw', 'aria-hidden': 'true' }),
      h('span', { class: 'amd-nav-text' }, e.text || '(empty heading)'));
    li.append(row);
    (li as HTMLLIElement & { entry?: NavEntry }).entry = e;
    if (e.children.length) {
      const ul = h('ul', { role: 'group' });
      li.append(ul);
      groups.set(e, ul);
    }
    (e.parent && groups.has(e.parent) ? groups.get(e.parent)! : this.tree).append(li);
    this.items.set(e, li);
  }

  private finishRender(rendered: NavEntry[]): void {
    this.paintOpen();
    const focusable = (this.focusedKey && rendered.find((e) => e.key === this.focusedKey)) || rendered[0];
    if (focusable && this.items.get(focusable)) this.items.get(focusable)!.tabIndex = 0;
    if (this.currentKey) this.markCurrent(this.currentKey);
    const total = this.entries.length;
    const suffix = total > rendered.length
      ? ` (showing first ${rendered.length} — use Filter to narrow)`
      : '';
    this.count.textContent = `${total} heading${total === 1 ? '' : 's'}${suffix}`;
  }

  private depth(e: NavEntry): number {
    let d = 0;
    for (let p = e.parent; p; p = p.parent) d++;
    return d;
  }

  private paintOpen(): void {
    for (const [e, li] of this.items) {
      if (e.children.length) li.setAttribute('aria-expanded', String(!!this.open[e.key]));
      else li.removeAttribute('aria-expanded');
    }
  }

  private setOpen(next: OpenState): void {
    if (next === this.open) return;
    this.open = next;
    if (this.savedOpen) this.savedOpen = null; // a manual change while filtering replaces the saved state
    this.paintOpen();
    this.deps.stateChanged();
  }

  private levelAction(action: 'expand' | 'collapse'): void {
    this.setOpen(applyLevelAction(this.entries, this.open, this.level, action));
  }

  expandAllEntries(open: boolean): void {
    this.setOpen(applyLevelAction(this.entries, this.open, 'all', open ? 'expand' : 'collapse'));
  }

  // ---------------------------------------------------------------- filter (FR-NAV-04)

  private applyFilter(): void {
    const q = this.filter.value.trim();
    if (!q) {
      for (const li of this.items.values()) li.classList.remove('amd-hide');
      if (this.savedOpen) {
        this.open = this.savedOpen;
        this.savedOpen = null;
        this.paintOpen();
      }
      this.count.textContent = `${this.entries.length} heading${this.entries.length === 1 ? '' : 's'}`;
      return;
    }
    if (!this.savedOpen) this.savedOpen = this.open;
    const { shown, matches } = filterEntries(this.entries, q);
    const open: Record<string, boolean> = { ...this.savedOpen };
    for (const [e, li] of this.items) {
      li.classList.toggle('amd-hide', !shown.has(e));
      if (shown.has(e) && e.children.some((c) => shown.has(c))) open[e.key] = true;
    }
    this.open = open;
    this.paintOpen();
    this.count.textContent = matches
      ? `${matches} matching heading${matches === 1 ? '' : 's'} (the document is not filtered)`
      : 'No matching headings';
  }

  // ---------------------------------------------------------------- current section (FR-NAV-11)

  setCurrent(key: string | null): void {
    if (key === this.currentKey) return;
    this.currentKey = key;
    this.markCurrent(key);
  }

  private markCurrent(key: string | null): void {
    for (const li of this.tree.querySelectorAll('[aria-current]')) li.removeAttribute('aria-current');
    if (!key) return;
    const e = this.entries.find((x) => x.key === key);
    if (!e) return;
    if (!this.savedOpen) {
      const next = withAncestorsOpen(e, this.open);
      if (next !== this.open) {
        this.open = next;
        this.paintOpen();
        this.deps.stateChanged();
      }
    }
    const li = this.items.get(e)!;
    li.setAttribute('aria-current', 'true');
    const row = li.firstElementChild as HTMLElement;
    const r = row.getBoundingClientRect();
    const box = this.tree.getBoundingClientRect();
    if (r.top < box.top || r.bottom > box.bottom) row.scrollIntoView({ block: 'nearest' });
  }

  entryByKey(key: string): NavEntry | undefined {
    return this.entries.find((e) => e.key === key);
  }

  // ---------------------------------------------------------------- mouse and keyboard

  private entryOf(el: Element | null): NavEntry | null {
    const li = el?.closest('li[role="treeitem"]') as (HTMLLIElement & { entry?: NavEntry }) | null;
    return li?.entry ?? null;
  }

  private onClick(ev: MouseEvent): void {
    const t = ev.target as HTMLElement;
    const row = t.closest('.amd-nav-row-item');
    if (!row) return;
    const e = this.entryOf(row);
    if (!e) return;
    if (t.closest('.amd-tw') && e.children.length) {
      this.setOpen({ ...this.open, [e.key]: !this.open[e.key] });
      this.focus(e);
      return;
    }
    this.focus(e);
    this.deps.navigate(e);
  }

  private visible(): NavEntry[] {
    return this.entries.filter((e) => !this.items.get(e)!.classList.contains('amd-hide') && isVisible(e, this.open));
  }

  private focus(e: NavEntry): void {
    for (const li of this.items.values()) li.tabIndex = -1;
    const li = this.items.get(e)!;
    li.tabIndex = 0;
    li.focus({ preventScroll: true });
    (li.firstElementChild as HTMLElement).scrollIntoView({ block: 'nearest' });
    this.focusedKey = e.key;
  }

  private onKey(ev: KeyboardEvent): void {
    const li = ev.target as HTMLElement;
    if (li.getAttribute('role') !== 'treeitem') return;
    const e = this.entryOf(li);
    if (!e) return;
    const vis = this.visible();
    const i = vis.indexOf(e);
    switch (ev.key) {
      case 'ArrowDown': if (i < vis.length - 1) this.focus(vis[i + 1]); break;
      case 'ArrowUp': if (i > 0) this.focus(vis[i - 1]); break;
      case 'Home': if (vis.length) this.focus(vis[0]); break;
      case 'End': if (vis.length) this.focus(vis[vis.length - 1]); break;
      case 'ArrowRight':
        if (e.children.length) {
          if (!this.open[e.key]) this.setOpen({ ...this.open, [e.key]: true });
          else this.focus(e.children[0]);
        }
        break;
      case 'ArrowLeft':
        if (e.children.length && this.open[e.key]) this.setOpen({ ...this.open, [e.key]: false });
        else if (e.parent) this.focus(e.parent);
        break;
      case 'Enter':
      case ' ':
        this.deps.navigate(e);
        break;
      case '*': {
        const next: Record<string, boolean> = { ...this.open };
        for (const s of e.parent ? e.parent.children : this.entries.filter((x) => !x.parent)) if (s.children.length) next[s.key] = true;
        this.setOpen(next);
        break;
      }
      default:
        return;
    }
    ev.preventDefault();
    ev.stopPropagation();
  }
}
