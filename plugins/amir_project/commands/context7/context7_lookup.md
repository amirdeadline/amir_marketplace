---
description: Look up docs for a library at the version this project actually installs
argument-hint: <library> <question>
---

# /amir:context7_lookup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.context7.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Detect the INSTALLED version first — never assume latest. Check, in order of authority: lockfile (`package-lock.json` / `pnpm-lock.yaml` / `poetry.lock` / `uv.lock` / `Cargo.lock` / `go.sum`), then manifest (`package.json`, `pyproject.toml`, ...), then the environment (`npm ls <pkg> --depth=0`, `pip show <pkg>`).
2. Resolve the library id with Context7 `resolve-library-id`, then request docs with the query from `$ARGUMENTS`, scoped to the detected version where Context7 offers versioned docs. If the exact version is unavailable, say which version's docs you received and how far it is from the installed one.
3. Privacy: send only the library name, version, and the question. Do not paste proprietary project source into the query unless strictly required and the user approves.
4. Validate before relying on the answer: cross-check any API signature you plan to use against the installed package itself (types in `node_modules/<pkg>`, `pip show -f`, or the package's shipped docs). If Context7 and the installed types disagree, the installed package wins — report the discrepancy.
5. Fallback: if Context7 is unreachable, use official vendor docs for the pinned version and label the source.
