# document_max

## Command

`/document_max {prompt}`

Options:

| Flag | Values | Description |
|------|--------|-------------|
| `--out` | Path | Output document path (required unless resuming existing sprint) |
| `--mode` | `full` \| `update` | `full` creates new doc sprint; `update` re-runs affected sections only |
| `--scope` | Text | Scope statement override or narrowing (merged with `{prompt}`) |

## Purpose

Run a multi-phase documentation sprint with `doc-lead`, `doc-worker`, and `doc-verifier` roles: inspect sources, obtain human approval on outline and budget, write sections incrementally with strict traceability, checkpoint every 15 sections, and complete only after three final verification passes.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{prompt}` | Yes | What to document and for whom |
| `--out` | Yes (full) / Read (update) | Final document output path |
| `--mode` | Optional | Default `full`; `update` requires existing docmax state |
| `--scope` | Optional | Additional scope boundaries or exclusions |
| Project root | Implicit | Current amir project root |
| Doc ID | Assigned | New `D###` in `tasks.json` (full) or existing docmax state (update) |
| Source tree | Implicit | Code, configs, tests, prior docs cited in coverage matrix |

## Behavior

### Phase 1 — Inspect (`doc-lead`)

1. Act as **`doc-lead`** per `core/naming-rules.md`; assign or resume Doc ID (`D###`).
2. Parse `{prompt}`, `--out`, `--mode`, `--scope`; verify `--out` parent path writable.
3. **Full mode:** inventory candidate source files, existing docs, and gaps; draft `scope_statement` and `non_goals`.
4. **Update mode:** load `ai/state/docmax-<doc-id>.json` and progress companion; read current `--out` document; determine which sections are affected by prompt/scope changes.
5. Record phase `inspect` → `complete` in docmax state; append `document_max` activity with mode and doc id.

### Phase 2 — Coverage matrix, glossary, approval gate (`doc-lead`)

6. Build **outline** array: stable section ids, titles, required topics, status `pending`.
7. Build **coverage_matrix**: each row links section → required topics → source files → claim_ratio placeholders (V/I/A/U).
8. Build **glossary** from domain terms found in sources; flag conflicts for human resolution.
9. Estimate cost: section count, projected worker+verifier cycles, token/cost estimate via `node tools/cost.js` when available; log `cost_estimate` per `core/budget-rules.md`.
10. Present **approval gate** to human per `core/question-format.md` and `core/interaction-style.md`:
    - Proposed outline (section ids + titles)
    - Section count and checkpoint plan (every 15 sections)
    - Coverage matrix summary
    - Glossary draft
    - Cost estimate
11. Wait for explicit human approval; record in `ai/state/decisions.json` and `ai/state/approvals.json`.
12. Initialize or update `ai/state/docmax-<doc-id>.json` conforming to `schemas/docmax.schema.json`; write progress companion `ai/state/docmax-<doc-id>-progress.json` (sections queued, current section, checkpoint counters, merge status).
13. Register documentation task in `ai/state/tasks.json` if new (`D###`, status `in_progress`).

### Phase 3 — Incremental sections (`doc-worker` + `doc-verifier`)

14. For each outline section (full: in order; **update:** only affected section ids and dependents):
    1. **doc-lead** assigns section; render worker prompt from `templates/docmax-section-worker-prompt.md.tmpl` into `ai/agents/doc-lead/workspaces/<doc-id>/<section-id>/worker-prompt.md` (or project-consistent doc agent path).
    2. **doc-worker** writes section file per template **Section Detail Template**; tag every factual claim **VERIFIED | INFERRED | ASSUMED | UNKNOWN** per `core/honesty-rules.md`; use **UNKNOWN block format** from template when evidence missing; reject and rewrite **banned lazy phrases** (etc., and so on, standard implementation, handled elsewhere, similar logic applies, refer to the code, implementation details omitted, additional cases may exist, as needed, various, typically, should be straightforward).
    3. Include **Mermaid** diagrams only when they clarify architecture or flow; diagrams must match cited sources; omit subsection if not useful.
    4. Append `doc_section` activity: `node tools/activity.js <root> append --agent doc-worker --action doc_section --task <doc-id> --result "drafted <section-id>"`.
    5. **doc-verifier** reviews via fresh prompt from `templates/docmax-section-verifier-prompt.md.tmpl`; **FAIL** on banned phrases, mislabeled claims, missing required topics, or shallow depth; update coverage row claim_ratio (V/I/A/U).
    6. On verifier **PASS**, mark section `verifier_passed` in docmax state and progress companion; on **FAIL**, return to doc-worker with issues (fix loop per section, logged).
    7. Merge approved section into staging path (not final `--out` until completion gate).
