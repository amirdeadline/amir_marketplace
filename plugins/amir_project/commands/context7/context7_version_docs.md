---
description: Fetch docs pinned to a specific library version and diff against installed
argument-hint: <library> [version] [topic]
---

# /amir:context7_version_docs

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.context7.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Determine the target version: use the version in `$ARGUMENTS` if given; otherwise detect the installed version from the project's lockfile/environment (that detection is mandatory — installed version is the top of the library-docs precedence chain).
2. Resolve the library id (`resolve-library-id`), then request docs for that id constrained to the target version and topic. Context7 library ids support version-pinned forms where the library publishes them; if the pinned form is unavailable, fetch the nearest documented version and STATE THE GAP (e.g. "docs are for 5.2, you run 5.0").
3. When the requested version differs from the installed version, produce a short delta list: APIs added/removed/changed between the two, sourced from the library's changelog or official migration guide (fetch it if needed).
4. Any code you subsequently write from these docs must be validated against the installed dependency (compile/type-check or a quick import test) before being presented as working.
5. Never claim "latest == installed". Always print both versions in the answer header.
