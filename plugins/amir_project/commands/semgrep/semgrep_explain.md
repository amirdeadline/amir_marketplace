---
description: Explain a Semgrep finding - rule intent, exploitability here, fix options
argument-hint: <rule id or finding reference from the latest scan>
---

# /amir:semgrep_explain

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Locate the finding: match `$ARGUMENTS` (rule id, file:line, or index) against the newest JSON in `.amir/state/semgrep/`. If no stored scans exist, say so and point to `/amir:semgrep_scan`.
2. Read the ACTUAL source at the finding location, with enough surrounding context to judge data flow. The stored match snippet alone is not enough.
3. Explain, in order: what the rule detects and why it matters (cite the rule's own message/metadata, and the registry page `https://semgrep.dev/r/<rule-id>` if network is allowed); whether the pattern is actually exploitable in THIS code path (trace where the tainted value comes from — user input vs constant); severity as reported vs your assessed real-world severity here, with reasoning.
4. If you assess it as a false positive, say so with the evidence, and show how to suppress it narrowly (`# nosemgrep: <rule-id>` on the exact line with a justification comment) — never blanket-disable the rule.
5. Offer concrete fix options with code sketches, ranked by safety. Do not apply anything — applying is `/amir:semgrep_fix`.
