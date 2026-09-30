// Custom node views: images (FR-IMG-02, 07), source blocks (FR-EDIT-15),
// checkbox list items (FR-EDIT-06), and code blocks with a language field (FR-EDIT-07).

import type { Node } from 'prosemirror-model';
import type { EditorView, NodeView, ViewMutationRecord } from 'prosemirror-view';

type GetPos = () => number | undefined;

export interface ImageHooks {
  /** Webview URL for a document image path, or null when it cannot be shown. */
  resolve(src: string): string | null;
  /** Ask the host for a path the webview could not load (outside the allowed folders). */
  unresolved(src: string): void;
  locate(pos: number): void;
  register(view: ImageView): void;
  unregister(view: ImageView): void;
}

export class ImageView implements NodeView {
  dom: HTMLElement;
  private img: HTMLImageElement;
  private missing: HTMLElement | null = null;
  private askedHost = false;

  constructor(public node: Node, private view: EditorView, private getPos: GetPos, private hooks: ImageHooks) {
    this.dom = document.createElement('span');
    this.dom.className = 'amd-img';
    this.img = document.createElement('img');
    this.img.draggable = false;
    this.img.addEventListener('error', () => this.onError());
    this.img.addEventListener('load', () => this.clearMissing());
    this.dom.appendChild(this.img);
    hooks.register(this);
    this.render();
  }

  render(): void {
    const a = this.node.attrs;
    this.img.alt = a.alt || '';
    if (a.title) this.img.title = a.title;
    else this.img.removeAttribute('title');
    if (a.width) this.img.setAttribute('width', String(a.width));
    else this.img.removeAttribute('width');
    const url = this.hooks.resolve(a.src || '');
    if (url === null) {
      this.showMissing(/^https?:/i.test(a.src || '') ? 'Remote images are turned off' : 'Image not found');
      return;
    }
    if (this.img.getAttribute('src') !== url) this.img.src = url;
  }

  private onError(): void {
    const src: string = this.node.attrs.src || '';
    if (!this.askedHost && !/^(https?|data):/i.test(src)) {
      this.askedHost = true;
      this.hooks.unresolved(src);
      return;
    }
    this.showMissing('Image not found');
  }

  private showMissing(reason: string): void {
    this.img.style.display = 'none';
    if (!this.missing) {
      this.missing = document.createElement('span');
      this.missing.className = 'amd-img-missing';
      this.missing.contentEditable = 'false';
      this.dom.appendChild(this.missing);
    }
    this.missing.textContent = '';
    const alt = document.createElement('strong');
    alt.textContent = this.node.attrs.alt || 'Image';
    const path = document.createElement('code');
    path.textContent = this.node.attrs.src || '';
    const why = document.createElement('span');
    why.textContent = reason;
    const locate = document.createElement('button');
    locate.type = 'button';
    locate.textContent = 'Locate file';
    locate.addEventListener('mousedown', (e) => {
      e.preventDefault();
      const p = this.getPos();
      if (p !== undefined) this.hooks.locate(p);
    });
    this.missing.append(alt, path, why, locate);
  }

  private clearMissing(): void {
    this.img.style.display = '';
    this.missing?.remove();
    this.missing = null;
  }

  /** Called when the host sends a resolved URL for this image. */
  refresh(): void {
    this.askedHost = true;
    this.clearMissing();
    this.render();
  }

  update(node: Node): boolean {
    if (node.type !== this.node.type) return false;
    const srcChanged = node.attrs.src !== this.node.attrs.src;
    this.node = node;
    if (srcChanged) {
      this.askedHost = false;
      this.clearMissing();
    }
    this.render();
    return true;
  }

  selectNode(): void { this.dom.classList.add('ProseMirror-selectednode'); }
  deselectNode(): void { this.dom.classList.remove('ProseMirror-selectednode'); }
  stopEvent(e: Event): boolean { return !!(e.target as HTMLElement).closest?.('.amd-img-missing button'); }
  ignoreMutation(): boolean { return true; }
  destroy(): void { this.hooks.unregister(this); }
}

/** A block amir_md keeps as Markdown text; the user can still edit the text (FR-EDIT-15). */
export class RawBlockView implements NodeView {
  dom: HTMLElement;
  private area: HTMLTextAreaElement;

