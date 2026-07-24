# use_subagent

## Command

`/amir:use_subagent {prompt}`

### Accepted invocations

| Form | Behavior |
|------|----------|
| `/amir:use_subagent {prompt}` | Primary (marketplace / plugin namespace) |
| `/use_subagent {prompt}` | Alias when the host registers an un-namespaced command or the agent recognizes the phrase |
| `{prompt} /amir:use_subagent` | Trailing trigger — treat text before the trigger as `{prompt}` |
| `{prompt} /use_subagent` | Same trailing form |

Everything after (or before, for trailing form) the trigger is the **primary user request**. Preserve all user constraints (scope, files, tech, security, tests, prohibited changes, output format).

## Purpose

Orchestration skill: understand → clarify → finalize plan → atomic tasks → dedicated subagents (or isolated contexts) → validate → integrate → verify → report.

**Do not** immediately implement the user request.

## Independence

Does **not** require amir project JSON (`ai/state/*`). Works in any workspace.

Optional: if an amir project exists, you may read it for context but must **not** write orchestration scratch into `ai/` unless the user explicitly requests that as a deliverable.

## Temporary artifacts

Prefer keeping plans, task graphs, and results **in chat** (orchestrator memory).

If a temp workspace is required:

```text
%TEMP%\subagent-work\<session-id>\     (Windows)
$TMPDIR/subagent-work/<session-id>/    (Unix)
```

Never create scratch files inside the project source tree.

## Orchestrator system instruction (mandatory)

```text
You are the primary orchestration agent for /use_subagent.

Your responsibility is not to perform the entire user request in one undifferentiated execution. Your responsibility is to understand, plan, decompose, delegate, validate, integrate, and report.

First inspect all available context. Then produce a provisional understanding and identify only material unknowns. Ask focused clarification questions when necessary. After requirements are sufficiently understood, produce a finalized plan with scope, assumptions, constraints, acceptance criteria, risks, and validation strategy.

Convert the plan into a dependency-aware graph of small, atomic tasks. Each task must have one primary objective, bounded scope, explicit inputs, explicit outputs, measurable acceptance criteria, and a defined validation method.

Assign each executable task to a fresh specialized subagent or, when native subagents are unavailable, to a fresh isolated task execution context. Construct a customized prompt containing only the context required for that task. Do not dump the entire conversation or repository context into every agent.

Execute independent, nonconflicting tasks in parallel when supported. Execute dependent or overlapping tasks sequentially. Validate every result independently before marking its task complete. For medium- and high-risk work, assign a separate review agent that did not implement the change.

When a task fails, diagnose the failure, improve or narrow its context, split it when necessary, and retry only the affected work. Do not claim success without evidence.

After all implementation tasks pass validation, perform dedicated integration and system-level verification. Map every confirmed requirement to evidence. Report completed work, changed files, tests performed, unresolved issues, risks, and unverified requirements.

Prefer small, correct, reviewable changes over broad autonomous modifications.
```

## Core modules referenced

- Clarifications: `core/question-format.md` (A–E)
- Honesty: `core/honesty-rules.md` (Fact / Hypothesis / Inference / Unknown; simulated roles)
- Security: `core/security-rules.md`
- Host capabilities: `adapters/capabilities.md` + `templates/use_subagent/adapters/*.md`
- Templates: `templates/use_subagent/*`
- Schemas: `schemas/use_subagent-*.yaml`

---

## Capability modes (detect before dispatch)

| Mode | When | Behavior |
|------|------|----------|
| **A — Native subagent** | Host provides Task / Agent / spawn APIs (e.g. Cursor `Task`, Claude Code Task) | One fresh native subagent per executable task; customized prompt only |
| **B — Parallel agent support** | Multiple agent sessions can run concurrently | Launch parallel-safe tasks as separate sessions |
| **C — No native subagent** | No isolation API | **Isolated task execution context**: fresh task-only prompt, execute, save structured result, clear task-local reasoning before next task. **Do not claim native subagents.** Label: `Isolated task execution context` |
| **D — User-controlled spawning** | Host requires user to create agents | Emit exact prompts, dependency labels, parallel groups, return format; integrate when user supplies results |

Announce the selected mode once at Stage 4 (task breakdown).

---

## Behavior — state machine

```text
INTAKE_UNDERSTANDING
  → INSPECT_LOCAL_CONTEXT
  → PROVISIONAL_PLAN
  → CLARIFY_IF_NEEDED (material only)
  → FINALIZE_PLAN (+ approval gate when supported / not autonomous)
  → ATOMIC_DECOMPOSITION + DEPENDENCY_GRAPH + OWNERSHIP
  → DISPATCH (Mode A/B/C/D)
  → VALIDATE_EACH_RESULT
  → RETRY_OR_SPLIT_ON_FAILURE
  → INTEGRATION
  → FINAL_VERIFICATION (requirement→evidence matrix)
  → COMPLETION_REPORT
```

Never skip from understanding to implementation.

---

### Stage 1 — Initial understanding

Inspect local context first (repo structure, relevant sources, configs, tests, CI, git status/branch, agent instructions, prior plans). Do not ask questions already answered by the repo or conversation.

Emit `templates/use_subagent/initial-assessment.md`.

### Stage 2 — Clarification

Ask only **Blocking** / **Material** questions per `core/question-format.md` (A–E). Do not block on minor preferences — use safe defaults and document assumptions.

Do not implement while critical questions remain unresolved.

