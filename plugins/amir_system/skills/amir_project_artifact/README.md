# amir_project_artifact

Claude Code skill that gives a project **one private claude.ai tracker artifact**, kept current by every
agent that works in the project.

```
/amir_project_artifact                         # set up, or refresh, this project's tracker
/amir_project_artifact "Short Name"            # with a title
/amir_project_artifact <artifact url>          # adopt a tracker made earlier
```

The page has six tabs on the artifact's shared database: Overview, Plan, Tasks, Questions, Mind map and Logs.
A task opens a side panel with details, linked questions and logs, Edit, Cancel with a reason, Reopen, a side
chat with Claude about that task, and Copy for Claude Code.

Layout:

| Path | Role |
|---|---|
| `SKILL.md` | the skill: setup, adopt, data contract, agent rules |
| `assets/tracker.html` | the page template (generic; title filled per project) |
| `scripts/install.py` | per project: page copy, `.claude/project_artifact.json`, `CLAUDE.md` rules, Stop hook in `.claude/settings.json`; idempotent; refuses a second URL |
| `scripts/stop_hook.py` | blocks a working turn once when the tracker was not written; never loops; passes on any error |

One real copy lives here; `scripts\install-user-skills.ps1 -Skills amir_project_artifact` creates the
junctions in `%USERPROFILE%\.claude\skills` and `%USERPROFILE%\.cursor\skills`.

Requires: Python 3 on PATH for the installer and the hook, and a claude.ai account for the artifact.
