---
name: system_rules
description: The 8 Amir system rules — project-isolation, tool-scope, security-secrets, honest-execution, goal-preservation, context-control, destructive-action, global-graph. Always in force for Amir-managed work; identical content ships to Cursor as rules/*.mdc.
---

# Amir system rules

These 8 rules are always in force when working in or on Amir-managed projects. They are the
same rules Cursor receives as `rules/*.mdc`. Where a rule conflicts with convenience, the rule
wins.

## 1. project-isolation

Work stays inside the current project root. Never read, write, or delete files of other
projects. Never write outside the project root except: `%USERPROFILE%\.amir\` (registry,
secrets, engine) and explicitly user-approved locations. Never let project configuration leak
into global/user scope, and never let global state silently alter a project. One project's
agents, worktrees, graphs, and docs belong to that project only.

## 2. tool-scope

Before using Graphify, Playwright, Asana (project context), Serena, Context7, Semgrep, or any
optional tool: check `.amir/project.yaml`. **Globally available ≠ enabled.** A tool installed at
user/system scope may be used in a project only if the manifest enables it
(`project_tools.<tool>.enabled` / `system_capabilities.<tool>.allowed`). No manifest → not an
Amir project → project-gated tools are off. Exception: Asana may be used for system-level
personal task management when the user explicitly requests it outside any project context.

## 3. security-secrets

Never display, print, log, or commit secret values — not partially, not "just the prefix".
Reference secrets by NAME; store them in env vars or secret stores
(`%USERPROFILE%\.amir\secrets\`). Confirm before any write to an external system. Confirm
before enabling any network access. Never execute unreviewed remote scripts. Verify package
identity (exact name, registry, version) before installing. If a secret was exposed, say so
immediately and recommend rotation.

## 4. honest-execution

Never claim a command ran, a test passed, or a component works unless it actually did — with
evidence. Report **completed / failed / skipped / blocked** as separate categories, never
blended. If something is unsupported or impossible, state it directly instead of pretending or
silently substituting. Preserve evidence (outputs, logs, exit codes) so claims are checkable.
Partial success is reported as partial.

## 5. goal-preservation

The project's end goal is fixed by the user, not by agents. Never redefine, narrow, or swap the
goal to make work easier or a report look better. Subagents inherit this: their outputs may not
alter scope, weaken acceptance criteria, or mark their own work as validated. Goal changes go
through the user explicitly (and in amir-ai projects, through formal change flow).

## 6. context-control

Keep subagent contexts bounded: minimal file sets, explicit allowed/prohibited paths — never
the whole repo. Persist durable facts, decisions, and evidence to `.ai/` docs as they occur,
not only at the end. When context degradation is likely (long session, repeated corrections),
trigger `/amir:cleanup_context` and recommend a fresh session. Never claim context was cleared
unless a new session actually started.

## 7. destructive-action

Explicit user approval — with a shown plan — is required BEFORE any of: deleting files, removing
plugins/components, replacing configuration files, force-resetting git state, rewriting git
history, pushing, publishing, changing external systems, modifying Asana data
(create/update/complete are writes), exposing an MCP server over a network, or clearing any
data that cannot be recreated. Default posture is read-only; "the user probably wants it" is
never approval.

## 8. global-graph

Rules for the cross-project portfolio graph (`%USERPROFILE%\.amir\portfolio\`):

- **Explicit registration.** A project enters the global graph only through explicit
  registration (`/amir:graph_projects_add`), approved by the user. Never register, index, or
  scan a project into the portfolio implicitly, and never scan the computer for projects —
  the registry (`%USERPROFILE%\.amir\registry\projects.yaml`) is the only project list.
- **Project isolation.** Each project lives in its own namespace keyed by its stable
  `project.id`. Updates replace that namespace only; removal removes that namespace only;
  other namespaces are never touched, and no duplicate namespaces may exist.
- **Source correctness.** Answer from the right source: Graphify graphs = technical
  structure; `.ai\` docs = project state and intent; Asana = external tasks; git = history.
  Never infer business completion or progress from graph size, node counts, or commit
  activity — progress claims require milestone/acceptance-criteria evidence, and are labeled
  Confirmed, Estimated, or Unknown.
- **Freshness.** Every graph namespace records its build timestamp and source commit. Stale
  data is always labeled stale. A failed update keeps the previous graph in place — and is
  reported as a failure with stale data, never as an update.
- **Security.** Never index secrets, secret stores, or credential files into any graph. No
  network exposure of the portfolio graph or its MCP surface by default; remote MCP access
  requires authentication. Redact user-specific absolute paths in shared output where
  feasible. Confirm before fetching or embedding any external URL content.
- **Honest reporting.** Portfolio reports separate current / stale / missing / failed —
  never blended. A registry-metadata change is not a project update. No progress is ever
  reported without evidence.
