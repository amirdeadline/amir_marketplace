// The amir_md webview: layout, editor, sync with the host, navigation, and actions.

import { Command, EditorState, Plugin, TextSelection, Transaction } from 'prosemirror-state';
import { EditorView } from 'prosemirror-view';
import { history } from 'prosemirror-history';
import { dropCursor } from 'prosemirror-dropcursor';
import { gapCursor } from 'prosemirror-gapcursor';
import { tableEditing } from 'prosemirror-tables';
import { parseDocument, reconcile, CodecMeta } from './codec/document';
import type { SerializeOptions } from './codec/serialize';
import { applyFoldKeys, foldKey, foldKeys, foldPlugin, revealPos, setAllFolds } from './editor/foldPlugin';
import { buildKeymaps } from './editor/keymap';
import { CodeBlockView, ImageHooks, ImageView, ListItemView, RawBlockView } from './editor/nodeViews';
import { insertImage, linkAt, removeLink, setLink, updateNodeAttrs } from './editor/commands';
import { DocSync } from './sync';
import { collectHeadings, HeadingInfo, NavEntry } from './outline';
import { slugger } from '../shared/slug';
import { NavPane } from './ui/navPane';
import { Toolbar } from './ui/toolbar';
import { Bubbles } from './ui/bubbles';
import { closePopover, form, h, openPopover } from './ui/dom';
import { host } from './host';
import type { ExportFormat, HostToWebview, Settings, ViewState } from '../shared/messages';

type InitMsg = Extract<HostToWebview, { type: 'init' }>;

const UNSAFE_HREF = /^\s*(javascript|vbscript|data):/i;
const MIN_NAV = 180;

function serializeOpts(s: Settings): SerializeOptions {
  return { bulletMarker: s.bulletMarker, emphasisMarker: s.emphasisMarker, strongMarker: s.strongMarker };
}

function debounce(fn: () => void, ms: number): () => void {
  let t: ReturnType<typeof setTimeout> | null = null;
  return () => {
    if (t) clearTimeout(t);
    t = setTimeout(() => { t = null; fn(); }, ms);
  };
}

export class App {
  private settings: Settings;
  private meta: CodecMeta;
  private view!: EditorView;
  private sync: DocSync;
  private nav: NavPane;
  private toolbar: Toolbar;
  private bubbles: Bubbles;
  private scroller: HTMLElement;
  private crumb: HTMLElement;
  private statusMsg: HTMLElement;
  private statusInfo: HTMLElement;
  private navWidth: number;
  private navHidden = false;
  private headings: HeadingInfo[] = [];
  private sourceBlocks = 0;
  private baseUri: string;
  private resources = new Map<string, string | null>();
  private images = new Set<ImageView>();
  private pending = new Map<number, (path: string | null) => void>();
  private nextRequest = 1;
  private statusTimer: ReturnType<typeof setTimeout> | null = null;

  private scheduleOutline = debounce(() => this.refreshOutline(), 300);
  private scheduleViewState = debounce(() => this.saveViewState(), 500);

