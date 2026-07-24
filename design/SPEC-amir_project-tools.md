# SPEC — amir_project plugin + new tool groups

Plugin dir: `plugins/amir_project` (renamed from `plugins/amir`). plugin.json `{"name": "amir", "version": "1.0.0"}`;
marketplace entry ID `amir_project`. Never auto-enabled; installed per-project or rendered as subset.
Command layout: `commands/<group>/<name>.md` (group dirs are organizational only; command name = filename).
Skills: `skills/<name>/SKILL.md` (underscore names). Every command's frontmatter: `description` (one line).
Every command body starts by checking `.amir/project.yaml` enables its group (tool-scope rule); if not enabled,
refuse with pointer to `/amir:configure_project`.

## Component metadata (catalog/catalog.json) — every component declares (spec §10):
id, plugin (amir_system|amir_project), version, scope, description, official_source, license, supported_hosts,
supported_operating_systems, installation_mode, dependencies, optional_dependencies, conflicts_with,
required_executables, required_credentials, network_access, secret_access, filesystem_access, write_capabilities,
destructive_capabilities, resource_requirements, health_check (a concrete command), uninstall_method.
Activation blocked when: dependency missing, host unsupported, credentials missing, permissions rejected,
version incompatible, conflicts with selected component.

## New tool groups (all disabled by default, project-selectable)

### serena (§8.1) — official: https://github.com/oraios/serena (uv-run MCP server; verify current install docs)
Commands serena_setup/status/index/find_symbol/find_references/analyze_symbol/refactor/validate/disable.
Purpose: symbol lookup, definition/reference lookup, LSP navigation, symbol-level editing, refactoring.
No global indexing; validate language server; detect unsupported languages; data in approved locations
(.serena/ in project); no Serena edits without source validation + tests. Precedence: Serena for precise
symbols, Graphify for broad architecture; define fallback (direct file inspection).

### context7 (§8.2) — official: https://github.com/upstash/context7 (MCP mode; CLI+skills mode where documented)
Commands context7_setup/status/lookup/library/version_docs/validate/disable.
Detect the project's installed dependency VERSION and request docs for that version; prefer official docs;
never assume latest == installed; validate generated code against installed dep; don't send proprietary source
unless required; network access explicit; API keys (CONTEXT7_API_KEY if used) stored securely.

### semgrep (§8.3) — both paths where available: Semgrep MCP (official mcp package) + "Semgrep Guardian"
(detect actual supported installation model from official docs; do NOT assume identical; report free vs
account-dependent functionality honestly). Commands semgrep_setup/status/scan/scan_changed/scan_dependencies/
scan_secrets/security_gate/explain/fix/validate/disable. Never claim clean scan == secure; preserve findings
(.amir/state/semgrep/); source-level verification before automatic fixes; run tests after fixes; severity
thresholds from manifest policy (block_on critical/high default, NOT enforced without project approval);
never silently upload proprietary code (local scans by default; `--pro`/cloud requires opt-in).

### langfuse (§8.4) — hosted / self-hosted / disabled modes. Commands langfuse_setup/status/start/stop/trace/
evaluate/dataset/experiment/cost_report/validate/disable. Never auto-enable telemetry; explicit approval;
redact secrets/sensitive content; configurable sampling; local-dev settings (self-host docker compose);
record model/latency/tokens/cost/retries/tool calls; hierarchical traces (Task → Planning → Context retrieval →
Architecture agent → Development agent → Test execution → QA agent → Security scan → Final validation);
avoid capturing full proprietary prompts by default; filtering/redaction support. Keys: LANGFUSE_PUBLIC_KEY,
LANGFUSE_SECRET_KEY, LANGFUSE_HOST via env refs only.

### openhands (§8.5) — official OpenHands docs. Commands openhands_setup/status/sandbox/run/compare/evaluate/
logs/reset/validate/disable. Sandboxed (docker) execution; never mount home; no credential forwarding; no
privileged containers; network disabled by default; mount only the selected project; report resource
requirements; never auto-install/launch per project. Default policy block (enabled false; project_mount
read_write; home_mount false; privileged false; network disabled; credentials none).

