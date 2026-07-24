# amir — message contract

Exact schema for **routine** agent status messages. Keeps human visibility high and token cost low.

## Five-field schema

Every routine message **must** use exactly these five lines in this order:

```
[AGENT <id>] <task-id> — <phase> (cycle <n>/<budget>)
DID: <what was done, one line>
RESULT: <evidence, numbers preferred, one line>
NEXT: <next action, one line>
NEED: <"nothing" or one specific ask/decision>
```

### Field definitions

| Field | Rules |
|-------|--------|
| `[AGENT <id>]` | Agent id per `core/naming-rules.md` (e.g. `1-orchestrator`, `dev-T001`, `qa-T001`) |
| `<task-id>` | Active task id (`T001`, `D001`, or `—` if none) |
| `<phase>` | Current phase: `discovery`, `design`, `plan`, `build`, `qa`, `fix`, `checkpoint`, `handoff`, etc. |
| `(cycle <n>/<budget>)` | Current fix/QA cycle number and max budget for this loop (see `core/budget-rules.md`) |
| `DID:` | One line — completed action only; no future tense |
| `RESULT:` | One line — measurable evidence (tests passed 12/12, file written, schema valid); prefer numbers |
| `NEXT:` | One line — single next action |
| `NEED:` | Default **`nothing`**. Otherwise **one** specific ask or decision — never a list |

### NEED: default and exceptions

- **`NEED: nothing`** is the default for routine updates.
- Put detail in workspace files (`ai/views/`, agent workspace under `ai/agents/`), not in the message body.
- Human invokes **`/details`** (or host equivalent) to dump the relevant workspace file or view.

**Exceptions** — may exceed the five-line schema:

| Exception | When allowed |
|-----------|----------------|
| Question batch | Material/Blocking discovery per `core/question-format.md` |
| **BLOCKED** | Hard stop; include **PROBLEM** label and reason |
| **NOT DOABLE** | Per `core/honesty-rules.md` — Reason/Evidence/Alternative/Decision Required |
| Human-requested expansion | Human explicitly asks for detail, logs, or diff in chat |

For exceptions, the five-field block may precede the expanded content, or the expanded format replaces it if the host requires a single block — but **never** mix long dumps into `DID`/`RESULT`/`NEXT`.

## Examples

Routine:

```
[AGENT dev-T001] T001 — build (cycle 1/10)
DID: Implemented user model and migration per task spec
RESULT: unit tests 8/8 pass; migration dry-run OK
NEXT: Hand off to qa-T001 for independent QA
NEED: nothing
```

Needs decision:

```
[AGENT 1-orchestrator] T003 — plan (cycle 1/10)
DID: Reviewed architect proposal against project-goal.md
RESULT: 2 acceptance criteria still untestable
NEXT: Pause T003 until criteria are fixed
NEED: Confirm revised acceptance criteria in ai/state/tasks.json
```

## Prohibited in routine messages

- Multi-paragraph explanations
- Full stack traces (put in workspace artifact; reference path in RESULT)
- Restating entire rules from `core/`
- Multiple asks in `NEED`
- Flattery or status without evidence

## Orchestrator and QA

- **QA agents** use the same contract; `RESULT` cites QA status (`PASS`, `FAIL`, etc.) per `core/qa-loop.md`.
- **Orchestrator** uses `NEED` for the single highest-priority human gate only.

## Cross-references

| Topic | File |
|-------|------|
| Labels (PROBLEM, etc.) | `core/interaction-style.md` |
| Questions | `core/question-format.md` |
| NOT DOABLE | `core/honesty-rules.md` |
| Cycle budget | `core/budget-rules.md` |

Skills and agents must say **"Follow `core/message-contract.md`"** — do not restate these rules elsewhere.