  constructor(root: HTMLElement, init: InitMsg) {
    this.settings = init.settings;
    this.baseUri = init.baseUri;
    this.navWidth = init.viewState?.navWidth || init.settings.navWidth;

    const parsed = parseDocument(init.text, serializeOpts(this.settings));
    this.meta = parsed.meta;
    this.sourceBlocks = parsed.stats.sourceBlocks;

    // layout
    this.nav = new NavPane({
      navigate: (e) => this.goToHeading(e),
      stateChanged: () => this.scheduleViewState(),
      defaultExpandLevel: () => this.settings.navDefaultExpandLevel,
    });
    const splitter = h('div', { class: 'amd-splitter', role: 'separator', 'aria-orientation': 'vertical', 'aria-label': 'Resize navigation pane', tabindex: '0' });
    this.crumb = h('div', { class: 'amd-crumb', 'aria-live': 'polite' });
    const editorHost = h('div', { class: 'amd-page' });
    this.scroller = h('div', { class: 'amd-scroll' }, editorHost);
    this.statusMsg = h('span', { class: 'amd-status-msg', 'aria-live': 'polite' });
    this.statusInfo = h('span', { class: 'amd-status-info' });
    const toolbarSlot = h('div');
    root.textContent = '';
    root.append(
      toolbarSlot,
      h('div', { class: 'amd-main' }, this.nav.el, splitter, h('section', { class: 'amd-docpane' }, this.crumb, this.scroller)),
      h('footer', { class: 'amd-status' }, this.statusMsg, this.statusInfo),
    );
    this.applySettingsCss();
    this.setupSplitter(splitter);

    // editor
    this.view = new EditorView(editorHost, {
      state: EditorState.create({ doc: parsed.doc, plugins: this.plugins() }),
      nodeViews: this.nodeViews(),
      dispatchTransaction: (tr) => this.dispatch(tr),
      attributes: { spellcheck: 'true', 'aria-label': `Document ${init.fileName}`, role: 'textbox', 'aria-multiline': 'true' },
      handleDOMEvents: {
        click: (_v, e) => this.onClick(e),
        auxclick: (_v, e) => this.onClick(e),
      },
      handlePaste: (_v, e) => this.onPasteFiles(e.clipboardData?.files ?? null, null),
      handleDrop: (v, e, _slice, moved) => {
        if (moved) return false;
        const at = v.posAtCoords({ left: e.clientX, top: e.clientY });
        return this.onPasteFiles(e.dataTransfer?.files ?? null, at ? at.pos : null);
      },
    });
    // Keys the editor handled are not passed on to VS Code keybindings.
    this.view.dom.addEventListener('keydown', (e) => { if (e.defaultPrevented) e.stopPropagation(); });

    this.toolbar = new Toolbar(() => this.view, () => this.settings, {
      run: (cmd) => this.run(cmd),
      linkDialog: (anchor) => this.linkDialog(anchor),
      imageFromFile: () => this.pickImage((path) => { if (path) this.run(insertImage(path, altFromPath(path))); }),
      imageFromAddress: (anchor) => this.imageFromAddress(anchor),
      exportAs: (format) => this.exportAs(format),
      toggleNav: () => this.toggleNav(),
    });
    toolbarSlot.replaceWith(this.toolbar.el);
    this.bubbles = new Bubbles(this.scroller, {
      run: (cmd, focus = true) => this.run(cmd, focus),
      openLink: (href) => this.openHref(href),
      editLink: (anchor) => this.linkDialog(anchor),
      locateImage: (pos) => this.locateImage(pos),
    });

    this.sync = new DocSync({
      post: (m) => host.post(m),
      doc: () => this.view.state.doc,
      meta: () => this.meta,
      load: (text) => this.load(text),
      notify: (m) => this.status(m, true),
    }, init.text, init.version);

    this.restoreViewState(init.viewState);
    this.refreshOutline();
    this.toolbar.update(this.view.state);
    this.scroller.addEventListener('scroll', () => this.onScroll(), { passive: true });
    window.addEventListener('resize', () => this.onScroll(), { passive: true });
    if (this.sourceBlocks) this.status(`${this.sourceBlocks} block${this.sourceBlocks === 1 ? '' : 's'} kept as Markdown source.`);
  }

  // ---------------------------------------------------------------- editor setup

  private plugins(): Plugin[] {
    return [
      foldPlugin((m) => this.status(m)),
      ...buildKeymaps(() => this.linkDialog()),
      history(),
      dropCursor(),
      gapCursor(),
      tableEditing(),
    ];
  }

  private nodeViews() {
    const hooks: ImageHooks = {
      resolve: (src) => this.resolveImage(src),
      unresolved: (src) => host.post({ type: 'resolveResources', paths: [src] }),
      locate: (pos) => this.locateImage(pos),
      register: (v) => this.images.add(v),
      unregister: (v) => this.images.delete(v),
    };
    return {
      image: (node: import('prosemirror-model').Node, view: EditorView, getPos: () => number | undefined) => new ImageView(node, view, getPos, hooks),
      raw_block: (node: import('prosemirror-model').Node, view: EditorView, getPos: () => number | undefined) => new RawBlockView(node, view, getPos),
      list_item: (node: import('prosemirror-model').Node, view: EditorView, getPos: () => number | undefined) => new ListItemView(node, view, getPos),
      code_block: (node: import('prosemirror-model').Node, view: EditorView, getPos: () => number | undefined) => new CodeBlockView(node, view, getPos),
    };
  }