15. **Budget checkpoint:** after every **15** completed sections (`budget.checkpoint_every`, default 15), pause per `core/budget-rules.md`:
    - **doc-verifier** batch review
    - Human checkpoint if material drift
    - Log `document_max_checkpoint` to `ai/state/activity.jsonl`
    - Update `budget.sections_completed` in docmax state
    - Do not start section 16+ without checkpoint completion
16. Register new unknowns in `unknowns_register`; never silently omit gaps.

### Final passes (`doc-lead` + `doc-verifier`)

17. **Pass 1 — Consistency:** terminology, cross-references, heading hierarchy, duplicate claims, glossary alignment.
18. **Pass 2 — Coverage:** every coverage_matrix row `complete`; no required topic `missing`; source_files exist and support claims.
19. **Pass 3 — Unknowns:** all `unknowns_register` entries dispositioned (`resolved` or `accepted_risk` with human approval); no stale UNKNOWN blocks in final text without register entry.
20. Assemble final document at `--out`; set `document_complete: true` only when all three passes PASS.

### Completion gate

21. Verify: all outline sections `complete` or `verifier_passed` merged; `document_complete` criteria met; task `D###` ready for orchestrator review.
22. Transition task toward `qa_passed` / `complete` per orchestrator workflow; append `document_max` completion activity.
23. Emit chat summary per `core/message-contract.md` — **chat output ONLY:**
    - Output path (`--out`)
    - Progress/state paths (`ai/state/docmax-<doc-id>.json`, progress companion)
    - **Unknowns summary** (open count + ids)
    - **Coverage summary** (sections complete/total, matrix rows blocked/missing)
    - Do **not** dump section bodies or full matrix in chat; offer `/details` for artifacts.

### Update mode specifics

24. When `--mode update`: skip full outline re-approval unless scope change affects section count or non-goals materially.
25. Diff affected sections from prompt + scope + changed source files; re-run Phase 3 for impacted ids only; re-run final passes on merged document.
26. Bump docmax state `mode: update` and record changed section ids in progress companion.

## Core modules referenced

- Follow `core/naming-rules.md`
- Follow `core/budget-rules.md`
- Follow `core/honesty-rules.md`
- Follow `core/message-contract.md`
- Follow `core/question-format.md`
- Follow `core/interaction-style.md`
- Follow `core/workspace-rules.md`
- Follow `core/qa-loop.md`
- Follow `core/no-drift-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/state/docmax-<doc-id>.json` | Read/Write |
| `ai/state/docmax-<doc-id>-progress.json` | Read/Write |
| `ai/state/tasks.json` | Read/Write (Doc task `D###`) |
| `ai/state/decisions.json` | Write (outline approval, unknown acceptances) |
| `ai/state/approvals.json` | Write |
| `ai/state/activity.jsonl` | Append (`document_max`, `doc_section`, `document_max_checkpoint`, `cost_estimate`) |
| `ai/state/status.json` | Write (current doc task, phase) |
| `ai/agents/doc-lead/**` | Write (prompts, plans, merge staging) |
| `ai/agents/doc-worker/**` | Write (section drafts) |
| `ai/agents/doc-verifier/**` | Write (section reviews) |
| `{--out}` | Write (final assembled document) |
| `templates/docmax-section-worker-prompt.md.tmpl` | Read |
| `templates/docmax-section-verifier-prompt.md.tmpl` | Read |
| `schemas/docmax.schema.json` | Read (validation) |

## Outputs

- Final document at `--out`
- `ai/state/docmax-<doc-id>.json` (complete sprint state)
- `ai/state/docmax-<doc-id>-progress.json` (progress companion)
- Section drafts and verifier reports under doc agent workspaces
- Chat summary: paths, unknowns count/ids, coverage summary only

## Failure/abort behavior

- Abort if `{prompt}` empty or `--out` missing in full mode.
- Abort Phase 3 until Phase 2 human approval recorded.
- **FAIL** section on banned phrases or mislabeled VERIFIED claims; do not merge failed sections.
- Refuse to exceed 15 sections without `document_max_checkpoint` per `core/budget-rules.md`.
- Abort completion gate if any coverage row `blocked` or open unknown without disposition.
- **Update mode:** abort if docmax state or `--out` document missing; do not invent prior outline.
- On schema validation failure for docmax JSON, emit **PROBLEM**; do not set `document_complete`.
- Do not paste full document content in chat on success or failure.
