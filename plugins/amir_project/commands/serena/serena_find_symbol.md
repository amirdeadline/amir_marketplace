---
description: Locate a symbol definition precisely via Serena's LSP tools
argument-hint: <symbol name or path/to/symbol>
---

# /amir:serena_find_symbol

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.serena.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Confirm the Serena MCP server is available in this session (its tools, e.g. `find_symbol`, appear in the tool list). If not, stop and point to `/amir:serena_setup` — do not silently substitute grep and call it Serena.
2. Use Serena's `find_symbol` tool with the symbol name from `$ARGUMENTS`. Prefer qualified name paths (`Class/method`) over bare names when the name is ambiguous.
3. Present: file path, line, kind (class/function/method/variable), and containing scope for each match.
4. Verify against source: open the reported location and confirm the definition is really there before asserting it. Serena output is evidence, not truth (precedence rule: Graphify for broad structure, Serena for precise symbols, source is final, tests define behavior).
5. Fallback: if Serena errors or the language is unsupported, say so explicitly, then fall back to direct file inspection (Grep/Read) and label the result as a text-search fallback, not an LSP result.
