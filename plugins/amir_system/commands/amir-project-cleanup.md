---
description: >-
  Full project audit and documentation rebuild — reconstruct current truth from
  code, rebuild PROJECT.md and .ai/, safely clean stale AI/project memory
argument-hint: [optional focus area or constraints]
disable-model-invocation: true
---

# /amir:amir-project-cleanup

Follow the skill at `skills/amir-project-cleanup/SKILL.md` in this plugin (also
installable at user scope as `/amir-project-cleanup` for Cursor and Claude Code).

Apply that skill now. Treat `$ARGUMENTS` as optional focus (e.g. "docs only",
"architecture + TODO", a subsystem path). Execute the full cleanup workflow in the
current repository: discover, audit, reconstruct, rebuild `.ai/` + `PROJECT.md`,
validate, then propose safe deletions for explicit approval.

This is not `/amir:cleanup_context` (session handoff) and not harness `project_cleanup`.
