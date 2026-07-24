---
description: Produce a reproducibility-grade report for a SWE-bench run
argument-hint: <run-id>
---

# /amir:swebench_report

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.swe_bench.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Load everything for `<run-id>` from `.amir/state/swebench/runs/<run-id>/`. Missing pieces (config, predictions, evaluator output, cost record) are listed as gaps in the report — never papered over.
2. Report sections (write to `.amir/state/swebench/runs/<run-id>/report.md`):
   - **Setup**: benchmark dataset + version, exact instance list (count + where the list is stored), harness commit, docker/platform, date.
   - **System under test**: model id and settings, agent/scaffold and version, prompt/config references.
   - **Results**: resolved rate with numerator/denominator, per-instance table (resolved / unresolved / error), error instances excluded from the denominator with justification.
   - **Cost**: tokens and dollar cost total and per resolved instance; wall time.
   - **Threats to validity**: subset selection, single run (no variance estimate), possible contamination (model may have seen these repos), and the standing caveat that SWE-bench measures historical-issue patch resolution in Python repos — not general capability, security, or maintainability.
   - **Reproduction**: the exact commands to regenerate evaluation from the preserved predictions.
3. If `generated_artifacts.commit_benchmark_results` in the manifest is true, stage the report for commit; otherwise leave it untracked and say so.
4. Chat summary: five lines max — headline rate with scope qualifier, cost, and the biggest caveat.
