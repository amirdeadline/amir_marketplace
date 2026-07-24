# amir — context engineering

How amir layers memory, retrieves context, and handoffs work without stuffing prompts.

## Principles

1. **Memory layers stay separate** — do not merge durable state into ephemeral chat
2. **Retrieval, not stuffing** — pull only what the current task phase needs
3. **JSON is truth** — regenerate prompts and views from state
4. **Fresh context per task** — new worker/verifier instance reads regenerated prompt

## Memory layers

| Layer | Location | Lifetime | Contents |
|-------|----------|----------|----------|
| **Project durable** | `.ai/state/*.json`, `.ai/project-goal.md` | Whole project | Goals, tasks, decisions, status |
| **Views** | `.ai/views/*.md` | Regenerated | Human-readable projections of JSON |
| **Agent workspace** | `.ai/agents/<agent-id>/` | Per agent / task | notes, drafts, QA artifacts |
| **Working notes** | `.ai/agents/<agent-id>/notes.md` | Session / task | Scratch, hypotheses — not authoritative |
| **Activity audit** | `.ai/state/activity.jsonl` | Append-only | Events, budgets, drift checks |
| **Ephemeral chat** | Host conversation | Session | Not source of truth |

Never treat chat history or `notes.md` as decisions — promote to `decisions.json` via orchestrator tools.

## Retrieval not stuffing

When building a prompt or handoff:

1. Read **task id** and **phase** from `status.json`
2. Load **minimal slice**: goal excerpt, current task, relevant decisions (by tag/id), last QA report if fix phase
3. Link paths to full files; do not paste entire repo or all decisions
4. For cross-task dependency, retrieve only predecessor task summary + acceptance ids

If context exceeds budget, compact per rules below — do not silently drop acceptance criteria or security constraints.

## Working memory: notes.md structure

Each active agent workspace should use:

```markdown
# notes — <agent-id> — <task-id>

## Current focus
<one line>

## Hypotheses (INFERRED/ASSUMED)
- ...

## Open questions
- ... → tier Blocking|Material|Minor

## Handoff snippet
<≤10 lines for next instance>
```

Clear or archive `notes.md` after task `complete` or handoff; durable outcomes go to JSON.

## Durable vs temporary context

| Durable (must persist to state) | Temporary (notes/chat only) |
|--------------------------------|-----------------------------|
| Decisions, acceptance changes | Exploration drafts |
| QA outcomes, gate flags | Command output snippets (link full log in workspace) |
| Budget extensions | Step-by-step reasoning |
| Approved architecture | Unapproved alternatives |

Promote temporary → durable only through orchestrator state updates or logged decisions.

## Context budget thresholds

Monitor estimated context usage (tokens or host equivalent):

| Usage | Action |
|-------|--------|
| **≤50%** | Normal operation |
| **>50%** | **Compact**: summarize completed steps in notes; drop redundant file contents from prompt; keep acceptance + goal |
| **>75%** | **Checkpoint + fresh instance handoff**: orchestrator writes handoff to `notes.md` + updates status; new agent reads regenerated prompt from JSON only |

Compaction must not remove: active acceptance criteria, security constraints, failing QA ids, or open **DECISION REQUIRED** items.

## Prompt regeneration from JSON state

Before each worker/verifier cycle:

1. Tools or orchestrator render prompt from templates + `tasks.json` + `decisions.json` + phase
2. Inject **only** retrieved slices per task
3. Include pointers: `core/*` rules by reference ("Follow `core/qa-loop.md`"), not full text duplication in skills

Stale prompts are forbidden — if JSON changed, regenerate before build/QA.

## Rebuild after QA

After every QA cycle (PASS or FAIL):

1. Update task status and QA artifact paths in JSON
2. Regenerate affected `.ai/views/`
3. If FAIL: render new **fix-prompt** from template with failed criterion ids
4. If PASS: trim worker notes; archive verbose logs to workspace files
5. Log `context_rebuild` event to activity.jsonl

## Handoff

`/handoff` or orchestrator-initiated pause:

- Write handoff block to `notes.md` and `status.json` (`paused`, `resume_token`)
- List: last VERIFIED state, open NEED, next action, cycle count
- Next session: read state files first — **no cached decisions**

## Cross-references

| Topic | File |
|-------|------|
| Workspace layout | `core/workspace-rules.md` |
| Budget at 75% | `core/budget-rules.md` |
| Message brevity | `core/message-contract.md` |

Skills and agents must say **"Follow `core/context-engineering.md`"** — do not restate these rules elsewhere.
