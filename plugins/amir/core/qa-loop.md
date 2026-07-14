# amir — QA loop

Independent verification, orchestrator issue review, and goal-alignment gates before any task completes.

## Loop overview

```
Goal-Safe Dev → QA → Orchestrator issue review → Goal-alignment review → Fix → Re-QA
                      ↑______________________________________________|
```

Repeat until one of:

| Outcome | Meaning |
|---------|---------|
| **PASS** | All gates satisfied; verifier sets `qa_passed` |
| **PASS_WITH_WARNINGS** | Criteria met; non-blocking warnings logged and accepted |
| **FAIL** | Defects remain; enter fix loop |
| **BLOCKED** | Cannot verify or proceed without human, tool, or environment action |

**Independent QA:** The verifier (`qa-<task-id>`) never relies on worker conclusions alone. Re-run commands, read artifacts, and apply static review independently.

## Roles

| Role | Agent id | Responsibility |
|------|----------|----------------|
| Worker | `dev-<task-id>` | Goal-safe implementation per task spec |
| Verifier | `qa-<task-id>` | Execute QA, produce report, set `qa_passed` only on PASS |
| Orchestrator | `1-orchestrator` | Review every QA issue, confirm gates, set `complete` |
| Security | `4-security` | Mandatory on security-touched tasks per `core/security-rules.md` |

## QA statuses

| Status | Criteria |
|--------|----------|
| **PASS** | All acceptance criteria verified; goal-alignment PASS; no unaccepted BLOCKING issues |
| **PASS_WITH_WARNINGS** | Acceptance met; warnings documented in decisions or QA report with human/orchestrator acknowledgment |
| **FAIL** | One or more acceptance criteria not met, or goal-alignment FAIL |
| **BLOCKED** | Missing env, credentials approval, external dependency, or NOT DOABLE |

### Never PASS when

- Required commands were **skipped** **and** no **meaningful static review** replaced them (see below)
- Worker-only evidence with no verifier re-execution
- Goal-alignment review **FAIL**
- Secrets scan failed or was NOT RUN when required
- Drift detected vs `ai/project-goal.md` (`core/no-drift-rules.md`)

## Commands not run

If a planned QA command was not executed, document in the QA report:

```
**NOT RUN:** `<command>`
- **Reason:** <environment, time, missing dependency>
- **Impact:** <what claims cannot be VERIFIED>
```

Compensating **meaningful static review** must include: direct inspection of changed files, logic paths for the acceptance criterion, and explicit list of unverified risks. Without that, max status is **FAIL** or **BLOCKED**, not **PASS**.

## Templates

Instantiate from project `templates/` (copied at project create):

| Template | Purpose |
|----------|---------|
| `templates/qa-report.md.tmpl` | Verifier output: criteria matrix, commands, evidence, status |
| `templates/qa-issue-review.md.tmpl` | Orchestrator per-issue disposition |
| `templates/goal-alignment-review.md.tmpl` | Goal vs shipped behavior |
| `templates/fix-prompt.md.tmpl` | Worker fix instructions scoped to failures only |

Render filled copies to agent workspace and/or `ai/views/`; link from activity.

## Orchestrator issue review

**Orchestrator reviews EVERY QA issue** — no silent drops.

For each issue in the QA report:

1. **Valid** → assign fix priority, link to fix cycle
2. **Duplicate** → merge, note in activity
3. **Spec wrong** → **DECISION REQUIRED**, pause fix until tasks.json updated
4. **Won't fix** → requires human risk acceptance logged to `decisions.json`
5. **False positive** → document VERIFIED reasoning; verifier amends report

Record review in `qa-issue-review` artifact and activity.jsonl.

## Goal-alignment review

**Required for every task** before `qa_passed` can stand.

Compare:

- `ai/project-goal.md` (must-haves, non-goals)
- Task acceptance criteria in `tasks.json`
- Actual behavior (demo steps, test scenarios, API samples)

| Goal-alignment result | Effect |
|-----------------------|--------|
| **PASS** | Task may proceed to completion gates |
| **FAIL** | Task **cannot complete** even if unit tests pass; status **FAIL** until product or goal/decisions updated |

If FAIL: orchestrator opens fix or change-request; no `complete` until realigned.

## Fix loop

1. Orchestrator issues **fix-prompt** from template — scoped to failed criteria only
2. Worker (`dev-<task-id>`) fixes per `core/no-drift-rules.md`
3. Increment cycle `(n/budget)` per `core/budget-rules.md`
4. Re-QA from scratch on affected criteria (full regression on touched areas)

Fix loop max **10 cycles** default; extension per budget rules.

## Regression protection

- QA maintains a **regression checklist** in task or project state: prior critical paths from completed tasks
- Any change to shared modules triggers re-run of affected regression items
- New failures in previously passing areas → **FAIL**, not waived as unrelated without orchestrator review
- Checkpoint commits before risky fixes (`/git_commit` checkpoint mode) for rollback

## Completion gates — two owners

Two **distinct** gates and owners:

| Gate | Owner | Sets |
|------|-------|------|
| **QA gate** | Verifier `qa-<task-id>` | `tasks.json` status → `qa_passed` on PASS or PASS_WITH_WARNINGS |
| **Completion gate** | Orchestrator `1-orchestrator` | `tasks.json` status → `complete` only after all confirmations |

Orchestrator **complete** checklist:

- [ ] Verifier status PASS or PASS_WITH_WARNINGS
- [ ] Orchestrator issue review done for all items
- [ ] Goal-alignment review PASS
- [ ] Security review if required
- [ ] No unresolved **BLOCKED**
- [ ] Checkpoint recorded if policy requires
- [ ] Activity and cost logged

**Never** let worker or verifier set `complete`.

## Status messaging

QA and orchestrator use `core/message-contract.md`. `RESULT` line must include status and evidence counts (e.g. `QA FAIL 2/7 criteria; regression 4/4 pass`).

## Cross-references

| Topic | File |
|-------|------|
| Fix budget | `core/budget-rules.md` |
| Drift | `core/no-drift-rules.md` |
| Honesty | `core/honesty-rules.md` |
| Security scan | `core/security-rules.md` |

Skills and agents must say **"Follow `core/qa-loop.md`"** — do not restate these rules elsewhere.
