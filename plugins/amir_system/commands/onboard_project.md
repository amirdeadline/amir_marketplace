---
description: Onboard an existing repository into the Amir system (discovery, evidence-based recommendations, safe migration)
argument-hint: [path-to-repo]
---

# /amir:onboard_project

Load and follow the `onboard_project` skill in this plugin (`skills/onboard_project/SKILL.md`).
That skill is the single source of truth for this workflow — do not improvise a shortened version.

Hard requirements (contract):

- Run the full discovery pass first (languages, frameworks, deps, build/test, CI/CD, containers,
  IaC, entry points, existing AI config for both Cursor and Claude, secrets PRESENCE only —
  never read or expose secret values).
- Classify every optional component with one of the fixed labels
  (Strongly recommended / Recommended / Optional / Not useful / Unsupported / Already configured /
  Conflicting / Requires migration) and cite the file-level evidence for each classification.
- Catalog options come from `catalog/catalog.json`; if missing, tell the user to run
  `/amir:update_catalog` before component selection.
- Migration is MERGE, never overwrite: back up existing AI config into `.amir/backups/<timestamp>/`
  first, preserve valid config, detect collisions and global-config leakage.
- Show the final plan and require explicit confirmation before writing anything.
- Finish by producing `.amir/onboarding/onboarding-report.md` with the honest per-item ledger
  (existed-before / preserved / migrated / added / disabled / skipped / failed /
  manual-config-needed / missing credentials / active-in-Cursor / active-in-Claude).

If `$ARGUMENTS` contains a path, treat it as the candidate repo root (verify it exists before
starting discovery); otherwise use the current working directory.
