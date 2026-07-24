---
description: Produce a model-usage cost report from Langfuse trace data
argument-hint: [period, e.g. 7d | 30d | since 2026-07-01]
---

# /amir:langfuse_cost_report

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Confirm connectivity; otherwise point to `/amir:langfuse_validate`.
2. Determine the period from `$ARGUMENTS` (default: last 7 days). Query the Langfuse API (metrics/daily-metrics endpoints or trace queries) for that window.
3. Report, with real numbers: total cost; cost and token totals by model; cost by trace/span stage (using the standard hierarchy names — which agent stage burns the money); top 10 most expensive traces with links; retry overhead (cost attributable to retried spans) when derivable.
4. Accuracy caveats to state: costs come from Langfuse's model-price table and token counts reported by SDKs — verify the price table covers the models in use (flag "unpriced model" rows as undercounted); sampled tracing undercounts totals — if sampling < 100%, extrapolate and label the extrapolation.
5. Compare with the previous equal-length period and highlight significant deltas.
6. Write the report to `.amir/state/langfuse/cost-reports/<date>.md` and summarize in chat. Do not include any prompt content in the report — figures and trace ids only.
