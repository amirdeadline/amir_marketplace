---
name: cleanup_context
description: Durable context handoff — persist facts, decisions, state, and the exact next action into .ai/ docs before context degrades; recommend a fresh session honestly. Use for /amir:cleanup_context.
---

# cleanup_context — durable handoff workflow

This is a real handoff, not theater. You CANNOT clear or compact your own context; what you can
do is make a fresh session able to continue seamlessly. **Never claim context was cleared unless
a new session actually started.**

## Step 1 — Extract (from the whole conversation so far)

Systematically collect:

1. **Durable facts** — things discovered that stay true (paths, versions, env quirks, API
   behaviors, decisions' rationales)
2. **Completed work** — with evidence (tests run, outputs seen), not just claims
3. **Pending work** — ordered, with enough detail to resume cold
4. **Decisions** — what was decided, why, alternatives rejected
5. **Risks** — known hazards, fragile areas, things that almost broke
6. **Unresolved questions** — waiting on user or investigation
7. **Modified files** — complete list, with one-line what/why each
8. **Validation evidence** — which tests/commands passed or failed, verbatim key outputs
9. **Rollback info** — how to undo the session's changes (commits, backups, original values)

## Step 2 — Persist (update, don't clobber)

Update the project docs by MERGING new content (append/update sections, preserve history):

- `.ai/status.md` — current state summary
- `.ai/tasks.md` — completed marked done (with evidence refs), pending re-ordered
- `.ai/decisions.md` — new decisions appended with date
- `.ai/risks.md` — new/changed risks
- `.ai/changelog.md` — APPEND one dated entry per session: what changed in the project this
  session (files, behavior, config), one line each — facts with evidence, never planned-but-
  not-done work (that belongs in tasks.md)
- `.ai/context_handoff.md` — REWRITTEN each time (it is the fresh-session entry point)

If not an Amir project (no `.amir/` and no `.ai/`), confirm a location with the user before
writing; default suggestion `.ai/context_handoff.md`.

## Step 3 — The handoff document must contain (all of these, explicitly)

1. Project goal (verbatim, so it cannot drift)
2. Current task and its exact state
3. Completed items (+ evidence pointers)
4. Pending items (ordered)
5. Files changed this session
6. Files a fresh session should read FIRST (ordered, with why)
7. Commands already run (so they are not blindly re-run)
8. Tests passed / failed (named)
9. Known risks and gotchas
10. DO-NOT-CHANGE list (things that look wrong but are intentional, with reasons)
11. **Next exact action** — the single concrete step a fresh session takes first

## Step 4 — Honest recommendation

Assess degradation risk (long session, many corrections, repeated confusion, large file dumps in
context). If degradation is likely, say so and recommend the user start a fresh session pointed
at `.ai/context_handoff.md`. State plainly: "I cannot clear my own context — a new session is the
only real reset." If the session is still healthy, say that too and continue.
