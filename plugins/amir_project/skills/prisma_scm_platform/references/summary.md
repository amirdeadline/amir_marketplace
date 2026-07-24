# prisma_scm_platform — baked reference summary

ingested: 2026-07-14

This summary is a **distilled index** of the local corpus. Prefer the live
layer (`PRISMA_DOCS_PATH`) for full procedures. Label claims:
`VERIFIED (source file/URL) | INFERRED | ASSUMED`.

## Corpus map

### Prisma SASE Architecture Agent Reference
- path: `prisma_sase_architecure.md`
- size: 4377891 bytes
- terms: adem, ion, prisma access, prisma sd-wan
- topic: Prisma SASE Architecture Agent Reference — source: `prisma_sase_architecure.md`#prisma-sase-architecture-agent-reference (line 3)
- topic: Purpose — source: `prisma_sase_architecure.md`#purpose (line 7)
- topic: How Agents Should Use This File — source: `prisma_sase_architecure.md`#how-agents-should-use-this-file (line 11)
- topic: Included Source PDFs — source: `prisma_sase_architecure.md`#included-source-pdfs (line 19)
- topic: Exact Duplicate PDFs Skipped — source: `prisma_sase_architecure.md`#exact-duplicate-pdfs-skipped (line 42)
- topic: Converted PDF Content — source: `prisma_sase_architecure.md`#converted-pdf-content (line 54)
- topic: Issue Description Date first reported Mitigation — source: `prisma_sase_architecure.md`#issue-description-date-first-reported-mitigation (line 7407)
- topic: Issue Description Date first reported Mitigation — source: `prisma_sase_architecure.md`#issue-description-date-first-reported-mitigation (line 7484)
- topic: Issue Description Date first reported Mitigation — source: `prisma_sase_architecure.md`#issue-description-date-first-reported-mitigation (line 7576)
- topic: Issue Description Date first reported Mitigation — source: `prisma_sase_architecure.md`#issue-description-date-first-reported-mitigation (line 7667)
- topic: Issue Description Date first reported Mitigation — source: `prisma_sase_architecure.md`#issue-description-date-first-reported-mitigation (line 7763)
- topic: Issue Description Date first reported Mitigation — source: `prisma_sase_architecure.md`#issue-description-date-first-reported-mitigation (line 7839)
- topic: P2S client root certificate private key — source: `prisma_sase_architecure.md`#p2s-client-root-certificate-private-key (line 21337)
- topic: please fill this field with a PEM formatted key — source: `prisma_sase_architecure.md`#please-fill-this-field-with-a-pem-formatted-key (line 21338)
- topic: P2S client root certificate private key — source: `prisma_sase_architecure.md`#p2s-client-root-certificate-private-key (line 21519)
- Source PDFs (sample):
  - aws-vpc-tgw — source: `prisma_sase_architecure.md`
  - azure-virtual-wan — source: `prisma_sase_architecure.md`
  - Extending SD-WAN into AWS for Private Application Access Solution Guide - Nov23 — source: `prisma_sase_architecure.md`
  - Extending SD-WAN into Azure for Private Application Access Solution Guide - Sep23 — source: `prisma_sase_architecure.md`
  - extending-sdwan-into-azure-for-private-apps-solution-guide — source: `prisma_sase_architecure.md`
  - Identity-Based and Posture-Based Security for SASE - Solution Guide - Dec25 — source: `prisma_sase_architecure.md`
  - Managing Risk in Connected Assets by Using Device Security - Solution Guide - Oct25 — source: `prisma_sase_architecure.md`
  - Network Security for Public Cloud - Overview - Nov25 — source: `prisma_sase_architecure.md`
  - On Premises Network Security and SD-WAN for the Branch - Design Guide - Oct22 — source: `prisma_sase_architecure.md`
  - On-Premises Network Security for the Branch - Overview - Oct22 — source: `prisma_sase_architecure.md`
  - prisma-sase-multitenant-platform — source: `prisma_sase_architecure.md`
  - prisma-sd-wan-instant-on-network-ion-device-specifications_dps — source: `prisma_sase_architecure.md`

### project.md — Markdowns Prisma SASE (Master Specification)
- path: `project.md`
- size: 18225 bytes
- terms: ion, prisma access, prisma sd-wan, remote network, strata cloud manager
- topic: project.md — Markdowns Prisma SASE (Master Specification) — source: `project.md`#project-md-markdowns-prisma-sase-master-specification (line 3)
- topic: 1. Overview and architecture of the documentation set — source: `project.md`#1-overview-and-architecture-of-the-documentation-set (line 9)
- topic: 2. Annotated directory structure — source: `project.md`#2-annotated-directory-structure (line 22)
- topic: 3. Question-routing map — source: `project.md`#3-question-routing-map (line 57)
- topic: 4. Technologies and dependencies — source: `project.md`#4-technologies-and-dependencies (line 69)
- topic: 5. Prisma SASE Python SDK — consolidated reference (from `prisma_sase_sdk/*.md`) — source: `project.md`#5-prisma-sase-python-sdk-consolidated-reference-from-prisma_sase_sdk-md (line 76)
- topic: 6. QA comparison contract — consolidated (from `ai_prisma_sdwan.md`) — source: `project.md`#6-qa-comparison-contract-consolidated-from-ai_prisma_sdwan-md (line 154)
- topic: 7. PDF-extract references — specification for rebuilding — source: `project.md`#7-pdf-extract-references-specification-for-rebuilding (line 166)
- topic: 8. API bundles (from `api/generation_stats.json`) — source: `project.md`#8-api-bundles-from-api-generation_stats-json (line 184)
- topic: 9. Configuration (names only — never store values) — source: `project.md`#9-configuration-names-only-never-store-values (line 195)
- topic: 10. Setup / usage workflows — source: `project.md`#10-setup-usage-workflows (line 199)
- topic: 11. Known quirks — source: `project.md`#11-known-quirks (line 206)

### Markdowns Prisma SASE — Documentation Index
- path: `README.md`
- size: 5054 bytes
- terms: ion, prisma access, prisma sd-wan, strata cloud manager
- topic: Folder contents — source: `README.md`#folder-contents (line 22)

## Gotchas

- Large PDF-extract files must be **searched**, never read whole — source: corpus README.
- Version-specific SCM/SASE UI paths change often — verify on docs.paloaltonetworks.com / pan.dev before asserting.
- Filename typo `prisma_sase_architecure.md` is intentional in the corpus.

## Live layer

Set `PRISMA_DOCS_PATH` (read env var `PRISMA_DOCS_PATH`; machine-specific default documented in the amir_project plugin README, section "Prisma docs corpus").
Use `references/index.json` to open only matching sections.
