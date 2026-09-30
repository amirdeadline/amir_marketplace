// Storage contract (SRS 4.2): what amir_md writes for each kind of formatting.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { schema } from '../src/webview/codec/schema';
import { serializeBlockVerified, parseDocument } from '../src/webview/codec/document';
import { STYLED_DEFAULTS, SerializeOptions } from '../src/webview/codec/serialize';
import type { Node } from 'prosemirror-model';

const OPTS: SerializeOptions = { bulletMarker: '-', emphasisMarker: '*', strongMarker: '**' };
const META = { env: {}, opts: OPTS };
const s = schema;
const txt = (t: string, ...marks: ReturnType<typeof s.mark>[]) => s.text(t, marks);
const para = (...inline: Node[]) => s.nodes.paragraph.create(null, inline);
const ser = (n: Node) => serializeBlockVerified(n, META);

test('font color is a span with the color first', () => {
  const m = s.marks.textStyle.create({ color: '#E53935' });
  assert.equal(ser(para(txt('Critical finding', m))), '<span style="color:#E53935;">Critical finding</span>');
});

test('color, background, font and size share one span in fixed order', () => {
  const m = s.marks.textStyle.create({ fontSize: '14pt', fontFamily: 'Georgia', bg: '#FFFF00', color: '#1E88E5' });
  assert.equal(
    ser(para(txt('x', m))),
    '<span style="color:#1E88E5;background-color:#FFFF00;font-family:Georgia;font-size:14pt;">x</span>',
  );
});

test('color wraps bold', () => {
  const c = s.marks.textStyle.create({ color: '#C00000' });
  assert.equal(ser(para(txt('bold red', c, s.marks.strong.create()))), '<span style="color:#C00000;">**bold red**</span>');
});

test('underline, sup, sub use HTML tags; strike uses ~~', () => {
  assert.equal(ser(para(txt('u', s.marks.underline.create()))), '<u>u</u>');
  assert.equal(ser(para(txt('H'), txt('2', s.marks.sub.create()), txt('O'))), 'H<sub>2</sub>O');
  assert.equal(ser(para(txt('x'), txt('2', s.marks.sup.create()))), 'x<sup>2</sup>');
  assert.equal(ser(para(txt('gone', s.marks.strikethrough.create()))), '~~gone~~');
});

test('links and images use Markdown syntax', () => {
  const l = s.marks.link.create({ href: 'https://example.com', title: null });
  assert.equal(ser(para(txt('site', l))), '[site](https://example.com)');
  const img = s.nodes.image.create({ src: 'images/topology.png', alt: 'Network Topology' });
  assert.equal(ser(para(img)), '![Network Topology](images/topology.png)');
  const up = s.nodes.image.create({ src: '../shared/images/logo.png', alt: 'Logo' });
  assert.equal(ser(para(up)), '![Logo](../shared/images/logo.png)');
});

test('a resized image is an img tag with width, and reopens as an image', () => {
  const img = s.nodes.image.create({ src: 'images/small.png', alt: 'Small', width: '120' });
  const out = ser(para(img));
  assert.equal(out, '<img src="images/small.png" alt="Small" width="120">');
  const { doc } = parseDocument(out + '\n', OPTS);
  assert.equal(doc.firstChild!.type.name, 'paragraph');
  assert.equal(doc.firstChild!.firstChild!.type.name, 'image');
  assert.equal(doc.firstChild!.firstChild!.attrs.width, '120');
});

test('Title and Subtitle are marked paragraphs', () => {
  const t = s.nodes.title.create({ styleAttr: STYLED_DEFAULTS.title }, [txt('Network '), txt('Design', s.marks.strong.create())]);
  assert.equal(ser(t), '<p data-amir-style="title" style="font-size:26pt;">Network <strong>Design</strong></p>');
  const st = s.nodes.subtitle.create({ styleAttr: STYLED_DEFAULTS.subtitle }, [txt('a < b & c')]);
  assert.equal(ser(st), '<p data-amir-style="subtitle" style="font-size:15pt;color:#595959;">a &lt; b &amp; c</p>');
  const { doc } = parseDocument(ser(st) + '\n', OPTS);
  assert.equal(doc.firstChild!.type.name, 'subtitle');
  assert.equal(doc.firstChild!.textContent, 'a < b & c');
});

test('headings and alignment', () => {
  assert.equal(ser(s.nodes.heading.create({ level: 3 }, [txt('Three')])), '### Three');
  assert.equal(ser(s.nodes.paragraph.create({ align: 'center' }, [txt('mid')])), '<p style="text-align:center;">mid</p>');
});

test('escaping is minimal', () => {
  assert.equal(ser(para(txt('5 * 3 = 15, a_b_c, cost $5'))), '5 * 3 = 15, a_b_c, cost $5');
  assert.equal(ser(para(txt('*not italic*'))), '\\*not italic\\*');
  assert.equal(ser(para(txt('# not a heading'))), '\\# not a heading');
  assert.equal(ser(para(txt('see [^1] and [{C-3101: note}]'))), 'see [^1] and [{C-3101: note}]');
  assert.equal(ser(para(txt('[a](b) literal'))), '\\[a](b) literal');
  assert.equal(ser(para(txt('<div> literal'))), '\\<div> literal');
});

test('lists use the configured marker; task items keep their box', () => {
  const li = (t: string, checked: boolean | null = null) => s.nodes.list_item.create({ checked }, [para(txt(t))]);
  const ul = s.nodes.bullet_list.create({ tight: true, bullet: null }, [li('one'), li('two')]);
  assert.equal(ser(ul), '- one\n- two');
  const tasks = s.nodes.bullet_list.create({ tight: true, bullet: '-' }, [li('open', false), li('done', true)]);
  assert.equal(ser(tasks), '- [ ] open\n- [x] done');
  const ol = s.nodes.ordered_list.create({ tight: true, order: 1 }, [li('a'), li('b')]);
  assert.equal(ser(ol), '1. a\n2. b');
});

test('a table is written as a GFM pipe table', () => {
  const cell = (type: 'table_header' | 'table_cell', t: string, align: string | null = null) =>
    s.nodes[type].create({ align }, [para(txt(t))]);
  const table = s.nodes.table.create(null, [
    s.nodes.table_row.create(null, [cell('table_header', 'Name'), cell('table_header', 'Qty', 'right')]),
    s.nodes.table_row.create(null, [cell('table_cell', 'a|b'), cell('table_cell', '3', 'right')]),
  ]);
  assert.equal(ser(table), '| Name | Qty |\n|---|---:|\n| a\\|b | 3 |');
});
