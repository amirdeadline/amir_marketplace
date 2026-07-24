---
description: Validate the Context7 integration with a live, version-aware lookup
---

# /amir:context7_validate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.context7.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Validation matrix (run all; pass/fail per line)

1. Runtime: `node --version` succeeds (mcp/cli modes need Node for npx).
2. Registration: `claude mcp list` shows `context7` connected (mcp mode), or `npx -y ctx7 --help` runs (cli mode).
3. Live resolve: `resolve-library-id` for one real dependency of this project returns a plausible id.
4. Live docs: fetch a small doc snippet for that id; result is non-empty and on-topic.
5. Version awareness: confirm the lookup flow used the installed version from the lockfile, not "latest" (show the detected version).
6. Secrets hygiene: if an API key is configured, confirm it lives outside the repo (e.g. `%USERPROFILE%\.amir\secrets\context7.env`) and appears nowhere in tracked files (grep the repo for `CONTEXT7_API_KEY=` values; the variable NAME may appear, a value must not).
7. Rate limiting: if calls fail with 429, report that as "reachable but rate-limited (no/insufficient API key)" — distinct from broken.

Verdict "healthy" requires 1-6 passing. Report failures precisely with the remedy.
