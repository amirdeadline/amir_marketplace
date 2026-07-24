# Cursor adapter — use_subagent

## Invocation

- Slash: `/amir:use_subagent {prompt}` (packed command)
- Aliases: `/use_subagent {prompt}`, trailing `{prompt} /amir:use_subagent`

## Mode selection

1. If `Task` (namespace `cursor`) is available → **Mode A**.
2. Else → **Mode C** (isolated task execution context). Say so explicitly.
3. If user must create Composer/Agents manually → **Mode D**.

## Mode A — Task mapping (examples)

| Profile | Suggested `subagent_type` |
|---------|---------------------------|
| Repository discovery | `explore` or `code-explorer` |
| Architect / design | `architect` or `code-architect` or `planner` |
| Backend / general impl | `generalPurpose` |
| Tests | `tdd-guide` or `generalPurpose` |
| Code review | `code-reviewer` (different agent than implementer) |
| Security review | `security-reviewer` (when user/skill requires security review) |
| Shell / CI | `shell` or `ci-investigator` |

Always pass a **complete** task prompt (`templates/use_subagent/subagent-prompt.md`). Subagents do not see parent history.

Launch parallel-safe tasks in **one message** with multiple Task calls.

Prefer `run_in_background: true` only when Multitask Mode or user expects async; otherwise validate results in order of dependency.

## Limitations

- `bugbot` / `security-review` fixed prompt forms apply only when those dedicated flows are chosen; for skill-driven reviews prefer `code-reviewer` / `security-reviewer` with the skill’s review template.
- Cloud `environment: cloud` only if the user explicitly requests cloud agents.
