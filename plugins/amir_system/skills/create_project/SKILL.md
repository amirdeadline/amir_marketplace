---
name: create_project
description: Interactive creation of a new Amir-managed project — one-question-at-a-time interview, catalog-driven component selection with evidence-based recommendations, secure defaults, confirmed plan, honest post-build validation. Use for /amir:create_project.
---

# create_project — full workflow

You are creating a new Amir-managed project. This is a guided, interactive process. Its three
non-negotiables: **one question at a time**, **secure defaults**, **honest reporting**.

## Phase 0 — Preflight

1. Locate the component catalog: `catalog/catalog.json` in the amir-marketplace repo
   (`E:\PC3_Shared\Plugins\amir_marketplace\catalog\catalog.json` on this machine, or the path
   the installed marketplace uses). **If the file does not exist**: tell the user plainly —
   "The component catalog is missing; run `/amir:update_catalog` first. I can continue the
   interview, but component selection will be limited to the built-in tool list and no
   dependency/credential metadata will be shown." Let the user decide whether to continue
   degraded or stop.
2. Check the engine: `python "$env:USERPROFILE\.amir\bin\amirctl.py" --help`. If missing, note
   it now — rendering/validation will be manual and the final report must label itself
   accordingly. Do not silently pretend the engine ran.
3. Never begin writing files in this phase. The entire interview is read-only.

## Phase 1 — Interview (ONE focused question per message, in this order)

Ask each item as a single, focused question. Wait for the answer before the next. Offer a
sensible default in brackets where one exists. Accept "back" to revisit the previous answer,
"review" to show answers so far, and "cancel" to abort safely (nothing has been written).

1. Project name (snake_case or kebab-case; used for directory and registry id)
2. Parent directory (the project is created at `<parent>\<name>`; verify parent exists and the
   target does not)
3. Short description (one sentence)
4. Business goal (what outcome this project serves)
5. Technical goal (what will technically exist when done)
6. Languages (list)
7. Frameworks (list)
8. Package manager
9. Build system
10. Application type (CLI / library / web app / service / desktop / agent / other)
11. Repo strategy (new git repo / existing remote / no git)
12. Use Cursor? (y/n)
13. Use Claude Code? (y/n)
14. Project plugins (amir_project component groups — catalog-driven, see Phase 2 mechanics)
15. Skills to include (catalog-driven)
16. MCP servers (catalog-driven; **default: none**)
17. Connectors (catalog-driven; **default: none**)
18. Rules (the 7 system rules are always included; ask about additional project-specific rules)
19. Agents (subagent definitions to scaffold, if any)
20. Testing requirements (framework, coverage target; default: tests required, 80% coverage)
21. Security requirements (secrets handling, scanning; default: secrets scan on, no plaintext
    secrets, confirm-before-external-writes)
22. Network access for tools (**default: none** — each network-using component asks separately)
23. Secret access for tools (**default: none**)
24. Per-tool selection, one question each: Graphify, Serena, Context7, Semgrep, Langfuse,
    OpenHands, Git worktrees, SWE-bench, Terminal-Bench (**default for each: disabled**)

## Phase 2 — Catalog display mechanics (applies to every selectable category)

For every category (14–17, 24), read the matching entries from `catalog/catalog.json` and show,
per option:

- short explanation and why it is useful for THIS project
- supported hosts and operating systems
- dependencies (`requires`, `optional_dependencies`, `conflicts_with`)
- required executables and required credentials (credential NAMES only)
- network requirements and secret access
- security implications and performance implications
- your recommendation with EVIDENCE from the user's earlier answers (e.g. "web app + browser
  flows → Playwright recommended; evidence: answers 10 and 7"). Recommendations are **advisory
  only — never auto-select**.

Selection controls to offer every time:
`recommended` (select all recommended) · `1,3,5` (individual) · `all` · `none` [default] ·
`search <term>` · `details <id>` · `back` · `review` · `cancel`.

Secure defaults, restated: **no optional MCP servers, no connectors, no network access, no
secret access, no telemetry, no external evaluation, no automatic global indexing** unless the
user explicitly opts in, each opt-in acknowledged individually.

## Phase 3 — Final plan and confirmation (before ANY file is written)

Present the complete configuration plan:

- project path; hosts (Cursor / Claude Code)
- plugins, skills, MCP servers, connectors, rules, agents
- per-tool status table (Graphify … Terminal-Bench: enabled/disabled + update policies)
- network permissions and secret permissions being granted (should be a short list; call out
  each one)
- credentials still required from the user (names + where they must be placed, e.g.
  `%USERPROFILE%\.amir\secrets\asana.env` → `ASANA_ACCESS_TOKEN`) — values never handled in chat
- exact files/directories that will be created or modified
- dependencies that will be installed

Then require an explicit confirmation. Destructive, credential-touching, or network-enabling
actions each get called out in the plan. "Cancel" here still means zero side effects.

## Phase 4 — Post-approval build (ordered; stop-and-report on failure)

1. Create the project directory (and git init if selected — with the user-chosen default branch).
2. Write `.amir/project.yaml` (manifest schema v2, per `schemas/project-manifest.schema.json`).
3. Resolve dependencies via the engine/validator (missing deps, host support, conflicts,
   credential requirements → surface problems NOW, adjust with the user, re-confirm if the
   selection changed).
4. Write `.amir/components.lock.json`.
5. Install ONLY selected components:
   - full amir_project selection → fast path
     `claude plugin install amir_project@amir-marketplace --scope project`
   - subset → render via the renderer engine into `.amir/generated/claude/...` and register.
6. Generate Cursor project files (flat `.cursor/commands/amir_<name>.md`, `.cursor/rules/
   amir_*.mdc`, merge-preserving `.cursor/mcp.json`) — only if Cursor was selected.
7. Generate Claude project files — only if Claude Code was selected.
8. Initialize docs: `ai/status.md`, `ai/tasks.md`, `ai/decisions.md`, `ai/risks.md`
   (+ `ai/architecture.md` stub).
9. Worktrees config if selected.
10. Run validation (`amirctl validate` / validator) and capture its real output.
11. Register the project in `%USERPROFILE%\.amir\registry\projects.json` (non-secret metadata
    only).

## Phase 5 — Honest final report

Per component, report one of: **installed+healthy** (its catalog `health_check` was actually
executed and passed — include the evidence), **installed, not verified** (health check could not
run — say why), **failed** (with the real error), **skipped**, **blocked (needs credential X)**.
NEVER report a component as installed/working unless its executable/integration was actually
tested. List every file created. State validation result verbatim. If the engine was missing,
the report's first line must say the build ran in manual mode.

Finish with next steps: place required credentials, run `/amir:project_status`, and (if
Graphify enabled) `/amir:graphify_setup` → `/amir:graphify_build`.
