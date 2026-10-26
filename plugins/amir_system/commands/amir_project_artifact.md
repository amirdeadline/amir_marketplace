---
description: Create, adopt or refresh this project's tracker artifact (Overview, Plan, Tasks, Questions, Mind map, Logs) and install the agent rules and Stop hook that keep it current
argument-hint: "[optional title] [optional existing artifact URL to adopt]"
---

# /amir:amir_project_artifact

Follow the skill at `skills/amir_project_artifact/SKILL.md` in this plugin (also installed at
user scope as `/amir_project_artifact` for Cursor and Claude Code).

Apply it now to the current project with `$ARGUMENTS`: check `install.py --status` first, so a
project never gets a second tracker; install or refresh; publish the page with the Artifact tool;
record the URL with `--url`; seed or update the database from the project's files; read it back
before reporting.
