# Compatibility matrix — /use_subagent

| Environment | Native isolation | Recommended mode | Notes |
|-------------|------------------|------------------|-------|
| Cursor (Agent + Task tool) | Yes — `Task` | **A** (parallel Task calls) | Map profiles to `subagent_type` (e.g. explore, generalPurpose, code-reviewer, security-reviewer). Do not dump parent chat into `prompt`. |
| Cursor (no Task / restricted) | No | **C** | Isolated task execution contexts; label simulated |
| Claude Code | Yes — Task / agents | **A** | Use plugin agents + Task; one agent per task |
| Codex CLI | Limited | **C** (or **B** if multi-session) | Sequential isolated contexts; honest labeling |
| IDE agents without spawn | No | **C** or **D** | Prefer C; use D if user must open agents |
| CLI agents | Varies | Detect | Document chosen mode |
| Multi-agent frameworks | Yes | **A** / **B** | One worker per task; orchestrator validates |
| User must spawn agents | Manual | **D** | Emit prompts + parallel groups |

## Hard vs instruction-based enforcement

| Rule | Enforcement |
|------|-------------|
| Plan before code | Instruction / prompt |
| One subagent per task | Instruction; host Task API when Mode A |
| No conflicting parallel writes | Instruction + ownership YAML |
| Evidence before COMPLETED | Instruction |
| Secret redaction | Instruction |

This skill does **not** provide an OS sandbox. Host tool permissions may still allow writes if the agent misbehaves.
