// Markdown to a standalone HTML page, used for HTML export and as the PDF source
// (FR-EXPORT-03, FR-EXPORT-09). Fold state never applies: the whole document is rendered.

import MarkdownIt from 'markdown-it';
import { createRefMd, escapeHtml, taskListRenderPlugin } from '../../shared/markdownIt';
import { slugger } from '../../shared/slug';
import { dataUri, resolveLocalImage, stripFrontMatter } from './images';

export interface HtmlOptions {
  title: string;
  docDir: string | null;
  pageSize: 'Letter' | 'A4';
  marginMm: number;
  pageNumbers: boolean;
}

export interface HtmlResult {
  html: string;
  missingImages: string[];
}

function headingIds(md: MarkdownIt): void {
  md.core.ruler.push('amir_heading_ids', (state) => {
    const slug = slugger();
    const t = state.tokens;
    for (let i = 0; i < t.length; i++) {
      if (t[i].type !== 'heading_open') continue;
      const text = (t[i + 1]?.children ?? []).filter((c) => c.type === 'text' || c.type === 'code_inline').map((c) => c.content).join('');
      t[i].attrSet('id', slug(text));
    }
  });
}

function embedImages(md: MarkdownIt, docDir: string | null, missing: string[]): void {
  const toData = (src: string): string => {
    if (/^(https?|data):/i.test(src)) return src;
    const file = resolveLocalImage(src, docDir);
    const uri = file ? dataUri(file) : null;
    if (!uri) missing.push(src);
    return uri ?? src;
  };
  const defaultImage = md.renderer.rules.image!;
  md.renderer.rules.image = (tokens, idx, options, env, self) => {
    const tok = tokens[idx];
    tok.attrSet('src', toData(tok.attrGet('src') || ''));
    return defaultImage(tokens, idx, options, env, self);
  };
  const rewrite = (html: string) =>
    html.replace(/(<img\b[^>]*?\bsrc\s*=\s*)(["'])(.*?)\2/gi, (_m, pre: string, q: string, src: string) => `${pre}${q}${toData(src)}${q}`);
  const block = md.renderer.rules.html_block!;
  const inline = md.renderer.rules.html_inline!;
  md.renderer.rules.html_block = (tokens, idx, options, env, self) => rewrite(block(tokens, idx, options, env, self));
  md.renderer.rules.html_inline = (tokens, idx, options, env, self) => rewrite(inline(tokens, idx, options, env, self));
}

export const PRINT_CSS = `
body { font-family: "Segoe UI", Calibri, Aptos, Arial, sans-serif; font-size: 11pt; line-height: 1.45; color: #1f1f1f; margin: 0 auto; max-width: 920px; padding: 24px; }
@media print { body { max-width: none; padding: 0; } }
h1, h2, h3, h4, h5, h6 { line-height: 1.25; margin: 1.1em 0 .45em; font-weight: 600; page-break-after: avoid; break-after: avoid; }
h1 { font-size: 20pt; } h2 { font-size: 16pt; } h3 { font-size: 13.5pt; } h4 { font-size: 12pt; } h5 { font-size: 11pt; } h6 { font-size: 11pt; color: #595959; }
p { margin: 0 0 .6em; }
p[data-amir-style="title"] { font-size: 26pt; font-weight: 300; margin: .2em 0 .15em; }
p[data-amir-style="subtitle"] { font-size: 15pt; color: #595959; margin: 0 0 .9em; }
a { color: #0563c1; }
code { font-family: Consolas, "Courier New", monospace; font-size: .92em; background: #f2f2f2; padding: .05em .3em; border-radius: 3px; }
pre { background: #f2f2f2; padding: 10px 12px; border-radius: 4px; white-space: pre-wrap; font-size: 9.5pt; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { margin: .6em 0; padding: .1em 1em; border-left: 4px solid #c8c8c8; color: #444; }
table { border-collapse: collapse; width: 100%; margin: .6em 0; font-size: 10pt; }
th, td { border: 1px solid #bfbfbf; padding: 4px 8px; vertical-align: top; }
th { background: #f2f2f2; text-align: left; }
tr { page-break-inside: avoid; }
img { max-width: 100%; height: auto; }
hr { border: 0; border-top: 1px solid #bfbfbf; margin: 1.2em 0; }
li.task-item { list-style: none; }
li.task-item input { margin: 0 .4em 0 -1.3em; }
`;

function pageCss(o: HtmlOptions): string {
  const numbers = o.pageNumbers
    ? '@bottom-center { content: counter(page) " / " counter(pages); font-family: "Segoe UI", Arial, sans-serif; font-size: 9pt; color: #666; }'
    : '';
  return `@page { size: ${o.pageSize}; margin: ${o.marginMm}mm; ${numbers} }`;
}

export function renderHtml(markdown: string, o: HtmlOptions): HtmlResult {
  const md = createRefMd();
  const missing: string[] = [];
  md.use(taskListRenderPlugin);
  headingIds(md);
  embedImages(md, o.docDir, missing);
  const body = md.render(stripFrontMatter(markdown));
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data: https:; style-src 'unsafe-inline'; font-src data:">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(o.title)}</title>
<style>${PRINT_CSS}
${pageCss(o)}</style>
</head>
<body>
${body}
</body>
</html>
`;
  return { html, missingImages: [...new Set(missing)] };
}
