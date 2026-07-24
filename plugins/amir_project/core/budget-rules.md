# amir — budget rules

Cost and cycle limits for fix loops, discovery, documentation, and context — all auditable.

## Fix-loop budget

| Rule | Value |
|------|--------|
| Default max cycles per task | **10** (each cycle = fix attempt + re-QA) |
| Counter | `(cycle n/10)` in `core/message-contract.md` |
| On exhaustion | **BLOCKED** unless extension approved |

### Extension request (required to exceed 10)

Worker or orchestrator must request extension with **all four elements**:

1. **Task id** and current cycle count
2. **Summary of prior attempts** — what was tried each cycle (≤1 line per cycle)
3. **Root cause hypothesis** — VERIFIED vs INFERRED labeled
4. **Why the next 10 cycles will differ** — concrete process or scope change, not "try harder"

Human approval logged to `decisions.json` → **+10 cycles** per approval.

Repeat extension requests require new four-element justification.

## Two-strike rule

Within a single fix loop, if the **same root cause class** fails QA **twice** consecutively (e.g. same acceptance id, same test file):

1. Stop blind retries
2. Orchestrator **must** intervene: spec review, pair with architect, or narrow scope
3. Log `two_strike` to activity.jsonl
4. Next fix-prompt must include changed approach — not duplicate prior fix

Third consecutive same-class failure without intervention → **BLOCKED**, escalate human.

## Discovery budget

Question batches consume discovery budget:

| Phase | Default cap |
|-------|-------------|
| Project create / design | Host-defined or 3 large batches (5–20 questions each) |
| Per-task clarification | 1 Material batch unless Blocking |

- **Blocking** questions do not count against Material batch cap but must be logged
- Exceeding cap → orchestrator consolidates into **DECISION REQUIRED** with recommended defaults (Material/Minor only)
- Format per `core/question-format.md`

## document_max budget

Documentation sprints (`document_max` skill) use section-based budget:

- **Every 15 sections** (or equivalent major outline nodes), pause for:
  - Verifier review (`doc-verifier`)
  - Human checkpoint if material drift
  - Activity log entry `document_max_checkpoint`

Do not exceed 15 sections without checkpoint — split into Doc IDs (`D001`, `D002`, …) per `core/naming-rules.md`.

## Context budget

Align with `core/context-engineering.md`:

- **>50%** → compact
- **>75%** → checkpoint + fresh instance handoff

Log `context_compact` and `context_handoff` to activity.

## Activity logging — all budget events

Append to `.ai/state/activity.jsonl` (any agent may append; see workspace rules):

| Event type | When |
|------------|------|
| `fix_cycle_start` / `fix_cycle_end` | Each fix loop iteration |
| `fix_budget_exhausted` | Cycle 10 without PASS |
| `fix_budget_extended` | +10 approved |
| `two_strike` | Two consecutive same-class QA failures |
| `discovery_batch` | Question batch sent (include count, tiers) |
| `document_max_checkpoint` | Every 15 sections |
| `context_compact` / `context_handoff` | Context thresholds |
| `cost_estimate` | When tools report token/cost estimate |

Fields: `timestamp`, `agent_id`, `task_id`, `event`, `details` (object).

## Orchestrator enforcement

- Refuse `complete` if fix cycles exceeded without extension
- Surface budget status in `/project_status` and `/project_cost` views
- **WARNING** at 80% of any budget; **PROBLEM** at 100% without approval

## Cross-references

| Topic | File |
|-------|------|
| QA cycles | `core/qa-loop.md` |
| Questions | `core/question-format.md` |
| Workspace activity | `core/workspace-rules.md` |

Skills and agents must say **"Follow `core/budget-rules.md`"** — do not restate these rules elsewhere.
