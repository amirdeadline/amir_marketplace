// markdown-it setup shared by the webview codec, the tests, and the exporters.
//
// Two flavours:
//   createRefMd()   plain CommonMark + GFM tables/strikethrough with HTML enabled.
//                   Used to segment documents, resolve references, and as the
//                   reference renderer for the fidelity check.
//   createParseMd() the same, plus "amir" core rules that turn the HTML amir_md
//                   writes (color spans, <u>, <sup>, Title/Subtitle paragraphs)
//                   and task-list markers into tokens the editor understands.

import MarkdownIt from 'markdown-it';

type Token = ReturnType<MarkdownIt['parse']>[number];
type StateCore = Parameters<Parameters<MarkdownIt['core']['ruler']['push']>[1]>[0];

export function createRefMd(): MarkdownIt {
  return new MarkdownIt('default', { html: true, linkify: false, typographer: false });
}

export function createParseMd(): MarkdownIt {
  const md = createRefMd();
  // Keep link and image paths exactly as written (no percent-encoding), so an edited
  // paragraph writes `images/my pic.png` back the way the author typed it (FR-IMG-08).
  md.normalizeLink = (url: string) => url;
  md.core.ruler.after('inline', 'amir_blocks', amirBlocks);
  md.core.ruler.after('amir_blocks', 'amir_inline', amirInline);
  md.core.ruler.after('amir_inline', 'amir_tasks', amirTasks);
  return md;
}

// ---------------------------------------------------------------- styles

export interface TextStyleAttrs {
  color: string | null;
  bg: string | null;
  fontFamily: string | null;
  fontSize: string | null;
}

const STYLE_PROPS: Record<string, keyof TextStyleAttrs> = {
  color: 'color',
  'background-color': 'bg',
  'font-family': 'fontFamily',
  'font-size': 'fontSize',
};

/** Parse a span style attribute. Returns null when it holds anything amir_md cannot represent. */
export function parseSpanStyle(style: string): TextStyleAttrs | null {
  const out: TextStyleAttrs = { color: null, bg: null, fontFamily: null, fontSize: null };
  let any = false;
  for (const decl of style.split(';')) {
    const d = decl.trim();
    if (!d) continue;
    const i = d.indexOf(':');
    if (i < 0) return null;
    const prop = d.slice(0, i).trim().toLowerCase();
    const value = d.slice(i + 1).trim();
    const key = STYLE_PROPS[prop];
    if (!key || !value || out[key] !== null) return null;
    out[key] = value;
    any = true;
  }
  return any ? out : null;
}

/** Build a span style attribute in the fixed order color, background-color, font-family, font-size (SRS 4.2). */
export function buildSpanStyle(a: Partial<TextStyleAttrs>): string {
  const parts: string[] = [];
  if (a.color) parts.push(`color:${a.color};`);
  if (a.bg) parts.push(`background-color:${a.bg};`);
  if (a.fontFamily) parts.push(`font-family:${a.fontFamily};`);
  if (a.fontSize) parts.push(`font-size:${a.fontSize};`);
  return parts.join('');
}

// ---------------------------------------------------------------- HTML helpers

const ENTITY: Record<string, string> = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };

export function decodeEntities(s: string): string {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e: string) => {
    if (e[0] === '#') {
      const code = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : m;
    }
    const v = ENTITY[e.toLowerCase()];
    return v ?? m;
  });
}

export function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

interface ParsedTag {
  close: boolean;
  name: string;
  attrs: Record<string, string>;
  selfClosing: boolean;
  extraAttr: boolean; // an attribute we could not parse
}

function parseTag(html: string): ParsedTag | null {
  const m = /^<\s*(\/)?\s*([a-zA-Z][a-zA-Z0-9]*)([^>]*?)(\/)?\s*>$/.exec(html.trim());
  if (!m) return null;
  const attrs: Record<string, string> = {};
  let rest = m[3] || '';
  let extraAttr = false;
  const re = /\s*([a-zA-Z_:][-a-zA-Z0-9_:.]*)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/y;
  let pos = 0;
  while (pos < rest.length) {
    re.lastIndex = pos;
    const a = re.exec(rest);
    if (!a || a[0].length === 0) {
      if (rest.slice(pos).trim()) extraAttr = true;
      break;
    }
    attrs[a[1].toLowerCase()] = decodeEntities(a[2] ?? a[3] ?? a[4] ?? '');
    pos = re.lastIndex;
  }
  return { close: !!m[1], name: m[2].toLowerCase(), attrs, selfClosing: !!m[4], extraAttr };
}

// Paired inline tags we convert to editor marks, and the token type they become.
const PAIRED: Record<string, string> = {
  strong: 'strong', b: 'strong', em: 'em', i: 'em',
  u: 'u', ins: 'u', s: 's', strike: 's', del: 's',
  sup: 'sup', sub: 'sub', span: 'span', a: 'link', code: 'code',
};

