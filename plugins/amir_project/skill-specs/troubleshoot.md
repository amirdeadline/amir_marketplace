# troubleshoot

## Command

`/amir:troubleshoot {problem description}`

Aliases in docs: `/troubleshoot` means the same skill when invoked as `/amir:troubleshoot`.

## Purpose

Interactive, human-controlled troubleshooting. Read-only investigation may run without approval. **Any command or action that can change the system requires an explicit plan and human approval.**

## Independence

This skill does **not** require amir project JSON (`ai/state/*`). It works in any repository or workspace. Optional: if an amir project exists, you may mention it but must not write troubleshooting scratch into `ai/` unless the user explicitly requests that as a deliverable.

## Temporary artifacts

Prefer keeping evidence **in chat** (in-memory).

If a temp workspace is required:

```text
%TEMP%\troubleshoot\<session-id>\     (Windows)
$TMPDIR/troubleshoot/<session-id>/    (Unix)
```

Creating that workspace is **state-changing** — include it in an approval-required plan unless the host already authorized an isolated agent workspace. **Never** create scratch/diagnostic files inside the project source tree (`plan.md`, `notes.md`, `app.log` dumps, etc.).

## Core modules referenced

- Follow `core/question-format.md` for clarification (A–E).
- Follow `core/honesty-rules.md` (Fact / Hypothesis / Inference / Unknown).
- Follow `core/security-rules.md` for secret handling.
- Command classifier: `templates/troubleshoot/command-classifier.md`
- Output templates: `templates/troubleshoot/*.md`

## Behavior — state machine

```text
INTAKE → SHOW_BASELINE_STEP → RUN_READ_ONLY_DIAGNOSTICS → ANALYZE_EVIDENCE
  ├── insufficient → SHOW_NEXT_READ_ONLY_STEP (repeat)
  ├── blocked → REPORT_BLOCKER
  └── root cause → REPORT_ROOT_CAUSE → PRESENT_OPTIONS → WAIT_FOR_CHOICE
        → BUILD_PLAN → WAIT_FOR_APPROVAL
             ├── revise → BUILD_PLAN
             ├── cancel → END
             └── approve → EXECUTE_APPROVED_ACTIONS → VALIDATE_FIX → FINAL_REPORT
```

**Never** skip from root-cause discovery to execution.

---

### Phase 0 — Intake

Produce:

```markdown
# Troubleshooting Session

## Reported Problem
## Current Understanding
## Scope
## Safety Constraints
## Initial Hypotheses
```

Ask A–E clarification **only** when needed to avoid wrong system or material risk (environment, host, prod vs local, blast radius, secrets in logs, recent changes). Do not ask when the local environment already answers safely.

Redact secrets always.

---

### Phase 1 — Show Step 1, then run read-only

**Before any command**, emit `# Step 1: Baseline Status` using `templates/troubleshoot/investigation-step.md`.

Rules:

1. List only **READ_ONLY** commands (classifier below).
2. Tailor to the symptom — no generic dump of every possible diagnostic.
3. After showing the list, run those commands **without waiting for approval**.
4. Before **each** execution, re-validate classification. If not clearly READ_ONLY → exclude and reserve for an approval plan (`UNCERTAIN` = fail closed → treat as STATE_CHANGING).

Then emit `# Step 1 Results` with observations, evidence, normals, suspected problems, hypotheses, and:

```markdown
## Root Cause Status
- Found | Not yet found | Investigation blocked
```

Finding table:

```markdown
| Finding | Classification | Evidence | Confidence |
|---|---|---|---|
```

Classifications: Fact | Hypothesis | Inference | Unknown.

---

### Phase 2+ — One step at a time

If more evidence is needed, emit the **next single** numbered step (`Step 2`, `Step 3`, …) based on prior evidence. Do **not** pre-list five speculative future steps.

Each step: hypothesis → why needed → read-only commands (with support/reject predictions) → run → interpret → update → decide next.

Do not repeat commands unless state may have changed or comparison is required.

---

### Root cause

Only report a root cause when evidence is sufficient. Use `templates/troubleshoot/root-cause-report.md`.

Confidence: `Confirmed` | `High confidence` | `Moderate confidence` | `Low confidence`.

Do not label Confirmed without direct supporting evidence. Do not invent a fix when root cause is not found — propose the next safe diagnostic step instead.

---

### Remediation options

Stop all state-changing intent. Present options via `templates/troubleshoot/resolution-options.md`.

- Option 1 = recommended.
- Last option = Other (custom).
- Include temporary mitigation / do-nothing when reasonable.
- End with: no changes until plan reviewed and explicitly approved.

Wait for the user's choice.

---

### Execution plan (after choice)

Build `templates/troubleshoot/execution-plan.md` with **exact** commands (no vague placeholders). Include target host/environment/repo/cluster fields that apply.

Then `templates/troubleshoot/approval-gate.md`.

**Approval is required.** Silence, “okay”, “interesting”, “continue investigating”, “maybe” do **not** count.

Accept only clear forms such as:

1. `Approve plan`
2. `Approve actions 1-3` (subset)
3. `Revise plan: <instructions>`
4. `Cancel`

---

### Execution

Run **only** approved actions, in order. Show per-action results. Stop on unexpected failure, excess impact, or if the next action is no longer appropriate. **Never** improvise unapproved state-changing commands.

On failure: read-only diagnostics only → explain → rollback need → revised plan → new approval.

---

### Validation

Read-only validation of the **original symptom**. Use `templates/troubleshoot/validation-report.md`. Exit code 0 alone is not resolution.

---

## Command classifier (mandatory)

Before every command, classify using `templates/troubleshoot/command-classifier.md`:

| Class | Action |
|-------|--------|
| `READ_ONLY` | May run without approval |
| `STATE_CHANGING` | Requires plan + approval |
| `UNCERTAIN` | Fail closed → treat as STATE_CHANGING |

Inspect compound shells: `>`, `>>`, `tee`, `xargs`, `sh -c`, `sudo`, `&&`, `||`, `;`, `eval`, `kill`, redirects, lifecycle scripts (`npm test`, `make`, etc.).

**Never automatically safe:** `npm install|test|run`, `make`, `terraform plan` (may refresh state), `kubectl apply`, `docker compose up`, `git checkout|restore|clean|reset`, `systemctl restart`, etc.

---

## Hard prohibitions

- Delete unrelated files; reset repos; discard uncommitted work without explicit approval + warning.
- `git clean` / `git reset --hard` without explicit approval and clear warning.
- Modify production without identifying the target environment.
- Reveal or copy secrets into prompts, plans, or reports.
- Broaden scope (host/cluster/account/namespace) without approval.
- Create project-tree scratch files for investigation.

## Outputs

Chat-only by default. Optional TEMP workspace only under approval (or host-authorized agent temp). Final report in chat:

```markdown
# Troubleshooting Completion

## Result
## Root Cause (or status)
## Changes Made (approved only)
## Validation
## Remaining Risks
## Recommended Monitoring
```