  private dispatch(tr: Transaction): void {
    const before = this.view.state;
    const { state, transactions } = before.applyTransaction(tr);
    this.view.updateState(state);
    const docChanged = transactions.some((t) => t.docChanged);
    const external = transactions.some((t) => t.getMeta('amir-external'));
    if (docChanged && !external) this.sync.changed();
    if (docChanged) this.scheduleOutline();
    if (foldKey.getState(before)?.folded !== foldKey.getState(state)?.folded) this.scheduleViewState();
    this.toolbar.update(state);
    this.bubbles.update(this.view);
  }

  run(cmd: Command, focus = true): void {
    cmd(this.view.state, (tr) => this.view.dispatch(tr), this.view);
    if (focus) this.view.focus();
  }

  /** Replace the editor content with `text` from the host, keeping unchanged blocks and folds. */
  private load(text: string): void {
    const keys = foldKeys(this.view.state);
    const r = reconcile(this.view.state.doc, text, serializeOpts(this.settings));
    this.meta = r.meta;
    this.sourceBlocks = r.stats.sourceBlocks;
    const doc = this.view.state.doc;
    let from = 0;
    for (let i = 0; i < r.fromChild; i++) from += doc.child(i).nodeSize;
    let to = from;
    for (let i = r.fromChild; i < r.toChild; i++) to += doc.child(i).nodeSize;
    if (from !== to || r.nodes.length) {
      const tr = this.view.state.tr.replaceWith(from, to, r.nodes);
      this.view.dispatch(tr.setMeta('amir-external', true).setMeta('addToHistory', false));
    }
    this.view.dispatch(applyFoldKeys(this.view.state, keys).setMeta('amir-external', true));
  }

  // ---------------------------------------------------------------- host messages

  handle(msg: HostToWebview): void {
    switch (msg.type) {
      case 'externalChange':
        this.sync.external(msg.text, msg.version);
        break;
      case 'editResult':
        this.sync.editResult(msg.ok, msg.version, msg.ok ? undefined : msg.text);
        break;
      case 'settings':
        this.settings = msg.settings;
        this.meta.opts = serializeOpts(msg.settings);
        this.meta.cache = new WeakMap();
        this.applySettingsCss();
        this.toolbar.fillFonts();
        for (const v of this.images) v.refresh();
        break;
      case 'resources':
        for (const [k, v] of Object.entries(msg.map)) this.resources.set(k, v);
        for (const v of this.images) if (v.node.attrs.src in msg.map) v.refresh();
        break;
      case 'imageInserted': {
        const cb = this.pending.get(msg.requestId);
        this.pending.delete(msg.requestId);
        cb?.(msg.path);
        break;
      }
      case 'command':
        this.command(msg.name, msg.format);
        break;
      case 'exportDone':
        this.status(msg.ok ? `Exported to ${msg.path ?? 'file'}.` : `Export failed: ${msg.error ?? 'unknown error'}`, !msg.ok);
        break;
      default:
        break;
    }
  }

  private command(name: string, format?: ExportFormat): void {
    switch (name) {
      case 'expandAll': this.view.dispatch(setAllFolds(this.view.state, false)); break;
      case 'collapseAll': this.view.dispatch(setAllFolds(this.view.state, true)); break;
      case 'toggleNav': this.toggleNav(); break;
      case 'flush': this.sync.flushNow(); break;
      case 'export': if (format) this.exportAs(format); break;
      default: break;
    }
  }

  // ---------------------------------------------------------------- outline, navigation, scroll-spy