function pairedAllowed(tag: ParsedTag): boolean {
  if (tag.extraAttr) return false;
  const keys = Object.keys(tag.attrs);
  switch (tag.name) {
    case 'span':
      return keys.length === 1 && keys[0] === 'style' && parseSpanStyle(tag.attrs.style) !== null;
    case 'a':
      return keys.includes('href') && keys.every((k) => k === 'href' || k === 'title');
    default:
      return keys.length === 0;
  }
}

// ---------------------------------------------------------------- amir_blocks

const TITLE_RE = /^<p\s+data-amir-style="(title|subtitle)"(?:\s+style="([^"]*)")?\s*>([\s\S]*?)<\/p>\s*$/;
const ALIGN_RE = /^<p\s+style="\s*text-align\s*:\s*(left|center|right|justify)\s*;?\s*"\s*>([\s\S]*?)<\/p>\s*$/;
// A line holding only an <img> tag is an HTML block in CommonMark; amir_md writes resized images that way.
const IMG_LINE_RE = /^\s*(<img\b[^>]*>)\s*$/i;

function htmlInlineTokens(state: StateCore, html: string): Token[] {
  // Tokenize inline HTML content (Title, Subtitle, aligned paragraphs) as HTML, not Markdown.
  const out: Token[] = [];
  const re = /<[^>]+>/g;
  let last = 0;
  let m: RegExpExecArray | null;
  const pushText = (s: string) => {
    if (!s) return;
    const t = new state.Token('text', '', 0);
    t.content = decodeEntities(s);
    out.push(t);
  };
  while ((m = re.exec(html))) {
    pushText(html.slice(last, m.index));
    const t = new state.Token('html_inline', '', 0);
    t.content = m[0];
    out.push(t);
    last = re.lastIndex;
  }
  pushText(html.slice(last));
  return out;
}

function amirBlocks(state: StateCore): void {
  const src = state.tokens;
  const out: Token[] = [];
  for (let i = 0; i < src.length; i++) {
    const tok = src[i];
    if (tok.type === 'html_block') {
      const content = tok.content.replace(/\r?\n$/, '');
      const img = IMG_LINE_RE.exec(content);
      if (img) {
        const open = new state.Token('paragraph_open', 'p', 1);
        open.map = tok.map;
        open.block = true;
        const inline = new state.Token('inline', '', 0);
        inline.content = img[1];
        inline.map = tok.map;
        inline.children = htmlInlineTokens(state, img[1]);
        const close = new state.Token('paragraph_close', 'p', -1);
        close.block = true;
        out.push(open, inline, close);
        continue;
      }
      const t = TITLE_RE.exec(content);
      const a = t ? null : ALIGN_RE.exec(content);
      if (t || a) {
        const kind = t ? `amir_${t[1]}` : 'paragraph';
        const open = new state.Token(`${kind}_open`, 'p', 1);
        open.map = tok.map;
        open.block = true;
        if (t && t[2] !== undefined) open.attrSet('amir-style', t[2]);
        if (a) open.attrSet('amir-align', a[1]);
        const inline = new state.Token('inline', '', 0);
        inline.content = t ? t[3] : a![2];
        inline.map = tok.map;
        inline.children = htmlInlineTokens(state, inline.content);
        const close = new state.Token(`${kind}_close`, 'p', -1);
        close.block = true;
        out.push(open, inline, close);
        continue;
      }
    }
    // GFM table cells hold inline content directly; the editor needs a paragraph in each cell.
    if ((tok.type === 'th_open' || tok.type === 'td_open') && src[i + 1]?.type === 'inline') {
      out.push(tok);
      const po = new state.Token('paragraph_open', 'p', 1);
      const pc = new state.Token('paragraph_close', 'p', -1);
      out.push(po, src[i + 1], pc);
      i++;
      continue;
    }
    if ((tok.type === 'th_open' || tok.type === 'td_open') && (src[i + 1]?.type === 'th_close' || src[i + 1]?.type === 'td_close')) {
      out.push(tok);
      out.push(new state.Token('paragraph_open', 'p', 1), new state.Token('paragraph_close', 'p', -1));
      continue;
    }
    out.push(tok);
  }
  state.tokens = out;
}

// ---------------------------------------------------------------- amir_inline

