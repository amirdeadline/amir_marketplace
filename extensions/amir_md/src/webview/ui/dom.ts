// Small DOM helpers for the webview UI.

type Child = Node | string | null | undefined | false;
type Props = Record<string, unknown> & { class?: string; style?: string };

export function h<K extends keyof HTMLElementTagNameMap>(tag: K, props: Props | null = null, ...children: Child[]): HTMLElementTagNameMap[K] {
  const el = document.createElement(tag);
  if (props) {
    for (const [k, v] of Object.entries(props)) {
      if (v === undefined || v === null || v === false) continue;
      if (k === 'class') el.className = String(v);
      else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2).toLowerCase(), v as EventListener);
      else if (k in el && typeof v !== 'string') (el as unknown as Record<string, unknown>)[k] = v;
      else el.setAttribute(k, v === true ? '' : String(v));
    }
  }
  for (const c of children) if (c !== null && c !== undefined && c !== false) el.append(c);
  return el;
}

/** Keep editor focus when a toolbar control is pressed. */
export function keepFocus(el: HTMLElement): HTMLElement {
  el.addEventListener('mousedown', (e) => {
    const t = e.target as HTMLElement;
    if (!t.closest('input, select, textarea')) e.preventDefault();
  });
  return el;
}

let active: { el: HTMLElement; anchor: HTMLElement | null; onClose?: () => void } | null = null;

function onDocDown(e: MouseEvent): void {
  if (!active) return;
  const t = e.target as globalThis.Node;
  if (active.el.contains(t) || active.anchor?.contains(t)) return;
  closePopover();
}

function onDocKey(e: KeyboardEvent): void {
  if (e.key === 'Escape' && active) {
    e.preventDefault();
    e.stopPropagation();
    const anchor = active.anchor;
    closePopover();
    anchor?.focus();
  }
}

export function closePopover(): void {
  if (!active) return;
  const a = active;
  active = null;
  a.el.remove();
  a.anchor?.setAttribute('aria-expanded', 'false');
  document.removeEventListener('mousedown', onDocDown, true);
  document.removeEventListener('keydown', onDocKey, true);
  a.onClose?.();
}

export function popoverOpenFor(anchor: HTMLElement): boolean {
  return !!active && active.anchor === anchor;
}

/** Show `content` in a floating panel below `anchor` (or at a point). Only one is open at a time. */
export function openPopover(content: HTMLElement, at: HTMLElement | { x: number; y: number }, onClose?: () => void): HTMLElement {
  closePopover();
  const el = h('div', { class: 'amd-pop', role: 'dialog' }, content);
  document.body.appendChild(el);
  const anchor = at instanceof HTMLElement ? at : null;
  const r = anchor ? anchor.getBoundingClientRect() : { left: (at as { x: number }).x, bottom: (at as { y: number }).y };
  const w = el.offsetWidth;
  const hgt = el.offsetHeight;
  let left = r.left;
  let top = r.bottom + 4;
  if (left + w > window.innerWidth - 8) left = Math.max(8, window.innerWidth - w - 8);
  if (top + hgt > window.innerHeight - 8) top = Math.max(8, window.innerHeight - hgt - 8);
  el.style.left = `${left}px`;
  el.style.top = `${top}px`;
  anchor?.setAttribute('aria-expanded', 'true');
  active = { el, anchor, onClose };
  document.addEventListener('mousedown', onDocDown, true);
  document.addEventListener('keydown', onDocKey, true);
  const first = el.querySelector<HTMLElement>('input, select, button, [tabindex="0"]');
  first?.focus();
  return el;
}

/** A small form: labelled fields plus buttons. Returns the form element. */
export interface Field { name: string; label: string; value?: string; placeholder?: string; type?: string; options?: { value: string; label: string }[] }

export function form(fields: Field[], buttons: { label: string; primary?: boolean; onClick: (values: Record<string, string>) => void }[]): HTMLFormElement {
  const f = h('form', { class: 'amd-form' });
  const inputs: Record<string, HTMLInputElement | HTMLSelectElement> = {};
  for (const fd of fields) {
    let input: HTMLInputElement | HTMLSelectElement;
    if (fd.options) {
      input = h('select', { name: fd.name });
      for (const o of fd.options) input.append(h('option', { value: o.value }, o.label));
      input.value = fd.value ?? '';
    } else {
      input = h('input', { name: fd.name, type: fd.type ?? 'text', placeholder: fd.placeholder ?? '', spellcheck: 'false' });
      input.value = fd.value ?? '';
    }
    inputs[fd.name] = input;
    f.append(h('label', null, h('span', null, fd.label), input));
  }
  const values = () => Object.fromEntries(Object.entries(inputs).map(([k, i]) => [k, i.value]));
  const row = h('div', { class: 'amd-form-buttons' });
  for (const b of buttons) {
    const btn = h('button', { type: b.primary ? 'submit' : 'button', class: b.primary ? 'primary' : '' }, b.label);
    if (!b.primary) btn.addEventListener('click', () => b.onClick(values()));
    row.append(btn);
  }
  f.append(row);
  f.addEventListener('submit', (e) => {
    e.preventDefault();
    buttons.find((b) => b.primary)?.onClick(values());
  });
  return f;
}
