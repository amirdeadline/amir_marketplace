// Markdown writer for one top-level block (SRS 4.2 and 4.3).
//
// Three escaping modes, tried in order by document.ts. Each result is parsed back
// and kept only if it gives the same content:
//   minimal  escape a character only where it would otherwise change meaning;
//            brackets are left alone, so [^1] footnotes and [{C-3101: ...}]
//            review comments keep their exact text
//   guarded  minimal, plus [ when it could start a link or definition
//   full     prosemirror-markdown's escaping plus < and entity-like &

import { MarkdownSerializerState } from 'prosemirror-markdown';
import { Mark, Node } from 'prosemirror-model';
import { schema } from './schema';
import { buildSpanStyle } from '../../shared/markdownIt';

export interface SerializeOptions {
  bulletMarker: string;
  emphasisMarker: string;
  strongMarker: string;
}

export type EscMode = 'minimal' | 'guarded' | 'full';
export const ESC_MODES: EscMode[] = ['minimal', 'guarded', 'full'];

const ASCII_PUNCT = /[!-/:-@[-`{-~]/;

function textEsc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function attrEsc(s: string): string {
  return textEsc(s).replace(/"/g, '&quot;');
}

function escLineStart(s: string): string {
  return s
    .replace(/^(\s*)([-+*])(\s|$)/, '$1\\$2$3')
    .replace(/^(\s*)(#{1,6})(\s|$)/, '$1\\$2$3')
    .replace(/^(\s*\d+)([.)])(\s|$)/, '$1\\$2$3')
    .replace(/^(\s*)>/, '$1\\>')
    .replace(/^(\s*)(=+|-+)(\s*)$/, '$1\\$2$3');
}

function minimalEsc(str: string, startOfLine: boolean, guardBrackets: boolean): string {
  let out = '';
  for (let i = 0; i < str.length; i++) {
    const c = str[i];
    const prev = str[i - 1];
    const next = str[i + 1];
    switch (c) {
      case '\\':
        out += next === undefined || ASCII_PUNCT.test(next) ? '\\\\' : c;
        break;
      case '`':
        out += '\\`';
        break;
      case '*':
        out += prev !== undefined && /\s/.test(prev) && next !== undefined && /\s/.test(next) ? c : '\\*';
        break;
      case '_': {
        const intraword = prev !== undefined && next !== undefined && /\w/.test(prev) && /\w/.test(next);
        const spaced = prev !== undefined && next !== undefined && /\s/.test(prev) && /\s/.test(next);
        out += intraword || spaced ? c : '\\_';
        break;
      }
      case '~':
        out += prev === '~' || next === '~' ? '\\~' : c;
        break;
      case '[': {
        const j = guardBrackets ? str.indexOf(']', i + 1) : -1;
        const risky = j >= 0 && (str[j + 1] === '(' || str[j + 1] === '[' || str[j + 1] === ':');
        out += risky ? '\\[' : c;
        break;
      }
      case '<':
        out += next !== undefined && /[A-Za-z/!?]/.test(next) ? '\\<' : c;
        break;
      case '&':
        out += /^&(#\d+|#x[0-9a-f]+|[a-z][a-z0-9]*);/i.test(str.slice(i)) ? '\\&' : c;
        break;
      default:
        out += c;
    }
  }
  return startOfLine ? escLineStart(out) : out;
}

