---
name: amir_md_artifact
description: >-
  Use when the user invokes /amir_md_artifact or /amir:amir_md_artifact, or asks to view, read,
  review, share or comment on a Markdown file as a web page, document viewer or artifact: "show me
  this md", "publish this as an artifact", "I want to read this with a navigation pane", "let me
  comment on this document", "make this md reviewable". Publishes any .md file as a private
  claude.ai Artifact with a collapsible outline rail, rendered tables and Mermaid diagrams, and
  per-section editing and commenting that persist.
argument-hint: "[path to the .md file] [optional title]"
---

# Markdown as a reviewable artifact

Turn any Markdown file into a private web page on claude.ai that reads like a real document and can
be marked up section by section. The Markdown file stays the source of truth; the page is a review
surface.

## 1. Skill folder

`<skill_dir>` is the folder holding this file. Claude Code: `${CLAUDE_SKILL_DIR}`. Cursor: the
folder of the SKILL.md path shown with the attached skill. Fallback:
`~/.claude/skills/amir_md_artifact`.

Two files live in `<skill_dir>/assets/`:

- `viewer.html` — the page itself. Do not rewrite it per document; it is generic.
- `build.py` — stages a document for publishing.

## 2. What the page gives the reader

__Reading__

- An outline rail on the left: every heading to six levels, with a filter box, expand and collapse
  all, and the current section highlighted while scrolling.
- __The outline pane is resizable.__ Drag the divider, double-click it to reset, or focus it and
  use the arrow keys. The width is remembered per reader.
- Every section collapsible by clicking its heading.
- __Refresh__ in the header reloads the document from its published source and keeps the reader's
  place. Edits and comments are already live through their subscriptions; `doc.md` is the one thing
  that does not update on its own, so after republishing a changed document the reader presses
  Refresh rather than reloading the page. It reports whether anything actually changed.
- Markdown tables as real tables, with __resizable columns__: drag the edge of any header cell.
  __Every column has a handle, including the last__, so dragging the last one makes the table
  itself wider rather than only moving space between columns; a table wider than the page scrolls
  inside its own frame. Double-click any handle to reset the whole table. Widths are shared with
  everyone who opens the page.
- Mermaid fences as rendered diagrams; a light and a dark theme following the reader's system
  setting, with a manual toggle.
- A list nested three or more levels deep is colour-coded by depth, so a menu map reads as a tree.
- `<<Comment>>`, `<<Screenshot: …>>` and `<<NOTE: …>>` markers render as coloured call-outs and
  are counted. Documents without them are unaffected.
- A leading `# Contents` list is dropped, because the outline replaces it.

__Editing__

- __Edit__ in the header turns the whole document editable in place. You type on the rendered
  page, not in markdown.
- A formatting toolbar appears, close to a word processor's: paragraph style, bold, italic,
  underline, strikethrough, inline code, alignment, indent and outdent, bullet and numbered lists,
  link, insert table, insert image by address, divider, text colour, text size in points, and
  clear formatting.
- Inside a table, __Tab__ moves to the next cell and __Tab in the last cell adds a row__.
  Shift+Tab goes back.
- Each section saves when you click away from it. Only sections that actually changed are written.
- The page converts the edited HTML back to markdown with a serializer written for the shapes it
  generates itself. Diagrams and review markers are held as non-editable blocks carrying their
  original markdown, so they survive untouched.

__Commenting__

- Select any text and choose __Comment__. The comments pane opens on the right with your selection
  quoted.
- The quoted text is highlighted in the document. Clicking either the highlight or the comment
  opens that thread.
- A thread is a conversation: your comment, replies, and __Ask Claude__, which sends the section,
  the quoted text and the conversation so far and posts the answer back into the thread.
- Every comment and every reply carries its date and time, and threads are sorted newest first
  while messages within a thread run oldest to newest.
- __Resolve__ marks a thread done with a timestamp; the filter at the top switches between open,
  resolved and all.
- The comments pane is resizable the same way as the outline.

## 3. Publish

**Stage first.** Put the staging directory inside this session's scratchpad directory, because the
Artifact tool only accepts source files from the scratchpad or the working directory.

```bash
python "<skill_dir>/assets/build.py" --md "<path to the .md>" --out "<scratchpad>/mdart/<name>"
```

