---
description: Full Graphify graph build for the current Amir project (skill-driven, manifest-gated)
---

# /amir:graphify_build

## Tool-scope gate (mandatory, run FIRST)

1. Nearest ancestor with `.amir/project.yaml`; if none → STOP: "Not an Amir project — no
   .amir/project.yaml. Run /amir:create_project or /amir:onboard_project first."
2. `project_tools.graphify.enabled` absent/false → STOP: Graphify disabled for this project;
   enable via `/amir:configure_project`, then run `/amir:graphify_setup`.

## Procedure

1. Confirm setup happened (project-local `.claude/skills/graphify` exists from
   `graphify install --project --platform claude`). If not, run `/amir:graphify_setup` first
   (with the user's go-ahead).
2. Announce the build before starting: scope (project root only), respected excludes
   (`.gitignore` + manifest exclude list), output location (`graphify-out/`), and that a full
   build may take a while on large repos. A full build is a heavyweight action — confirm.
3. Execute the full build via the project-local `/graphify` skill flow
   (`.claude/skills/graphify/SKILL.md`) — that skill owns chunking, god-node extraction, and
   community detection. Follow it; do not reimplement it ad hoc.
4. Respect boundaries: never index files outside the project root; never follow symlinks out of
   the project; never include paths the manifest excludes.
5. After the build: verify `graphify-out/graph.json` exists and is non-empty; record build
   timestamp and current source commit (if git) in the report.
6. Honest report: nodes/communities summary if available, elapsed time, anything skipped or
   failed. If the build failed partway, say exactly that — never present a partial graph as
   complete.
