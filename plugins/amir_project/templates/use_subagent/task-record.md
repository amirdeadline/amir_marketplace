# Task Record

Fill one record per atomic task. Validate against `schemas/use_subagent-task.schema.yaml`.

```yaml
task_id: T001
title: Short action-oriented title
type: discovery # discovery | design | implementation | test | review | documentation | integration | validation
objective: One precise outcome
description: Exact work the subagent must perform
reason: Why this task exists
inputs:
  - Required files, artifacts, decisions, or prior task outputs
dependencies:
  - T000
context_scope:
  - Files, directories, APIs, or concepts the subagent may inspect
allowed_changes:
  - Files or areas the subagent may modify
prohibited_changes:
  - Files, behavior, or scope the subagent must not modify
acceptance_criteria:
  - Observable conditions required for success
validation:
  - Commands, tests, inspections, or evidence required
deliverables:
  - Expected code, patch, report, test, or artifact
risk_level: low # low | medium | high
execution_mode: sequential # sequential | parallel
estimated_complexity: small # trivial | small | moderate
assigned_agent_profile: Specialized role for the task
status: pending # pending | ready | dispatched | in_progress | result_received | validating | completed | blocked | failed | retry_required | superseded | cancelled
```

## Ownership block (before parallel dispatch)

```yaml
ownership:
  T004:
    files:
      - path/to/file.ts
  T005:
    files:
      - path/to/test.ts
  T006:
    interfaces:
      - TokenService.verify()
```

## Task table (user-facing)

| ID | Task | Type | Dependency | Agent Role | Execution |
|----|------|------|------------|------------|-----------|