  private refreshOutline(): void {
    this.headings = collectHeadings(this.view.state.doc);
    this.nav.setHeadings(this.headings);
    this.onScroll();
    const words = this.view.state.doc.textBetween(0, this.view.state.doc.content.size, ' ', ' ').split(/\s+/).filter(Boolean).length;
    const src = this.sourceBlocks ? ` · ${this.sourceBlocks} source block${this.sourceBlocks === 1 ? '' : 's'}` : '';
    this.statusInfo.textContent = `${words.toLocaleString()} words · ${this.headings.length} headings${src}`;
  }

  private headingEl(hd: HeadingInfo): HTMLElement | null {
    const el = this.view.nodeDOM(hd.pos) as HTMLElement | null;
    return el && el.nodeType === 1 ? el : null;
  }

  private scrollTicking = false;

  private onScroll(): void {
    if (this.scrollTicking) return;
    this.scrollTicking = true;
    requestAnimationFrame(() => {
      this.scrollTicking = false;
      const top = this.scroller.getBoundingClientRect().top + 24;
      let current: HeadingInfo | null = null;
      for (const hd of this.headings) {
        const el = this.headingEl(hd);
        if (!el || el.closest('[hidden]')) continue;
        if (el.getBoundingClientRect().top <= top) current = hd;
        else break;
      }
      this.nav.setCurrent(current?.key ?? null);
      const entry = current ? this.nav.entryByKey(current.key) : undefined;
      const parts: string[] = [];
      for (let e: NavEntry | null | undefined = entry; e; e = e.parent) parts.unshift(e.text);
      this.crumb.textContent = parts.join('  ›  ');
      this.scheduleViewState();
    });
  }

  private goToHeading(e: NavEntry | HeadingInfo): void {
    const reveal = revealPos(this.view.state, e.pos);
    if (reveal) this.view.dispatch(reveal);
    const node = this.view.state.doc.nodeAt(e.pos);
    if (!node) return;
    this.view.dispatch(this.view.state.tr.setSelection(TextSelection.create(this.view.state.doc, e.pos + 1 + node.content.size)));
    const el = this.view.nodeDOM(e.pos) as HTMLElement | null;
    if (el && el.nodeType === 1) {
      const box = this.scroller.getBoundingClientRect();
      this.scroller.scrollTop += el.getBoundingClientRect().top - box.top - 12;
      this.flash(el);
    }
    this.view.focus();
  }

  private flash(el: HTMLElement): void {
    const box = this.scroller.getBoundingClientRect();
    const r = el.getBoundingClientRect();
    const f = h('div', { class: 'amd-flash', style: `top:${r.top - box.top + this.scroller.scrollTop - 4}px;left:${r.left - box.left - 8}px;width:${r.width + 16}px;height:${r.height + 8}px` });
    this.scroller.append(f);
    setTimeout(() => f.remove(), 1400);
  }

  private goToSlug(slug: string): boolean {
    const s = slugger();
    const target = this.headings.find((hd) => s(hd.text) === slug);
    if (target) this.goToHeading(target);
    return !!target;
  }

  // ---------------------------------------------------------------- links

  private onClick(e: MouseEvent): boolean {
    const a = (e.target as HTMLElement).closest('a');
    if (!a) return false;
    // Stop VS Code's webview link handler; a plain click only places the cursor (FR-LINK-04).
    e.preventDefault();
    e.stopPropagation();
    if ((e.ctrlKey || e.metaKey) && e.type === 'click') this.openHref(a.getAttribute('href') || '');
    return false;
  }

  private openHref(href: string): void {
    if (!href || UNSAFE_HREF.test(href)) {
      this.status('This link type cannot be opened.', true);
      return;
    }
    if (href.startsWith('#')) {
      if (!this.goToSlug(decodeURIComponent(href.slice(1)))) this.status(`No heading matches ${href}.`, true);
      return;
    }
    host.post({ type: 'openLink', href });
  }

  private cursorPoint(): { x: number; y: number } {
    const c = this.view.coordsAtPos(this.view.state.selection.head);
    return { x: c.left, y: c.bottom };
  }

