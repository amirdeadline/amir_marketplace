---
description: Symbol-level refactor via Serena with source validation and mandatory tests
argument-hint: <refactor description, e.g. "rename UserSvc to UserService">
---

# /amir:serena_refactor

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.serena.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Hard rules

- No Serena edit is applied without prior source validation: read every location Serena intends to change and confirm the change is correct there.
- Tests MUST run after the refactor. A refactor without a passing test run is reported as "applied, unverified" — never as "done".
- Refactors touching more than ~10 files require an explicit user go-ahead before applying.

## Steps

1. Confirm Serena MCP tools are available; otherwise stop and point to `/amir:serena_setup`.
2. Analyze first: run the equivalent of `/amir:serena_analyze_symbol` on the target — definition, all references, covering tests.
3. Plan: list every file/line that will change and show the user the plan. Wait for confirmation if the change is wide or touches public API.
4. Apply using Serena's symbol-level editing tools (replace/insert at symbol granularity), not blind text substitution. For pure renames verify that textual occurrences in strings, docs, and config are handled deliberately (list them; ask whether to update).
5. Validate: re-run `find_references` on the new symbol to confirm no dangling references; run the project's test suite (or the closest relevant subset) and report actual results.
6. If tests fail, either fix forward with user agreement or revert the edits; never leave the project silently broken.
