// Word export (FR-EXPORT-04). Walks markdown-it tokens (with the amir rules, so color
// spans, underline, Title and Subtitle arrive as tokens) and builds a .docx with the
// docx library. Title, Subtitle, and Heading 1 to 6 use Word's built-in style names,
// and headings carry outline levels, so Word's own heading collapse works.

import * as fs from 'fs';
import {
  AlignmentType, Bookmark, BorderStyle, Document, ExternalHyperlink, Footer, HeadingLevel, ImageRun,
  InternalHyperlink, LevelFormat, Packer, PageNumber, Paragraph, ParagraphChild, ShadingType, Table,
  TableCell, TableRow, TextRun, WidthType,
} from 'docx';
import { createParseMd } from '../../shared/markdownIt';
import { slugger } from '../../shared/slug';
import { imageSize, kindOf, resolveLocalImage, stripFrontMatter } from './images';

type Token = ReturnType<ReturnType<typeof createParseMd>['parse']>[number];
type Block = Paragraph | Table;

export interface DocxOptions {
  title: string;
  docDir: string | null;
  pageSize: 'Letter' | 'A4';
  marginMm: number;
  pageNumbers: boolean;
}

export interface DocxResult {
  buffer: Buffer;
  sourceBlocks: number;
  missingImages: string[];
}

interface Fmt {
  bold?: boolean;
  italics?: boolean;
  underline?: boolean;
  strike?: boolean;
  superScript?: boolean;
  subScript?: boolean;
  color?: string;
  fill?: string;
  font?: string;
  size?: number;
  code?: boolean;
  link?: boolean;
}

interface Ctx {
  quote: number;
  lists: { ordered: boolean; reference: string; instance: number }[];
  item: { first: boolean; checked: string | null } | null;
}

const PAGE = { Letter: { width: 12240, height: 15840 }, A4: { width: 11906, height: 16838 } };
const TWIPS_PER_MM = 56.6929;
const HEADINGS = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4, HeadingLevel.HEADING_5, HeadingLevel.HEADING_6];
const ALIGN: Record<string, (typeof AlignmentType)[keyof typeof AlignmentType]> = {
  left: AlignmentType.LEFT, center: AlignmentType.CENTER, right: AlignmentType.RIGHT, justify: AlignmentType.JUSTIFIED,
};

const NAMED: Record<string, string> = {
  black: '000000', white: 'FFFFFF', red: 'FF0000', green: '008000', blue: '0000FF', yellow: 'FFFF00', orange: 'FFA500',
  purple: '800080', gray: '808080', grey: '808080', silver: 'C0C0C0', maroon: '800000', olive: '808000', lime: '00FF00',
  aqua: '00FFFF', cyan: '00FFFF', teal: '008080', navy: '000080', fuchsia: 'FF00FF', magenta: 'FF00FF', brown: 'A52A2A',
  pink: 'FFC0CB', gold: 'FFD700', darkred: '8B0000', darkgreen: '006400', darkblue: '00008B', crimson: 'DC143C',
};

/** CSS color (hex, rgb(), or a common name) to Word's RRGGBB, or undefined. */
export function cssColor(value: string | null | undefined): string | undefined {
  if (!value) return undefined;
  const v = value.trim().toLowerCase();
  let m = /^#([0-9a-f])([0-9a-f])([0-9a-f])$/.exec(v);
  if (m) return `${m[1]}${m[1]}${m[2]}${m[2]}${m[3]}${m[3]}`.toUpperCase();
  m = /^#([0-9a-f]{6})$/.exec(v);
  if (m) return m[1].toUpperCase();
  m = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/.exec(v);
  if (m) return [m[1], m[2], m[3]].map((n) => Math.min(255, +n).toString(16).padStart(2, '0')).join('').toUpperCase();
  return NAMED[v];
}

