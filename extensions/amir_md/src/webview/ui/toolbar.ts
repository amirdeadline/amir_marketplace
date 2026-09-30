// Word-style toolbar (SRS FR-EDIT-01 to 11, FR-COLOR-01, 02, 05, FR-EXPORT-01).

import type { Command, EditorState } from 'prosemirror-state';
import type { EditorView } from 'prosemirror-view';
import { redo, redoDepth, undo, undoDepth } from 'prosemirror-history';
import {
  addColumnAfter, addColumnBefore, addRowAfter, addRowBefore, deleteColumn, deleteRow, deleteTable,
  isInTable, selectedRect, toggleHeaderRow,
} from 'prosemirror-tables';
import { schema } from '../codec/schema';
import {
  alignAt, BLOCK_STYLES, blockStyleAt, clearFormatting, inBlockquote, indentList, insertRule, insertTable,
  linkAt, listKindAt, markActive, normalizeHex, outdentList, setAlign, setBlockStyle, setTextStyle,
  textStyleAt, toggle, toggleBlockquote, toggleCodeBlock, toggleList, Align, BlockStyle, StyleAttr,
} from '../editor/commands';
import { closePopover, h, keepFocus, openPopover, popoverOpenFor } from './dom';
import { ICONS } from './icons';
import type { ExportFormat, Settings } from '../../shared/messages';

export const FONT_SIZES = [8, 9, 10, 10.5, 11, 12, 14, 16, 18, 20, 24, 28, 36, 48, 72];
export const HIGHLIGHTS = [
  { name: 'Yellow', hex: '#FFF59D' }, { name: 'Green', hex: '#C8E6C9' }, { name: 'Cyan', hex: '#B2EBF2' },
  { name: 'Pink', hex: '#F8BBD0' }, { name: 'Gray', hex: '#E0E0E0' },
];

export interface ToolbarActions {
  run(cmd: Command): void;
  linkDialog(anchor: HTMLElement): void;
  imageFromFile(): void;
  imageFromAddress(anchor: HTMLElement): void;
  exportAs(format: ExportFormat): void;
  toggleNav(): void;
}

const RECENT_KEY = 'amir_md.recentColors';

function loadRecent(): string[] {
  try {
    const v = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
    return Array.isArray(v) ? v.filter((x) => typeof x === 'string').slice(0, 8) : [];
  } catch {
    return [];
  }
}

function saveRecent(list: string[]): void {
  try { localStorage.setItem(RECENT_KEY, JSON.stringify(list)); } catch { /* storage unavailable */ }
}

export class Toolbar {
  el: HTMLElement;
  private pressed = new Map<HTMLElement, (s: EditorState) => boolean>();
  private enabled = new Map<HTMLButtonElement, (s: EditorState) => boolean>();
  private styleSel!: HTMLSelectElement;
  private fontSel!: HTMLSelectElement;
  private sizeInput!: HTMLInputElement;
  private colorBar!: HTMLElement;
  private highlightBar!: HTMLElement;
  private lastColor = '#E53935';
  private lastHighlight = '#FFF59D';
  private recent: string[] = loadRecent();

  constructor(private view: () => EditorView, private settings: () => Settings, private actions: ToolbarActions) {
    this.el = keepFocus(h('div', { class: 'amd-toolbar', role: 'toolbar', 'aria-label': 'Formatting' }));
    this.build();
  }

  // ---------------------------------------------------------------- building blocks

  private btn(icon: string, title: string, onClick: (b: HTMLButtonElement) => void, opts: { pressed?: (s: EditorState) => boolean; enabled?: (s: EditorState) => boolean } = {}): HTMLButtonElement {
    const b = h('button', { type: 'button', class: 'amd-tb', title, 'aria-label': title });
    b.innerHTML = icon;
    b.addEventListener('click', () => onClick(b));
    if (opts.pressed) {
      b.setAttribute('aria-pressed', 'false');
      this.pressed.set(b, opts.pressed);
    }
    if (opts.enabled) this.enabled.set(b, opts.enabled);
    return b;
  }