Add `--title "Something Short"` to override the name. Without it the title comes from the first
level-1 heading, or the file name.

The script copies the document to `doc.md`, copies every local image it references into `assets/`
and rewrites the links to match, fills the title into the page, and prints the exact `files`
mapping to use next. Read its output: it reports any image the document references that is not on
disk.

**Then publish** with the Artifact tool, passing the staged page and the printed mapping:

- `file_path`: `<out>/index.html`
- `root`: `<out>` — so each published path is the same as its source path
- `files`: the list the script printed, e.g. `[{"path": "doc.md"}, {"path": "assets/001_x.png"}]`.
  It is also saved as `<out>/files.json`, so a long list need not be retyped.
- `capabilities`: `{"db": {}, "user": {}, "sample": {}}` — `db` and `user` make editing and
  comments persist; `sample` is what lets a thread ask Claude for an opinion. Leave `sample`
  out if you do not want the page able to call Claude.
- `icon`: one plain word for the document's subject, on the first publish only
- `description`: one sentence for the gallery card

Give the user the URL. Say in one line that the page is private until they share it, and that
editing and comments need them to be signed in.

## 4. Update the same page later

Publish again with the **same** `url` and the same `index.html` path, after re-running `build.py`
to refresh `doc.md`. Never publish without `url` for a document that already has a page: that
creates a second artifact and the stored edits and comments stay with the first.

If the page was published in an earlier conversation, read it first (`action: "read"`) — a publish
to an artifact this conversation has not read is refused.

## 5. Read the reader's edits and comments back

Edits and comments live in the artifact's own database, not in the page, so they survive every
republish. Read them with the `ArtifactData` tool against the artifact's URL:

- collection `threads` — one per comment thread: `key`, `section`, `title`, `quote` (the text
  that was selected), `text` (the opening comment), `status` (`open` or `resolved`), `createdAt`,
  `resolvedAt`.
- collection `messages` — one per reply: `threadId`, `text`, `kind` (`user` or `ai`), `createdAt`.
  Sort by `createdAt` to read a conversation in order.
- collection `edits` — one per edited section: `key`, `section`, `title`, `md` (the edited
  Markdown), `updatedAt`.
- collection `tablecols` — one per table: `widths`, in pixels, in column order.

Both are keyed on `key`, a slug of the heading text. Each document also carries the section number
and heading, so a comment can still be placed if a heading is later renamed.

**Fold edits into the source file, then delete the override.** This is the one step that must not be
skipped:

1. Read the `edits` collection.
2. Apply each `md` to the matching section of the real Markdown file.
3. Delete that `edits` document (`ArtifactData`, `action: "delete"`).
4. Re-run `build.py` and republish.

An override left in place after its edit has been folded in keeps shadowing the source, so later
changes to that section will not appear on the page. Resolved comments can be kept as a record or
deleted; they do not affect rendering.

## 6. Things to know

- **Renumbering headings orphans the stored notes.** The keys come from heading text, which usually
  includes the section number. Before any renumbering, read both collections out; afterwards, write
  them back under the new keys or tell the user what was attached where.
- **Duplicate heading titles are handled.** The second "Overview" becomes `overview-2`, stable as
  long as the document's order does not change.
- **Some formatting is not markdown.** Bold, italic, strikethrough, code, links, headings, lists,
  tables and images round-trip exactly. Colour, text size and alignment are stored as inline HTML,
  which the page renders but the Word and Google Docs builds will show as plain text until those
  converters are taught to read it. Prefer the structural controls for anything that matters.
- **A line break inside a table cell stays as HTML.** A markdown table row is a single line, so a
  break inside a cell is written as `<br>`. Removing that handling corrupts the table.
- **Headings are not editable in place.** Only section bodies are. Change a heading in the
  Markdown file.
- **Word and PDF are not this skill's job.** Mermaid diagrams render here but not in Word; if the
  user wants a Word file, convert separately and export diagrams as images.
- **Read the file before publishing it.** Publishing distributes the content. If the document is
  someone else's or its contents are unknown, read it first. Never publish a document that
  impersonates a real person or organisation.
- **Large documents are fine.** The page is a few tens of kilobytes; the document is fetched
  separately at view time. The limit is 16 MB per file.