  linkDialog(anchor?: HTMLElement): void {
    const st = this.view.state;
    const link = linkAt(st);
    const text = link ? link.text : st.doc.textBetween(st.selection.from, st.selection.to, ' ');
    const s = slugger();
    const options = [{ value: '', label: '(choose a heading)' }, ...this.headings.map((hd) => ({ value: `#${s(hd.text)}`, label: `${'  '.repeat(hd.level - 1)}${hd.text}` }))];
    const f = form([
      { name: 'text', label: 'Text to display', value: text },
      { name: 'href', label: 'Address', value: link?.href ?? '', placeholder: 'https://..., docs/other.md, or #heading' },
      { name: 'heading', label: 'Or a heading in this document', options },
      { name: 'title', label: 'Title (optional)', value: link?.title ?? '' },
    ], [
      {
        label: 'OK', primary: true, onClick: (v) => {
          const href = v.href.trim() || v.heading;
          const input = f.querySelector<HTMLInputElement>('input[name="href"]')!;
          if (!href || UNSAFE_HREF.test(href)) { input.classList.add('invalid'); input.focus(); return; }
          closePopover();
          this.run(setLink(href, v.title.trim() || null, v.text));
        },
      },
      ...(link ? [{ label: 'Remove link', onClick: () => { closePopover(); this.run(removeLink); } }] : []),
      { label: 'Cancel', onClick: () => { closePopover(); this.view.focus(); } },
    ]);
    const sel = f.querySelector<HTMLSelectElement>('select[name="heading"]')!;
    sel.addEventListener('change', () => { f.querySelector<HTMLInputElement>('input[name="href"]')!.value = sel.value; });
    openPopover(h('div', { class: 'amd-dialog' }, h('div', { class: 'amd-dialog-title' }, link ? 'Edit link' : 'Insert link'), f), anchor ?? this.cursorPoint(), () => this.refocus());
  }

  /** After a dialog closes, give focus back to the document unless something else took it. */
  private refocus(): void {
    setTimeout(() => {
      const a = document.activeElement;
      if (!a || a === document.body) this.view.focus();
    }, 0);
  }

  // ---------------------------------------------------------------- images