  private cmdBtn(icon: string, title: string, cmd: Command, pressed?: (s: EditorState) => boolean): HTMLButtonElement {
    return this.btn(icon, title, () => this.actions.run(cmd), { pressed, enabled: (s) => cmd(s) || !!pressed?.(s) });
  }

  private menuBtn(icon: string, title: string, content: () => HTMLElement): HTMLButtonElement {
    const b = this.btn(`${icon}<span class="amd-dd">${ICONS.caret}</span>`, title, () => {
      if (popoverOpenFor(b)) closePopover();
      else openPopover(content(), b);
    });
    b.setAttribute('aria-haspopup', 'true');
    b.setAttribute('aria-expanded', 'false');
    return b;
  }

  private group(...items: HTMLElement[]): HTMLElement {
    return h('div', { class: 'amd-tb-group' }, ...items);
  }

  private build(): void {
    const s = schema.marks;

    // undo / redo
    const undoB = this.btn(ICONS.undo, 'Undo (Ctrl+Z)', () => this.actions.run(undo), { enabled: (st) => undoDepth(st) > 0 });
    const redoB = this.btn(ICONS.redo, 'Redo (Ctrl+Y)', () => this.actions.run(redo), { enabled: (st) => redoDepth(st) > 0 });

    // paragraph style
    this.styleSel = h('select', { class: 'amd-style', title: 'Paragraph style', 'aria-label': 'Paragraph style' });
    this.styleSel.append(h('option', { value: '' }, ''));
    for (const st of BLOCK_STYLES) this.styleSel.append(h('option', { value: st.value }, st.label));
    this.styleSel.addEventListener('change', () => {
      if (this.styleSel.value) this.actions.run(setBlockStyle(this.styleSel.value as BlockStyle));
    });

    // font
    this.fontSel = h('select', { class: 'amd-font', title: 'Font', 'aria-label': 'Font' });
    this.fillFonts();
    this.fontSel.addEventListener('change', () => this.actions.run(setTextStyle('fontFamily', this.fontSel.value || null)));

    // size
    const list = h('datalist', { id: 'amd-sizes' });
    for (const n of FONT_SIZES) list.append(h('option', { value: String(n) }));
    this.sizeInput = h('input', { class: 'amd-size', list: 'amd-sizes', title: 'Font size (pt)', 'aria-label': 'Font size in points', inputmode: 'decimal' });
    const applySize = () => {
      const raw = this.sizeInput.value.trim().replace(/pt$/i, '');
      if (!raw) return this.actions.run(setTextStyle('fontSize', null));
      const n = Number(raw);
      if (!Number.isFinite(n) || n < 1 || n > 400) {
        this.sizeInput.classList.add('invalid');
        return;
      }
      this.sizeInput.classList.remove('invalid');
      this.actions.run(setTextStyle('fontSize', `${n}pt`));
    };
    this.sizeInput.addEventListener('change', applySize);
    this.sizeInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        applySize();
      }
    });

    // character formatting
    const bold = this.cmdBtn(ICONS.bold, 'Bold (Ctrl+B)', toggle.strong, (st) => markActive(st, s.strong));
    const italic = this.cmdBtn(ICONS.italic, 'Italic (Ctrl+I)', toggle.em, (st) => markActive(st, s.em));
    const under = this.cmdBtn(ICONS.underline, 'Underline (Ctrl+U)', toggle.underline, (st) => markActive(st, s.underline));
    const strike = this.cmdBtn(ICONS.strike, 'Strikethrough (Alt+Shift+5)', toggle.strikethrough, (st) => markActive(st, s.strikethrough));
    const sup = this.cmdBtn(ICONS.sup, 'Superscript', toggle.sup, (st) => markActive(st, s.sup));
    const sub = this.cmdBtn(ICONS.sub, 'Subscript', toggle.sub, (st) => markActive(st, s.sub));
    const color = this.colorControl('color');
    const highlight = this.colorControl('bg');
    const clear = this.cmdBtn(ICONS.clear, 'Clear formatting (Ctrl+Space)', clearFormatting);

    // paragraphs
    const bullets = this.cmdBtn(ICONS.bullets, 'Bulleted list (Ctrl+Shift+8)', toggleList('bullet'), (st) => listKindAt(st) === 'bullet');
    const numbers = this.cmdBtn(ICONS.numbers, 'Numbered list (Ctrl+Shift+7)', toggleList('ordered'), (st) => listKindAt(st) === 'ordered');
    const tasks = this.cmdBtn(ICONS.tasks, 'Checkbox list', toggleList('task'), (st) => listKindAt(st) === 'task');
    const outdent = this.cmdBtn(ICONS.outdent, 'Decrease indent (Shift+Tab)', outdentList);
    const indent = this.cmdBtn(ICONS.indent, 'Increase indent (Tab)', indentList);
    const align = (a: Align, icon: string, title: string) =>
      this.cmdBtn(icon, title, setAlign(a), (st) => (alignAt(st) ?? null) === a && a !== null);
    const aLeft = this.btn(ICONS.alignLeft, 'Align left', () => this.actions.run(setAlign(null)), { pressed: (st) => !alignAt(st) || alignAt(st) === 'left' });
    const aCenter = align('center', ICONS.alignCenter, 'Center');
    const aRight = align('right', ICONS.alignRight, 'Align right');

    // insert
    const link = this.btn(ICONS.link, 'Link (Ctrl+K)', (b) => this.actions.linkDialog(b), { pressed: (st) => !!linkAt(st) });
    const image = this.menuBtn(ICONS.image, 'Picture', () => this.menu([
      ['From file...', () => this.actions.imageFromFile()],
      ['From web address...', () => this.actions.imageFromAddress(image)],
    ]));
    const table = this.menuBtn(ICONS.table, 'Table', () => this.tablePanel());
    const quote = this.cmdBtn(ICONS.quote, 'Quote', toggleBlockquote, inBlockquote);
    const code = this.cmdBtn(ICONS.code, 'Inline code', toggle.code, (st) => markActive(st, s.code));
    const codeBlock = this.cmdBtn(ICONS.codeBlock, 'Code block', toggleCodeBlock(), (st) => st.selection.$from.parent.type === schema.nodes.code_block);
    const rule = this.cmdBtn(ICONS.rule, 'Horizontal line', insertRule);

    // right side
    const nav = this.btn(ICONS.nav, 'Navigation pane', () => this.actions.toggleNav());
    const exp = this.menuBtn(`${ICONS.export}<span class="amd-tb-text">Export</span>`, 'Export', () => this.menu([
      ['Export to PDF...', () => this.actions.exportAs('pdf')],
      ['Export to Word...', () => this.actions.exportAs('docx')],
      ['Export to HTML...', () => this.actions.exportAs('html')],
      ['Save As Markdown...', () => this.actions.exportAs('md')],
    ]));

    this.el.append(
      this.group(undoB, redoB),
      this.group(this.styleSel, this.fontSel, this.sizeInput, list),
      this.group(bold, italic, under, strike, sup, sub),
      this.group(color, highlight, clear),
      this.group(bullets, numbers, tasks, outdent, indent),
      this.group(aLeft, aCenter, aRight),
      this.group(link, image, table, quote, code, codeBlock, rule),
      h('div', { class: 'amd-tb-spacer' }),
      this.group(nav, exp),
    );
  }

  private menu(items: [string, () => void][]): HTMLElement {
    const m = h('div', { class: 'amd-menu', role: 'menu' });
    for (const [label, fn] of items) {
      m.append(h('button', { type: 'button', role: 'menuitem', onclick: () => { closePopover(); fn(); } }, label));
    }
    return m;
  }

  fillFonts(): void {
    const cur = this.fontSel.value;
    this.fontSel.textContent = '';
    this.fontSel.append(h('option', { value: '' }, 'Default'));
    for (const f of this.settings().fontFamilies) this.fontSel.append(h('option', { value: f, style: `font-family:${f}` }, f));
    this.fontSel.value = cur;
  }

  // ---------------------------------------------------------------- colors

  private colorControl(attr: 'color' | 'bg'): HTMLElement {
    const isFont = attr === 'color';
    const label = isFont ? 'Font color' : 'Highlight color';
    const main = h('button', { type: 'button', class: 'amd-tb amd-split-main', title: label, 'aria-label': label });
    main.innerHTML = isFont ? '<span class="amd-a">A</span>' : ICONS.highlight;
    const bar = h('span', { class: 'amd-bar' });
    main.append(bar);
    if (isFont) this.colorBar = bar;
    else this.highlightBar = bar;
    main.addEventListener('click', () => this.applyColor(attr, isFont ? this.lastColor : this.lastHighlight));
    const arrow = h('button', { type: 'button', class: 'amd-tb amd-split-arrow', title: `${label} options`, 'aria-label': `${label} options`, 'aria-haspopup': 'true', 'aria-expanded': 'false' });
    arrow.innerHTML = ICONS.caret;
    arrow.addEventListener('click', () => {
      if (popoverOpenFor(arrow)) closePopover();
      else openPopover(this.palette(attr), arrow);
    });
    this.paintBars();
    return h('div', { class: 'amd-split' }, main, arrow);
  }

  private paintBars(): void {
    if (this.colorBar) this.colorBar.style.background = this.lastColor;
    if (this.highlightBar) this.highlightBar.style.background = this.lastHighlight;
  }

  private applyColor(attr: StyleAttr, value: string | null): void {
    const v = value ? normalizeHex(value) : null;
    this.actions.run(setTextStyle(attr, v));
    if (!v) return;
    if (attr === 'color') {
      this.lastColor = v;
      this.recent = [v, ...this.recent.filter((c) => c !== v)].slice(0, 8);
      saveRecent(this.recent);
    } else {
      this.lastHighlight = v;
    }
    this.paintBars();
  }

  private swatch(hex: string, name: string, attr: StyleAttr): HTMLButtonElement {
    return h('button', {
      type: 'button', class: 'amd-swatch', title: `${name} ${hex}`, 'aria-label': `${name} ${hex}`, style: `background:${hex}`,
      onclick: () => { closePopover(); this.applyColor(attr, hex); },
    });
  }

  private palette(attr: 'color' | 'bg'): HTMLElement {
    const isFont = attr === 'color';
    const p = h('div', { class: 'amd-palette' });
    p.append(h('button', { type: 'button', class: 'amd-auto', onclick: () => { closePopover(); this.applyColor(attr, null); } }, isFont ? 'Automatic' : 'No color'));
    const grid = h('div', { class: 'amd-swatches' });
    if (isFont) for (const hex of this.settings().palette) grid.append(this.swatch(normalizeHex(hex), 'Color', attr));
    else for (const c of HIGHLIGHTS) grid.append(this.swatch(c.hex, c.name, attr));
    p.append(grid);
    if (isFont && this.recent.length) {
      const r = h('div', { class: 'amd-swatches' });
      for (const hex of this.recent) r.append(this.swatch(hex, 'Recent', attr));
      p.append(h('div', { class: 'amd-pal-label' }, 'Recent colors'), r);
    }
    const picker = h('input', { type: 'color', 'aria-label': 'Pick a color' });
    picker.value = isFont ? this.lastColor : this.lastHighlight;
    const hex = h('input', { type: 'text', class: 'amd-hex', placeholder: '#RRGGBB', 'aria-label': 'Hex color', spellcheck: 'false' });
    hex.value = picker.value.toUpperCase();
    picker.addEventListener('input', () => { hex.value = picker.value.toUpperCase(); hex.classList.remove('invalid'); });
    const apply = h('button', { type: 'button', class: 'primary' }, 'Apply');
    const doApply = () => {
      if (!/^#?([0-9a-f]{3}|[0-9a-f]{6})$/i.test(hex.value.trim())) {
        hex.classList.add('invalid');
        return;
      }
      closePopover();
      this.applyColor(attr, hex.value);
    };
    apply.addEventListener('click', doApply);
    hex.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); doApply(); } });
    p.append(h('div', { class: 'amd-pal-label' }, 'More colors'), h('div', { class: 'amd-more' }, picker, hex, apply));
    return p;
  }

  // ---------------------------------------------------------------- tables

  private tablePanel(): HTMLElement {
    const wrap = h('div', { class: 'amd-table-pop' });
    const label = h('div', { class: 'amd-pal-label' }, 'Insert table');
    const grid = h('div', { class: 'amd-grid', role: 'grid', 'aria-label': 'Table size' });
    const cells: HTMLElement[] = [];
    const MAX = 8;
    const mark = (r: number, c: number) => {
      cells.forEach((cell, i) => cell.classList.toggle('on', Math.floor(i / MAX) < r && i % MAX < c));
      label.textContent = r && c ? `${c} x ${r} table` : 'Insert table';
    };
    for (let r = 1; r <= MAX; r++) {
      for (let c = 1; c <= MAX; c++) {
        const cell = h('button', { type: 'button', class: 'amd-cell', 'aria-label': `${c} columns by ${r} rows` });
        cell.addEventListener('mouseenter', () => mark(r, c));
        cell.addEventListener('focus', () => mark(r, c));
        cell.addEventListener('click', () => { closePopover(); this.actions.run(insertTable(r, c)); });
        cells.push(cell);
        grid.append(cell);
      }
    }
    wrap.append(label, grid);
    const st = this.view().state;
    if (isInTable(st)) {
      const alignCol = (a: string | null): Command => (state, dispatch) => {
        if (!isInTable(state)) return false;
        const rect = selectedRect(state);
        const tr = state.tr;
        const done = new Set<number>();
        for (let row = 0; row < rect.map.height; row++) {
          for (let col = rect.left; col < rect.right; col++) {
            const rel = rect.map.map[row * rect.map.width + col];
            if (done.has(rel)) continue;
            done.add(rel);
            const pos = rect.tableStart + rel;
            const cell = tr.doc.nodeAt(pos);
            if (cell) tr.setNodeMarkup(pos, undefined, { ...cell.attrs, align: a });
          }
        }
        if (dispatch) dispatch(tr);
        return true;
      };
      wrap.append(h('div', { class: 'amd-pal-label' }, 'Table'), this.menu([
        ['Insert row above', () => this.actions.run(addRowBefore)],
        ['Insert row below', () => this.actions.run(addRowAfter)],
        ['Insert column left', () => this.actions.run(addColumnBefore)],
        ['Insert column right', () => this.actions.run(addColumnAfter)],
        ['Delete row', () => this.actions.run(deleteRow)],
        ['Delete column', () => this.actions.run(deleteColumn)],
        ['Header row on or off', () => this.actions.run(toggleHeaderRow)],
        ['Align column left', () => this.actions.run(alignCol('left'))],
        ['Align column center', () => this.actions.run(alignCol('center'))],
        ['Align column right', () => this.actions.run(alignCol('right'))],
        ['Delete table', () => this.actions.run(deleteTable)],
      ]));
    }
    return wrap;
  }

  // ---------------------------------------------------------------- state

  update(state: EditorState): void {
    for (const [b, fn] of this.pressed) b.setAttribute('aria-pressed', String(fn(state)));
    for (const [b, fn] of this.enabled) b.disabled = !fn(state);
    if (document.activeElement !== this.styleSel) this.styleSel.value = blockStyleAt(state) ?? '';
    const ts = textStyleAt(state);
    if (document.activeElement !== this.fontSel) {
      const f = ts.fontFamily ?? '';
      if (f && ![...this.fontSel.options].some((o) => o.value === f)) this.fontSel.append(h('option', { value: f }, f));
      this.fontSel.value = f;
    }
    if (document.activeElement !== this.sizeInput) {
      this.sizeInput.value = ts.fontSize ? ts.fontSize.replace(/pt$/, '') : '';
      this.sizeInput.placeholder = String(this.settings().defaultFontSize);
      this.sizeInput.classList.remove('invalid');
    }
  }
}
