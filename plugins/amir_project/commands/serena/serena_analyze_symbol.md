---
description: Deep analysis of one symbol - definition, references, callers, contract
argument-hint: <symbol name or path/to/symbol>
---

# /amir:serena_analyze_symbol

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.serena.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Confirm Serena MCP tools are available; otherwise stop and point to `/amir:serena_setup`.
2. Using Serena: locate the definition (`find_symbol`), read its full body and docstring/signature, list its references (`find_referencing_symbols`), and identify the symbols it depends on.
3. Read the actual source of the definition and at least the top referencing sites — source is the final authority, never the tool summary alone.
4. Produce an analysis covering: purpose, signature/contract, inputs and outputs, side effects, error paths, callers and what they expect, and tests that cover it (search the test tree for the symbol name).
5. If tests covering the symbol exist, cite them; if none exist, say so explicitly — that changes the risk of any refactor.
6. Scope: analysis stays within this project. For broad architectural context ("where does this sit in the system"), recommend Graphify rather than stretching Serena beyond symbol-level questions.
