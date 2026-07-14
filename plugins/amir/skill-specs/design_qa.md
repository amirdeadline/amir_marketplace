# design_qa

## Command

`/design_qa`

## Purpose

Define QA strategy: produce `ai/qa-objectives.md`, QA environment design, and project-level QA skill hooks so verification is testable before build.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| `ai/design.md` | Yes | Approved architecture |
| `ai/project-goal.md` | Yes | Approved goal |
| `verify.sh` | Optional | Baseline verification script if instantiated |

## Behavior

1. Act as **`2-architect`** with **`3-qa`** input; coordinate verifier requirements per `core/qa-loop.md`.
2. Instantiate `ai/qa-objectives.md` from `templates/qa-objectives.md.tmpl` with project-specific commands, environments, and acceptance tiers.
3. Design QA environment: dependencies, test data policy, CI/local parity, blocked prerequisites — per `core/security-rules.md` for secrets handling.
4. Define project-level QA skills or host commands list (read-only primitives, test runners, scan steps) without duplicating `core/qa-loop.md` text.
5. Map goal requirements to verifiable criteria ids for later `tasks.json` population.
6. Confirm `verify.sh` exists or document BLOCKED prerequisites in qa-objectives.
7. Present summary to human per `core/interaction-style.md`; obtain approval for QA strategy.
8. Record approval in `ai/state/decisions.json`; append `design_qa_complete` to activity.
9. Recommend `/design_agents`.

## Core modules referenced

- Follow `core/qa-loop.md`
- Follow `core/naming-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/question-format.md`
- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/security-rules.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `ai/qa-objectives.md` | Write |
| `ai/design.md` | Read |
| `ai/project-goal.md` | Read |
| `verify.sh` | Read / Write (update commands section if needed) |
| `ai/state/decisions.json` | Write |
| `ai/state/activity.jsonl` | Append |
| `ai/agents/3-qa/notes.md` | Write (working) |

## Outputs

- `ai/qa-objectives.md`
- QA environment specification (section inside qa-objectives or linked doc)
- Project-level QA skill/command manifest
- Approval decision record

## Failure/abort behavior

- Abort if `ai/design.md` not approved.
- Stop if QA environment has Blocking unknowns (no test runner, no deploy target) unresolved.
- Do not populate `tasks.json` in this skill.
- If `verify.sh` cannot be made runnable, document BLOCKED and get human acknowledgment before build phase.
