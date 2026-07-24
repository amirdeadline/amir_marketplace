---
name: context7_usage
description: >-
  When and how to use Context7 for library documentation in an amir project:
  installed-version discipline, precedence chain, privacy, fallbacks.
---

# context7_usage

Context7 (https://github.com/upstash/context7) serves current, version-aware library documentation over MCP (`npx -y @upstash/context7-mcp`, or the remote endpoint `https://mcp.context7.com/mcp`) or the `ctx7` CLI. Gated on `project_tools.context7.enabled`; mode (`mcp` | `cli`) from the manifest.

## The one rule that matters: installed version first

Never assume latest == installed. Before any lookup, detect the version the PROJECT actually installs — lockfile first (`package-lock.json`, `poetry.lock`, `uv.lock`, `Cargo.lock`, ...), then manifest ranges, then the live environment. Ask Context7 for THAT version's docs; when only other versions exist, state the gap and check the changelog for drift.

## Precedence (SPEC §13, libraries chain)

Installed version (ground truth) → Context7 → official vendor docs → type definitions shipped with the package → tests. Code written from any doc source is validated against the installed dependency (type-check, import smoke test) before being called working. When Context7 and the installed package disagree, the package wins.

## Privacy and credentials

- Send only library names, versions, and questions. Do not paste proprietary project source into Context7 queries unless strictly required for the answer and the user approves.
- Network access is explicit: the manifest's `permissions.network` must allow context7.
- `CONTEXT7_API_KEY` is optional (free key raises rate limits; get it at context7.com/dashboard). Store it in `%USERPROFILE%\.amir\secrets\context7.env`, referenced by env var; never in tracked files. Account-dependent behavior (higher limits) must be labeled as such when reporting.

## Fallback behavior

Context7 unreachable or rate-limited (429): fall back to the official vendor documentation for the pinned version, then to the package's own shipped docs/types. Always label which source answered. A rate-limit is "reachable, limited", not "broken" — report it accurately.
