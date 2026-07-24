---
description: Interactively create a new Amir-managed project (interview, catalog selection, manifest, render, validate)
argument-hint: [project-name]
---

# /amir:create_project

Load and follow the `create_project` skill in this plugin (`skills/create_project/SKILL.md`).
That skill is the single source of truth for this workflow — do not improvise a shortened version.

Hard requirements (the skill enforces these; restated here as a contract):

- Ask ONE focused question at a time. Never batch the whole interview into one message.
- Display catalog options from `catalog/catalog.json` for every selectable category. If the
  catalog file is missing, stop the selection step and tell the user to run `/amir:update_catalog`.
- Recommendations are advisory only and must cite evidence. Never auto-select anything.
- Secure defaults: no optional MCP servers, no connectors, no network access, no secret access,
  no telemetry, no external evaluation, no automatic global indexing.
- Show the complete final configuration plan and get explicit confirmation BEFORE writing any file,
  enabling any network/credential access, or installing anything.
- After approval, execute the post-approval pipeline in the skill (manifest → lock → render →
  host files → docs → git → validation → registry) and report per-component results honestly:
  a component is "installed" only if its health check actually ran and passed. Report
  completed / failed / skipped / blocked separately.

If `$ARGUMENTS` contains a project name, use it as the proposed answer to the first interview
question (still confirm it).
