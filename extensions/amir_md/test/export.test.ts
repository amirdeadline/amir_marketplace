import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import JSZip from 'jszip';
import { buildDocx, cssColor, halfPoints, bookmarkId } from '../src/extension/export/docx';
import { renderHtml } from '../src/extension/export/html';
import { findBrowser, printPdf } from '../src/extension/export/pdf';
import { imageSize, stripFrontMatter } from '../src/extension/export/images';

const FIX = join(__dirname, 'fixtures');
const MIXED = readFileSync(join(FIX, 'mixed.md'), 'utf8');
const OPTS = { title: 'Mixed', docDir: FIX, pageSize: 'Letter' as const, marginMm: 20, pageNumbers: true };

async function docxXml(md: string) {
  const r = await buildDocx(md, OPTS);
  const zip = await JSZip.loadAsync(r.buffer);
  return {
    r,
    doc: await zip.file('word/document.xml')!.async('string'),
    styles: await zip.file('word/styles.xml')!.async('string'),
    numbering: await zip.file('word/numbering.xml')!.async('string'),
  };
}

test('Word export uses built-in Title, Subtitle, and Heading styles (FR-EXPORT-04)', async () => {
  const { doc, styles } = await docxXml(MIXED);
  for (const s of ['Title', 'Subtitle', 'Heading1', 'Heading2', 'Heading3', 'Heading4', 'Heading5', 'Heading6']) {
    assert.ok(doc.includes(`<w:pStyle w:val="${s}"/>`), `paragraph with style ${s}`);
  }
  assert.ok(/w:styleId="Subtitle"/.test(styles), 'Subtitle style defined');
  assert.ok(/<w:outlineLvl w:val="0"\/>/.test(styles), 'Heading 1 has an outline level');
});

test('Word export keeps character formatting, links, and lists', async () => {
  const { doc, numbering, r } = await docxXml(MIXED);
  assert.ok(doc.includes('<w:color w:val="E53935"/>'), 'font color');
  assert.ok(/<w:u w:val="single"\/>/.test(doc), 'underline');
  assert.ok(doc.includes('<w:vertAlign w:val="subscript"/>') && doc.includes('<w:vertAlign w:val="superscript"/>'));
  assert.ok(doc.includes('<w:hyperlink'), 'hyperlink');
  assert.ok(doc.includes('<w:numPr>'), 'list numbering');
  assert.ok(/w:numFmt w:val="decimal"/.test(numbering) && /w:numFmt w:val="bullet"/.test(numbering));
  assert.ok(doc.includes('\u2610') && doc.includes('\u2612'), 'task boxes');
  assert.ok(doc.includes('<w:tbl>'), 'table');
  assert.ok(!doc.includes('title: Mixed fixture'), 'front matter is not printed');
  assert.equal(r.sourceBlocks, 1, 'the raw <div> block (the comment is skipped)');
  assert.deepEqual(r.missingImages.sort(), ['images/small.png', 'images/topology.png']);
});

test('HTML export: ids, task boxes, page setup, no front matter', () => {
  const { html, missingImages } = renderHtml(MIXED, OPTS);
  assert.ok(html.includes('<h1 id="heading-one">'));
  assert.ok(html.includes('<input type="checkbox" disabled checked>'));
  assert.ok(html.includes('@page { size: Letter; margin: 20mm;'));
  assert.ok(html.includes('counter(page)'));
  assert.ok(!html.includes('tags: [a, b]'));
  assert.ok(html.includes("script-src") === false && html.includes("default-src 'none'"), 'no scripts allowed');
  assert.equal(missingImages.length, 2);
});

test('CSS values convert to Word units', () => {
  assert.equal(cssColor('#e53935'), 'E53935');
  assert.equal(cssColor('#abc'), 'AABBCC');
  assert.equal(cssColor('red'), 'FF0000');
  assert.equal(cssColor('rgb(229, 57, 53)'), 'E53935');
  assert.equal(cssColor('nonsense'), undefined);
  assert.equal(halfPoints('14pt'), 28);
  assert.equal(halfPoints('16px'), 24);
  assert.equal(halfPoints('1.5em'), 33);
  assert.equal(bookmarkId('111-idp-federation'), 'h_111_idp_federation');
});

test('image size and front matter helpers', () => {
  const png = Buffer.from('89504e470d0a1a0a0000000d49484452000000400000002008060000', 'hex');
  assert.deepEqual(imageSize(Buffer.concat([png, Buffer.alloc(8)])), { width: 64, height: 32 });
  assert.equal(stripFrontMatter('---\na: 1\n---\n# H\n'), '# H\n');
  assert.equal(stripFrontMatter('# H\n---\n'), '# H\n---\n');
});

const MA_GUIDE = 'E:/PC3_Shared/Palo/COE/PRISMA_SDWAN_SnO/.ai/ma/claude/docs/Prisma SD-WAN Maturity Assessment.md';

test('MA guide exports to Word', { skip: !existsSync(MA_GUIDE) }, async () => {
  const t0 = performance.now();
  const r = await buildDocx(readFileSync(MA_GUIDE, 'utf8'), { ...OPTS, docDir: null });
  assert.ok(r.buffer.length > 50_000);
  console.log(`MA guide docx: ${(r.buffer.length / 1024).toFixed(0)} KB in ${(performance.now() - t0).toFixed(0)} ms, ${r.sourceBlocks} source blocks`);
});

const browser = findBrowser('');

test('PDF export prints through the installed browser (FR-EXPORT-03)', { skip: !browser, timeout: 120_000 }, async () => {
  const dir = mkdtempSync(join(tmpdir(), 'amir-md-test-'));
  try {
    const out = join(dir, 'mixed.pdf');
    await printPdf(browser!, renderHtml(MIXED, OPTS).html, out);
    const head = readFileSync(out).subarray(0, 5).toString('ascii');
    assert.equal(head, '%PDF-');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
