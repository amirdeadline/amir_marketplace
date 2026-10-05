---
name: amir_md_to_words
description: >-
  Use when the user invokes /amir_md_to_words or /amir:amir_md_to_words, or asks to convert, export
  or save a Markdown file as Microsoft Word (.docx): "make this a Word doc", "export the md to
  Word", "give me the Word version", "I need a customer-facing Word file". Produces a review copy
  where every review marker becomes a real Word comment, and a clean copy with the markers removed,
  both with section cross-references as working hyperlinks.
argument-hint: "[path to the .md file] [optional output .docx path]"
---

# Markdown to Microsoft Word

Two Word files from one Markdown source. The Markdown stays the single source of truth.

| File | What it is | Review markers |
|---|---|---|
| `<name>.docx` | The review copy, matching the Markdown exactly | Become **real Word comments** in the reviewing pane |
| `<name> Clean.docx` | The customer-facing copy | **Removed** |

Both carry the same body text, headings, tables, images and links. The only difference is what
happens to the material written for the author rather than the reader.

## 1. Skill folder

`<skill_dir>` is the folder holding this file. Claude Code: `${CLAUDE_SKILL_DIR}`. Cursor: the
folder of the SKILL.md path shown with the attached skill. Fallback:
`~/.claude/skills/amir_md_to_words`.

The converter is `<skill_dir>/assets/md2docx.py`. It needs `python-docx` and `lxml`.

## 2. Run it

Build **both** files unless the user asks for one:

```bash
python "<skill_dir>/assets/md2docx.py" --md "<file>.md" --out "<name>.docx"
python "<skill_dir>/assets/md2docx.py" --md "<file>.md" --out "<name> Clean.docx" --clean
```

With `--out` omitted the output sits beside the Markdown, with ` Clean` appended under `--clean`.

Worth passing when known, because they appear on the title page:

- `--title "Day 2 Operations Guide"` — the document name
- `--product "Prisma SD-WAN"` — the product line, set in letter-spaced caps above the title
- `--applies "ION software 6.3.x through 6.5.x"` — **must match what the document itself says.**
  Never put a wider claim on the cover than the body supports; read the version section first.
- `--audience "..."`, `--author "..."` (the name on the Word comments; default `Review`)

Read the output. It reports headings, tables, list items, images, section links, external links,
how many markers were moved or dropped, and how many Word comments were written. **The marker count
and the comment count must match** in the review copy; if they do not, a marker was lost.

## 3. What becomes a Word comment

Anything written for the author rather than the reader:

- `<<Comment>> … <<Comment>>` blocks, including the `VERIFY:` notes
- `<<Screenshot: …>>` — a capture still to be taken
- `<<NOTE: …>>` — a placeholder for the reader or the author to fill in

Each is attached to the paragraph it followed, so the comment lands where it belongs. A marker
inside a table cell is attached to that cell. The body text is left clean in both files.

Real images and their `Figure:` captions are content, not markers. They stay in both files.

## 4. Cross-references become links

Every numbered heading gets a bookmark. The rules, in order:

| In the Markdown | In Word |
|---|---|
| A section number in body text — `see 3.1.2` | the number becomes a link |
| The section written out in full — `2.3 Control plane and data plane` | **the whole phrase** becomes one link, not just the number. A period after the number is allowed |
| An explicit link — `[2](#2)`, `[__2__](#2)`, `[3.1 Navigation](#3.1)` | a link to that section. Use it for a **bare chapter number**, which is never auto-linked, and anywhere you want to choose the wording yourself. Emphasis in the label is honoured |
| A section number in a **heading** | left as plain text. **A heading never carries a link** |
| A number with no matching heading | left as plain text |

Links work inside table cells as well as in paragraphs.

Software versions are deliberately left alone. A number is skipped when it is followed by `.x`,
another digit or a `+`, or when it follows the words release, version, software, ION or PAN-OS.
That keeps `6.3.x`, `6.3.1+` and "releases 6.3–6.5" as text, and `release 2.3` is not a link even
though 2.3 is a real section.

External links in the Markdown stay external links.

## 5. Formatting carried across

- Headings become real Word heading styles, so the navigation pane and the contents field work
- **Lists are coloured by nesting depth** — blue at the top level, orange one level in, green two
  levels in, applied to the bold lead-in of each item. A nested menu map or taxonomy therefore
  reads as a tree rather than as a wall of bullets. The colour is derived from the indentation in
  the Markdown; there is nothing to mark up by hand.
- Tables become real Word tables with borders and a shaded header row
- Bold, italic, inline code, block quotes, images, code fences
- A title page in the shape Palo Alto Networks product documentation uses, a contents field, and a
  page footer with the document name and page number

A fenced diagram (for example `mermaid`) cannot render in Word. The fence is written as monospace
text under a line saying it renders in the online version.

## 6. Things that go wrong

- **"Permission denied" or a file called `… (new).docx`.** The target was open in Word. The
  converter builds beside the target and moves it into place, so nothing is lost; it falls back to
  `… (new).docx` and says so. Close Word and re-run to replace the original.
- **A marker count that does not match the comment count.** A marker was dropped. The usual cause
  is a new marker spelling the converter does not recognise.
- **Review language left in the clean copy.** Removing the markers is not enough: body text that
  *refers* to them ("see the VERIFY in 3.2.12") then points at nothing. After building the clean
  copy, search it for `VERIFY`, `COMMENT`, `SCREENSHOT`, `TODO` and `TBD`. Anything found is a
  sentence to fix in the Markdown, not in the Word file.
- **A stale "Applies to" on the cover.** It comes from the flag, not the document. If the body has
  moved on, fix the body and pass the new value.

## 7. Before handing the files over

1. Both files built, and the review copy's comment count equals its marker count.
2. The clean copy searched for review language and found none.
3. Headings, tables and image counts identical between the two files.
4. Tell the user that the contents page needs **Update Field** in Word on first open, since Word
   fills that in itself.