function convertInline(state: StateCore, children: Token[]): Token[] {
  // 1. softbreaks show as spaces (a hard-wrapped paragraph reads as one paragraph).
  // 2. pair recognised inline HTML tags; everything else becomes literal raw source.
  const tags = children.map((c) => (c.type === 'html_inline' ? parseTag(c.content) : null));
  const partner = new Array<number>(children.length).fill(-1);
  const stack: number[] = [];
  for (let i = 0; i < children.length; i++) {
    const tag = tags[i];
    if (!tag || tag.selfClosing || !PAIRED[tag.name]) continue;
    if (!tag.close) {
      stack.push(i);
    } else {
      for (let s = stack.length - 1; s >= 0; s--) {
        if (tags[stack[s]]!.name === tag.name) {
          partner[stack[s]] = i;
          partner[i] = stack[s];
          stack.length = s;
          break;
        }
      }
    }
  }

  const out: Token[] = [];
  const raw = (content: string) => {
    const o = new state.Token('raw_open', '', 1);
    const t = new state.Token('text', '', 0);
    t.content = content;
    const c = new state.Token('raw_close', '', -1);
    out.push(o, t, c);
  };

  for (let i = 0; i < children.length; i++) {
    const c = children[i];
    if (c.type === 'softbreak') {
      const t = new state.Token('text', '', 0);
      t.content = ' ';
      out.push(t);
      continue;
    }
    if (c.type !== 'html_inline') {
      out.push(c);
      continue;
    }
    const tag = tags[i];
    if (!tag) {
      raw(c.content);
      continue;
    }
    // void elements
    if (tag.name === 'br' && !tag.close && Object.keys(tag.attrs).length === 0) {
      out.push(new state.Token('hardbreak', 'br', 0));
      continue;
    }
    if (tag.name === 'img' && !tag.close && tag.attrs.src && !tag.extraAttr &&
        Object.keys(tag.attrs).every((k) => ['src', 'alt', 'title', 'width'].includes(k))) {
      const img = new state.Token('image', 'img', 0);
      img.attrSet('src', tag.attrs.src);
      if (tag.attrs.title) img.attrSet('title', tag.attrs.title);
      if (tag.attrs.width) img.attrSet('width', tag.attrs.width);
      img.attrSet('amir-html', 'true');
      img.content = tag.attrs.alt ?? '';
      img.children = [];
      out.push(img);
      continue;
    }
    const p = partner[i];
    const kind = PAIRED[tag.name];
    if (p < 0 || !kind) {
      raw(c.content);
      continue;
    }
    const openTag = tag.close ? tags[p]! : tag;
    if (!pairedAllowed(openTag)) {
      raw(c.content);
      continue;
    }
    if (kind === 'code') {
      // <code>text</code> with plain text only becomes an inline code span.
      if (tag.close) continue; // handled at the open tag
      const inner = children.slice(i + 1, p);
      if (inner.every((x) => x.type === 'text')) {
        const t = new state.Token('code_inline', 'code', 0);
        t.content = inner.map((x) => x.content).join('');
        out.push(t);
        i = p;
      } else {
        raw(c.content);
        partner[p] = -1; // its close becomes raw too
      }
      continue;
    }
    const t = new state.Token(`${kind}_${tag.close ? 'close' : 'open'}`, tag.name, tag.close ? -1 : 1);
    if (!tag.close) {
      if (kind === 'span') {
        const st = parseSpanStyle(tag.attrs.style)!;
        if (st.color) t.attrSet('amir-color', st.color);
        if (st.bg) t.attrSet('amir-bg', st.bg);
        if (st.fontFamily) t.attrSet('amir-font', st.fontFamily);
        if (st.fontSize) t.attrSet('amir-size', st.fontSize);
      } else if (kind === 'link') {
        t.attrSet('href', tag.attrs.href);
        if (tag.attrs.title) t.attrSet('title', tag.attrs.title);
      }
    }
    out.push(t);
  }
  return out;
}

function amirInline(state: StateCore): void {
  for (const tok of state.tokens) {
    if (tok.type === 'inline' && tok.children) tok.children = convertInline(state, tok.children);
  }
}

// ---------------------------------------------------------------- amir_tasks

function amirTasks(state: StateCore): void {
  const t = state.tokens;
  for (let i = 0; i + 2 < t.length; i++) {
    if (t[i].type !== 'list_item_open' || t[i + 1].type !== 'paragraph_open' || t[i + 2].type !== 'inline') continue;
    const inline = t[i + 2];
    const first = inline.children?.[0];
    if (!first || first.type !== 'text') continue;
    const m = /^\[([ xX])\] /.exec(first.content);
    if (!m) continue;
    t[i].attrSet('amir-checked', m[1] === ' ' ? 'false' : 'true');
    first.content = first.content.slice(4);
  }
}

// ---------------------------------------------------------------- task-list rendering (export)

/** Render "- [ ] item" as a checkbox in exported HTML. */
export function taskListRenderPlugin(md: MarkdownIt): void {
  md.core.ruler.after('inline', 'amir_task_render', (state) => {
    const t = state.tokens;
    for (let i = 0; i + 2 < t.length; i++) {
      if (t[i].type !== 'list_item_open' || t[i + 2].type !== 'inline') continue;
      const first = t[i + 2].children?.[0];
      if (!first || first.type !== 'text') continue;
      const m = /^\[([ xX])\] /.exec(first.content);
      if (!m) continue;
      first.content = first.content.slice(4);
      const box = new state.Token('html_inline', '', 0);
      box.content = `<input type="checkbox" disabled${m[1] === ' ' ? '' : ' checked'}> `;
      t[i + 2].children!.unshift(box);
      t[i].attrJoin('class', 'task-item');
    }
  });
}
