---
name: amir_project_artifact
description: >-
  Use when the user invokes /amir_project_artifact or /amir:amir_project_artifact, or asks to create, set up,
  adopt, refresh or update the project tracker, project manager artifact or project dashboard for the current
  project: "make a project artifact", "track this project in an artifact", "set up the project tracker",
  "update the project artifact". Creates one private claude.ai Artifact per project with Overview, Plan, Tasks,
  Questions, Mind map and Logs tabs on a shared database, task details with edit, cancel and a per-task side
  chat, and installs rules plus a Stop hook so every agent in the project keeps it current.
argument-hint: "[optional title] [optional existing artifact URL to adopt]"
---

# Project tracker artifact

One tracker page per project, kept current by every agent that works in it. The page is the user's view and
input surface; the artifact's database is the record; Claude is the bridge to the project's files, because the
page itself cannot read the local disk.

## 1. Skill folder

`<skill_dir>` is the folder holding this file. Claude Code: `${CLAUDE_SKILL_DIR}`. Fallback:
`~/.claude/skills/amir_project_artifact`.

- `assets/tracker.html` - the page template. Generic; never rewrite it per project.
- `scripts/install.py` - installs or refreshes the tracker in a project (page copy, config, rules, Stop hook).
- `scripts/stop_hook.py` - the Stop hook the installer registers.

## 2. What the page gives the user

| Tab | What it shows | What the user can do |
|---|---|---|
| Overview | Status block (overall, stage, last updated, tasks done, open questions, blockers), process map, summary, what is needed from the user, key project files, decisions log | Read |
| Plan | Milestones in order with goal, dates, exit criteria, progress bar and their tasks; a timeline when milestones have dates | Open any task |
| Tasks | Filterable table with status icons | Open a task drawer: details, linked questions, linked logs; Edit; Cancel with a reason; Reopen; New task; side chat with Claude about that task; Copy for Claude Code |
| Questions | Every question with status, answer, dates, what it unblocks | Answer in place, set Answered or Follow up |
| Mind map | Tree of process phases, plan, milestones, tasks, open questions by group, decisions, blockers | Open and close branches, zoom, open a task, jump to a question |
| Logs | Every decision, change, question, finding and action, with files touched and task id | Search, filter by type and date |

Status icons, fixed forever: Done ✅, Failed ❌, Not started ⬜, In progress 🔄, Blocked ⛔, Cancelled 🚫. Use the
same icons in chat replies.

Every edit made in the page also writes a `logs` row, so Claude sees what the user changed.

## 3. First use in a project

1. Check for an existing tracker: `python -I "<skill_dir>/scripts/install.py" --project "<root>" --status`.
   If it prints a `url`, this project already has one: go to section 4. One artifact per project, always.
2. Install: `python -I "<skill_dir>/scripts/install.py" --project "<root>" --title "<Short Name>" --subtitle "<one line>"`.
   It writes `.claude/project_artifact/tracker.html`, `.claude/project_artifact.json`, the rules section in
   `CLAUDE.md`, and the Stop hook in `.claude/settings.json`. It never touches anything outside its own markers
   and its own hook entry.
3. Load the `artifact-capabilities` skill if this session has not, then publish with the Artifact tool:
   - `file_path`: `<root>/.claude/project_artifact/tracker.html`
   - `capabilities`: `{"db": {}, "user": {}, "sample": {}}` (`sample` powers the per-task side chat; leave it
     out only if the user does not want the page to call Claude)
   - `icon`: `checklist` on the first publish only; `description`: one sentence.
4. Record the URL: re-run `install.py --project "<root>" --url "<artifact url>"`. This also writes the URL into
   the `CLAUDE.md` rules so every agent finds it.
5. Seed the database (section 5) from the project itself: read the README, `PROJECT.md`, `.ai/`, `CLAUDE.md`,
   plans, TODO lists and recent git history. Write `meta/project` (with `project_path`, `artifact_url` and
   `key_files`), `plan` milestones, `tasks` with a `milestone` each, open `questions`, and one `logs` row that
   says what was seeded from which files. Never invent dates, owners or numbers: leave them blank and raise a
   question. Use one `batch` per collection (50 writes per batch at most).