/** CSS font size to half-points (Word's unit). */
export function halfPoints(value: string | null | undefined, basePt = 11): number | undefined {
  if (!value) return undefined;
  const m = /^([\d.]+)\s*(pt|px|em|rem|%)?$/i.exec(value.trim());
  if (!m) return undefined;
  const n = parseFloat(m[1]);
  const unit = (m[2] || 'px').toLowerCase();
  const pt = unit === 'pt' ? n : unit === 'px' ? n * 0.75 : unit === '%' ? (basePt * n) / 100 : basePt * n;
  return Math.max(2, Math.round(pt * 2));
}

function firstFont(value: string | null): string | undefined {
  if (!value) return undefined;
  return value.split(',')[0].trim().replace(/^["']|["']$/g, '') || undefined;
}

/** Word bookmark names: start with a letter, letters, digits, and underscores, at most 40 characters. */
export function bookmarkId(slug: string): string {
  return `h_${slug.replace(/[^A-Za-z0-9_]/g, '_')}`.slice(0, 40);
}

function closeIndex(tokens: Token[], i: number): number {
  const type = tokens[i].type.replace(/_open$/, '_close');
  const level = tokens[i].level;
  for (let j = i + 1; j < tokens.length; j++) if (tokens[j].type === type && tokens[j].level === level) return j;
  return tokens.length - 1;
}

class Builder {
  sourceBlocks = 0;
  missing: string[] = [];
  numberStarts = new Set<number>();
  private instances = 0;
  private slug = slugger();

  constructor(private docDir: string | null, private maxWidthPx: number) {}

  // ---------------------------------------------------------------- inline

  private run(text: string, f: Fmt): TextRun {
    return new TextRun({
      text,
      style: f.link ? 'Hyperlink' : undefined,
      bold: f.bold,
      italics: f.italics,
      underline: f.underline ? {} : undefined,
      strike: f.strike,
      superScript: f.superScript,
      subScript: f.subScript,
      color: f.link ? undefined : f.color,
      shading: f.fill || f.code ? { type: ShadingType.CLEAR, color: 'auto', fill: f.fill ?? 'F2F2F2' } : undefined,
      font: f.code ? 'Consolas' : f.font,
      size: f.size,
    });
  }

  private image(tok: Token): ParagraphChild {
    const src = tok.attrGet('src') || '';
    const alt = (tok.children?.map((c) => c.content).join('') || tok.content || '').trim();
    const placeholder = (why: string) => new TextRun({ text: `[${alt || 'image'}${why}]`, italics: true, color: '808080' });
    const file = resolveLocalImage(src, this.docDir);
    if (!file) {
      this.missing.push(src);
      return placeholder('');
    }
    const kind = kindOf(file);
    if (kind !== 'png' && kind !== 'jpg' && kind !== 'gif' && kind !== 'bmp') return placeholder(`: ${kind ?? 'unknown'} images are not embedded`);
    const data = fs.readFileSync(file);
    const size = imageSize(data) ?? { width: 480, height: 360 };
    let w = Number(tok.attrGet('width')) || size.width;
    let hgt = (size.height * w) / Math.max(1, size.width);
    if (w > this.maxWidthPx) {
      hgt = (hgt * this.maxWidthPx) / w;
      w = this.maxWidthPx;
    }
    return new ImageRun({ type: kind, data, transformation: { width: Math.round(w), height: Math.round(hgt) }, altText: { name: alt || 'image', description: alt, title: alt } });
  }

  inline(children: Token[] | null | undefined, base: Fmt = {}): ParagraphChild[] {
    const out: ParagraphChild[] = [];
    const stack: Fmt[] = [base];
    let link: { href: string; runs: ParagraphChild[] } | null = null;
    let skipText = false;
    const cur = () => stack[stack.length - 1];
    const push = (c: ParagraphChild) => (link ? link.runs : out).push(c);
    const open = (patch: Fmt) => stack.push({ ...cur(), ...patch });
    const close = () => { if (stack.length > 1) stack.pop(); };
    for (const c of children ?? []) {
      switch (c.type) {
        case 'text':
          if (skipText) { skipText = false; break; }
          if (c.content) push(this.run(c.content, cur()));
          break;
        case 'softbreak': push(this.run(' ', cur())); break;
        case 'hardbreak': push(new TextRun({ text: '', break: 1 })); break;
        case 'code_inline': push(this.run(c.content, { ...cur(), code: true })); break;
        case 'strong_open': open({ bold: true }); break;
        case 'em_open': open({ italics: true }); break;
        case 'u_open': open({ underline: true }); break;
        case 's_open': open({ strike: true }); break;
        case 'sup_open': open({ superScript: true, subScript: false }); break;
        case 'sub_open': open({ subScript: true, superScript: false }); break;
        case 'span_open': {
          const patch: Fmt = {};
          const color = cssColor(c.attrGet('amir-color'));
          const fill = cssColor(c.attrGet('amir-bg'));
          const font = firstFont(c.attrGet('amir-font'));
          const size = halfPoints(c.attrGet('amir-size'));
          if (color) patch.color = color;
          if (fill) patch.fill = fill;
          if (font) patch.font = font;
          if (size) patch.size = size;
          open(patch);
          break;
        }
        case 'link_open':
          link = { href: c.attrGet('href') || '', runs: [] };
          open({ link: true });
          break;
        case 'link_close':
          close();
          if (link) {
            out.push(...this.hyperlink(link.href, link.runs));
            link = null;
          }
          break;
        case 'image': push(this.image(c)); break;
        case 'raw_open': skipText = true; break; // inline HTML Word cannot show; its text is markup
        case 'strong_close': case 'em_close': case 'u_close': case 's_close':
        case 'sup_close': case 'sub_close': case 'span_close':
          close();
          break;
        default:
          break;
      }
    }
    if (link) out.push(...link.runs);
    return out;
  }

  private hyperlink(href: string, runs: ParagraphChild[]): ParagraphChild[] {
    if (href.startsWith('#')) return [new InternalHyperlink({ anchor: bookmarkId(href.slice(1)), children: runs as TextRun[] })];
    if (/^(https?|mailto):/i.test(href) || !/^[a-z][a-z0-9+.-]*:/i.test(href)) return [new ExternalHyperlink({ link: href, children: runs })];
    return runs; // unsafe or unknown schemes become plain text
  }

  // ---------------------------------------------------------------- blocks

  private paraProps(ctx: Ctx): Record<string, unknown> {
    const props: Record<string, unknown> = {};
    const depth = ctx.lists.length;
    let left = 0;
    if (depth && ctx.item?.first) {
      const l = ctx.lists[depth - 1];
      props.numbering = { reference: l.reference, level: Math.min(depth - 1, 8), instance: l.instance };
    } else if (depth) {
      left += 720 * depth;
    }
    if (ctx.quote) {
      left += 360 * ctx.quote;
      props.border = { left: { style: BorderStyle.SINGLE, size: 12, color: 'BFBFBF', space: 8 } };
    }
    if (left) props.indent = { left };
    return props;
  }

  private taskPrefix(ctx: Ctx): ParagraphChild[] {
    if (!ctx.item?.first || ctx.item.checked === null) return [];
    return [new TextRun({ text: ctx.item.checked === 'true' ? '☒ ' : '☐ ' })];
  }

  private monospace(text: string, ctx: Ctx): Paragraph {
    const lines = text.replace(/\r?\n$/, '').split(/\r?\n/);
    return new Paragraph({ ...this.paraProps(ctx), style: 'AmirCode', children: lines.map((l, i) => new TextRun({ text: l, break: i ? 1 : 0 })) });
  }

  blocks(tokens: Token[], from: number, to: number, ctx: Ctx): Block[] {
    const out: Block[] = [];
    for (let i = from; i < to; i++) {
      const t = tokens[i];
      switch (t.type) {
        case 'heading_open': {
          const inl = tokens[i + 1];
          const level = Number(t.tag.slice(1));
          const text = (inl.children ?? []).filter((c) => c.type === 'text' || c.type === 'code_inline').map((c) => c.content).join('');
          out.push(new Paragraph({
            ...this.paraProps(ctx),
            heading: HEADINGS[level - 1],
            children: [new Bookmark({ id: bookmarkId(this.slug(text)), children: this.inline(inl.children) })],
          }));
          i = closeIndex(tokens, i);
          break;
        }
        case 'amir_title_open':
        case 'amir_subtitle_open': {
          const kids = this.inline(tokens[i + 1].children);
          out.push(t.type === 'amir_title_open'
            ? new Paragraph({ heading: HeadingLevel.TITLE, children: kids })
            : new Paragraph({ style: 'Subtitle', children: kids }));
          i = closeIndex(tokens, i);
          break;
        }
        case 'paragraph_open': {
          const align = t.attrGet('amir-align');
          out.push(new Paragraph({
            ...this.paraProps(ctx),
            alignment: align ? ALIGN[align] : undefined,
            children: [...this.taskPrefix(ctx), ...this.inline(tokens[i + 1].children)],
          }));
          if (ctx.item) ctx.item.first = false;
          i = closeIndex(tokens, i);
          break;
        }
        case 'bullet_list_open':
        case 'ordered_list_open': {
          const end = closeIndex(tokens, i);
          const ordered = t.type === 'ordered_list_open';
          const start = ordered ? Number(t.attrGet('start') || 1) : 1;
          if (ordered) this.numberStarts.add(start);
          const reference = ordered ? `amir-number-${start}` : 'amir-bullet';
          const instance = ctx.lists.length && ctx.lists[ctx.lists.length - 1].ordered === ordered
            ? ctx.lists[ctx.lists.length - 1].instance
            : ++this.instances;
          out.push(...this.blocks(tokens, i + 1, end, { ...ctx, lists: [...ctx.lists, { ordered, reference, instance }], item: null }));
          i = end;
          break;
        }
        case 'list_item_open': {
          const end = closeIndex(tokens, i);
          out.push(...this.blocks(tokens, i + 1, end, { ...ctx, item: { first: true, checked: t.attrGet('amir-checked') } }));
          i = end;
          break;
        }
        case 'blockquote_open': {
          const end = closeIndex(tokens, i);
          out.push(...this.blocks(tokens, i + 1, end, { ...ctx, quote: ctx.quote + 1 }));
          i = end;
          break;
        }
        case 'fence':
        case 'code_block':
          out.push(this.monospace(t.content, ctx));
          break;
        case 'hr':
          out.push(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: 'BFBFBF', space: 1 } }, children: [] }));
          break;
        case 'html_block':
          if (/^\s*<!--[\s\S]*-->\s*$/.test(t.content)) break; // comments are not content
          this.sourceBlocks++;
          out.push(this.monospace(t.content, ctx));
          break;
        case 'table_open': {
          const end = closeIndex(tokens, i);
          out.push(this.table(tokens, i + 1, end));
          i = end;
          break;
        }
        default:
          break;
      }
    }
    return out;
  }

  private table(tokens: Token[], from: number, to: number): Table {
    const rows: { head: boolean; cells: { head: boolean; align: string | null; kids: ParagraphChild[] }[] }[] = [];
    let inHead = false;
    for (let i = from; i < to; i++) {
      const t = tokens[i];
      if (t.type === 'thead_open') inHead = true;
      else if (t.type === 'thead_close') inHead = false;
      else if (t.type === 'tr_open') rows.push({ head: inHead, cells: [] });
      else if (t.type === 'th_open' || t.type === 'td_open') {
        const align = /text-align:\s*(left|center|right)/.exec(t.attrGet('style') || '')?.[1] ?? null;
        const end = closeIndex(tokens, i);
        const inl = tokens.slice(i + 1, end).find((x) => x.type === 'inline');
        const head = t.type === 'th_open';
        rows[rows.length - 1]?.cells.push({ head, align, kids: this.inline(inl?.children, head ? { bold: true } : {}) });
        i = end;
      }
    }
    const width = Math.max(1, ...rows.map((r) => r.cells.length));
    return new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: rows.map((r) => new TableRow({
        tableHeader: r.head,
        children: Array.from({ length: width }, (_v, c) => {
          const cell = r.cells[c];
          return new TableCell({
            shading: r.head ? { type: ShadingType.CLEAR, color: 'auto', fill: 'F2F2F2' } : undefined,
            children: [new Paragraph({ alignment: cell?.align ? ALIGN[cell.align] : undefined, children: cell?.kids ?? [] })],
          });
        }),
      })),
    });
  }
}

