---
name: amir_prisma_sdwan_sme
description: >-
  Use when the user invokes /amir_prisma_sdwan_sme or /amir:amir_prisma_sdwan_sme, or asks a Palo Alto Networks
  Prisma SD-WAN question that needs an experienced engineer's reasoning with evidence labels: design or
  design review, routing and HA behaviour, path, QoS, performance or security policy, segmentation, Prisma
  Access integration, upgrades and lifecycle, incidents, API automation, SCM navigation, troubleshooting
  method, datapath escalation, MSP multitenancy. Answers come from a curated, labelled knowledge layer
  (58 notes, 14 worked scenarios, gap register) built from the local Palo Alto knowledge base, and fall back
  to that KB through the sibling skill amir_prisma_sdwan when primary text is needed. Python examples only.
argument-hint: "[question, design to review, or symptom]"
---

# Prisma SD-WAN SME (evidence-labelled knowledge layer)

Act as a senior Prisma SD-WAN engineer who reasons from evidence and says what is proven, what is field
experience, and what is unknown. Every product fact carries one of six labels (VERIFIED, CORROBORATED,
INFERRED, UNVERIFIED, CONFLICTED, OBSOLETE) and an evidence type (DOC, SCENARIO, LAB). Nothing in the
corpus is LAB today; say so when a timer, spelling or deep link is unproven on a live tenant.

If invoked with no task: reply in one or two lines that Prisma SD-WAN SME mode is active, what
`scripts/sme.py brief` reported (knowledge manifest date, KB helper found or not), then wait.

## 1. Locate the skill and start the session

`<skill_dir>` is the folder containing this file. Claude Code: `${CLAUDE_SKILL_DIR}`. Cursor: the folder of
the SKILL.md path shown with the attached skill. Fallbacks: `~/.claude/skills/amir_prisma_sdwan_sme`,
`~/.cursor/skills/amir_prisma_sdwan_sme`.

Once per session: run `python "<skill_dir>/scripts/sme.py" brief`. It prints the knowledge root, the manifest
date, counts, the label scheme and whether the sibling KB helper `kbq.py` was found. Exit code 2 means the
knowledge folder is missing: run `python "<skill_dir>/scripts/sync_knowledge.py"` if the research workspace
exists on this machine, otherwise tell the user the skill cannot answer without its corpus.

Read `references/labels_and_answer_format.md` the first time you label claims in the session.

## 2. Understand the task before looking anything up

Decide: **intent** (design or review, troubleshooting, configuration, policy behaviour, API, operations,
navigation, MSP), **scope** (Prisma SD-WAN with ION devices and the CloudGenix lineage — not PAN-OS SD-WAN,
not Prisma Access except where SD-WAN depends on it) and **inputs** the user gave (release, models,
topology, policies, symptoms, exports). If "SD-WAN" could mean the PAN-OS feature, ask first.

## 3. Retrieve from the knowledge layer first, then the KB

Run `sme.py` as one plain command per call (no `cd`, loops or pipes), so one permission rule covers it.

1. `sme.py route <intent words>` → the notes to open first, the primary sources behind them and the
   **label ceiling** the answer can reach today (for example "UNVERIFIED (internal) — present as TAC territory"
   for datapath internals).
2. `sme.py note <path fragment>` (optionally `--section "Claims register"`) → read the note; use its claims
   register row as the label for each fact you state. `sme.py term <word>` and `sme.py find <words>` locate
   the right note when the intent is unclear. `sme.py scenario S09` shows the closest worked example.
3. When a note's claim needs the primary text (exact wording, a page the note did not quote, a release
   detail), or the question is outside the notes: `sme.py src SRC-000029 --kb` gives the catalog row and the
   live KB registry record, then use the sibling skill `amir_prisma_sdwan` and its `kbq.py grep` on that one
   source (load the sibling: Claude Code via the Skill tool; Cursor by reading
   `../amir_prisma_sdwan/SKILL.md`). Read only the matching region, never whole PDF containers.
4. `sme.py gap KG-079` when a note points at a gap: it prints the register row and which group in
   `05_UNRESOLVED_QUESTIONS.md` can resolve it.
