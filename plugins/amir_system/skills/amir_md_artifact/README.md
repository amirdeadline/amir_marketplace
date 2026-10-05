# amir_md_artifact

Publishes any Markdown file as a private claude.ai Artifact that reads like a real document and can
be worked on: an outline rail, rendered tables and diagrams, editing in the rendered view, and
threaded comments anchored to selected text. The Markdown file stays the source of truth; the page
is a review surface.

## Invoke

| Tool | How |
|---|---|
| Claude Code | `/amir_md_artifact <path to the .md>` |
| Cursor | Type `/` in Agent chat, pick `amir_md_artifact`, then the path |

## What the reader gets

- __Outline rail__ to six heading levels, with a filter box, expand and collapse all, and the
  current section tracked while scrolling. Drag the divider to resize it; double-click resets.
- __Refresh__ reloads the document from its published source, keeping the reader's place. Edits and
  comments are already live; the source is what needs re-reading after a republish.
- __Tables__ with resizable columns. Every column has a handle, including the last, so dragging the
  last one widens the table itself rather than only moving space between columns.
- __Edit__ turns the whole document editable in the rendered view, with a word-processor toolbar:
  paragraph style, bold, italic, underline, strikethrough, code, alignment, indent, lists, link,
  insert table, insert image, divider, colour, size in points. Sections save when focus leaves them.
- __Comments__: select text, comment on it, and the quote is highlighted in the document. Threads
  take replies and an __Ask Claude__ button that answers in the thread. Everything is timestamped.
- Light and dark themes, and `<<Comment>>`, `<<Screenshot: …>>` and `<<NOTE: …>>` markers rendered
  as call-outs and counted.

## How it is put together

| File | Does |
|---|---|
| `SKILL.md` | The instructions an agent follows: staging, publishing, and reading edits back |
| `assets/build.py` | Stages a document: copies it to `doc.md`, copies and rewrites local image links, fills in the title, prints the exact `files` mapping to publish |
| `assets/viewer.html` | The page itself. Generic, and not to be rewritten per document |

The page needs the `db` and `user` capabilities to save anything, and `sample` for Ask Claude.

## The one thing that must not be forgotten

Edits made in the page are stored against the section they belong to, not written back to the
Markdown file. Once an edit has been folded into the source, __its stored override must be
deleted__, or it keeps shadowing the file and later changes to that section never appear. `SKILL.md`
section 5 sets out the loop.

## Round trip

Editing in the rendered view means converting HTML back to Markdown. The serializer is written for
the shapes this page generates itself, which is more reliable here than a general-purpose one.
Diagrams and review markers are held as non-editable blocks carrying their original Markdown, so
they pass through untouched. The conversion is verified by serializing every section, re-rendering
it, and comparing structure; it currently runs clean across a 224-section document.

Colour, text size and alignment have no Markdown equivalent and are stored as inline HTML. The page
renders them; the Word and Google Docs builds show that text plain.
