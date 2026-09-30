// Editor document model. Every top-level block type carries a `srcIdx` attribute:
// the index of the source block it was parsed from, used to keep the original
// spacing between blocks that did not change (SRS 4.4).

import { Schema, NodeSpec, MarkSpec, DOMOutputSpec } from 'prosemirror-model';
import { tableNodes } from 'prosemirror-tables';
import { buildSpanStyle, parseSpanStyle } from '../../shared/markdownIt';

const src = { srcIdx: { default: null } };

const tables = tableNodes({
  tableGroup: 'block',
  cellContent: 'paragraph',
  cellAttributes: {
    align: {
      default: null,
      getFromDOM(dom) {
        return (dom as HTMLElement).style?.textAlign || null;
      },
      setDOMAttr(value, attrs) {
        if (value) attrs.style = `${attrs.style || ''}text-align:${value};`;
      },
    },
  },
});
tables.table = { ...tables.table, attrs: { ...(tables.table.attrs || {}), ...src } };

const nodes: Record<string, NodeSpec> = {
  doc: { content: 'block+' },

  paragraph: {
    content: 'inline*',
    group: 'block',
    attrs: { ...src, align: { default: null } },
    parseDOM: [{ tag: 'p', getAttrs: (dom) => ({ align: (dom as HTMLElement).style?.textAlign || null }) }],
    toDOM(node): DOMOutputSpec {
      return node.attrs.align ? ['p', { style: `text-align:${node.attrs.align}` }, 0] : ['p', 0];
    },
  },

  title: {
    content: 'inline*',
    group: 'block',
    defining: true,
    attrs: { ...src, styleAttr: { default: null } },
    parseDOM: [{ tag: 'p.amd-title', priority: 60 }],
    toDOM: () => ['p', { class: 'amd-title' }, 0],
  },

  subtitle: {
    content: 'inline*',
    group: 'block',
    defining: true,
    attrs: { ...src, styleAttr: { default: null } },
    parseDOM: [{ tag: 'p.amd-subtitle', priority: 60 }],
    toDOM: () => ['p', { class: 'amd-subtitle' }, 0],
  },

  heading: {
    content: 'inline*',
    group: 'block',
    defining: true,
    attrs: { ...src, level: { default: 1 } },
    parseDOM: [1, 2, 3, 4, 5, 6].map((level) => ({ tag: `h${level}`, attrs: { level } })),
    toDOM: (node) => [`h${node.attrs.level}`, 0],
  },

  blockquote: {
    content: 'block+',
    group: 'block',
    defining: true,
    attrs: { ...src },
    parseDOM: [{ tag: 'blockquote' }],
    toDOM: () => ['blockquote', 0],
  },

  code_block: {
    content: 'text*',
    marks: '',
    group: 'block',
    code: true,
    defining: true,
    attrs: { ...src, params: { default: '' } },
    parseDOM: [{ tag: 'pre', preserveWhitespace: 'full', getAttrs: () => ({ params: '' }) }],
    toDOM: () => ['pre', ['code', 0]],
  },

  horizontal_rule: {
    group: 'block',
    attrs: { ...src, markup: { default: '---' } },
    parseDOM: [{ tag: 'hr' }],
    toDOM: () => ['hr'],
  },

  bullet_list: {
    content: 'list_item+',
    group: 'block',
    attrs: { ...src, tight: { default: true }, bullet: { default: '-' } },
    parseDOM: [{ tag: 'ul', getAttrs: (dom) => ({ tight: (dom as HTMLElement).hasAttribute('data-tight') }) }],
    toDOM: (node) => ['ul', { 'data-tight': node.attrs.tight ? 'true' : null }, 0],
  },

  ordered_list: {
    content: 'list_item+',
    group: 'block',
    attrs: { ...src, order: { default: 1 }, tight: { default: true } },
    parseDOM: [{
      tag: 'ol',
      getAttrs: (dom) => ({
        order: (dom as HTMLElement).hasAttribute('start') ? +(dom as HTMLElement).getAttribute('start')! : 1,
        tight: (dom as HTMLElement).hasAttribute('data-tight'),
      }),
    }],
    toDOM: (node) => ['ol', { start: node.attrs.order === 1 ? null : node.attrs.order, 'data-tight': node.attrs.tight ? 'true' : null }, 0],
  },

  list_item: {
    content: 'paragraph block*',
    defining: true,
    attrs: { checked: { default: null } },
    parseDOM: [{ tag: 'li', getAttrs: (dom) => {
      const v = (dom as HTMLElement).getAttribute('data-checked');
      return { checked: v === null ? null : v === 'true' };
    } }],
    toDOM: (node) => node.attrs.checked === null
      ? ['li', 0]
      : ['li', { class: 'amd-task', 'data-checked': String(node.attrs.checked) }, 0],
  },

  raw_block: {
    group: 'block',
    atom: true,
    selectable: true,
    attrs: { ...src, text: { default: '' } },
    parseDOM: [{ tag: 'pre.amd-raw', preserveWhitespace: 'full', getAttrs: (dom) => ({ text: (dom as HTMLElement).textContent || '' }) }],
    toDOM: (node) => ['pre', { class: 'amd-raw' }, node.attrs.text],
  },

  ...tables,

  image: {
    inline: true,
    group: 'inline',
    draggable: true,
    attrs: { src: {}, alt: { default: null }, title: { default: null }, width: { default: null } },
    parseDOM: [{
      tag: 'img[src]',
      getAttrs: (dom) => {
        const el = dom as HTMLElement;
        return { src: el.getAttribute('src'), alt: el.getAttribute('alt'), title: el.getAttribute('title'), width: el.getAttribute('width') };
      },
    }],
    toDOM: (node) => ['img', { src: node.attrs.src, alt: node.attrs.alt, title: node.attrs.title, width: node.attrs.width }],
  },

  hard_break: {
    inline: true,
    group: 'inline',
    selectable: false,
    parseDOM: [{ tag: 'br' }],
    toDOM: () => ['br'],
  },

  text: { group: 'inline' },
};

