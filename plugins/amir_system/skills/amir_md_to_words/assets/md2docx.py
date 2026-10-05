#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Markdown -> Microsoft Word.

    python md2docx.py --md <file.md> [--out <file.docx>] [--clean]
                      [--title "Name"] [--product "Product"] [--applies "..."]

Two things make this different from a plain converter.

  * Review markers become REAL WORD COMMENTS.  Anything written for the author
    rather than the reader -- <<Comment>> blocks, <<Screenshot: ...>> requests,
    <<NOTE: ...>> placeholders -- is taken out of the body and attached to the
    paragraph it belonged to, as a comment in Word's reviewing pane.  The body
    text reads clean; nothing is lost.
  * Cross-references become links.  A section number in the text ("see 3.1.2")
    turns into a hyperlink to that heading, with a bookmark on every heading to
    land on.  Version numbers are left alone.

Lists are coloured by nesting depth, so a nested menu map or taxonomy reads as
a tree rather than as a wall of bullets.

With --clean the markers are dropped instead of becoming comments, for a file
that goes outside.
"""
from __future__ import print_function
import argparse, io, os, re, shutil, sys, tempfile, time, zipfile

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement

GREY = RGBColor(0x60, 0x60, 0x60)
ORANGE = RGBColor(0xFA, 0x58, 0x2D)
LINK = RGBColor(0x0B, 0x4F, 0x9E)
# depth colours for nested lists, matching the review viewer
DEPTH = [RGBColor(0x1F, 0x4E, 0x79), RGBColor(0xB4, 0x45, 0x1F),
         RGBColor(0x2F, 0x6B, 0x46)]

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


# ----------------------------------------------------------------- utilities
def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k), str(v))
    return e


def shade(cell, fill):
    cell._tc.get_or_add_tcPr().append(el("w:shd", **{"w:val": "clear",
                                                     "w:color": "auto",
                                                     "w:fill": fill}))


def hrule(par, colour="FA582D", size=12):
    pPr = par._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    bdr.append(el("w:bottom", **{"w:val": "single", "w:sz": size,
                                 "w:space": 6, "w:color": colour}))
    pPr.append(bdr)


def add_field(par, instr, placeholder=""):
    r = par.add_run()
    for e in (el("w:fldChar", **{"w:fldCharType": "begin"}),):
        r._r.append(e)
    t = OxmlElement("w:instrText")
    t.set(qn("xml:space"), "preserve")
    t.text = instr
    r._r.append(t)
    r._r.append(el("w:fldChar", **{"w:fldCharType": "separate"}))
    tx = OxmlElement("w:t")
    tx.text = placeholder
    r._r.append(tx)
    r._r.append(el("w:fldChar", **{"w:fldCharType": "end"}))
    return r


def bookmark(par, bid, name):
    """wrap a paragraph in a bookmark so links can target it"""
    pPr = par._p.find(qn("w:pPr"))
    at = 1 if pPr is not None else 0
    par._p.insert(at, el("w:bookmarkStart", **{"w:id": bid, "w:name": name}))
    par._p.append(el("w:bookmarkEnd", **{"w:id": bid}))


def external_link(par, url, text, size=None, bold=False):
    rid = par.part.relate_to(
        url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True)
    h = el("w:hyperlink", **{"r:id": rid})
    h.append(_run_xml(text, colour="0B4F9E", underline=True, size=size, bold=bold))
    par._p.append(h)


def internal_link(par, anchor, text, bold=False, size=None):
    h = el("w:hyperlink", **{"w:anchor": anchor})
    h.append(_run_xml(text, colour="0B4F9E", underline=True, bold=bold, size=size))
    par._p.append(h)


def _run_xml(text, colour=None, underline=False, bold=False, italic=False,
             mono=False, size=None):
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    if bold:
        rPr.append(OxmlElement("w:b"))
    if italic:
        rPr.append(OxmlElement("w:i"))
    if mono:
        rPr.append(el("w:rFonts", **{"w:ascii": "Consolas", "w:hAnsi": "Consolas"}))
    if colour:
        rPr.append(el("w:color", **{"w:val": colour}))
    if underline:
        rPr.append(el("w:u", **{"w:val": "single"}))
    if size:
        rPr.append(el("w:sz", **{"w:val": int(size * 2)}))
    r.append(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    # control characters are not valid in XML; a stray marker token must never
    # reach the document
    t.text = re.sub("[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    r.append(t)
    return r


# ------------------------------------------------------------------ comments
class Comments(object):
    """collects Word comments and injects the parts python-docx cannot write"""

    def __init__(self, author="Review"):
        self.author = author
        self.items = []

    def add(self, par, text):
        if par is None:
            return
        cid = len(self.items) + 1
        self.items.append((cid, text))
        pPr = par._p.find(qn("w:pPr"))
        at = 1 if pPr is not None else 0
        par._p.insert(at, el("w:commentRangeStart", **{"w:id": cid}))
        par._p.append(el("w:commentRangeEnd", **{"w:id": cid}))
        r = OxmlElement("w:r")
        r.append(el("w:commentReference", **{"w:id": cid}))
        par._p.append(r)

    def xml(self):
        ns = ('xmlns:w="%s" xmlns:r="http://schemas.openxmlformats.org/'
              'officeDocument/2006/relationships"' % W)
        when = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               "<w:comments %s>" % ns]
        for cid, text in self.items:
            body = ""
            for i, line in enumerate(str(text).split("\n")):
                body += ("<w:p><w:r>" +
                         ('<w:rPr><w:b/></w:rPr>' if i == 0 else "") +
                         '<w:t xml:space="preserve">' + esc(line) +
                         "</w:t></w:r></w:p>")
            out.append('<w:comment w:id="%d" w:author="%s" w:initials="%s" w:date="%s">%s</w:comment>'
                       % (cid, esc(self.author), esc(self.author[:2].upper()), when, body))
        out.append("</w:comments>")
        return "".join(out)

    def inject(self, path):
        """add comments.xml, its relationship and its content type"""
        if not self.items:
            return 0
        tmp = path + ".tmp"
        zin = zipfile.ZipFile(path, "r")
        zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
        REL = ('<Relationship Id="rIdComments" Type="http://schemas.openxmlformats.org/'
               'officeDocument/2006/relationships/comments" Target="comments.xml"/>')
        CT = ('<Override PartName="/word/comments.xml" ContentType="application/'
              'vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>')
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                s = data.decode("utf-8")
                if "comments+xml" not in s:
                    s = s.replace("</Types>", CT + "</Types>")
                data = s.encode("utf-8")
            elif item.filename == "word/_rels/document.xml.rels":
                s = data.decode("utf-8")
                if "rIdComments" not in s:
                    s = s.replace("</Relationships>", REL + "</Relationships>")
                data = s.encode("utf-8")
            zout.writestr(item, data)
        zout.writestr("word/comments.xml", self.xml().encode("utf-8"))
        zin.close()
        zout.close()
        shutil.move(tmp, path)
        return len(self.items)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


# ------------------------------------------------------------------- inline
INLINE = re.compile(
    r"(?P<img>!\[[^\]]*\]\([^)]*\))"
    r"|(?P<link>\[[^\]]+\]\([^)]+\))"
    r"|(?P<bold>__[^_]+__|\*\*[^*]+\*\*)"
    r"|(?P<code>`[^`]+`)"
    r"|(?P<ital>(?<![\w*])\*[^*\n]+\*(?![\w*]))")

# a section number, but never a software version
XREF = re.compile(r"(?<![0-9A-Za-z.])(\d{1,2}(?:\.\d{1,2}){1,2})(?![0-9]|\.[0-9xX]|\+)")
VBEF = re.compile(r"\b(?:release|releases|version|versions|software|PAN-OS|ION)[\s_*]*$", re.I)


class Writer(object):
    def __init__(self, doc, base_dir, sections, comments, clean):
        self.doc = doc
        self.base_dir = base_dir
        self.sections = sections          # "3.1.2" -> bookmark name
        self.comments = comments
        self.clean = clean
        self.last_par = None
        self.stats = {"links": 0, "xrefs": 0, "images": 0}

    # -- plain text with cross-reference links woven in
    def _text(self, par, text, link=True, **kw):
        if not link:
            self._plain(par, text, **kw)
            return
        pos = 0
        for m in XREF.finditer(text):
            if m.start() < pos:
                continue                       # swallowed by a link already made
            num = m.group(1)
            if num not in self.sections:
                continue
            if VBEF.search(text[max(0, m.start() - 30):m.start()]):
                continue
            anchor, title = self.sections[num]
            end = m.end()
            # when the reference spells the section out in full, link all of it
            if title:
                tail = re.match(r"\.?[  ]+" + re.escape(title),
                                text[m.end():], re.I)
                if tail:
                    end = m.end() + tail.end()
            if m.start() > pos:
                self._plain(par, text[pos:m.start()], **kw)
            internal_link(par, anchor, text[m.start():end],
                          bold=kw.get("bold", False), size=kw.get("size"))
            self.stats["xrefs"] += 1
            pos = end
        if pos < len(text):
            self._plain(par, text[pos:], **kw)

    def _plain(self, par, text, bold=False, italic=False, mono=False,
               colour=None, size=None):
        if not text:
            return
        par._p.append(_run_xml(text, colour=colour, bold=bold, italic=italic,
                               mono=mono, size=size))

    def inline(self, par, text, bold=False, colour=None, size=None, depth=None,
               link=True):
        """render one markdown string; depth colours the first bold run.

        Any inline marker token found is attached to this paragraph as a Word
        comment, wherever in the document it turned up.
        """
        text, marks = pull_inline(text)
        for tag, body in marks:
            self.comments.add(par, "%s\n%s" % (tag, body))
        # <br> becomes a real line break, so one table cell can hold a list
        # with one item per line
        segs = re.split(r"<br\s*/?>", text)
        for si, seg in enumerate(segs):
            if si:
                br = OxmlElement("w:r")
                br.append(OxmlElement("w:br"))
                par._p.append(br)
            self._inline_seg(par, seg, bold, colour, size, depth, link)

    def _inline_seg(self, par, text, bold=False, colour=None, size=None,
                    depth=None, link=True):
        pos, first_bold = 0, True
        for m in INLINE.finditer(text):
            if m.start() > pos:
                self._text(par, text[pos:m.start()], bold=bold, colour=colour,
                           size=size, link=link)
            kind, raw = m.lastgroup, m.group(0)
            if kind == "img":
                mm = re.match(r"!\[([^\]]*)\]\(([^)]*)\)", raw)
                self.image(par, mm.group(2).split()[0], mm.group(1), size)
            elif kind == "link":
                mm = re.match(r"\[([^\]]+)\]\(([^)]+)\)", raw)
                label, url = mm.group(1), mm.group(2).split()[0]
                # a label may carry its own emphasis, as in [__2__](#2)
                lbl_bold = bold
                emph = re.match(r"^(?:__|\*\*)(.+?)(?:__|\*\*)$", label)
                if emph:
                    label, lbl_bold = emph.group(1), True
                if url.startswith(("http://", "https://", "mailto:")):
                    external_link(par, url, label, size, bold=lbl_bold)
                    self.stats["links"] += 1
                elif url.startswith("#"):
                    # an explicit link to a section, written [label](#2) or
                    # [label](#3.1.2).  Use it where the number alone would not
                    # be picked up, such as a bare chapter number.
                    key = url[1:].lstrip("sS").lstrip("#").strip().rstrip(".")
                    if key in self.sections:
                        internal_link(par, self.sections[key][0], label,
                                      bold=lbl_bold, size=size)
                        self.stats["xrefs"] += 1
                    else:
                        self._text(par, label, bold=bold, colour=colour, size=size,
                                   link=link)
                else:
                    self._text(par, label, bold=bold, colour=colour, size=size,
                               link=link)
            elif kind == "bold":
                c = colour
                if depth is not None and first_bold and depth < len(DEPTH):
                    c = "%02X%02X%02X" % tuple(DEPTH[depth])
                    first_bold = False
                self._text(par, raw.strip("_*"), bold=True,
                           colour=(c if isinstance(c, str) else colour), size=size,
                           link=link)
            elif kind == "code":
                self._plain(par, raw[1:-1], mono=True, colour=colour, size=size)
            elif kind == "ital":
                self._plain(par, raw[1:-1], italic=True, colour=colour, size=size)
            pos = m.end()
        if pos < len(text):
            self._text(par, text[pos:], bold=bold, colour=colour, size=size, link=link)

    def image(self, par, src, alt, size=None):
        path = src if os.path.isabs(src) else os.path.normpath(
            os.path.join(self.base_dir, src))
        if os.path.isfile(path):
            try:
                par.add_run().add_picture(path, width=Inches(6.1))
                self.stats["images"] += 1
                return
            except Exception:
                pass
        self._plain(par, "[image: %s]" % (alt or os.path.basename(src)),
                    italic=True, colour="606060", size=size)


# -------------------------------------------------------------- front matter
def styles(doc):
    n = doc.styles["Normal"]
    n.font.name = "Calibri"
    n.font.size = Pt(10.5)
    n.paragraph_format.space_after = Pt(6)
    for s in doc.sections:
        s.left_margin = s.right_margin = Inches(0.85)
        s.top_margin = s.bottom_margin = Inches(0.8)


def title_page(doc, title, product, applies, audience, version):
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run(product.upper())
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = ORANGE
    r._r.get_or_add_rPr().append(el("w:spacing", **{"w:val": 60}))
    p.paragraph_format.space_after = Pt(2)

    p = doc.add_paragraph()
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(34)
    r.font.color.rgb = RGBColor(0x14, 0x14, 0x14)
    p.paragraph_format.space_after = Pt(10)
    hrule(p)

    rows = [("Document version", version), ("Date", time.strftime("%d %B %Y"))]
    if applies:
        rows.append(("Applies to", applies))
    if audience:
        rows.append(("Audience", audience))
    doc.add_paragraph().paragraph_format.space_after = Pt(18)
    t = doc.add_table(rows=0, cols=2)
    for label, value in rows:
        c = t.add_row().cells
        c[0].width = Inches(1.6)
        c[1].width = Inches(4.4)
        a = c[0].paragraphs[0].add_run(label)
        a.bold = True
        a.font.size = Pt(9.5)
        a.font.color.rgb = GREY
        b = c[1].paragraphs[0].add_run(value)
        b.font.size = Pt(9.5)

    for _ in range(8):
        doc.add_paragraph()
    hrule(doc.add_paragraph(), "D9D6CF", 6)
    p = doc.add_paragraph()
    r = p.add_run(product.split()[0] if False else "Palo Alto Networks, Inc.")
    r.bold = True
    r.font.size = Pt(9)
    p.paragraph_format.space_after = Pt(0)
    p = doc.add_paragraph()
    r = p.add_run("www.paloaltonetworks.com")
    r.font.size = Pt(9)
    r.font.color.rgb = GREY
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def footer(doc, text):
    for sec in doc.sections:
        sec.different_first_page_header_footer = True
        f = sec.footer.paragraphs[0]
        f.text = ""
        r = f.add_run(text + "\t\t")
        r.font.size = Pt(8)
        r.font.color.rgb = GREY
        r2 = add_field(f, "PAGE", "1")
        r2.font.size = Pt(8)
        r2.font.color.rgb = GREY


def contents(doc):
    p = doc.add_paragraph()
    r = p.add_run("Contents")
    r.bold = True
    r.font.size = Pt(18)
    hrule(p, "D9D6CF", 6)
    p = doc.add_paragraph()
    add_field(p, r'TOC \o "1-3" \h \z \u',
              "Right-click here and choose Update Field to build the contents.")
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ------------------------------------------------------------------- parsing
def collect_sections(md):
    """section number -> (bookmark name, heading title)

    The title is kept so that a reference written out in full, such as
    "2.3 Control plane and data plane", can be linked across its whole length
    rather than on the number alone.
    """
    out = {}
    for m in re.finditer(r"(?m)^#{1,6}\s+((?:\d+\.)+)\s*(.*)$", md):
        num = m.group(1).rstrip(".")
        title = re.sub(r"<a id=[^>]*></a>", "", m.group(2))
        title = title.replace("__", "").replace("**", "").replace("`", "")
        title = title.strip().rstrip(".").strip()
        out.setdefault(num, ("S" + num.replace(".", "_"), title))
    return out


def prepare(md, clean):
    """Pull the review markers out of the body.

    Each marker becomes a one-line token so the main loop can attach it to the
    paragraph it followed, as a Word comment.  With clean, they are dropped.
    """
    removed = [0]

    # A marker inside a table cell cannot become a block of its own without
    # breaking the row, so it becomes an inline token that stays on the line.
    # The table writer pulls it out and anchors a comment to that cell.
    def cell_marker(tag):
        def f(mo):
            removed[0] += 1
            if clean:
                return ""
            return "\x01%s\x02%s\x01" % (tag, mo.group(1).strip())
        return f

    fixed = []
    for ln in md.split("\n"):
        if ln.lstrip().startswith("|"):
            ln = re.sub(r"_*\**<<NOTE:\s*(.*?)>>\**_*", cell_marker("NOTE"), ln)
            ln = re.sub(r"_*\**<<Screenshot:\s*(.*?)>>\**_*",
                        cell_marker("SCREENSHOT"), ln)
        fixed.append(ln)
    md = "\n".join(fixed)

    def block(mo):
        removed[0] += 1
        if clean:
            return "\n\n"
        inner = re.sub(r"\n{2,}", "\n", mo.group(1).strip().strip("_* \n"))
        tag = "SCREENSHOT" if re.match(r"(?i)^screenshot\s*:", inner) else "COMMENT"
        return "\n\n@@MK|%s|%s@@\n\n" % (tag, inner.replace("\n", "  "))

    md = re.sub(r"<<Comment>>([\s\S]*?)<<Comment>>", block, md)

    def single(tag):
        def f(mo):
            removed[0] += 1
            if clean:
                return "\n\n"
            return "\n\n@@MK|%s|%s@@\n\n" % (tag, mo.group(1).strip().replace("\n", "  "))
        return f

    md = re.sub(r"_*\**<<Screenshot:\s*([\s\S]*?)>>\**_*", single("SCREENSHOT"), md)
    md = re.sub(r"_*\**<<NOTE:\s*([\s\S]*?)>>\**_*", single("NOTE"), md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md, removed[0]


BORDERS = ["top", "left", "bottom", "right", "insideH", "insideV"]
TABLE_TWIPS = 9360          # 6.5 inches, the usable width inside the margins
LEADIN = RGBColor(0x1F, 0x4E, 0x79)


def column_widths(rows, width):
    """Share the table width out by how much text each column actually holds.

    Word's own autofit gives every column the same share, which leaves a column
    of one-word values as wide as a column of sentences.  This measures the
    content instead, so the column that needs room gets it.
    """
    n = width
    avg = []
    for c in range(n):
        lens = [len(re.sub(r"\[([^\]]*)\]\([^)]*\)|[_*`|]", r"\1", r[c]))
                for r in rows if c < len(r)]
        avg.append(max(sum(lens) / float(len(lens) or 1), 4.0))
    total = sum(avg)
    lo, hi = TABLE_TWIPS * 0.07, TABLE_TWIPS * 0.55
    w = [min(max(TABLE_TWIPS * a / total, lo), hi) for a in avg]
    scale = TABLE_TWIPS / sum(w)
    return [int(x * scale) for x in w]


def lead_in_colour(par):
    """Colour a bold label at the start of a paragraph.

    Sections in this document open with a short bold label - Purpose, Where to
    look, Healthy - followed by the text.  Colouring the label turns a wall of
    paragraphs into something that can be scanned.
    """
    runs = par.runs
    if not runs or not runs[0].bold:
        return False
    head = runs[0].text.strip()
    if not head or len(head) > 70:
        return False

    # a label on a line of its own, which this document uses as a sub-heading
    if len(runs) == 1 or not "".join(r.text for r in runs[1:]).strip():
        runs[0].font.color.rgb = LEADIN
        par.paragraph_format.space_before = Pt(8)
        par.paragraph_format.space_after = Pt(1)
        par.paragraph_format.keep_with_next = True
        return True

    # a label that opens a paragraph and is followed by its text
    if re.search(r"[.:]$", head):
        runs[0].font.color.rgb = LEADIN
        return True
    return False

# the separator inside the token must not be a pipe, because a table row is
# split on pipes before the token is read back
CELL_MARKER = re.compile("\x01([A-Z]+)\x02([^\x01]*)\x01")


def pull_inline(text):
    """strip inline marker tokens from a string, returning them separately"""
    found = [(m.group(1), m.group(2)) for m in CELL_MARKER.finditer(text)]
    if found:
        text = CELL_MARKER.sub("", text).rstrip()
    return text, found


def convert(md_path, out_path, title=None, product="Prisma SD-WAN",
            applies=None, audience=None, clean=False, author="Review"):
    base_dir = os.path.dirname(os.path.abspath(md_path))
    src = io.open(md_path, encoding="utf-8", newline="").read()
    src = re.sub(r"(?s)^#{1,3}\s+(Contents|Table of Contents)\s*$.*?(?=^#{1,3}\s+\S)",
                 "", src, flags=re.M | re.I)

    sections = collect_sections(src)
    src, removed = prepare(src, clean)

    doc = Document()
    styles(doc)
    name = title or os.path.splitext(os.path.basename(md_path))[0]
    title_page(doc, name, product, applies, audience,
               "1.0" if clean else "Working draft — internal review")
    footer(doc, "%s %s" % (product, name))
    contents(doc)

    cmts = Comments(author)
    w = Writer(doc, base_dir, sections, cmts, clean)
    stats = {"headings": 0, "tables": 0, "lists": 0, "paras": 0,
             "comments": 0, "removed": removed}
    bid = [1000]

    lines = src.split("\n")
    i, n = 0, len(lines)

    def is_row(s):
        return s.startswith("|") and s.endswith("|")

    while i < n:
        raw, s = lines[i], lines[i].strip()
        if not s:
            i += 1
            continue

        mo = re.match(r"^@@MK\|([^|]+)\|(.*)@@$", s)
        if mo:
            cmts.add(w.last_par, "%s\n%s" % (mo.group(1), mo.group(2)))
            i += 1
            continue

        mo = re.match(r"^(#{1,6})\s+(.*)$", s)
        if mo:
            lvl = min(len(mo.group(1)), 4)
            p = doc.add_heading(level=lvl)
            p.paragraph_format.keep_with_next = True
            # a heading never carries a hyperlink
            w.inline(p, mo.group(2), link=False)
            for r in p.runs:
                r.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
            num = re.match(r"((?:\d+\.)+)", mo.group(2))
            if num:
                key = num.group(1).rstrip(".")
                if key in sections:
                    bookmark(p, bid[0], sections[key][0])
                    bid[0] += 1
            w.last_par = p
            stats["headings"] += 1
            i += 1
            continue

        if s.startswith("```") or s.startswith("~~~"):
            f, lang, i = s[:3], s[3:].strip(), i + 1
            buf = []
            while i < n and not lines[i].strip().startswith(f):
                buf.append(lines[i])
                i += 1
            i += 1
            if lang:
                p = doc.add_paragraph()
                r = p.add_run("%s diagram (rendered in the online version)" % lang)
                r.bold = True
                r.font.size = Pt(9)
                r.font.color.rgb = GREY
                w.last_par = p
            for b in buf:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.left_indent = Inches(0.2)
                r = p.add_run(b)
                r.font.name = "Consolas"
                r.font.size = Pt(9)
            continue

        if is_row(s):
            rows = []
            while i < n and is_row(lines[i].strip()):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            body = [c for c in cells
                    if not all(re.match(r"^:?-{2,}:?$", x) for x in c if x != "")]
            if not body:
                continue
            width = max(len(r) for r in body)
            t = doc.add_table(rows=len(body), cols=width)
            bd = OxmlElement("w:tblBorders")
            for side in BORDERS:
                bd.append(el("w:" + side, **{"w:val": "single", "w:sz": 4,
                                             "w:space": 0, "w:color": "BFBFBF"}))
            t._tbl.tblPr.append(bd)
            t._tbl.tblPr.append(el("w:tblLayout", **{"w:type": "fixed"}))
            t.alignment = WD_TABLE_ALIGNMENT.LEFT
            t.autofit = False
            widths = column_widths(body, width)
            grid = t._tbl.find(qn("w:tblGrid"))
            if grid is not None:
                for gc, wd in zip(grid.findall(qn("w:gridCol")), widths):
                    gc.set(qn("w:w"), str(wd))
            for ri, row in enumerate(body):
                for ci in range(width):
                    cell = t.cell(ri, ci)
                    cell.text = ""
                    cell._tc.get_or_add_tcPr().append(
                        el("w:tcW", **{"w:w": widths[ci], "w:type": "dxa"}))
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(1)
                    # <br> is left in place: the renderer turns it into a real
                    # line break, so a cell can hold one item per line
                    txt = (row[ci] if ci < len(row) else "")
                    w.inline(p, txt, bold=(ri == 0), size=9)
                    if ri == 0:
                        shade(cell, "ECEAE5")
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            stats["tables"] += 1
            continue

        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]).strip())
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            w.inline(p, " ".join(x for x in buf if x))
            for r in p.runs:
                r.italic = True
            w.last_par = p
            continue

        mo = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", raw)
        if mo:
            depth = min(len(mo.group(1)) // 4, 2)
            ordered = bool(re.match(r"^\d", mo.group(2)))
            style = ("List Number" if ordered else "List Bullet")
            if depth:
                style += " %d" % (depth + 1)
            try:
                p = doc.add_paragraph(style=style)
            except KeyError:
                p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(2)
            w.inline(p, mo.group(3), depth=depth)
            w.last_par = p
            stats["lists"] += 1
            i += 1
            continue

        if re.match(r"(?i)^(figure|table)\s*[:0-9]", s):
            p = doc.add_paragraph()
            w.inline(p, s, size=9)
            for r in p.runs:
                r.italic = True
                r.font.color.rgb = GREY
            w.last_par = p
            i += 1
            continue

        if re.match(r"^([-*_])\1{2,}$", s):
            i += 1
            continue

        p = doc.add_paragraph()
        w.inline(p, s)
        if lead_in_colour(p):
            stats["leadins"] = stats.get("leadins", 0) + 1
        w.last_par = p
        stats["paras"] += 1
        i += 1

    stats["images"] = len(doc.inline_shapes)
    stats["links"] = w.stats["links"]
    stats["xrefs"] = w.stats["xrefs"]

    # Build beside the target and move into place, so a copy open in Word does
    # not lose the work.  If the target cannot be replaced, keep the new file
    # under a clear name and say so.
    tmp = out_path + ".building"
    doc.save(tmp)
    stats["comments"] = cmts.inject(tmp)
    try:
        os.replace(tmp, out_path)
        stats["written"] = out_path
    except OSError:
        alt = re.sub(r"\.docx$", " (new).docx", out_path)
        try:
            os.replace(tmp, alt)
        except OSError:
            alt = tmp
        stats["written"] = alt
        stats["locked"] = out_path
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--product", default="Prisma SD-WAN")
    ap.add_argument("--applies", default=None)
    ap.add_argument("--audience", default=None)
    ap.add_argument("--author", default="Review")
    ap.add_argument("--clean", action="store_true",
                    help="drop the review markers instead of making them Word comments")
    a = ap.parse_args()
    out = a.out or (os.path.splitext(a.md)[0] +
                    (" Clean.docx" if a.clean else ".docx"))
    st = convert(a.md, out, a.title, a.product, a.applies, a.audience,
                 a.clean, a.author)
    out = st.get("written", out)
    print("wrote %s  (%.1f MB)" % (out, os.path.getsize(out) / 1048576.0))
    if st.get("locked"):
        print("  NOTE: %s is open in another program, so it was left alone."
              % os.path.basename(st["locked"]))
        print("        Close it and re-run to replace it.")
    print("  headings %(headings)d, tables %(tables)d, list items %(lists)d, "
          "paragraphs %(paras)d, images %(images)d" % st)
    print("  section links %(xrefs)d, external links %(links)d" % st)
    if st.get("leadins"):
        print("  coloured section labels: %d" % st["leadins"])
    if st["removed"]:
        print("  review markers: %d %s"
              % (st["removed"], "dropped" if a.clean else "moved into Word comments"))
    if st["comments"]:
        print("  Word comments written: %d" % st["comments"])


if __name__ == "__main__":
    main()
