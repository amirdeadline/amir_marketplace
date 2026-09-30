// Floating bubbles: link actions at the cursor (FR-LINK-02) and image properties
// for a selected image (FR-IMG-05, FR-IMG-06).

import { Command, NodeSelection } from 'prosemirror-state';
import type { EditorView } from 'prosemirror-view';
import { linkAt, removeLink, updateNodeAttrs } from '../editor/commands';
import { h } from './dom';

export interface BubbleDeps {
  run(cmd: Command, focus?: boolean): void;
  openLink(href: string): void;
  editLink(anchor: HTMLElement): void;
  locateImage(pos: number): void;
}

export class Bubbles {
  private el: HTMLElement;
  private target = '';

  constructor(private scroller: HTMLElement, private deps: BubbleDeps) {
    this.el = h('div', { class: 'amd-bubble', role: 'toolbar', hidden: true });
    scroller.append(this.el);
  }

  hide(): void {
    this.el.hidden = true;
    this.target = '';
  }

  update(view: EditorView): void {
    const st = view.state;
    const sel = st.selection;
    if (sel instanceof NodeSelection && sel.node.type.name === 'image') {
      const key = `img:${sel.from}:${sel.node.attrs.src}`;
      if (key !== this.target || this.el.hidden) {
        this.target = key;
        this.renderImage(sel.from, sel.node.attrs);
      }
      this.place(view, sel.to);
      return;
    }
    const link = view.hasFocus() || this.el.contains(document.activeElement) ? linkAt(st) : null;
    if (link && sel.empty) {
      const key = `link:${link.from}:${link.href}`;
      if (key !== this.target || this.el.hidden) {
        this.target = key;
        this.renderLink(link.href);
      }
      this.place(view, link.to);
      return;
    }
    if (!this.el.contains(document.activeElement)) this.hide();
  }

  private place(view: EditorView, pos: number): void {
    this.el.hidden = false;
    const c = view.coordsAtPos(pos);
    const box = this.scroller.getBoundingClientRect();
    const top = c.bottom - box.top + this.scroller.scrollTop + 6;
    let left = c.left - box.left + this.scroller.scrollLeft - 20;
    const maxLeft = this.scroller.clientWidth - this.el.offsetWidth - 8;
    left = Math.max(8, Math.min(left, maxLeft));
    this.el.style.top = `${top}px`;
    this.el.style.left = `${left}px`;
  }

  private button(label: string, onClick: () => void): HTMLButtonElement {
    const b = h('button', { type: 'button' }, label);
    b.addEventListener('mousedown', (e) => e.preventDefault());
    b.addEventListener('click', onClick);
    return b;
  }

  private renderLink(href: string): void {
    this.el.textContent = '';
    const shown = href.length > 60 ? `${href.slice(0, 57)}...` : href;
    const edit = this.button('Edit', () => this.deps.editLink(edit));
    this.el.append(
      h('span', { class: 'amd-bubble-href', title: href }, shown),
      edit,
      this.button('Open', () => this.deps.openLink(href)),
      this.button('Remove', () => this.deps.run(removeLink, true)),
    );
  }

  private renderImage(pos: number, attrs: Record<string, unknown>): void {
    this.el.textContent = '';
    const field = (label: string, name: string, value: unknown, width: string) => {
      const input = h('input', { type: 'text', spellcheck: 'false', 'aria-label': label, placeholder: label, style: `width:${width}` });
      input.value = value == null ? '' : String(value);
      input.addEventListener('change', () => {
        const v: string | null = input.value.trim() || null;
        if (name === 'width' && v !== null && !/^\d{1,4}$/.test(v)) {
          input.classList.add('invalid');
          return;
        }
        input.classList.remove('invalid');
        this.deps.run(updateNodeAttrs(pos, { [name]: v }), false);
      });
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          input.dispatchEvent(new Event('change'));
        }
      });
      return h('label', null, h('span', null, label), input);
    };
    this.el.append(
      field('Alt text', 'alt', attrs.alt, '14em'),
      field('Title', 'title', attrs.title, '10em'),
      field('Width px', 'width', attrs.width, '4.5em'),
      this.button('Replace...', () => this.deps.locateImage(pos)),
    );
  }
}
