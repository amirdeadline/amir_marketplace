#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Stage a markdown file for publishing as a reviewable Artifact.

    python build.py --md <path to .md> --out <staging dir> [--title "Name"]

Writes <out>/index.html (the viewer, with the title filled in), <out>/doc.md
(the document, with local image links rewritten) and <out>/assets/* (every
local image, copied under a safe published path).  Prints the exact `files`
mapping to pass to the Artifact tool.

Nothing is published from here; the agent does that with the Artifact tool.
"""
from __future__ import print_function
import argparse, io, json, os, re, shutil, sys

try:
    from urllib.parse import unquote
except ImportError:                       # python 2
    from urllib import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "viewer.html")

IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".avif")


def is_remote(u):
    return bool(re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", u, re.I))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default=None)
    a = ap.parse_args()

    md_path = os.path.abspath(a.md)
    if not os.path.isfile(md_path):
        sys.exit("not a file: " + md_path)
    md_dir = os.path.dirname(md_path)
    out = os.path.abspath(a.out)
    assets = os.path.join(out, "assets")
    if not os.path.isdir(out):
        os.makedirs(out)

    md = io.open(md_path, encoding="utf-8", errors="replace", newline="").read()

    # ---- title: the flag, else the first level-1 heading, else the file name
    title = a.title
    if not title:
        # Only an unnumbered level-1 heading is the document's own title.  A
        # heading like "# 1. Introduction" is a chapter, so the file name names
        # the whole document better.
        for m in re.finditer(r"(?m)^#\s+(.+?)\s*$", md):
            cand = m.group(1).strip()
            if cand.lower() in ("contents", "table of contents"):
                continue
            if re.match(r"^((?:\d+\.)+|\d+\)|[A-Z]\.)\s", cand):
                break
            title = cand
            break
    if not title:
        # underscores become spaces; hyphens are left alone, because they are
        # usually part of a real name (SD-WAN, Day-2)
        title = re.sub(r"_+", " ", os.path.splitext(os.path.basename(md_path))[0]).strip()
    title = re.sub(r"[\r\n\t]+", " ", title).strip()[:90]

    # ---- local images -> assets/, with the markdown rewritten to match
    files, seen, missing, n = {}, {}, [], [0]

    def take(raw):
        """copy one local image and return its published path"""
        url = unquote(raw.strip()).split("#")[0].split("?")[0]
        if not url or is_remote(url):
            return None
        src = url if os.path.isabs(url) else os.path.normpath(os.path.join(md_dir, url))
        if src in seen:
            return seen[src]
        if not os.path.isfile(src):
            missing.append(url)
            return None
        base = re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.basename(src)) or "image"
        if not base.lower().endswith(IMG_EXT):
            base += ".png"
        n[0] += 1
        pub = "assets/%03d_%s" % (n[0], base)
        if not os.path.isdir(assets):
            os.makedirs(assets)
        shutil.copyfile(src, os.path.join(out, pub))
        seen[src] = pub
        files[pub] = os.path.join(out, pub)
        return pub

    def md_img(mo):
        pub = take(mo.group(2))
        return "![%s](%s)" % (mo.group(1), pub) if pub else mo.group(0)

    def html_img(mo):
        pub = take(mo.group(2))
        return "%s%s%s" % (mo.group(1), pub, mo.group(3)) if pub else mo.group(0)

    md = re.sub(r"!\[([^\]]*)\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)", md_img, md)
    md = re.sub(r"(<img\b[^>]*?\bsrc=[\"'])([^\"']+)([\"'])", html_img, md, flags=re.I)

    io.open(os.path.join(out, "doc.md"), "w", encoding="utf-8", newline="\n").write(md)

    tpl = io.open(TEMPLATE, encoding="utf-8", newline="").read()
    assert "__DOC_TITLE__" in tpl, "viewer.html is missing its title placeholder"
    tpl = tpl.replace("__DOC_TITLE__", title.replace("<", "").replace(">", ""))
    io.open(os.path.join(out, "index.html"), "w", encoding="utf-8", newline="\n").write(tpl)

    files["doc.md"] = os.path.join(out, "doc.md")

    heads = re.findall(r"(?m)^(#{1,6})\s+\S", md)
    print("title       : %s" % title)
    print("staging dir : %s" % out)
    print("page        : %s" % os.path.join(out, "index.html"))
    print("headings    : %d (levels %s)" % (
        len(heads), ", ".join(str(x) for x in sorted(set(len(h) for h in heads)))))
    print("images      : %d copied" % n[0])
    if missing:
        print("MISSING     : %d image(s) referenced but not found on disk:" % len(missing))
        for u in missing[:10]:
            print("              " + u)
    # The Artifact tool's list form takes objects, and `root` makes every
    # published path the same as its source path.
    rel = [{"path": p} for p in sorted(files.keys())]
    io.open(os.path.join(out, "files.json"), "w", encoding="utf-8",
            newline="\n").write(json.dumps(rel, indent=2))
    print("\nPublish with the Artifact tool:")
    print("  root      : %s" % out)
    print("  file_path : %s" % os.path.join(out, "index.html"))
    print("  files     : %s" % json.dumps(rel))


if __name__ == "__main__":
    main()