// Mark order matters: the serializer opens marks in this order, so a color span
// wraps bold text (<span style="color:...">**text**</span>, SRS FR-COLOR-06).
const marks: Record<string, MarkSpec> = {
  textStyle: {
    attrs: { color: { default: null }, bg: { default: null }, fontFamily: { default: null }, fontSize: { default: null } },
    parseDOM: [{
      tag: 'span[style]',
      getAttrs: (dom) => {
        const st = parseSpanStyle((dom as HTMLElement).getAttribute('style') || '');
        return st ? { ...st } : false;
      },
    }],
    toDOM: (mark) => ['span', { style: buildSpanStyle(mark.attrs) }, 0],
  },

  link: {
    attrs: { href: {}, title: { default: null } },
    inclusive: false,
    parseDOM: [{ tag: 'a[href]', getAttrs: (dom) => ({ href: (dom as HTMLElement).getAttribute('href'), title: (dom as HTMLElement).getAttribute('title') }) }],
    toDOM: (mark) => ['a', { href: mark.attrs.href, title: mark.attrs.title }, 0],
  },

  em: {
    parseDOM: [{ tag: 'i' }, { tag: 'em' }, { style: 'font-style=italic' }],
    toDOM: () => ['em', 0],
  },

  strong: {
    parseDOM: [{ tag: 'strong' }, { tag: 'b', getAttrs: (dom) => (dom as HTMLElement).style.fontWeight !== 'normal' && null }],
    toDOM: () => ['strong', 0],
  },

  underline: {
    parseDOM: [{ tag: 'u' }, { tag: 'ins' }],
    toDOM: () => ['u', 0],
  },

  strikethrough: {
    parseDOM: [{ tag: 's' }, { tag: 'del' }, { tag: 'strike' }],
    toDOM: () => ['s', 0],
  },

  sup: { excludes: 'sub', parseDOM: [{ tag: 'sup' }], toDOM: () => ['sup', 0] },
  sub: { excludes: 'sup', parseDOM: [{ tag: 'sub' }], toDOM: () => ['sub', 0] },

  code: {
    parseDOM: [{ tag: 'code' }],
    toDOM: () => ['code', 0],
  },

  // Inline source amir_md cannot show as formatting (unknown HTML tags, comments).
  // It is written back exactly as it was.
  rawInline: {
    parseDOM: [{ tag: 'span.amd-raw-inline' }],
    toDOM: () => ['span', { class: 'amd-raw-inline' }, 0],
  },
};

export const schema = new Schema({ nodes, marks });

export const TOP_LEVEL_WITH_SRC = [
  'paragraph', 'title', 'subtitle', 'heading', 'blockquote', 'code_block',
  'horizontal_rule', 'bullet_list', 'ordered_list', 'raw_block', 'table',
];