function numberingConfig(starts: Set<number>) {
  const bulletChars = ['•', '◦', '▪'];
  const numberFormats = [LevelFormat.DECIMAL, LevelFormat.LOWER_LETTER, LevelFormat.LOWER_ROMAN];
  const indent = (l: number) => ({ paragraph: { indent: { left: 720 * (l + 1), hanging: 360 } } });
  const levels = (ordered: boolean, start: number) => Array.from({ length: 9 }, (_v, l) => ({
    level: l,
    format: ordered ? numberFormats[l % 3] : LevelFormat.BULLET,
    text: ordered ? `%${l + 1}.` : bulletChars[l % 3],
    start: l === 0 ? start : 1,
    alignment: AlignmentType.LEFT,
    style: indent(l),
  }));
  return [
    { reference: 'amir-bullet', levels: levels(false, 1) },
    ...[...starts].map((s) => ({ reference: `amir-number-${s}`, levels: levels(true, s) })),
  ];
}

function headingStyle(sizePt: number, outline: number, color = '1F3864') {
  return { run: { size: sizePt * 2, bold: true, color, font: 'Calibri Light' }, paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: outline, keepNext: true } };
}

export async function buildDocx(markdown: string, o: DocxOptions): Promise<DocxResult> {
  const page = PAGE[o.pageSize];
  const margin = Math.round(o.marginMm * TWIPS_PER_MM);
  const contentPx = ((page.width - 2 * margin) / 1440) * 96;
  const md = createParseMd();
  const tokens = md.parse(stripFrontMatter(markdown), {});
  const b = new Builder(o.docDir, contentPx);
  const children = b.blocks(tokens, 0, tokens.length, { quote: 0, lists: [], item: null });
  const doc = new Document({
    title: o.title,
    creator: 'amir_md',
    styles: {
      default: {
        document: { run: { font: 'Calibri', size: 22 }, paragraph: { spacing: { after: 120, line: 276 } } },
        title: { run: { size: 52, font: 'Calibri Light' }, paragraph: { spacing: { after: 60 } } },
        heading1: headingStyle(16, 0, '2F5496'),
        heading2: headingStyle(13, 1, '2F5496'),
        heading3: headingStyle(12, 2),
        heading4: headingStyle(11, 3),
        heading5: headingStyle(11, 4, '404040'),
        heading6: headingStyle(11, 5, '595959'),
      },
      paragraphStyles: [
        { id: 'Subtitle', name: 'Subtitle', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 30, color: '595959' }, paragraph: { spacing: { after: 160 } } },
        { id: 'AmirCode', name: 'Code', basedOn: 'Normal', next: 'Normal', run: { font: 'Consolas', size: 19 }, paragraph: { spacing: { before: 60, after: 120, line: 240 }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'F2F2F2' } } },
      ],
    },
    numbering: { config: numberingConfig(b.numberStarts) },
    sections: [{
      properties: { page: { size: page, margin: { top: margin, right: margin, bottom: margin, left: margin } } },
      footers: o.pageNumbers
        ? { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT, ' / ', PageNumber.TOTAL_PAGES], size: 18, color: '666666' })] })] }) }
        : undefined,
      children: children.length ? children : [new Paragraph({ children: [] })],
    }],
  });
  const buffer = await Packer.toBuffer(doc);
  return { buffer, sourceBlocks: b.sourceBlocks, missingImages: [...new Set(b.missing)] };
}
