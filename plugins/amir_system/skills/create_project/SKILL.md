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

Portfolio/PM questions (these feed `.amir\portfolio.yaml` and the shared registry — blanks
are valid answers; NEVER fabricate values the user did not give):

25. Lifecycle stage at creation (active / paused / planned) [active]
26. Priority (p0 / p1 / p2 / p3, or unset) [unset]
27. Target deadline (date, or none) [none]
28. Initial milestones (names + rough dates, or none yet) [none]
29. Current phase name (e.g. "design", "mvp") [blank]
30. Owner and stakeholders [blank]
31. Link an Asana project? (**default: no**; if yes, the GID/reference — configured later via
    the asana capability, value names only)
32. Join the global portfolio graph? (**default: no** — joining is always explicit; requires
    Graphify enabled for a code graph, otherwise metadata-only registration)
33. Related registered projects (dependencies on / from other portfolio projects, picked from
    the registry list — never guessed) [none]
34. Progress tracking source (milestones / .ai tasks / Asana / none) [milestones]
35. Status staleness threshold in days (when is `.ai\status.md` considered stale) [14]
36. Include in portfolio reports? (y/n) [y]

## Phase 2 — Catalog display mechanics (applies to every selectable category)

For every category (14–17, 24; and question 33's registry picker), read the matching entries
from `catalog/catalog.json` (registry entries for 33) and show,
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
- exact files/directories that will be created or modified — including the FULL folder
  structure below, so the user sees every path before approval
- dependencies that will be installed
- portfolio/PM display (from questions 25–36): the exact `.amir\portfolio.yaml` content that
  will be written (lifecycle, priority, deadline, milestones, phase, owner/stakeholders,
  progress source, staleness threshold, reporting flag — with blanks shown AS blanks), the
  registry entry that will be added to `%USERPROFILE%\.amir\registry\projects.yaml`, the
  Asana link decision, the related-projects list, and the global-graph decision (join /
  metadata-only / no — restated explicitly, since joining is never implicit)

### Folder structure that will be created (show it in the plan, then build exactly this)

Mandatory, every project:

```
<project>\
  .amir\project.yaml            # manifest (schema v2)
  .amir\portfolio.yaml          # from templates\portfolio.yaml.tmpl — blanks, not fabrications
  .amir\components.lock.json
  .ai\project.md  .ai\status.md  .ai\tasks.md  .ai\decisions.md  .ai\risks.md
  .ai\architecture.md  .ai\references.md  .ai\changelog.md  .ai\context_handoff.md
  README.md  AGENTS.md  CLAUDE.md  .gitignore
```

The 9 `.ai\` files are seeded from `templates\dot-ai\` in this plugin — structured headers,
empty content sections; never pre-filled with invented state.

Conditional (only when selected/applicable):

- `.cursor\` (commands/rules/mcp.json) — Cursor selected
- `.claude\` (settings, rendered subset) — Claude Code selected
- `tests\` — testing requirements selected (adapt name to the framework's convention)
- `docs\` — user opted into docs scaffold
- graphify config — Graphify enabled
- `.ai\agents\<role>\` — subagent orchestration enabled: create ONLY the roles needed, with
  `.ai\agents\orchestrator\` and `.ai\agents\qa\` as the mandatory minimum
- source layout — **language/framework-specific adaptation**: use the framework's canonical
  layout (e.g. a Next.js `app\`, a Rust `src\` via cargo, a Python package dir). Do NOT
  create an empty generic `src\` when the chosen framework scaffolds or expects a different
  layout; if a framework generator will be run, let it own the layout.

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
8. Initialize the FULL `.ai\` workspace from `templates\dot-ai\`: `project.md`, `status.md`,
   `tasks.md`, `decisions.md`, `risks.md`, `architecture.md`, `references.md`,
   `changelog.md`, `context_handoff.md` — plus `.ai\agents\orchestrator\` and
   `.ai\agents\qa\` (and only the additional role dirs actually needed) when subagent
   orchestration is enabled.
9. Worktrees config if selected.
10. Run validation (`amirctl validate` / validator) and capture its real output.
11. Continue with the post-creation portfolio steps below (they include registration).

## Phase 4b — Post-creation portfolio steps (ordered 1–11; stop-and-report on failure)

1. Write `.amir\portfolio.yaml` from this plugin's `templates\portfolio.yaml.tmpl`, filled
   ONLY with interview answers (questions 25–36). Unanswered fields stay blank/unset —
   **never fabricate progress, health, or dates**; a brand-new project has confirmed
   progress blank, not "0%" pretending to be measured.
2. Verify the stable `project.id` in `.amir\project.yaml` — it is the permanent registry and
   namespace key (never the folder name).
3. Register in `%USERPROFILE%\.amir\registry\projects.yaml` (the ONE shared registry;
   non-secret metadata only), via the engine when present.
4. Record the related-projects answers (question 33) in `portfolio.yaml` — links to registry
   ids, never to unregistered guesses.
5. If Asana linking was chosen: record the reference in `portfolio.yaml`
   (`integrations.asana`) — reference/GID only, never credentials.
6. If the user chose to join the global graph AND Graphify is enabled: run the
   `/amir:graph_projects_add` procedure for the new project (build graph, merge namespace,
   registration report). If they chose to join but Graphify is disabled: register
   metadata-only and state the 4 limitations from that command. If they declined: do
   nothing graph-related — joining is never implicit.
7. Confirm the registration report exists when step 6 ran
   (`.amir\reports\global-graph-registration.md`).
8. Seed `.ai\status.md` with the true initial state ("project created, no work done") and
   `.ai\changelog.md` with the creation entry — facts only.
9. Validate the registry entry: `amirctl portfolio-list` (or `registry-list`) shows the new
   project with correct id/path.
10. Run `amirctl portfolio-status` and confirm the new entry introduces no findings
    (missing files, invalid manifest).
11. Fold results into the Phase 5 report: registry status, portfolio.yaml path, global-graph
    decision and outcome — each as completed / failed / skipped / blocked, never blended.

## Phase 5 — Honest final report

Per component, report one of: **installed+healthy** (its catalog `health_check` was actually
executed and passed — include the evidence), **installed, not verified** (health check could not
run — say why), **failed** (with the real error), **skipped**, **blocked (needs credential X)**.
NEVER report a component as installed/working unless its executable/integration was actually
tested. List every file created. State validation result verbatim. If the engine was missing,
the report's first line must say the build ran in manual mode.

Finish with next steps: place required credentials, run `/amir:project_status`, (if
Graphify enabled) `/amir:graphify_setup` → `/amir:graphify_build`, and (if the project
joined the portfolio graph) `/amir:graph_projects_list` to see it in the portfolio view.
