# amir_doc_review

Evidence-based multi-phase review skill for large technical design documents (HLD, LLD,
as-built, migration, Prisma SASE / Access / SD-WAN, network and security architecture).

Part of the `amir_system` plugin (`/amir:amir_doc_review`). Also installable as a user-scope
skill (`/amir_doc_review`) for Cursor and Claude Code testing.

## Invocation

```text
/amir:amir_doc_review <document path>
```

```text
/amir_doc_review <document path>
```

Optional flags (see skill frontmatter / SKILL.md):

```text
/amir:amir_doc_review path/to/design.docx `
  --knowledge-base "D:\kb\prisma-sase" `
  --references "D:\designs\approved" `
  --requirements "D:\projects\req.md" `
  --document-type HLD `
  --product-version auto `
  --management-platform scm `
  --internet-research enabled `
  --review-depth deep `
  --strict-evidence `
  --output ".ai/doc_review/hld-review.md"
```

## Workflow summary

1. Intake + document-type rubric  
2. Knowledge collection (local then official vendor docs)  
3. Logical document map (not equal page chunks)  
4. Shared registries (requirements, objects, flows, …)  
5. Fresh sub-agent per review unit with bounded context  
6. Separate tracks: requirements, architecture, flows, security, resiliency, scale, ops,
   migration, consistency, diagrams, editorial  
7. Independent validation that tries to **disprove** each candidate  
8. Synthesis with coverage gate and structured report  

## Knowledge sources

Configure defaults in `config/knowledge_sources.yaml`. Prefer retrieval; never embed the
full KB in every agent. Prefer `docs.paloaltonetworks.com` and related official domains when
internet research is enabled and permitted.

## Hallucination controls

- Evidence-before-findings; materiality threshold; no forced criticism  
- Independent validation stage  
- Explicit zero-finding disposition allowed and preferred when justified  
- Optional and editorial separated from technical findings  
- Product-version / management-platform awareness  

## Install (user scope, for testing)

Cursor and Claude skills junctions (from plugin skill directory):

```bat
cmd /c mklink /J "%USERPROFILE%\.cursor\skills\amir_doc_review" "E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir_system\skills\amir_doc_review"
cmd /c mklink /J "%USERPROFILE%\.claude\skills\amir_doc_review" "E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir_system\skills\amir_doc_review"
```

Plugin-level: reinstall or refresh `amir_system` marketplace plugin, or use the existing Cursor
local junction to `plugins/amir_system`.

## Tests

See `tests/test_cases.md`.
