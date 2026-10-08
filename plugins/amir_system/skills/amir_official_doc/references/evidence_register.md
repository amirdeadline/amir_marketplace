# Evidence register

The register keeps traceability out of the reading flow. The reader-facing document stays clean; the
register records where every substantive technical claim came from.

## 1. File and format

`<slug>.evidence.md`, next to `<slug>.md`. `mddoc.py check <slug>.md` finds it automatically.

The example shows the format only. Its claims, labels and line numbers are placeholders, not evidence.

```markdown
# Evidence register: Prisma SD-WAN Branch Health Assessment

Document: `branch-health-assessment.md`
Audience: customer
KB root: E:\PC3_Shared\Palo\COE\Prisma_SASE_KB

## Non-technical sections

- Introduction
- Purpose
- Scope
- Intended Audience
- Sources

## Claims

| ID | Section | Claim | Label | Sources | Notes |
|---|---|---|---|---|---|
| C-001 | Circuit Health > Packet Loss | The ION measures loss per path with LQM probes | CONFIRMED | SRC-000029 (admin guide, line 41230) | |
| C-002 | Circuit Health > Packet Loss | CLI steps to collect uplink loss data | INTERNAL | SRC-000101; `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/lqm-uplink-pkt-loss.md` | internal only |
| C-003 | Circuit Health > Packet Loss | Persistent loss above the policy threshold warrants a carrier ticket | INFERENCE | SRC-000036 | engineering advice |
| C-004 | Circuit Health > Packet Loss | Default loss threshold | UNKNOWN | | user to confirm their policy value |
```

## 2. Columns

| Column | Content |
|---|---|
| ID | `C-001`, `C-002`, ... stable once assigned. |
| Section | Heading text without its number. Use `Parent > Child` when the same heading text appears more than once. |
| Claim | The fact as stated in the document, shortened. |
| Label | `CONFIRMED`, `INTERNAL`, `INFERENCE` or `UNKNOWN` (definitions in `/amir_prisma_sdwan`). |
| Sources | SRC IDs, file paths in backticks, or `user: <what the user supplied>` for facts the user gave you (notes, outputs, decisions). Add a line number or section name when it helps a reviewer. |
| Notes | Conflicts, freshness concerns, internal-only warnings, decisions taken by the user. |

Facts the user supplied: cite them as `user: notes in the request, <date>` (no backticks needed) and label
them INTERNAL unless the user says they come from official documentation. Facts about the user's own
environment (their tenant, their procedure) are theirs to confirm; record the decision in Notes.

## 3. Rules the check enforces

`mddoc.py check <doc> --registry <KB root>/palo-alto-knowledge-base/source-registry.json`:

| Code | Rule |
|---|---|
| E008 | Every SRC ID in the register or the document exists in the registry. |
| E009 | Every register section exists in the document. |
| E010 | Labels are one of the four allowed values. |
| E011 | CONFIRMED and INTERNAL rows cite at least one source. |
| E012 | Every backticked file path (contains `/` or `\`, or ends in a file extension) exists under the KB root. |
| W107 | Every section with text has a register row, or is listed under "Non-technical sections". |
| W110 | A CONFIRMED row cites at least one official (rank 1-4) source. |
| W111 | An INFERENCE row names the evidence it rests on. |
| I201 | UNKNOWN rows are listed so you can confirm each one is visible to the reader. |

## 4. Sources appendix in the document

Add `## Appendix: Sources` listing the documents the reader may consult:

- Customer documents: official sources by title (and public URL when the registry has one). Internal
  sources do not appear by path or Confluence link. If a recommendation depends on internal material,
  either confirm with the user that it can be shared, or describe it as Palo Alto Networks field guidance
  without a reference.
- Internal documents: list SRC IDs, titles and paths, and mark internal sources as internal.

Do not put citations after every sentence. A short inline reference ("see the Prisma SD-WAN Administration
Guide") is fine where a reader would want to follow up.
