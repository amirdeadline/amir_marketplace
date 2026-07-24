---
description: Resolve a library name to its Context7 id and summarize doc coverage
argument-hint: <library name>
---

# /amir:context7_library

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.context7.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Take the library name from `$ARGUMENTS`. If it is a dependency of this project, note the installed version from the lockfile first.
2. Call Context7 `resolve-library-id` with the name. Present the candidate ids with their trust/popularity signals and pick the one matching the official package (prefer the official org's entry; say why you picked it).
3. Report: resolved id, whether versioned docs exist and which versions, and doc coverage (topics available).
4. If several plausible ids exist (forks, renamed packages), list them and ask the user rather than guessing.
5. Cache nothing outside the conversation; do not write files for this read-only lookup.
