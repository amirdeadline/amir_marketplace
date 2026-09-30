# amir_md

amir_md is a Word-style editor for Markdown files in VS Code. You edit formatted text with a toolbar, move around with a heading navigation pane, fold sections the way Word does, and export to PDF or Word. The file on disk stays plain Markdown.

Requirements are in `docs/PRD.md` and `docs/SRS.md` in the source folder.

## Open a file

- Right-click a `.md` file in the Explorer and choose **Open with amir_md**.
- Or use the book icon in the title bar of a Markdown text editor, or **Reopen Editor With...** > **amir_md**.
- To open every `.md` file in amir_md, turn on the setting `amir_md.defaultEditor`.
- **Open as Markdown Text** (code icon in the title bar) shows the same file as text beside amir_md. Changes in either view appear in the other.

Save, Save As, Revert, auto save, and the unsaved-changes dot work the same as for any text file.

## What you can do

| Area | Features |
|---|---|
| Navigation pane | Heading tree, filter box, level list (All, Heading 1 to Heading 5) with **Expand** and **Collapse**, current section highlight, breadcrumb, keyboard navigation, resizable, hide with the toolbar button |
| Section folding | Triangle to the left of every heading; it grows on hover, points right when folded and down when open. Folds are remembered per document and never change the file |
| Paragraph styles | Normal text, Title, Subtitle, Heading 1 to Heading 6, left, center, and right alignment |
| Character formatting | Font, size in points, bold, italic, underline, strikethrough, superscript, subscript, font color, highlight color, clear formatting |
| Lists and blocks | Bulleted, numbered, and checkbox lists with Tab and Shift+Tab, quotes, inline code, code blocks with a language, horizontal lines, tables |
| Links | Ctrl+K dialog with a list of the document's headings, link bubble with Edit, Open, and Remove. Ctrl+click opens a link |
| Pictures | From a file, from a web address, or paste and drop. Relative paths such as `images/topology.png` and `../shared/diagram.png` work. Select a picture to edit its alternative text, title, and width |
| Export | PDF (through Microsoft Edge or Google Chrome), Word (.docx with real Title, Subtitle, and Heading styles), HTML, and Save As Markdown |

## How formatting is saved

Markdown has no syntax for colors, fonts, underline, or Title and Subtitle, so amir_md writes a small amount of inline HTML for those. Everything else stays standard Markdown.

| Formatting | Saved as |
|---|---|
| Bold, italic, strikethrough, code | `**bold**`, `*italic*`, `~~strike~~`, `` `code` `` |
| Underline, superscript, subscript | `<u>text</u>`, `<sup>2</sup>`, `<sub>2</sub>` |
| Font color | `<span style="color:#E53935;">Critical finding</span>` |
| Several styles on one run | `<span style="color:#1E88E5;background-color:#FFF59D;font-family:Georgia;font-size:14pt;">text</span>` |
| Title and Subtitle | `<p data-amir-style="title" style="font-size:26pt;">Title</p>` |
| Centered paragraph | `<p style="text-align:center;">text</p>` |
| Link | `[text](https://example.com)` |
| Picture | Markdown picture syntax with a relative path; after a width change, an `img` tag with a `width` attribute |

GitHub and some other viewers remove `style` attributes, so colors and fonts show in amir_md, the VS Code preview, and exports, but not on github.com.

## Your file stays as you wrote it

- Opening and saving without changes leaves the file byte for byte the same.
- When you edit, only the blocks you changed are written again. Spacing, list markers, escapes, and line breaks in other blocks stay as they were.
- Parts amir_md cannot show as formatting (front matter, HTML blocks, reference definitions) appear as a gray **Markdown source** panel. You can edit the text in the panel, and it is saved as written.

## Keyboard shortcuts

| Action | Shortcut |
|---|---|
| Bold, italic, underline | Ctrl+B, Ctrl+I, Ctrl+U |
| Strikethrough | Alt+Shift+5 |
| Link | Ctrl+K |
| Normal text, Heading 1 to 6 | Ctrl+Alt+0, Ctrl+Alt+1 to Ctrl+Alt+6 |
| Bulleted, numbered list | Ctrl+Shift+8, Ctrl+Shift+7 |
| Clear formatting | Ctrl+Space |
| Indent, outdent in a list | Tab, Shift+Tab |
| Fold, unfold the section at the cursor | Alt+Shift+Minus, Alt+Shift+Plus |
| Undo, redo | Ctrl+Z, Ctrl+Y |
| Line break inside a paragraph | Shift+Enter |
| Find | Ctrl+F |

## Settings

All settings start with `amir_md.`: default editor, file size warning, pictures folder and remote pictures, font list and default font, color palette, fold memory, navigation pane width and starting level, Markdown markers for new content, and export engine, browser path, page size, margins, and page numbers.

## Build

```bash
npm install
npm run compile
npm test
npm run package
```

`npm run package` writes `amir-md-<version>.vsix`. Install it with **Extensions: Install from VSIX...**.

## Known limits in this version

- Undo from the VS Code **Edit** menu acts on the text document, not on amir_md's own history. Use Ctrl+Z or the toolbar buttons.
- PDF export uses the browser's command line print instead of puppeteer-core (spike S3). There is no table of contents option yet.
- SVG and WebP pictures are not embedded in Word exports; a placeholder with the alternative text is written instead.
- Pressing Enter at the end of a folded heading adds the new paragraph after the hidden content, and the section opens so you can type in it.
- Tables with several paragraphs in a cell and the format painter are not supported yet.