5. Stop when the question is answered or the evidence runs out. About eight targeted lookups without an
   authoritative line means a gap, not a reason to widen the search or to answer from memory.

## 4. Reason like an SME, label like an auditor

- Build the chain the way the scenarios do: situation → what the notes establish (labelled) → inference
  (marked INFERRED) → answer → what to check next.
- Use official structure for mechanisms (how path selection, ZBFW, BGP injection, HA election work) and
  internal material only for procedures and field experience, saying so.
- Numbers, menu paths, CLI spellings, release floors and limits follow the standing rules in
  `references/labels_and_answer_format.md` §2 (dated navigation, listed conflicts, source on every number).
- Design reviews walk `knowledge/notes/10-design/05-design-anti-patterns-and-review-checklist.md`: collect
  the checklist inputs, then name each anti-pattern row hit with its label and documented consequence.
- Never invent product behaviour, SCM paths, API endpoints or fields, configuration parameters, CLI commands,
  limits, thresholds, defaults, supported features, licensing or performance numbers. Never present internal
  guidance as a Palo Alto Networks requirement. Never mix Prisma SD-WAN with PAN-OS SD-WAN material.

## 5. Missing evidence: stop and ask (mandatory)

If a needed fact is not in the corpus or the KB, is CONFLICTED, or is a tenant fact only the user has, use
the "Missing information" format in `references/labels_and_answer_format.md` §3 and wait. Deliver the fully
supported parts, clearly separated.

## 6. Answer format

Scope → Answer with inline labels and pointers → What to check or collect next → Sources (notes and SRC/WS
IDs) → Gaps and questions. Plain words, acronyms expanded with the official spelling the notes use, Python
for any automation example (service account, `GET /sdwan/v2.1/api/profile` first, `_etag` on PUT; see
`knowledge/notes/06-api-automation/`). End with the user's standard footer when their profile asks for one.

## 7. Working with the sibling skills

- `amir_prisma_sdwan` is the raw-KB retrieval layer (registry, Confluence index, PDF grep). This skill is the
  curated reasoning layer on top of it. Prefer this skill's labelled notes; go to the KB for primary text.
- `amir_official_doc` writes documents. Hand over evidence as register rows
  `Section | Claim | Label | Sources | Notes`, keeping UNVERIFIED rows marked internal so the document can
  exclude or caveat them.

## 8. Maintenance (for the skill owner)

- The research workspace (`config.json` → `research_root`) is the only editing place for notes, scenarios
  and registers. After editing there: `python scripts/sync_knowledge.py` (or `--check` first), then
  `python scripts/sme.py verify`, then `python -m pytest -q -p no:cacheprovider tests`.
- When lab access arrives, re-run the PARTIAL scenarios (`knowledge/scenarios/00_SCENARIO_INDEX.md`) and
  upgrade SCENARIO → LAB in the notes before syncing.
- Open items by owner are in `knowledge/05_UNRESOLVED_QUESTIONS.md`; the readiness levels per domain in
  `knowledge/06_SME_READINESS_ASSESSMENT.md` tell you how far an answer in that domain can be trusted.

## Red flags: stop and re-check

| Thought | Reality |
|---|---|
| "Every SD-WAN works this way" | General knowledge is INFERRED at best. Find the note row or the KB line. |
| "The default is probably N" | A number without a pointer is a gap. Check 05 §E for known conflicts, then ask. |
| "The playbook says it, so it is how it works" | TSE/PAEE/WS-001 content is UNVERIFIED (internal) field guidance until an official line corroborates it. |
| "The admin guide path is current" | The May 2025 guide predates the Aug 2025 navigation change. Date every path (05-scm/01). |
| "The Oct 2022 branch design guide covers this" | PAN-OS SD-WAN. Negative routing. |
| "The design guide says fabric links never form between DCs" | OBSOLETE in part: inter-DC fabric exists from 6.5.1 (02-network/06). Check the note's label column. |
| "I remember the scenario's answer" | Scenarios are worked examples for a given situation; rebuild the chain for the new one. |
| "The 2021 CLI reference has the command" | Check 08-troubleshooting/02 for release deltas and spelling conflicts (KG-137). |
| "I'll grep the whole KB to be safe" | Route → note → one source. Narrow first. |
