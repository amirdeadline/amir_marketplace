# amir — question format

Rules for discovery, clarification, and decision questions during amir projects.

## Triage tiers

Every unknown or ambiguous item is classified into exactly one tier before asking the human.

| Tier | When to use | Agent behavior |
|------|-------------|----------------|
| **Blocking** | Work cannot proceed safely or correctly without an answer | Ask **now**; stop related work until answered |
| **Material** | Answer changes design, cost, security, or acceptance materially | **Batch** ask; continue only on paths that do not depend on the answer |
| **Minor** | Reasonable default exists; wrong default is recoverable | **Do not ask**; apply default, log to `ai/state/decisions.json`, note in activity |

### Default tier assignment

- Missing acceptance criteria → **Blocking**
- Security or data-handling ambiguity → **Blocking** or **Material** (never Minor)
- Naming, log level, non-critical copy → **Minor**
- Architecture fork with >2× cost or timeline difference → **Material** or **Blocking**

Log every **Minor** default to decisions with: `id`, `question`, `default_chosen`, `rationale`, `timestamp`, `agent`.

## Batching rules

- Batch **5–10** questions per message for **Material** (and non-urgent **Blocking** that can wait one cycle).
- If the human requests **faster discovery**, batch **10–20** questions in one message.
- Never interleave unrelated question batches with routine `message-contract` status lines — send questions as their own message type (exception in `core/message-contract.md`).
- Order questions: **Blocking** first, then **Material**, grouped by theme (scope, architecture, QA, security, ops).

## Multiple-choice table format

Every question **must** use this exact structure:

```markdown
### Q\<n\>: \<short title\> [Blocking|Material]

**Context:** \<one to three sentences; plain language during planning/design\>

**Why it matters:** \<one sentence tying the choice to goal, risk, cost, or acceptance\>

| Choice | Option |
|--------|--------|
| **A** | \<Best-practice recommended option — state the default amir recommends\> **(Recommended)** |
| **B** | \<Alternative — valid but tradeoff vs A\> |
| **C** | \<Higher-risk — faster/cheaper/shortcut; state the risk\> |
| **D** | **Not Sure — Argue it out** |
| **E** | **Other** — \<prompt for free text if they pick E\> |
```

Rules:

- **A** is always the best-practice path amir recommends unless project state already decided otherwise.
- **B** must be a real alternative, not a straw man.
- **C** must honestly describe elevated risk (security, maintenance, scale, or rollback).
- **D** and **E** are fixed labels; do not reword them.
- Include **Why it matters** on **every** question — no exceptions.

## Choice D behavior — "Not Sure — Argue it out"

When the human selects **D**:

1. **Do not assume.** "Not Sure" is not permission to pick a default silently.
2. Explain **tradeoffs** across: safest, simplest, cheapest, fastest, most scalable — only the dimensions relevant to the question.
3. **Challenge weak reasoning** if the human stated a preference without criteria.
4. **Compare** options A/B/C with a small table or bullet list when helpful.
5. **Recommend one** option explicitly: *"Recommendation: A because …"*
6. Ask **confirmation**: *"Confirm A, or reply with B/C/E + brief reason."*
7. **Record the decision** in `ai/state/decisions.json` and append to `ai/state/activity.jsonl`.

If after argument the human still refuses to choose and the item is **Blocking**, escalate with **DECISION REQUIRED** and stop dependent work.

## Choice E behavior — Other

- Ask for a **one-line** specification.
- If the custom answer contradicts best practice or project goal, respond with **WARNING** or **PROBLEM** and propose alignment.
- Record verbatim in decisions.

## Blocking vs batch timing

| Situation | Action |
|-----------|--------|
| Single Blocking item mid-task | Ask immediately; may interrupt batch |
| Multiple Blocking at phase start | One batch if answers are independent |
| Material only | Batch 5–10 (or 10–20 on request) |
| Minor | Never ask; log default |

## Discovery budget

Question batches consume **discovery budget** per `core/budget-rules.md`. Log each batch to activity with question count and tier breakdown.

## Output integration

- Answers update `ai/state/decisions.json` and relevant task/spec JSON.
- Regenerate views per `core/context-engineering.md`.
- Routine status after a batch still uses `core/message-contract.md` with `NEED: nothing` once decisions are recorded.

## Cross-references

| Topic | File |
|-------|------|
| Message exceptions for batches | `core/message-contract.md` |
| Decision storage | `core/workspace-rules.md` |
| Budget | `core/budget-rules.md` |
| Tone | `core/interaction-style.md` |

Skills and agents must say **"Follow `core/question-format.md`"** — do not restate these rules elsewhere.
