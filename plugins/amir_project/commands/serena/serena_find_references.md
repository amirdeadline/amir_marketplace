---
description: Find all references to a symbol via Serena's LSP tools
argument-hint: <symbol name or path/to/symbol>
---

# /amir:serena_find_references

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.serena.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Confirm Serena MCP tools are available; otherwise stop and point to `/amir:serena_setup`.
2. Resolve the symbol first (Serena `find_symbol`) so the reference search targets the right definition, then use Serena's reference-finding tool (`find_referencing_symbols`) on it.
3. Report every referencing location grouped by file, with line numbers and the referencing scope.
4. Caveats to state honestly: LSP reference results can miss dynamic references (reflection, string-based dispatch, templates in some languages). If the language uses such patterns, supplement with a Grep pass over the literal name and report the two result sets separately.
5. Fallback on Serena failure: direct Grep for the symbol name, clearly labeled as textual search (may include false positives).
