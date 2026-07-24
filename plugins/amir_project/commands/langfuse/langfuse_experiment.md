---
description: Run an experiment over a Langfuse dataset and compare configurations
argument-hint: <dataset name> [run name] [what varies, e.g. model or prompt version]
---

# /amir:langfuse_experiment

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Confirm connectivity and that the dataset exists (via API); otherwise stop with a pointer to `/amir:langfuse_dataset`.
2. Define the experiment before running: dataset, run name (unique, dated), the single variable under test (model, prompt version, temperature, agent config) and what stays fixed. Refuse to run "compare everything at once" — one variable per run, or explicitly labeled multi-arm runs.
3. Cost guard: estimate items × expected tokens × model price and show the estimate. Get explicit confirmation before any run that will spend real model credits; small smoke subsets (5-10 items) first.
4. Execute: iterate dataset items, run the project's pipeline for each, link results to the dataset run via the SDK (dataset item `run` linkage) so Langfuse groups them; record model, latency, tokens, cost per item.
5. Score the run (reuse `/amir:langfuse_evaluate` logic) and fetch aggregates from the API.
6. Compare against a named baseline run when one exists: per-metric deltas with counts. State clearly that dataset performance is evidence about these cases only, not a general quality guarantee.
7. Append the experiment record (config, run id, aggregates, cost) to `.amir/state/langfuse/experiments.md`.
