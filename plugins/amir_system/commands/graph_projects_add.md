---
description: Register a project in the cross-project portfolio graph — validate, confirm scope, build/refresh its graph, merge as an isolated namespace, verify
argument-hint: project_directory
---

# /amir:graph_projects_add

Mutating (registry + global graph). Requires an explicit directory argument; if `$ARGUMENTS`
is empty, ASK for the project directory — one question. Never infer a directory from fuzzy
conversation text and never scan the computer for candidates.

Engine: `python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-add <dir>`. If the engine is
missing, say so honestly and offer only the supervised manual path (each phase below performed
step-by-step with the user, ending in `/amir:graph_projects_validate`). If a subcommand name is
rejected, run `--help` once, use the closest documented subcommand, and report which you used.

## Phase 1 — Validate the directory

1. Resolve the path; verify it exists and is readable. Missing → STOP with the exact path shown.
2. Look for `.amir\project.yaml`:
   - **Present** → read the stable `project.id`. The namespace and registry key come from this
     id — **NEVER from the folder name** (folders get renamed; ids do not).
   - **Absent (non-onboarded project)** → present exactly three options and wait:
     1. **Onboard now** — run `/amir:onboard_project` first, then return here.
     2. **Register metadata only** — registry entry without a knowledge-graph namespace.
        State these 4 limitations explicitly before the user chooses:
        - no local knowledge graph will exist, so no code/architecture answers for it;
        - it gets no namespace in the global graph — cross-project queries and dependency
          analysis will not see it;
        - health/progress columns will be limited to externally observable facts (directory,
          git); no `.ai\` structure is guaranteed;
        - `/amir:graph_projects_update` can only refresh its registry metadata, not a graph.
     3. **Cancel** — zero side effects.
3. Check the registry for an existing entry with the same id (idempotency): already registered
   → report that, offer `/amir:graph_projects_update` instead, and stop unless the user wants a
   forced re-registration (which follows the same confirmation flow).

## Phase 2 — Graphify gate

Read `project_tools.graphify.enabled` from the manifest.

- **Enabled** → a graph build/update is in scope.
- **Disabled/absent** → ASK: "Graphify is disabled for this project. Enable it (via
  `/amir:configure_project` + `/amir:graphify_setup`) so a graph can be built, or register
  metadata-only?" **Never enable Graphify silently** — a globally installed CLI is not
  authorization (tool-scope rule).

## Phase 3 — Scope, plan, confirm

Show the user exactly what will be indexed BEFORE anything runs:

- **Included**: project source per graphify config; `.ai\` docs (project.md, status.md,
  tasks.md, decisions.md, risks.md, architecture.md, references.md, changelog.md,
  context_handoff.md); SAFE manifest metadata (id, name, languages, frameworks, enabled
  components — never credential names' values or secret store paths).
- **Excluded, always**: secrets and secret stores (`.env*`, `*credential*`, key material,
  `%USERPROFILE%\.amir\secrets\`), `.git\`, dependency dirs (node_modules, venvs, vendor),
  build outputs, caches, `graphify-out\`, `.amir\backups\`, binaries/media.
- The registry entry to be written, and the namespace name (= `project.id`).
- The report file that will be created: `<project>\.amir\reports\global-graph-registration.md`.

Require explicit confirmation. Cancel = zero side effects.

## Phase 4 — Execute

1. Acquire the portfolio lock (`%USERPROFILE%\.amir\portfolio\locks\` — the engine manages it;
   if a lock is held, report who/when and stop rather than forcing).
2. Local graph: build (`graphify update` / `/amir:graphify_build` procedure) if missing or
   stale — announced, never silent.
3. Run the engine:
   ```powershell
   python "$env:USERPROFILE\.amir\bin\amirctl.py" portfolio-add <dir>
   ```
   The engine backs up `%USERPROFILE%\.amir\portfolio\graph\global-graph.json` before merging
   the namespace; confirm the backup exists in its output. Show real output; a failed merge is
   reported as failed — the previous global graph remains authoritative.

## Phase 5 — Validate and report

1. Verify: registry entry present with the stable id; namespace exists in
   `global-graph.json`; no duplicate namespaces; other namespaces untouched (count before ==
   count after, minus the addition).
2. Idempotency check: state clearly that re-running this command for the same id updates
   rather than duplicates.
3. Write `<project>\.amir\reports\global-graph-registration.md`: timestamp, id, namespace,
   what was included/excluded, engine output summary, backup path, validation results.
4. Chat report separates **completed / failed / skipped / blocked** — never blended. If the
   graph build failed but the metadata registered, say exactly that.
