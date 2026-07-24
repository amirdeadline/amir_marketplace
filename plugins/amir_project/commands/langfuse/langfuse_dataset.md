---
description: Create or manage Langfuse datasets for repeatable test cases
argument-hint: <create|add|list|show> [dataset name]
---

# /amir:langfuse_dataset

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Confirm connectivity (`langfuse.auth_check()`); otherwise point to `/amir:langfuse_validate`.
2. Parse the action from `$ARGUMENTS`:
   - `create <name>`: create the dataset via SDK (`langfuse.create_dataset(name=...)`). Use project-prefixed names (`<project-id>-<purpose>`) so shared Langfuse instances stay tidy.
   - `add <name>`: add items (input, expected_output, metadata). Sources: hand-written cases from the user, or promotion of real traced inputs — when promoting traces, apply the same redaction rules as tracing; never move raw proprietary prompts into a dataset the redaction config would have blocked.
   - `list` / `show <name>`: enumerate datasets / items via the API and summarize (item counts, last updated).
3. Keep a local mirror of dataset definitions in `.amir/state/langfuse/datasets/<name>.jsonl` so the project can rebuild the dataset if the Langfuse instance is wiped; note in the file header that Langfuse is the runtime source, the mirror is for reproducibility.
4. Never delete a dataset or items without explicit user confirmation (destructive-action rule).
5. Report what changed with real counts from the API response, not assumptions.
