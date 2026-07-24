---
name: swebench_method
description: >-
  SWE-bench methodology for amir projects: what it measures, reproducibility
  requirements, subset-first economics, honest reporting.
---

# swebench_method

SWE-bench (https://github.com/SWE-bench/SWE-bench) evaluates whether a system can produce patches that resolve real historical GitHub issues, verified by each repo's own tests in reproducible docker environments. Gated on `project_tools.swe_bench.enabled`.

## What it measures — and does not

It measures patch-level issue resolution on historical, mostly-Python open-source repos with existing test suites. It does NOT measure: greenfield design, non-Python ecosystems, security quality, maintainability, interaction quality, or "every capability" — never present a SWE-bench number as general capability. Contamination (the model has seen these repos) is a standing threat to validity; mention it in reports.

## Evaluation precedence (SPEC §13)

Project acceptance tests → project-specific benchmarks → SWE-bench/Terminal-Bench → human review. Public benchmarks are the third opinion, not the first.

## Reproducibility requirements (every run, no exceptions)

Record BEFORE running, in `.amir/state/swebench/runs/<run-id>/config.yaml`: benchmark dataset + version (`princeton-nlp/SWE-bench_Lite` 300 / `SWE-bench_Verified` 500 / full), the exact instance-id list, model + settings, scaffold/agent + version, harness commit hash, planned workers, cost budget. Preserve AFTER running: predictions (`{instance_id, model_name_or_path, model_patch}`), full evaluator output and logs, token/cost actuals. Config change = new run id. Runs without preserved evidence are anecdotes.

## Economics: subset first

Default to a 5-25 instance Lite slice (deterministic selection) before anything bigger. Full or Verified runs need explicit approval with a cost estimate shown (they can burn hundreds of dollars and hours). Gold-prediction runs (`--predictions_path gold`) are the free way to validate the harness itself — near-100% expected; use them when results look implausible.

## Environment

Official harness: source install (`pip install -e .`), Python 3.10+, docker, ~120 GB disk, 16 GB+ RAM, x86_64 (ARM experimental). On this Windows machine: WSL 2 + Docker Desktop, watch the virtual disk size. `max_workers` conservative (< 0.75 × cores, < 28).

## Honest reporting

Rates always carry their denominator and scope ("14/25 resolved on a Lite slice with X"). Environment-error instances are unmeasured, not failed — exclude and disclose. A subset score is not a leaderboard score. Small slices get a significance caveat.

## Fallback

No disk/docker budget → run the project's own acceptance tests and say a public benchmark was not run; never substitute an estimated or remembered score.
