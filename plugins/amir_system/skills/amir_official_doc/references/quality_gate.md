# Quality gate

Run this before calling a document complete. `mddoc.py check` covers the items marked (auto). Review the
rest yourself by reading the document from the top as the intended reader. Report the result to the user
(pass, or what remains and why); do not write the gate result into the document.

## 1. Technical

- [ ] Every important claim has a register row with a label and source. (auto: W107, E011)
- [ ] No behavior, threshold, default, limit, command, API endpoint or field appears without evidence.
- [ ] Nothing from PAN-OS SD-WAN or other wrong-product material (negative routing respected).
- [ ] Internal material is labeled INTERNAL in the register and handled per audience in the document.
- [ ] Conflicting sources are shown or resolved with a stated reason, never merged silently.
- [ ] INFERENCE reads as advice, not as a Palo Alto requirement.

## 2. Content

- [ ] The topics the evidence says matter are covered; gaps are listed as open items.
- [ ] Each major topic explains what, why and how to interpret, as far as useful.
- [ ] No section exists only to make the document look complete.
- [ ] Procedures can be followed start to finish without guessing.

## 3. Writing

- [ ] Reads like a human engineer wrote it: no filler, hype or repeated summaries. (auto: W102 for common phrases)
- [ ] No em dashes as sentence separators. (auto: W101)
- [ ] One term per concept; product names exact.
- [ ] Acronyms defined at first use. (auto: W105)
- [ ] Notes and callouts only where a reader must not miss something. (auto: W106 counts them)

## 4. Structure

- [ ] One title; numbering correct; no skipped levels. (auto: E001, E002, E003)
- [ ] Hierarchy is logical: each heading sits under the right parent.
- [ ] Tables render: header row, consistent columns. (auto: E005)
- [ ] Internal links and relative file links resolve. (auto: E006, E007)
- [ ] Code fences closed and tagged with a language. (auto: E004 for closing)
- [ ] No empty sections; long sections split. (auto: W103, W104)
- [ ] Opens in amir_md with a clean navigation tree.

## 5. Evidence

- [ ] SRC IDs exist in the registry; paths exist. (auto: E008, E012)
- [ ] Register sections match the document. (auto: E009)
- [ ] CONFIRMED rows cite an official source. (auto: W110)
- [ ] Every UNKNOWN item is visible to the reader. (auto lists them: I201)
