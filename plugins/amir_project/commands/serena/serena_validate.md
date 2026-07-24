---
description: Validate the Serena integration end to end with concrete checks
---

# /amir:serena_validate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.serena.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Validation matrix (run every check; report pass/fail per line)

1. Binary: `serena --version` exits 0.
2. Registration: `claude mcp list` includes `serena` and shows it connected.
3. Language server: pick one real symbol from this project's source and resolve it with Serena `find_symbol`; the result must match the actual file/line (open the file to confirm).
4. References: run `find_referencing_symbols` on the same symbol; spot-check one reported reference against source.
5. Data location: all Serena project data is under `.serena/` in the project root; nothing was written to other project locations. Flag any violation of the approved-locations rule.
6. Unsupported languages: list project file extensions Serena's LSP backend cannot serve, if any.

Verdict rules: "healthy" only if checks 1-5 all pass. Otherwise report the exact failing check and the remedy (`/amir:serena_setup`, `/amir:serena_index`, or disable). Never report success from cached memory — every check runs now.
