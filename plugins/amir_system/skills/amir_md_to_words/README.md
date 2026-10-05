# amir_md_to_words

Converts a Markdown file to Microsoft Word, as two files from one source: a review copy where every
review marker becomes a real Word comment, and a clean copy with the markers removed for anyone
outside. The Markdown file stays the source of truth.

## Invoke

| Tool | How |
|---|---|
| Claude Code | `/amir_md_to_words <path to the .md> [output .docx]` |
| Cursor | Type `/` in Agent chat, pick `amir_md_to_words`, then the path |

## The two files

| File | Review markers |
|---|---|
| `<name>.docx` | Become __real Word comments__ in the reviewing pane |
| `<name> Clean.docx` | __Removed__ |

Both carry the same body text, headings, tables, images and links.

## What it carries across

- Headings as real Word heading styles, so the navigation pane and the contents field work
- __Cross-references as working links.__ A section number in the text becomes a hyperlink to that
  heading; a section written out in full — `2.3 Control plane and data plane` — links across the
  whole phrase. A heading never carries a link. Software versions are left alone
- Tables with borders and a shaded header row; bold, italic, inline code, block quotes, images
- __Lists coloured by nesting depth__, so a menu map reads as a tree
- A title page in the shape Palo Alto Networks product documentation uses, a contents field, and a
  page footer with the document name and page number

## Things that go wrong

- __A marker count that does not match the comment count__ means a marker was lost.
- __Review language left in the clean copy.__ Removing the markers is not enough: body text that
  refers to them then points at nothing. Search the clean copy for `VERIFY`, `COMMENT`,
  `SCREENSHOT`, `TODO` and `TBD`, and fix anything found in the Markdown, not in the Word file.
- __A file called `… (new).docx`__ means the target was open in Word. Nothing is lost; close Word
  and run again.
- __A stale "Applies to" on the cover__ comes from the flag, not the document. Fix the body first.

`SKILL.md` has the full checklist to run before handing the files over.