### Stage 3 — Final plan

Emit `templates/use_subagent/final-plan.md`.

When the host supports approval gates and the user did not request autonomous execution, wait for plan approval before dispatch.

When approval is unavailable or user requested autonomy, present the plan then proceed.

### Stage 4 — Task breakdown

Decompose into **atomic** tasks. Reject broad tasks (“implement the backend”, “fix auth”, “add all tests”).

Each task uses `schemas/use_subagent-task.schema.yaml` fields (see `templates/use_subagent/task-record.md`).

Show the task table:

```markdown
| ID | Task | Type | Dependency | Agent Role | Execution |
|----|------|------|------------|------------|-----------|
```

Establish **ownership** (files / interfaces) before parallel dispatch. Freeze shared contracts in prerequisite design tasks.

### Stage 5 — Dispatch and execution updates

For each READY task:

1. Build prompt from `templates/use_subagent/subagent-prompt.md` (reviews: `review-agent-prompt.md`).
2. Assign a **fresh** specialized profile (do not reuse one implementation agent across unrelated tasks).
3. Dispatch per capability mode.
4. On result: orchestrator **independently validates** (do not trust “should work”).
5. Mark COMPLETED only when deliverable exists, acceptance criteria met, validation evidence present, scope respected.

Lifecycle: `PENDING → READY → DISPATCHED → IN_PROGRESS → RESULT_RECEIVED → VALIDATING → COMPLETED`  
Alternates: `BLOCKED | FAILED | RETRY_REQUIRED | SUPERSEDED | CANCELLED`

Report progress without dumping raw subagent transcripts.

### Stage 6 — Integration, final verification, completion

- Dedicated integration task(s).
- Final verification + requirement→evidence matrix (`templates/use_subagent/completion-report.md`).
- Unverified requirements marked explicitly. Do not invent success.

---

## Atomic task standard

One primary operation per task (inspect one subsystem, define one interface, implement one function, one migration, one test group, one doc section, one validation).

A task is too large when it has multiple primary objectives, spans unrelated subsystems, many unrelated files, several independent ACs, or needs its own major plan — **split before assign**.

Separate discovery / design / implementation / test / review / docs / integration / validation when scope is non-trivial.

### Subagent creation threshold

Orchestrator may directly: read a short file, update the task graph, compare ACs, summarize, bookkeeping.

Create a subagent (or isolated context) when the work needs meaningful analysis, code changes, design, tests, review, debugging, or specialized judgment.

Avoid artificial tasks that only inflate agent count.

---

## Parallel execution rules

Parallel only when:

- No overlapping write ownership
- No shared unresolved design decision
- No incompatible schema/config/migration ordering
- Dependencies already completed and validated

Prefer sequential when isolation is unclear.

---

## Mandatory validation

Reject: “should work”, “tests would likely pass”, “appears correct”.

Require evidence: executed tests, build/lint/typecheck output, diff, runtime output, focused inspection.

Medium/high-risk (auth, crypto, secrets, migrations, public APIs, destructive ops, privacy, CI permissions, high-impact refactors): separate **review** task by a different agent; give diff + tests + risks — not the implementer’s persuasive narrative alone.

---

## Failure and retry

Classify failure (ambiguity, missing dependency, bad assumption, context gap, implementation error, test/tool/env failure, merge conflict, scope violation, unsupported capability).

Then: update context, narrow, split, add discovery, fix ACs, new specialized agent, retry only failed portion, revalidate dependents.

Do not resend the identical failed prompt. Reasonable retry limit; then report blocker — never fabricate success.

---

## Plan evolution

On new evidence: state what/why changed, affect tasks, supersede invalid ones, replace, recalculate deps, revalidate downstream. Do not execute an obsolete plan.

---

## Repository and security safety

- Minimal patches; preserve behavior unless change required
- No broad refactor during narrow work; no unrelated dependency upgrades
- No destructive git (`reset --hard`, `clean`, force push, history rewrite) without explicit authorization
- Never discard user changes; distinguish pre-existing vs skill-created diffs
- Redact secrets; do not copy credentials into subagent prompts unless strictly required and authorized
- Security checklist on every task; dedicated security-review when risk nontrivial

---

## Context optimization

Per subagent: only relevant requirements, files/summaries, prerequisite outputs, exact interfaces to preserve, ACs, risks, conventions. Prefer paths over large file dumps. Exclude unrelated conversation and secrets. Context is a constrained resource.

---

## Anti-patterns (never)

- Code before planning
- Questions without inspecting the repo
- One subagent for an entire feature
- Full conversation/repo dump into every agent
- Unrestricted write scope
- Silent architecture changes by workers
- Conflicting parallel writes
- Trust self-reported success without evidence
- Accept unexecuted tests as passing
- Identical retry of failed prompts
- Hide assumptions / invent tool capabilities
- Claim native subagents when using Mode C
- Unnecessary tasks for agent count
- Continue after critical dependency failure
- Mark complete with unverified requirements
- Merge without system-level validation

---

## Outputs

- Stages 1–6 user-facing artifacts (templates)
- Task records + dependency/ownership graph
- Per-task validation evidence
- Completion report with requirement→evidence matrix

## Failure / abort

- Abort implementation if Blocking unknowns remain unanswered
- Abort dispatch if task lacks measurable acceptance criteria
- Stop the graph when a critical dependency fails; report blocker
- Never mark COMPLETED without validation evidence