function fullEsc(str: string, startOfLine: boolean): string {
  let s = str.replace(/[`*\\~\[\]_]/g, (m, i: number) =>
    m === '_' && i > 0 && i + 1 < str.length && /\w/.test(str[i - 1]) && /\w/.test(str[i + 1]) ? m : '\\' + m);
  s = s.replace(/<(?=[A-Za-z/!?])/g, '\\<').replace(/&(?=(#\d+|#x[0-9a-f]+|[a-z][a-z0-9]*);)/gi, '\\&');
  return startOfLine ? escLineStart(s) : s;
}

// MarkdownSerializerState's constructor is internal in the typings; describe it here.
const StateBase = MarkdownSerializerState as unknown as new (
  nodes: Record<string, unknown>,
  marks: Record<string, unknown>,
  options: Record<string, unknown>,
) => MarkdownSerializerState;

class AmirState extends StateBase {
  escMode: EscMode = 'minimal';
  esc(str: string, startOfLine = false): string {
    return this.escMode === 'full' ? fullEsc(str, startOfLine) : minimalEsc(str, startOfLine, this.escMode === 'guarded');
  }
}

// `out` and `inAutolink` are internal to prosemirror-markdown's typings.
type S = AmirState & { inAutolink?: boolean; out: string };

function backticksFor(node: Node, side: number): string {
  const ticks = /`+/g;
  let m: RegExpExecArray | null;
  let len = 0;
  if (node.isText) while ((m = ticks.exec(node.text!))) len = Math.max(len, m[0].length);
  let result = len > 0 && side > 0 ? ' `' : '`';
  for (let i = 0; i < len; i++) result += '`';
  if (len > 0 && side < 0) result += ' ';
  return result;
}

function isPlainURL(link: Mark, parent: Node, index: number): boolean {
  if (link.attrs.title || !/^\w+:/.test(link.attrs.href)) return false;
  const content = parent.child(index);
  if (!content.isText || content.text !== link.attrs.href || content.marks[content.marks.length - 1] !== link) return false;
  return index === parent.childCount - 1 || !link.isInSet(parent.child(index + 1).marks);
}

// ---------------------------------------------------------------- inline HTML (Title, Subtitle, aligned paragraphs)

function markHtml(m: Mark): [string, string] {
  switch (m.type.name) {
    case 'strong': return ['<strong>', '</strong>'];
    case 'em': return ['<em>', '</em>'];
    case 'underline': return ['<u>', '</u>'];
    case 'strikethrough': return ['<s>', '</s>'];
    case 'sup': return ['<sup>', '</sup>'];
    case 'sub': return ['<sub>', '</sub>'];
    case 'code': return ['<code>', '</code>'];
    case 'textStyle': return [`<span style="${buildSpanStyle(m.attrs)}">`, '</span>'];
    case 'link': return [`<a href="${attrEsc(m.attrs.href)}"${m.attrs.title ? ` title="${attrEsc(m.attrs.title)}"` : ''}>`, '</a>'];
    default: return ['', ''];
  }
}

function imgHtml(node: Node): string {
  const a = node.attrs;
  return `<img src="${attrEsc(a.src)}"${a.alt ? ` alt="${attrEsc(a.alt)}"` : ''}${a.title ? ` title="${attrEsc(a.title)}"` : ''}${a.width ? ` width="${attrEsc(String(a.width))}"` : ''}>`;
}

export function inlineHtml(node: Node): string {
  let out = '';
  node.forEach((child) => {
    if (child.type.name === 'hard_break') { out += '<br>'; return; }
    if (child.type.name === 'image') { out += imgHtml(child); return; }
    if (!child.isText) return;
    const raw = child.marks.some((m) => m.type.name === 'rawInline');
    let open = '';
    let close = '';
    for (const m of child.marks) {
      if (m.type.name === 'rawInline') continue;
      const [o, c] = markHtml(m);
      open += o;
      close = c + close;
    }
    out += open + (raw ? child.text! : textEsc(child.text!)) + close;
  });
  return out;
}

/** Default inline style for new Title and Subtitle paragraphs, so other viewers show them large. */
export const STYLED_DEFAULTS: Record<'title' | 'subtitle', string> = {
  title: 'font-size:26pt;',
  subtitle: 'font-size:15pt;color:#595959;',
};

function styledParagraph(kind: 'title' | 'subtitle', node: Node): string {
  const style: string | null = node.attrs.styleAttr;
  return `<p data-amir-style="${kind}"${style !== null ? ` style="${attrEsc(style)}"` : ''}>${inlineHtml(node)}</p>`;
}

// ---------------------------------------------------------------- tables

function cellMarkdown(cell: Node, opts: SerializeOptions, mode: EscMode): string {
  const para = cell.firstChild;
  if (!para) return '';
  const st = newState(opts, mode);
  st.renderInline(para);
  return st.out
    .replace(/\\\n/g, '<br>')
    .replace(/\n/g, ' ')
    .replace(/(^|[^\\])\|/g, '$1\\|')
    .replace(/(^|[^\\])\|/g, '$1\\|')
    .trim();
}

function alignDelim(a: string | null): string {
  switch (a) {
    case 'left': return ':---';
    case 'center': return ':---:';
    case 'right': return '---:';
    default: return '---';
  }
}

function writeTable(state: S, table: Node, opts: SerializeOptions): void {
  const rows: string[][] = [];
  const aligns: (string | null)[] = [];
  table.forEach((row, _o, r) => {
    const cells: string[] = [];
    row.forEach((cell) => {
      if (r === 0) aligns.push(cell.attrs.align);
      cells.push(cellMarkdown(cell, opts, state.escMode));
    });
    rows.push(cells);
  });
  const width = Math.max(1, ...rows.map((r) => r.length));
  const line = (cells: string[]) => {
    const padded = cells.concat(new Array(Math.max(0, width - cells.length)).fill(''));
    return '| ' + padded.join(' | ') + ' |';
  };
  const delim = '|' + Array.from({ length: width }, (_v, i) => alignDelim(aligns[i] ?? null)).join('|') + '|';
  const lines = [line(rows[0] || []), delim, ...rows.slice(1).map(line)];
  state.text(lines.join('\n'), false);
}

// ---------------------------------------------------------------- node and mark writers

function nodeWriters(opts: SerializeOptions): Record<string, (state: S, node: Node, parent: Node, index: number) => void> {
  return {
    blockquote(state, node) {
      state.wrapBlock('> ', null, node, () => state.renderContent(node));
    },
    code_block(state, node) {
      const backticks = node.textContent.match(/`{3,}/gm);
      const fence = backticks ? backticks.sort().slice(-1)[0] + '`' : '```';
      state.write(fence + (node.attrs.params || '') + '\n');
      state.text(node.textContent, false);
      state.write('\n');
      state.write(fence);
      state.closeBlock(node);
    },
    heading(state, node) {
      state.write(state.repeat('#', node.attrs.level) + ' ');
      state.renderInline(node, false);
      state.closeBlock(node);
    },
    horizontal_rule(state, node) {
      state.write(node.attrs.markup || '---');
      state.closeBlock(node);
    },
    bullet_list(state, node) {
      const bullet = node.attrs.bullet || opts.bulletMarker || '-';
      state.renderList(node, '  ', () => bullet + ' ');
    },
    ordered_list(state, node) {
      const start = node.attrs.order ?? 1;
      const maxW = String(start + node.childCount - 1).length;
      const space = state.repeat(' ', maxW + 2);
      state.renderList(node, space, (i) => {
        const n = String(start + i);
        return state.repeat(' ', maxW - n.length) + n + '. ';
      });
    },
    list_item(state, node) {
      if (node.attrs.checked !== null) state.write(node.attrs.checked ? '[x] ' : '[ ] ');
      state.renderContent(node);
    },
    paragraph(state, node) {
      if (node.attrs.align) {
        state.write(`<p style="text-align:${node.attrs.align};">${inlineHtml(node)}</p>`);
      } else {
        state.renderInline(node);
      }
      state.closeBlock(node);
    },
    title(state, node) {
      state.write(styledParagraph('title', node));
      state.closeBlock(node);
    },
    subtitle(state, node) {
      state.write(styledParagraph('subtitle', node));
      state.closeBlock(node);
    },
    image(state, node) {
      const a = node.attrs;
      if (a.width) {
        state.write(imgHtml(node));
        return;
      }
      const src: string = a.src || '';
      const dest = /[\s<>]/.test(src) ? `<${src.replace(/[<>]/g, '')}>` : src.replace(/[()]/g, '\\$&');
      const alt = (a.alt || '').replace(/[\\[\]]/g, '\\$&');
      state.write('![' + alt + '](' + dest + (a.title ? ` "${String(a.title).replace(/"/g, '\\"')}"` : '') + ')');
    },
    hard_break(state, node, parent, index) {
      for (let i = index + 1; i < parent.childCount; i++) {
        if (parent.child(i).type !== node.type) {
          state.write('\\\n');
          return;
        }
      }
    },
    text(state, node) {
      state.text(node.text!, !state.inAutolink);
    },
    raw_block(state, node) {
      state.text(node.attrs.text, false);
      state.closeBlock(node);
    },
    table(state, node) {
      writeTable(state, node, opts);
      state.closeBlock(node);
    },
  };
}

function markWriters(opts: SerializeOptions): Record<string, unknown> {
  return {
    textStyle: {
      open: (_s: S, mark: Mark) => `<span style="${buildSpanStyle(mark.attrs)}">`,
      close: '</span>',
    },
    link: {
      open(state: S, mark: Mark, parent: Node, index: number) {
        state.inAutolink = isPlainURL(mark, parent, index);
        return state.inAutolink ? '<' : '[';
      },
      close(state: S, mark: Mark) {
        const inAutolink = state.inAutolink;
        state.inAutolink = undefined;
        return inAutolink
          ? '>'
          : '](' + String(mark.attrs.href).replace(/[()"\s]/g, (c) => (c === ' ' ? '%20' : '\\' + c)) +
              (mark.attrs.title ? ` "${String(mark.attrs.title).replace(/"/g, '\\"')}"` : '') + ')';
      },
      mixable: true,
    },
    em: { open: opts.emphasisMarker || '*', close: opts.emphasisMarker || '*', mixable: true, expelEnclosingWhitespace: true },
    strong: { open: opts.strongMarker || '**', close: opts.strongMarker || '**', mixable: true, expelEnclosingWhitespace: true },
    underline: { open: '<u>', close: '</u>' },
    strikethrough: { open: '~~', close: '~~', mixable: true, expelEnclosingWhitespace: true },
    sup: { open: '<sup>', close: '</sup>' },
    sub: { open: '<sub>', close: '</sub>' },
    code: {
      open: (_s: S, _m: Mark, parent: Node, index: number) => backticksFor(parent.child(index), -1),
      close: (_s: S, _m: Mark, parent: Node, index: number) => backticksFor(parent.child(index - 1), 1),
      escape: false,
    },
    rawInline: { open: '', close: '', escape: false },
  };
}

const writerCache = new Map<string, { nodes: Record<string, unknown>; marks: Record<string, unknown> }>();

function newState(opts: SerializeOptions, mode: EscMode): S {
  const key = `${opts.bulletMarker}|${opts.emphasisMarker}|${opts.strongMarker}`;
  let w = writerCache.get(key);
  if (!w) {
    w = { nodes: nodeWriters(opts), marks: markWriters(opts) };
    writerCache.set(key, w);
  }
  const st = new AmirState(w.nodes, w.marks, { tightLists: true, hardBreakNodeName: 'hard_break', strict: true }) as S;
  st.escMode = mode;
  return st;
}

/** Serialize one top-level block to Markdown with "\n" line endings and no trailing newline. */
export function renderBlock(node: Node, opts: SerializeOptions, mode: EscMode): string {
  const st = newState(opts, mode);
  st.renderContent(schema.node('doc', null, [node]));
  return st.out.replace(/\n+$/, '');
}