### worktrees (§8.6) — native git. Commands worktree_create/list/assign/status/validate/merge/cleanup/repair.
One agent = one task branch = one worktree; no multiple write-agents per tree; deterministic naming
`.amir/worktrees/{task-id}-{short-name}` (fall back to sibling dir `../<repo>-worktrees/` if in-repo placement
breaks tools — document choice); check uncommitted work before cleanup; never force-delete without approval;
validate commits before merge; integration tests after merge; preserve failed worktrees unless explicitly removed.

### swebench (§8.7) — official SWE-bench (princeton-nlp). Commands swebench_setup/status/prepare/run/evaluate/
compare/report/cleanup. Record benchmark version, task set, model+harness config, tokens/cost; reproducible
(docker) environments; preserve patches + evaluator output (.amir/state/swebench/); support small validation
subsets (e.g. SWE-bench Lite slice) before large runs; no expensive full runs without approval; never claim
SWE-bench measures every capability.

### terminalbench (§8.8) — official Terminal-Bench (laude-institute / tbench). Commands terminalbench_setup/
status/prepare/run/evaluate/compare/report/cleanup. Isolated envs; never expose host credentials; record task/
env/model/harness/result; preserve logs; enforce time/token/disk/network limits; benchmark ≠ production safety.

## Manifest schema v2 (.amir/project.yaml) — schemas/project-manifest.schema.json
Top-level keys: schema_version (const 2), project {id, name, description, root, created_at, onboarded},
hosts {cursor.enabled, claude_code.enabled}, plugins {amir_project {enabled, components: [group ids]}},
system_capabilities {asana.allowed, playwright.allowed}, project_tools {graphify {enabled, output_directory,
update_policy manual|after-major-change|before-impact-analysis|before-architecture-task|before-code-review|
after-git-commit, include, exclude, commit_generated_graph}, serena {enabled}, context7 {enabled, mode mcp|cli},
semgrep {enabled, integration guardian|mcp|both, policy {scan_changed_files, scan_before_commit, block_on[],
scan_secrets, scan_dependencies}}, langfuse {enabled, mode hosted|self_hosted|disabled}, openhands {enabled,
sandbox {project_mount, home_mount, privileged, network, credentials}}, git_worktrees {enabled}, swe_bench
{enabled}, terminal_bench {enabled}}, permissions {network {default deny|allow, allowed_components[]},
secrets {default, allowed_references[]}, destructive_actions {require_confirmation}}, documentation {enabled,
files...}, generated_artifacts {commit_graphify_output, commit_playwright_artifacts, commit_benchmark_results}.
State distinctions (validator reports separately): installed_at_system_scope, available_to_project,
enabled_in_project, authorized_write, configured, healthy.
Lock: .amir/components.lock.json {component_id: {version, source_path, sha256 of each source file}}.

## Selection recommendations (§12) and precedence (§13) — embed in create/onboard skills and docs
Recommend: medium/large repo→Graphify; symbol-heavy supported lang→Serena; external frameworks/APIs→Context7;
security-sensitive/exposed→Semgrep; web UI→Playwright; LLM/multi-agent app→Langfuse; sandboxed experiments→
OpenHands; parallel subagents→worktrees; issue-resolution eval→SWE-bench; terminal-agent eval→Terminal-Bench.
Advisory only. Precedence: understanding = Graphify(broad)→Serena(precise)→source(final)→tests(behavior);
libraries = installed version→Context7→official docs→types→tests; security = threat model→Semgrep→dep scan→
secret scan→tests→manual review; evaluation = project acceptance tests→project benchmark→SWE/Terminal-Bench→
human review. No tool is an unquestionable source of truth.

## Satellite groups: mechanical migration
Copy from plugins/amir-<x>/ into plugins/amir_project/commands/<group>/ + skills/ with renames per
design/component-map.md. Preserve scripts/ per group under plugins/amir_project/scripts/<group>/ and fix
`${CLAUDE_PLUGIN_ROOT}` references (root is now amir_project). Fold each old plugin's .mcp.json into
plugins/amir_project/.claude-plugin/plugin.json mcpServers (aws-mcp, azure-mcp, litellm, elastic-agent-builder)
— but MCP entries load only when the plugin (or rendered subset containing them) is enabled; renderer includes
only selected groups' MCP servers in rendered builds.
