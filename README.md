# amir marketplace

Cross-host plugin marketplace for Claude Code and Cursor. **Version 1.0.0** (see [`VERSION`](VERSION)).

Design docs: [`design/component-map.md`](design/component-map.md) ·
[`design/SPEC-amir_system.md`](design/SPEC-amir_system.md) ·
[`design/SPEC-amir_project-tools.md`](design/SPEC-amir_project-tools.md) ·
security matrix: [`SECURITY.md`](SECURITY.md)

## Architecture: the two-plugin model

The marketplace ships exactly **two** plugins. Both declare plugin.json `"name": "amir"`, so every
command surfaces under the single **`/amir:`** namespace; their command sets are disjoint (enforced by
`design/component-map.md` and `tools/validator.py`).

| Marketplace entry | Scope | Contents |
|---|---|---|
| `amir_system` | **user** — installed once, available before any project exists | Project lifecycle (`create_project`, `onboard_project`, `use_subagents`, `list_projects`, `cleanup_context`, configure/validate/repair/status/help), Graphify wrappers, Asana MCP + task skills, Playwright MCP, the 7 system rules, and the deterministic tooling in `plugins/amir_system/tools/` |
| `amir_project` | **project** — never auto-enabled | 24 component groups: harness, aws, azure, xdr, docker, elastic, litellm, nmap, paloalto, prisma, qradar, sentinel, splunk, ssh, terraform, wireshark, serena, context7, semgrep, langfuse, openhands, worktrees, swebench, terminalbench |

A project opts in through its manifest `.amir/project.yaml` (schema v2,
[`schemas/project-manifest.schema.json`](schemas/project-manifest.schema.json)). Selections are pinned
in `.amir/components.lock.json` (per-source-file sha256) and materialized either by installing the full
plugin (`claude plugin install amir_project@amir-marketplace --scope project`) or by rendering a
manifest-selected subset with `tools/renderer.py`. Installed ≠ available ≠ enabled ≠ authorized ≠
configured ≠ healthy — the validator reports each state separately.

## `/amir:` namespace

All commands are `/amir:{snake_case}` (sole exception: skill `create-project-doc`, user-specified).
Examples: `/amir:create_project`, `/amir:graphify_status`, `/amir:plan`, `/amir:terraform_plan`,
`/amir:serena_find_symbol`, `/amir:semgrep_security_gate`. Full inventory:
[`design/component-map.md`](design/component-map.md) and [`catalog/catalog.json`](catalog/catalog.json).

In Cursor, project-rendered commands are flat files `.cursor/commands/amir_<name>.md`
(colons are illegal in Windows filenames).

## Install quickstart

Claude Code (user scope — do this once):

```text
claude plugin marketplace add E:/PC3_Shared/Plugins/amir_marketplace
claude plugin install amir_system@amir-marketplace --scope user
```

Cursor (user scope, junction):

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.cursor\plugins\local\amir_system" `
  -Target "E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir_system"
# then: Developer: Reload Window
```

Per project: run `/amir:create_project` (new) or `/amir:onboard_project` (existing repo). These write
the manifest + lock, install or render only the selected component groups for the enabled hosts, and
register the project in `%USERPROFILE%\.amir\registry\projects.json`.

## Deterministic tooling (`plugins/amir_system/tools/`)

`amirctl.py` drives everything (also bootstrapped at `%USERPROFILE%\.amir\bin\amirctl.py` via
`%USERPROFILE%\.amir\config.json`):

```text
python amirctl.py validate | generate [--dry-run] | lock | drift | repair | doctor
python amirctl.py catalog-list | catalog-resolve <ids...>
python amirctl.py registry-list|registry-add|registry-remove|registry-repair
python amirctl.py remove-project-config --plan|--apply
python amirctl.py migrate
```

Requires Python 3.12 with `pip install pyyaml jsonschema`. Self-test: `python plugins/amir_system/tools/_selftest.py`.

## Repository layout

```text
.claude-plugin/marketplace.json   Claude Code marketplace manifest (2 plugins)
.cursor-plugin/marketplace.json   Cursor marketplace manifest (pluginRoot ./plugins)
.agents/plugins/marketplace.json  Agents-host marketplace manifest
catalog/catalog.json              Component registry (29 groups, honest capability metadata)
catalog/hosts.json                Host matrix + install commands
schemas/                          Manifest v2, component metadata, lock schemas (JSON Schema 2020-12)
plugins/amir_system/              User-scope plugin (+ tools/)
plugins/amir_project/             Project-scope plugin (24 groups)
design/                           Authoritative specs
```

## Security

Secrets are referenced by environment-variable **name** only (e.g. `ASANA_ACCESS_TOKEN`, loaded from
`%USERPROFILE%\.amir\secrets\asana.env`) — never stored in the repo, manifests, or logs. Network and
secret access are deny-by-default per project (`permissions` block in the manifest). Destructive
actions require confirmation. The `prisma` group's baked corpus is **internal/personal use only** —
keep the marketplace private while it is included.
