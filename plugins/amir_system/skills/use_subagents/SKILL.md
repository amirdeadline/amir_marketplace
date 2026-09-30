---
name: use_subagents
description: Decompose project work into bounded, independently verifiable subagent tasks with scoped context packages, path allowlists, and evidence requirements; merge only validated work. Use for /amir:use_subagents.
---

# use_subagents — orchestration workflow

## Step 1 — Ground yourself (before any decomposition)

1. Read the project goal (from `.ai/` docs or the user), `.amir/project.yaml`, and the system
   rules (this plugin's `system_rules` skill / `rules/*.mdc`).
2. If no `.amir/project.yaml` exists: say so; ad-hoc mode is allowed only after the user agrees,
   and manifest-gated tools (Graphify, Serena, worktrees) are then OFF.
3. Note from the manifest: are git worktrees enabled? Is Graphify enabled? Is Serena enabled?
   These gate what subagents may use — **globally available is not enabled** (tool-scope rule).

## Step 2 — Decompose

Break the goal into ordered, **independently verifiable** tasks. Good tasks: single
responsibility, clear done-condition, verifiable without trusting the agent's word. Identify
which tasks are parallelizable (no shared files, no ordering dependency) vs. sequential.

## Step 2b — Agent workspaces (host-local)

Each subagent role gets a workspace under the **active host**, never under `.ai/agents/` for
new work:

| Host | Workspace root |
|------|----------------|
| Cursor | `.cursor/agents/<role>/` |
| Claude Code | `.claude/agents/<role>/` |
| Codex | `.codex/agents/<role>/` |

Recognized roles: `orchestrator`, `architect`, `developer`, `qa`, `security`, `research`.
Create ONLY the role directories the current work actually needs — with `orchestrator` and `qa`
as the mandatory minimum whenever subagent orchestration is enabled.

Each agent folder includes at least `report.md` (from `templates/host/agents/report.md`).
Agents write inside their own host workspace (plus allowed code paths), never in another
role's folder and never into another host's tree.

Shared project facts (status, tasks, design, assumptions, TODO, report index) stay in `.ai/`
per `templates/project-layout.md`. After an agent updates `report.md`, refresh the matching
row in `.ai/reports.md`.

## Step 3 — Context packages (one per subagent)

Each subagent receives ONE bounded package — **never the whole repository**:

- objective and acceptance criteria (checkable, specific)
- allowed paths (files/dirs it may modify) and prohibited paths (explicitly listed)
- the minimal set of files/snippets it must read first
- required tests it must run/write, and required EVIDENCE it must return (command outputs, test
  results, diffs — not just claims)
- relevant excerpts of rules (goal-preservation, honest-execution) — a subagent may NOT change
  the project end goal, weaken acceptance criteria, or mark its own work validated
- tool permissions: only manifest-enabled tools; state them explicitly

## Step 4 — Isolation for parallel code modification

- Worktrees enabled in manifest → create one worktree per parallel code-writing agent; each
  agent works only in its worktree; record worktree→task mapping.
- Worktrees NOT enabled → do not use them; serialize code-writing tasks instead. Read-only
  analysis tasks may always run in parallel.

## Step 5 — Execute and verify

1. Launch independent agents in parallel; dependent ones in order.
2. On each result: verify against acceptance criteria YOURSELF (run the tests / check the
   evidence). Reported-done is not done — evidence decides.
3. Merge ONLY validated work. Failed/unverified work is returned with precise feedback or
   reassigned; never merged "provisionally".
4. Watch for goal drift: if any agent's output redefines scope or goal, reject that part
   (goal-preservation rule).

## Step 6 — Record and report

- Record decisions, task outcomes, and evidence in `.ai/` docs (`.ai/tasks.md`,
  `.ai/decisions.md`, `.ai/TODO.md`, `.ai/assumptions.md`; risks → `.ai/risks.md`).
  Per-agent evidence and `report.md` stay under `.<host>/agents/<role>/`; update
  `.ai/reports.md` with agent, host, score (1–100 human attention), datetime, summary, and
  link to that report.
- Final report separates: **completed (with evidence) / failed (with errors) / skipped /
  blocked (with blocker)**. Never blend these. Recommend `/amir:cleanup_context` if the
  orchestration consumed substantial context.