  private resolveImage(src: string): string | null {
    if (this.resources.has(src)) return this.resources.get(src)!;
    if (/^https?:/i.test(src)) return this.settings.allowRemoteImages ? src : null;
    if (/^data:image\//i.test(src)) return src;
    try {
      return new URL(src.replace(/\\/g, '/'), this.baseUri).toString();
    } catch {
      return null;
    }
  }

  private request(cb: (path: string | null) => void): number {
    const id = this.nextRequest++;
    this.pending.set(id, cb);
    return id;
  }

  private pickImage(cb: (path: string | null) => void): void {
    host.post({ type: 'pickImage', requestId: this.request(cb) });
  }

  private locateImage(pos: number): void {
    const src = this.view.state.doc.nodeAt(pos)?.attrs.src;
    this.pickImage((path) => {
      const node = this.view.state.doc.nodeAt(pos);
      if (!path || !node || node.type.name !== 'image' || node.attrs.src !== src) return;
      this.run(updateNodeAttrs(pos, { src: path }));
    });
  }

  private imageFromAddress(anchor: HTMLElement): void {
    const f = form([
      { name: 'url', label: 'Image address (https)', placeholder: 'https://example.com/diagram.png' },
      { name: 'alt', label: 'Alternative text' },
    ], [
      {
        label: 'Insert', primary: true, onClick: (v) => {
          const url = v.url.trim();
          if (!/^https:\/\/\S+$/i.test(url)) { f.querySelector('input')!.classList.add('invalid'); return; }
          closePopover();
          this.run(insertImage(url, v.alt.trim() || altFromPath(url)));
        },
      },
      { label: 'Cancel', onClick: () => { closePopover(); this.view.focus(); } },
    ]);
    openPopover(h('div', { class: 'amd-dialog' }, h('div', { class: 'amd-dialog-title' }, 'Picture from the web'), f), anchor, () => this.refocus());
  }

  /** Pasted or dropped image files are saved next to the document by the host (FR-IMG-03). */
  private onPasteFiles(files: FileList | null, at: number | null): boolean {
    const images = files ? [...files].filter((f) => f.type.startsWith('image/')) : [];
    if (!images.length) return false;
    for (const file of images) {
      const reader = new FileReader();
      reader.onload = () => {
        const data = String(reader.result).replace(/^data:[^,]*,/, '');
        const id = this.request((path) => {
          if (!path) return;
          if (at !== null && at <= this.view.state.doc.content.size) {
            this.view.dispatch(this.view.state.tr.setSelection(TextSelection.near(this.view.state.doc.resolve(at))));
          }
          this.run(insertImage(path, altFromPath(path)));
        });
        host.post({ type: 'saveImage', requestId: id, dataBase64: data, mime: file.type });
      };
      reader.readAsDataURL(file);
    }
    return true;
  }

  // ---------------------------------------------------------------- layout, view state, status

  private applySettingsCss(): void {
    const st = document.documentElement.style;
    if (this.settings.defaultFontFamily) st.setProperty('--amd-font', this.settings.defaultFontFamily);
    else st.removeProperty('--amd-font');
    st.setProperty('--amd-size', `${this.settings.defaultFontSize}pt`);
    st.setProperty('--amd-nav-w', `${this.navWidth}px`);
  }

  private setupSplitter(splitter: HTMLElement): void {
    const setWidth = (w: number) => {
      const max = Math.max(MIN_NAV, window.innerWidth * 0.5);
      this.navWidth = Math.round(Math.min(max, Math.max(MIN_NAV, w)));
      document.documentElement.style.setProperty('--amd-nav-w', `${this.navWidth}px`);
    };
    splitter.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      splitter.setPointerCapture(e.pointerId);
      const startX = e.clientX;
      const startW = this.navWidth;
      const move = (ev: PointerEvent) => setWidth(startW + ev.clientX - startX);
      const up = () => {
        splitter.removeEventListener('pointermove', move);
        splitter.removeEventListener('pointerup', up);
        this.scheduleViewState();
      };
      splitter.addEventListener('pointermove', move);
      splitter.addEventListener('pointerup', up);
    });
    splitter.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      e.preventDefault();
      setWidth(this.navWidth + (e.key === 'ArrowLeft' ? -20 : 20));
      this.scheduleViewState();
    });
  }

  toggleNav(): void {
    this.navHidden = !this.navHidden;
    document.body.classList.toggle('amd-nav-hidden', this.navHidden);
    this.scheduleViewState();
  }

  private restoreViewState(vs: ViewState | null): void {
    if (!vs) return;
    this.nav.restore(vs.navOpen && Object.keys(vs.navOpen).length ? vs.navOpen : null, vs.navLevel);
    if (vs.navHidden) {
      this.navHidden = true;
      document.body.classList.add('amd-nav-hidden');
    }
    if (this.settings.foldRemember && vs.folds?.length) this.view.dispatch(applyFoldKeys(this.view.state, vs.folds));
    requestAnimationFrame(() => { this.scroller.scrollTop = vs.scrollTop || 0; });
  }

  private saveViewState(): void {
    host.post({
      type: 'saveViewState',
      state: {
        folds: this.settings.foldRemember ? foldKeys(this.view.state) : [],
        navOpen: { ...this.nav.openState },
        navLevel: this.nav.level,
        navWidth: this.navWidth,
        navHidden: this.navHidden,
        scrollTop: Math.round(this.scroller.scrollTop),
      },
    });
  }

  private exportAs(format: ExportFormat): void {
    this.sync.flush();
    host.post({ type: 'export', format });
  }

  status(message: string, important = false): void {
    this.statusMsg.textContent = message;
    this.statusMsg.classList.toggle('amd-status-important', important);
    if (this.statusTimer) clearTimeout(this.statusTimer);
    this.statusTimer = setTimeout(() => { this.statusMsg.textContent = ''; }, important ? 12000 : 6000);
  }
}

function altFromPath(path: string): string {
  const name = decodeURIComponent(path.split(/[\\/]/).pop() || '').replace(/\.[a-z0-9]+$/i, '');
  return name.replace(/[-_]+/g, ' ').trim() || 'Image';
}