  constructor(private node: Node, private view: EditorView, private getPos: GetPos) {
    this.dom = document.createElement('div');
    this.dom.className = 'amd-raw';
    this.dom.contentEditable = 'false';
    const label = document.createElement('div');
    label.className = 'amd-raw-label';
    label.textContent = 'Markdown source';
    this.area = document.createElement('textarea');
    this.area.spellcheck = false;
    this.area.value = node.attrs.text;
    this.area.setAttribute('aria-label', 'Markdown source');
    this.fit();
    this.area.addEventListener('input', () => {
      this.fit();
      const pos = this.getPos();
      if (pos === undefined) return;
      const cur = this.view.state.doc.nodeAt(pos);
      if (!cur) return;
      this.view.dispatch(this.view.state.tr.setNodeMarkup(pos, undefined, { ...cur.attrs, text: this.area.value }));
    });
    this.dom.append(label, this.area);
  }

  private fit(): void {
    this.area.rows = Math.max(1, this.area.value.split('\n').length);
  }

  update(node: Node): boolean {
    if (node.type !== this.node.type) return false;
    this.node = node;
    if (this.area.value !== node.attrs.text) {
      this.area.value = node.attrs.text;
      this.fit();
    }
    return true;
  }

  selectNode(): void { this.dom.classList.add('ProseMirror-selectednode'); }
  deselectNode(): void { this.dom.classList.remove('ProseMirror-selectednode'); }
  stopEvent(e: Event): boolean { return e.target === this.area; }
  ignoreMutation(): boolean { return true; }
}

/** List item with a clickable checkbox when it is a task item. */
export class ListItemView implements NodeView {
  dom: HTMLElement;
  contentDOM: HTMLElement;
  private box: HTMLInputElement | null = null;

  constructor(private node: Node, private view: EditorView, private getPos: GetPos) {
    this.dom = document.createElement('li');
    this.contentDOM = document.createElement('div');
    this.contentDOM.className = 'amd-li-body';
    if (node.attrs.checked !== null) {
      this.dom.className = 'amd-task';
      this.box = document.createElement('input');
      this.box.type = 'checkbox';
      this.box.contentEditable = 'false';
      this.box.checked = !!node.attrs.checked;
      this.box.addEventListener('mousedown', (e) => e.preventDefault());
      this.box.addEventListener('click', (e) => {
        e.preventDefault();
        const pos = this.getPos();
        if (pos === undefined) return;
        const cur = this.view.state.doc.nodeAt(pos);
        if (cur) this.view.dispatch(this.view.state.tr.setNodeMarkup(pos, undefined, { ...cur.attrs, checked: !cur.attrs.checked }));
      });
      this.dom.appendChild(this.box);
    }
    this.dom.appendChild(this.contentDOM);
  }

  update(node: Node): boolean {
    if (node.type !== this.node.type || (node.attrs.checked === null) !== (this.node.attrs.checked === null)) return false;
    this.node = node;
    if (this.box) this.box.checked = !!node.attrs.checked;
    return true;
  }

  stopEvent(e: Event): boolean { return e.target === this.box; }
  ignoreMutation(m: ViewMutationRecord): boolean { return m.type !== 'selection' && m.target === this.box; }
}

/** Code block with a small language field above it. */
export class CodeBlockView implements NodeView {
  dom: HTMLElement;
  contentDOM: HTMLElement;
  private lang: HTMLInputElement;

  constructor(private node: Node, private view: EditorView, private getPos: GetPos) {
    this.dom = document.createElement('div');
    this.dom.className = 'amd-code';
    this.lang = document.createElement('input');
    this.lang.className = 'amd-code-lang';
    this.lang.placeholder = 'language';
    this.lang.spellcheck = false;
    this.lang.value = node.attrs.params || '';
    this.lang.contentEditable = 'false';
    this.lang.setAttribute('aria-label', 'Code language');
    this.lang.addEventListener('change', () => {
      const pos = this.getPos();
      if (pos === undefined) return;
      const cur = this.view.state.doc.nodeAt(pos);
      const value = this.lang.value.trim().replace(/\s+/g, '');
      if (cur && cur.attrs.params !== value) this.view.dispatch(this.view.state.tr.setNodeMarkup(pos, undefined, { ...cur.attrs, params: value }));
    });
    const pre = document.createElement('pre');
    this.contentDOM = document.createElement('code');
    pre.appendChild(this.contentDOM);
    this.dom.append(this.lang, pre);
  }

  update(node: Node): boolean {
    if (node.type !== this.node.type) return false;
    this.node = node;
    if (document.activeElement !== this.lang) this.lang.value = node.attrs.params || '';
    return true;
  }

  stopEvent(e: Event): boolean { return e.target === this.lang; }
  ignoreMutation(m: ViewMutationRecord): boolean { return m.type !== 'selection' && (m.target === this.lang || m.target === this.dom); }
}
