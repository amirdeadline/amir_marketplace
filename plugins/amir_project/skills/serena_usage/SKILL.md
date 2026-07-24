---
name: serena_usage
description: >-
  When and how to use Serena (LSP-based symbol tools) in an amir project:
  precedence vs Graphify and source, safe refactoring, fallbacks.
---

# serena_usage

Serena (https://github.com/oraios/serena) is an MCP server exposing language-server-grade symbol operations: find definitions, find references, symbol-level edits. It is installed per project via `/amir:serena_setup` and gated on `project_tools.serena.enabled` in `.amir/project.yaml`.

## When to use Serena — and when not

Use Serena for PRECISE, symbol-level questions: where is this defined, who calls it, what is its exact signature, rename/move this symbol. Use Graphify for BROAD architecture questions: module boundaries, dependency shape, "what talks to what". Do not stretch either tool across that line — Serena on architecture questions produces myopic answers; Graphify on symbol questions produces stale approximations.

## Precedence (SPEC §13, understanding chain)

Graphify (broad) → Serena (precise) → source (final) → tests (behavior). Every Serena result is evidence to verify against the actual file, and behavior claims come only from tests. No tool output is an unquestionable source of truth.

## Security and scope constraints

- Project-only: Serena is configured with `--project <this project>`; never index or navigate outside the project root, never enable global indexing.
- Data lives in `.serena/` inside the project (gitignore `.serena/cache/`). Any Serena data appearing elsewhere is a policy violation — report it.
- Edits: no Serena-applied edit without prior source validation of every target location, and no completed refactor claim without a test run afterwards (see `/amir:serena_refactor`).

## Environment reality (this machine)

The only official install path is uv (`uv tool install -p 3.13 serena-agent`). This machine ships without uv and pipx; setup installs uv first via the official Astral installer, only after explicit user confirmation. pip installs of `serena-agent` are unofficial — if used, label them so.

## Unsupported languages and fallback

Serena's LSP backend covers ~40+ languages (Python, TS/JS, Java, Go, Rust, C/C++, ...). For unsupported languages or when the language server fails: fall back to direct file inspection (Grep for the symbol, Read the definition) and LABEL results as textual search — textual matches include false positives (comments, strings, same-named symbols) that LSP results would not.
