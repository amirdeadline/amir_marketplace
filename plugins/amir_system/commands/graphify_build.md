---
description: Full Graphify graph build for the current Amir project (skill-driven, manifest-gated)
---

# /amir:graphify_build

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml. Run /amir:create_project or /amir:onboard_project first."
2. `project_tools.graphify.enabled` absent/false → STOP: Graphify disabled for this project;
   enable via `/amir:configure_project`, then run `/amir:graphify_setup`.

## Output location (mandatory)

Read `project_tools.graphify.output_directory` (default **`.amir/graphify-out`**). Never build
into a root-level `graphify-out/`. AI narrative docs go to `.ai/` (e.g. architecture via
`/amir:graphify_architecture`), not into the graph output folder.

```powershell
$env:GRAPHIFY_OUT = "<manifest output_directory or .amir/graphify-out>"
```

## Procedure

1. Confirm setup happened (project-local `.claude/skills/graphify` exists from
   `graphify install --project --platform claude`, and `.cursor/rules/graphify.mdc` points at
   `.amir/graphify-out/` when Cursor is enabled). If not, run `/amir:graphify_setup` first
   (with the user's go-ahead).
2. Announce the build before starting: scope (project root only), respected excludes
   (`.gitignore` + manifest exclude list + `.amir/` + `.ai/`), output location
   (`.amir/graphify-out/`), and that a full build may take a while on large repos. A full
   build is a heavyweight action — confirm.
3. With `GRAPHIFY_OUT` set, execute the full build via the project-local `/graphify` skill flow
   (`.claude/skills/graphify/SKILL.md`) — that skill owns chunking, god-node extraction, and
   community detection. Follow it; do not reimplement it ad hoc. Prefer
   `graphify update .` / skill steps that honor `GRAPHIFY_OUT` over any path that hardcodes
   root `graphify-out/`.
4. Respect boundaries: never index files outside the project root; never follow symlinks out of
   the project; never include paths the manifest excludes; never index `.amir/` or `.ai/` as
   source.
5. After the build: verify `.amir/graphify-out/graph.json` exists and is non-empty; record build
   timestamp and current source commit (if git) in the report. If a root `graphify-out/`
   appeared anyway, report it as FAILED path discipline and move/remove it after confirmation.
6. Honest report: nodes/communities summary if available, elapsed time, anything skipped or
   failed. If the build failed partway, say exactly that — never present a partial graph as
   complete.
