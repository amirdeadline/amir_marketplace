---
name: amir_handoff
description: >-
  Write a self-contained session handoff document so a fresh agent session in any
  host can resume cold without the chat history. Works in any repository, with or
  without an Amir project. Use for /amir_handoff or /amir:amir_handoff.
argument-hint: [optional reason or output path]
---

# amir_handoff — self-contained session handoff

Produce ONE document that lets a fresh session continue this work without reading a single
line of the current conversation. Assume the next reader has zero context, cannot see this
chat, and cannot ask you questions.

**This does not clear or compact your context.** Only starting a new session does that. Never
claim context was cleared, compacted, or reset.

## Step 1 — Choose the output path

Detect, in order:

1. `.ai/` exists → write `.ai/context_handoff.md`.
2. `.amir/` exists but `.ai/` does not → create `.ai/` and write `.ai/context_handoff.md`.
3. Neither exists → propose `HANDOFF.md` in the repo root, **confirm the path with the user
   before writing**, and state whether it is git-ignored.

If `$ARGUMENTS` contains a path, use it instead. If `$ARGUMENTS` is free text, treat it as the
reason for pausing and record it.

Rewrite the file in full — it is a snapshot of NOW, not an append-only log. Before overwriting
an existing handoff, read it and carry forward anything still true that is not recoverable
elsewhere.

On an Amir project where `.ai/status.md`, `tasks.md`, `decisions.md`, `risks.md`, and
`changelog.md` should all be updated together, use `/amir:cleanup_context` instead. This skill
deliberately writes one portable file and touches nothing else.

## Step 2 — Gather evidence, not recollection

Check the working tree before writing. Do not describe state from memory:

- `git status --short` — what is actually modified, staged, untracked
- `git diff --stat` — scale of uncommitted change
- `git log --oneline -10` — what was committed during this session
- Re-read any file whose current contents you are about to describe

Label every claim **VERIFIED** (you saw the evidence) or **INFERRED** (believed, not checked).
Never present INFERRED as VERIFIED. If something important cannot be verified, put it under
Open Questions rather than guessing. If the directory is not a git repository, say so and
describe changed files from your own edit history, marked INFERRED.

## Step 3 — Write the document

Use exactly these sections. Omit none; write "None" where a section is genuinely empty.

```markdown
# Handoff — <project name> — <YYYY-MM-DD HH:MM>

Reason for handoff: <context budget | user request | end of session | blocked>

## 1. Goal
<The user's objective, verbatim where possible, so it cannot drift.>

## 2. Current state
<Where things stand right now, in 3-6 sentences. What works, what does not.>

## 3. Next exact action
<The single concrete step the fresh session takes first. A command, a file and
line, or a decision to put to the user. Not a theme — one action.>

## 4. Completed (with evidence)
- <what> — evidence: <command output, test name, commit sha, file:line>

## 5. Pending (ordered)
1. <next-most-important unit of work, with enough detail to start cold>

## 6. Files changed this session
| File | What changed | Why |
|------|--------------|-----|

## 7. Read these first
1. `<path>` — <why it matters to the next session>

## 8. Decisions made
- <decision> — rationale: <why> — rejected: <alternative and why not>

## 9. Commands already run
<So they are not blindly repeated. Note which mutate state.>

## 10. Tests and checks
- PASSED: <named>
- FAILED: <named, with the actual error>
- NOT RUN: <named, and why>

## 11. Risks and gotchas
<Fragile areas, near-misses, environment quirks, things that will surprise.>

## 12. DO NOT CHANGE
<Things that look wrong but are intentional, each with the reason.>

## 13. Open questions
<Waiting on the user, or unverifiable without more work.>

## 14. Rollback
<How to undo this session: commit shas, backup paths, original values.>
```

Sections 1, 2, and 3 are the ones a fresh session reads first — put real information in them,
not summaries of the other sections.

## Step 4 — Tell the user how to resume

Report the absolute path written, then give the resume instruction for the current host:

- **Claude Code** — start a new session in this directory and open with:
  `Read <path> and continue from "Next exact action".`
- **Cursor** — open a new chat and `@`-mention the handoff file, or paste the same instruction.
- **Codex / other** — start a new session and paste the same instruction; attach the file if
  the host cannot read the repo directly.

Then assess degradation honestly. If this session is long, has needed repeated corrections, or
has absorbed large file dumps, say so and recommend the user actually start fresh. State
plainly: "I cannot clear my own context — a new session is the only real reset." If the
session is still healthy, say that and offer to keep working.

## Failure and honesty rules

- If the target path cannot be written, say so and print the document in chat instead. Do not
  report success.
- Do not claim the handoff is complete until the file exists on disk.
- Never omit BLOCKED or FAILED items to make the handoff look cleaner — those are the most
  valuable lines in the document.
- Do not delete, compact, or "tidy" evidence files as part of a handoff.
- Writing outside the current project root is out of scope for this skill.
