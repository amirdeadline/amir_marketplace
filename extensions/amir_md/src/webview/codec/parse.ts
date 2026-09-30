// Markdown to editor nodes, one top-level block at a time.

import { MarkdownParser } from 'prosemirror-markdown';
import { Mark, Node } from 'prosemirror-model';
import { schema } from './schema';
import { createParseMd } from '../../shared/markdownIt';

type Tok = { attrGet(n: string): string | null; tag: string; markup: string; info: string; content: string; children: Tok[] | null; hidden: boolean; type: string };

const md = createParseMd();

function listIsTight(tokens: Tok[], i: number): boolean {
  while (++i < tokens.length) if (tokens[i].type !== 'list_item_open') return tokens[i].hidden;
  return false;
}

function alignOf(tok: Tok): string | null {
  const m = /text-align\s*:\s*(left|center|right)/.exec(tok.attrGet('style') || '');
  return m ? m[1] : null;
}

/* eslint-disable @typescript-eslint/no-explicit-any */
export const pmParser = new MarkdownParser(schema, md, {
  blockquote: { block: 'blockquote' },
  paragraph: { block: 'paragraph', getAttrs: (tok: any) => ({ align: tok.attrGet('amir-align') }) },
  amir_title: { block: 'title', getAttrs: (tok: any) => ({ styleAttr: tok.attrGet('amir-style') }) },
  amir_subtitle: { block: 'subtitle', getAttrs: (tok: any) => ({ styleAttr: tok.attrGet('amir-style') }) },
  list_item: {
    block: 'list_item',
    getAttrs: (tok: any) => {
      const c = tok.attrGet('amir-checked');
      return { checked: c === null ? null : c === 'true' };
    },
  },
  bullet_list: { block: 'bullet_list', getAttrs: (tok: any, tokens: any, i: number) => ({ tight: listIsTight(tokens, i), bullet: tok.markup || '-' }) },
  ordered_list: {
    block: 'ordered_list',
    getAttrs: (tok: any, tokens: any, i: number) => ({ order: +(tok.attrGet('start') || 1), tight: listIsTight(tokens, i) }),
  },
  heading: { block: 'heading', getAttrs: (tok: any) => ({ level: +tok.tag.slice(1) }) },
  code_block: { block: 'code_block', noCloseToken: true },
  fence: { block: 'code_block', getAttrs: (tok: any) => ({ params: tok.info || '' }), noCloseToken: true },
  hr: { node: 'horizontal_rule', getAttrs: (tok: any) => ({ markup: tok.markup || '---' }) },
  image: {
    node: 'image',
    getAttrs: (tok: any) => ({
      src: tok.attrGet('src'),
      title: tok.attrGet('title') || null,
      alt: (tok.children && tok.children.length ? tok.children.map((c: Tok) => c.content).join('') : tok.content) || null,
      width: tok.attrGet('width') || null,
    }),
  },
  hardbreak: { node: 'hard_break' },
  em: { mark: 'em' },
  strong: { mark: 'strong' },
  s: { mark: 'strikethrough' },
  u: { mark: 'underline' },
  sup: { mark: 'sup' },
  sub: { mark: 'sub' },
  span: {
    mark: 'textStyle',
    getAttrs: (tok: any) => ({
      color: tok.attrGet('amir-color'),
      bg: tok.attrGet('amir-bg'),
      fontFamily: tok.attrGet('amir-font'),
      fontSize: tok.attrGet('amir-size'),
    }),
  },
  raw: { mark: 'rawInline' },
  link: { mark: 'link', getAttrs: (tok: any) => ({ href: tok.attrGet('href'), title: tok.attrGet('title') || null }) },
  code_inline: { mark: 'code', noCloseToken: true },
  table: { block: 'table' },
  thead: { ignore: true },
  tbody: { ignore: true },
  tr: { block: 'table_row' },
  th: { block: 'table_header', getAttrs: (tok: any) => ({ align: alignOf(tok) }) },
  td: { block: 'table_cell', getAttrs: (tok: any) => ({ align: alignOf(tok) }) },
} as any);
/* eslint-enable @typescript-eslint/no-explicit-any */

export interface MdEnv {
  references?: Record<string, unknown>;
}

/** Parse one block's source. Returns null if it is not exactly one supported block. */
export function parseBlock(source: string, env: MdEnv): Node | null {
  try {
    const doc = pmParser.parse(source, { references: env.references || {} });
    if (doc.childCount !== 1) return null;
    return doc.firstChild;
  } catch {
    return null;
  }
}

function attrsEqual(a: Record<string, unknown>, b: Record<string, unknown>): boolean {
  for (const k of Object.keys(a)) {
    if (k === 'srcIdx') continue;
    const x = a[k] ?? null;
    const y = b[k] ?? null;
    if (x !== y && String(x) !== String(y)) return false;
  }
  return true;
}

/** Structural equality that ignores the srcIdx bookkeeping attribute. */
export function sameContent(a: Node, b: Node): boolean {
  if (a.type !== b.type || !attrsEqual(a.attrs, b.attrs) || !Mark.sameSet(a.marks, b.marks)) return false;
  if (a.isText) return a.text === b.text;
  if (a.childCount !== b.childCount) return false;
  for (let i = 0; i < a.childCount; i++) if (!sameContent(a.child(i), b.child(i))) return false;
  return true;
}