6. Verify: read back `meta/project` and one page of `tasks`. Tell the user in one line what was checked.
7. Give the user the URL and say the page is private until they share it.

## 4. Adopt or refresh an existing tracker

- Tracker made by hand earlier in this project: run `install.py --url "<existing url>"`, then read the artifact
  (`action: "read"`) before any publish, then republish the project page to that `url` so it runs the current
  template. The database is kept across republishes; add missing fields (section 5) with `update`.
- Template upgraded in the skill: re-run `install.py` (no `--url`) to refresh the page copy, then republish to
  the `url`. Omit `capabilities` on a republish unless they change; a non-empty `capabilities` replaces the
  whole set.

## 5. Data contract

| Collection | Document id | Fields |
|---|---|---|
| `meta` | `project` | `project_name`, `subtitle`, `project_path`, `artifact_url`, `overall_status`, `current_stage`, `last_updated` (YYYY-MM-DD), `blockers` [text], `summary` [text, about 5], `needed` [text], `phases` [{`id`, `name`, `status`, `summary`}], `key_files` [{`path`, `purpose`}] |
| `plan` | `M1`, `M2`, ... | `id`, `name`, `order` (number), `goal`, `start`, `end` (YYYY-MM-DD or blank), `status`, `exit` |
| `tasks` | `T-01`, ... | `id`, `task`, `stage`, `milestone` (a plan id), `owner`, `status`, `due`, `notes`, `description`, `done_when`, `depends_on`, `files`, `cancel_reason`, `updated_on` |
| `questions` | `Q-01`, ... | `id`, `group`, `question`, `why`, `asked_on`, `status` (Not answered, Answered, Follow up), `answer`, `answered_on`, `unblocks` |
| `logs` | `L-<n>` | `ts` (YYYY-MM-DD HH:MM), `type` (decision, change, question, finding, action), `summary`, `detail`, `files`, `task` (optional task id) |
| `chats` | the task's document id | `task`, `messages` [{`role`, `text`, `ts`}], the last 30 kept |

A question or log links to a task when its text names the task id (`T-03`) or its `task` field holds it. A
decision is a `logs` row of type `decision`: `summary` is the decision, `detail` is why.

## 6. Rules for every agent, and the Stop hook

The installer writes the rules into `CLAUDE.md` between `<!-- amir_project_artifact:start -->` and
`<!-- amir_project_artifact:end -->`, so the main agent and every subagent load them. In short: write the changed
rows at the end of every turn that changed anything; read before overwriting and pin `if_version`; never re-ask
an answered question; never mark Done without saying how it was verified; cancel, never delete; subagents
without `ArtifactData` hand their rows to the parent in a "Tracker update" section.

The Stop hook (`scripts/stop_hook.py`) reads the session transcript. If the turn used a working tool (edit,
write, shell, subagent, a question to the user) and made no `ArtifactData` write, it blocks the stop once with a
reason naming the tracker URL. It never blocks twice in a row, never blocks in a project without
`.claude/project_artifact.json`, never blocks a read-only turn, and lets the stop through on any error. It is
registered for the main agent only: subagent types such as Explore have no `ArtifactData` tool, so a
SubagentStop hook would trap them; rule 5 covers subagents instead.

## 7. Things to know

- **The page cannot read the project's files.** Claude reads them and writes rows; `key_files` and the `files`
  field of logs and tasks are how the page points back at the project.
- **Side chat spends the viewer's own Claude usage** and asks consent on first use. It sees only that task, its
  linked questions and logs, and the project summary. Copy for Claude Code hands the task to a real session.
- **Edits are last-writer-wins.** Claude pins `if_version`; the page writes plain updates and logs each one.
- **Private by default.** Only the owner can open the link until they share it from the page's Share menu.
- **Never create a second tracker for a project.** Publishing without `url` creates a new artifact and the data
  stays with the old one. The installer refuses a second URL.
