# GitLab MCP Server — Reference

> Standalone reference for the **gitlab** MCP server exposed through the Palo Alto
> **mcp-gateway** aggregator. Aligns with the consolidated gateway doc
> `Z:\Palo\LiteLLM\.ai\docs\mcp_gw.md` (see §5.1 there). Where the two conflict on
> tool naming or risk classification, this file is the per-server detail.

---

## 1. Overview

The gitlab server wraps the GitLab REST API and lets an agent inspect and operate a
GitLab instance without leaving the gateway. It covers:

- **Projects** — list/search projects (personal, group, membership) and read project metadata.
- **Repository files & commits** — read file contents and directory trees at any ref,
  create/update single files, push multiple files in one commit, and list/read commits and diffs.
- **Branches** — create branches from a source ref.
- **Issues** — list/search issues, list issues assigned to the caller, read one issue,
  create and update issues.
- **Issue links & notes** — link issues together (relates/blocks), and read/create/update
  issue discussion notes.
- **Labels** — list/read/create/update project labels.
- **Merge requests** — list/read MRs, create/update MRs, read diffs and versions, and read
  the approval state.
- **MR notes, discussions & draft notes** — list/read/create/update/delete MR notes and
  threaded discussion notes, create threads, resolve threads, and manage draft (pending
  review) notes.
- **Pipelines & jobs** — list/read pipelines, retry/cancel pipelines, list/read jobs, read
  job logs (trace), and play/retry/cancel jobs plus list trigger (bridge) jobs.

Most tools accept `project_id` as either the **numeric project ID** or the
**URL-encoded `group/project` path** (e.g. `mygroup%2Fmyproject`). Some list tools make
`project_id` optional and fall back to `GITLAB_PROJECT_ID` or to all accessible projects.

---

## 2. How to call it

Through the gateway, every tool is addressed with the aggregated name:

```
mcp__mcp-gateway__gitlab__<tool>
```

The server segment (`gitlab`) is fixed and uses underscores like the rest of the name.
**Bare tool names (e.g. `list_projects`) are rejected** — always use the full
`mcp__mcp-gateway__gitlab__<tool>` form.

Examples:

```jsonc
// List projects the current user is a member of
mcp__mcp-gateway__gitlab__list_projects
{ "membership": true, "per_page": 20 }

// Read a file at a specific branch/tag/commit
mcp__mcp-gateway__gitlab__get_file_contents
{ "project_id": "mygroup%2Fmyproject", "file_path": "README.md", "ref": "main" }

// Get the log tail of a CI job
mcp__mcp-gateway__gitlab__get_pipeline_job_output
{ "project_id": "1234", "job_id": "99887", "limit": 200 }
```

---

## 3. Authentication

- **Credential:** a **GitLab token** brokered by the gateway. It is referenced **by name
  only** — never print, log, or invent the value.
- **Session model:** the gateway uses a session/handshake auth flow. On a fresh session the
  status may report `is_authenticated: false` / `auth_status.state: not_started` until the
  **first call** performs the handshake; subsequent calls reuse the session. A first call
  reporting an auth transition is expected, not an error.
- **Scope of the token** determines what you can see/do; read tools that span "all accessible
  projects" only return what the token is authorized for.

**Project rule (D-042) — binding:** the official product git is **`SDWAN_LAB`** / GitLab
**`prisma-sdwan-lab`**. Do **not** add files, push, or commit there, and keep **no AI scratch**
in that repo, unless the work is fully tested and the **owner explicitly asked**. Terraform
state lives in GCS (`sase-lab-sdwan-tfstate`), not git.

---

## 4. Environment / configuration

| Variable | Effect |
|---|---|
| `GITLAB_PROJECT_ID` | Default project used when a tool's `project_id` is optional. `my_issues` and other list tools accept it as the implicit project scope so `project_id` can be omitted. |

Notes on optional-scope tools:

- `list_issues` — `project_id` optional; if omitted, lists issues across all accessible
  projects. Defaults to issues created by the current user unless `scope: "all"`.
- `list_merge_requests` — `project_id` optional; if omitted, lists MRs the user has access to
  (defaults to MRs assigned to the caller; use `scope: "all"` for all accessible).
- `my_issues` — `project_id` optional when `GITLAB_PROJECT_ID` is set.

---

## 5. Complete tool catalog (61 tools)

Risk legend: **RO** = read-only · **WRITE** = changes state (approval-gated) ·
**DESTRUCTIVE** = deletes data. Per the classification rule, `create_*` / `update_*` /
`push_*` / `cancel_*` / `retry_*` / `play_*` / `resolve_*` are WRITE; `delete_*` is DESTRUCTIVE.

### 5.1 Projects (3)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__list_projects` | List projects accessible to the current user | — | `search`, `membership`, `owned`, `visibility`, `order_by`, `sort`, `page`, `per_page`, `simple`, `archived` | RO |
| `mcp__mcp-gateway__gitlab__list_group_projects` | List projects in a group (with filtering) | `group_id` | `include_subgroups`, `search`, `with_*_enabled`, `min_access_level`, `order_by`, `sort`, `page`, `per_page`, `visibility` | RO |
| `mcp__mcp-gateway__gitlab__get_project` | Get details of one project | `project_id` | — | RO |

### 5.2 Repository files & commits (7)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__get_file_contents` | Read a file or directory from the repo | `file_path` | `project_id`, `ref` | RO |
| `mcp__mcp-gateway__gitlab__get_repository_tree` | List files/dirs in the repo tree | `project_id` | `path`, `ref`, `recursive`, `per_page`, `page_token`, `pagination` | RO |
| `mcp__mcp-gateway__gitlab__create_or_update_file` | Create/update a single file in one commit | `file_path`, `content`, `commit_message`, `branch` | `project_id`, `previous_path`, `last_commit_id`, `commit_id` | **WRITE** |
| `mcp__mcp-gateway__gitlab__push_files` | Commit multiple files in a single commit | `branch`, `files[]`, `commit_message` | `project_id` | **WRITE** |
| `mcp__mcp-gateway__gitlab__list_commits` | List repository commits (filterable) | `project_id` | `ref_name`, `since`, `until`, `path`, `author`, `all`, `with_stats`, `first_parent`, `order`, `trailers`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__get_commit` | Get details of one commit | `sha` | `project_id`, `stats` | RO |
| `mcp__mcp-gateway__gitlab__get_commit_diff` | Get the diff/changes of one commit | `sha` | `project_id`, `full_diff` | RO |

### 5.3 Branches (1)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__create_branch` | Create a new branch | `branch` | `project_id`, `ref` (source) | **WRITE** |

### 5.4 Issues (5)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__list_issues` | List issues (project or cross-project) | — | `project_id`, `scope`, `state`, `labels`, `assignee_*`, `author_*`, `milestone`, `search`, `created_*`, `updated_*`, `issue_type`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__my_issues` | Issues assigned to the caller (defaults open) | — | `project_id` (opt w/ `GITLAB_PROJECT_ID`), `state`, `labels`, `milestone`, `search`, `created_*`, `updated_*`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__get_issue` | Get one issue's details | `project_id`, `issue_iid` | — | RO |
| `mcp__mcp-gateway__gitlab__create_issue` | Create an issue | `title` | `project_id`, `description`, `assignee_ids`, `labels`, `milestone_id`, `issue_type` | **WRITE** |
| `mcp__mcp-gateway__gitlab__update_issue` | Update an issue | `issue_type` | `project_id`, `issue_iid`, `title`, `description`, `labels`, `assignee_ids`, `state_event` (close/reopen), `milestone_id`, `due_date`, `weight`, `confidential`, `discussion_locked` | **WRITE** |

### 5.5 Issue links & notes (7)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__list_issue_discussions` | List discussions on an issue | `issue_iid` | `project_id`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__list_issue_links` | List links for an issue | `issue_iid` | `project_id` | RO |
| `mcp__mcp-gateway__gitlab__get_issue_link` | Get one issue link | `issue_iid`, `issue_link_id` | `project_id` | RO |
| `mcp__mcp-gateway__gitlab__create_issue_link` | Link two issues | `issue_iid`, `target_issue_iid` | `project_id`, `target_project_id`, `link_type` (relates_to/blocks/is_blocked_by) | **WRITE** |
| `mcp__mcp-gateway__gitlab__create_issue_note` | Add a note to an issue thread | `body` | `project_id`, `issue_iid`, `discussion_id`, `created_at` | **WRITE** |
| `mcp__mcp-gateway__gitlab__update_issue_note` | Edit an issue thread note | `body` (per schema) | `project_id`, `issue_iid`, `discussion_id`, `note_id`, `resolved` | **WRITE** |
| `mcp__mcp-gateway__gitlab__create_note` | Add a comment to an issue or MR | `noteable_type` (issue/merge_request), `body` | `project_id`, `noteable_iid` | **WRITE** |

### 5.6 Labels (4)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__list_labels` | List labels in a project | — | `project_id`, `search`, `with_counts`, `include_ancestor_groups` | RO |
| `mcp__mcp-gateway__gitlab__get_label` | Get one label | — | `project_id`, `label_id`, `include_ancestor_groups` | RO |
| `mcp__mcp-gateway__gitlab__create_label` | Create a label | `name`, `color` | `project_id`, `description`, `priority` | **WRITE** |
| `mcp__mcp-gateway__gitlab__update_label` | Update a label | — | `project_id`, `label_id`, `new_name`, `color`, `description`, `priority` | **WRITE** |

### 5.7 Merge requests (9)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__list_merge_requests` | List MRs (project or user-scoped) | — | `project_id`, `scope`, `state`, `labels`, `milestone`, `author_*`, `assignee_*`, `reviewer_*`, `source_branch`, `target_branch`, `search`, `order_by`, `sort`, `wip`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__get_merge_request` | Get one MR (by iid or source branch) | — | `project_id`, `merge_request_iid`, `source_branch` | RO |
| `mcp__mcp-gateway__gitlab__create_merge_request` | Create an MR | `title`, `source_branch`, `target_branch` | `project_id`, `description`, `draft`, `labels`, `assignee_ids`, `reviewer_ids`, `target_project_id`, `remove_source_branch`, `squash`, `allow_collaboration` | **WRITE** |
| `mcp__mcp-gateway__gitlab__update_merge_request` | Update an MR | — | `project_id`, `merge_request_iid`, `source_branch`, `title`, `description`, `target_branch`, `labels`, `assignee_ids`, `reviewer_ids`, `state_event` (close/reopen), `draft`, `squash`, `remove_source_branch` | **WRITE** |
| `mcp__mcp-gateway__gitlab__get_merge_request_diffs` | Get MR changes/diffs | — | `project_id`, `merge_request_iid`, `source_branch`, `view`, `excluded_file_patterns` | RO |
| `mcp__mcp-gateway__gitlab__list_merge_request_diffs` | List MR diffs (paginated) | — | `project_id`, `merge_request_iid`, `source_branch`, `page`, `per_page`, `unidiff` | RO |
| `mcp__mcp-gateway__gitlab__get_merge_request_version` | Get one MR diff version | `version_id` | `project_id`, `merge_request_iid`, `unidiff` | RO |
| `mcp__mcp-gateway__gitlab__list_merge_request_versions` | List MR diff versions | — | `project_id`, `merge_request_iid` | RO |
| `mcp__mcp-gateway__gitlab__get_merge_request_approval_state` | Get MR approval rules/approvers | — | `project_id`, `merge_request_iid` | RO |

### 5.8 MR notes, discussions & draft notes (14)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__mr_discussions` | List discussion items on an MR | — | `project_id`, `merge_request_iid`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__get_merge_request_note` | Get one MR note | — | `project_id`, `merge_request_iid`, `note_id` | RO |
| `mcp__mcp-gateway__gitlab__get_merge_request_notes` | List MR notes | — | `project_id`, `merge_request_iid`, `order_by`, `sort`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__create_merge_request_note` | Add a note to an MR | `body` | `project_id`, `merge_request_iid` | **WRITE** |
| `mcp__mcp-gateway__gitlab__update_merge_request_note` | Edit an MR note | `body` | `project_id`, `merge_request_iid`, `note_id` | **WRITE** |
| `mcp__mcp-gateway__gitlab__create_merge_request_thread` | Start a new thread on an MR (optionally on a diff position) | `body` | `project_id`, `merge_request_iid`, `position`, `created_at` | **WRITE** |
| `mcp__mcp-gateway__gitlab__create_merge_request_discussion_note` | Reply into an existing MR thread | `body` | `project_id`, `merge_request_iid`, `discussion_id`, `created_at` | **WRITE** |
| `mcp__mcp-gateway__gitlab__update_merge_request_discussion_note` | Edit / resolve a discussion note | — | `project_id`, `merge_request_iid`, `discussion_id`, `note_id`, `body`, `resolved` | **WRITE** |
| `mcp__mcp-gateway__gitlab__delete_merge_request_discussion_note` | Delete a discussion note | — | `project_id`, `merge_request_iid`, `discussion_id`, `note_id` | **DESTRUCTIVE** |
| `mcp__mcp-gateway__gitlab__resolve_merge_request_thread` | Resolve/unresolve a thread | `resolved` | `project_id`, `merge_request_iid`, `discussion_id` | **WRITE** |
| `mcp__mcp-gateway__gitlab__list_draft_notes` | List draft (pending) notes on an MR | — | `project_id`, `merge_request_iid` | RO |
| `mcp__mcp-gateway__gitlab__get_draft_note` | Get one draft note | — | `project_id`, `merge_request_iid`, `draft_note_id` | RO |
| `mcp__mcp-gateway__gitlab__create_draft_note` | Create a draft review note | `body` | `project_id`, `merge_request_iid`, `position`, `in_reply_to_discussion_id`, `resolve_discussion` | **WRITE** |
| `mcp__mcp-gateway__gitlab__update_draft_note` | Update a draft note | — | `project_id`, `merge_request_iid`, `draft_note_id`, `body`, `position`, `resolve_discussion` | **WRITE** |

### 5.9 Pipelines & jobs (11)

| Tool (callable) | Purpose | Required params | Notable optional | Risk |
|---|---|---|---|---|
| `mcp__mcp-gateway__gitlab__list_pipelines` | List pipelines (filterable) | — | `project_id`, `scope`, `status`, `ref`, `sha`, `username`, `updated_*`, `order_by`, `sort`, `yaml_errors`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__get_pipeline` | Get one pipeline | — | `project_id`, `pipeline_id` | RO |
| `mcp__mcp-gateway__gitlab__retry_pipeline` | Retry a failed/canceled pipeline | — | `project_id`, `pipeline_id` | **WRITE** |
| `mcp__mcp-gateway__gitlab__cancel_pipeline` | Cancel a running pipeline | — | `project_id`, `pipeline_id` | **WRITE** |
| `mcp__mcp-gateway__gitlab__list_pipeline_jobs` | List jobs in a pipeline | — | `project_id`, `pipeline_id`, `scope`, `include_retried`, `page`, `per_page` | RO |
| `mcp__mcp-gateway__gitlab__get_pipeline_job` | Get one job's details | — | `project_id`, `job_id`, `limit`, `offset` | RO |
| `mcp__mcp-gateway__gitlab__get_pipeline_job_output` | Get a job's log/trace (paginated) | — | `project_id`, `job_id`, `limit`, `offset` | RO |
| `mcp__mcp-gateway__gitlab__play_pipeline_job` | Run a manual job | — | `project_id`, `job_id`, `job_variables_attributes` | **WRITE** |
| `mcp__mcp-gateway__gitlab__retry_pipeline_job` | Retry a failed/canceled job | — | `project_id`, `job_id` | **WRITE** |
| `mcp__mcp-gateway__gitlab__cancel_pipeline_job` | Cancel a running job | — | `project_id`, `job_id`, `force` | **WRITE** |
| `mcp__mcp-gateway__gitlab__list_pipeline_trigger_jobs` | List trigger/bridge jobs (downstream pipelines) | — | `project_id`, `pipeline_id`, `scope`, `page`, `per_page` | RO |

**Catalog summary:** 61 tools — 38 read-only, 22 WRITE, 1 DESTRUCTIVE
(`delete_merge_request_discussion_note`).

---

## 6. Common recipes

| I want to… | Tool | Minimal args |
|---|---|---|
| See merge requests assigned to me | `mcp__mcp-gateway__gitlab__list_merge_requests` | `{ "scope": "assigned_to_me", "state": "opened" }` |
| See issues assigned to me | `mcp__mcp-gateway__gitlab__my_issues` | `{ }` (uses `GITLAB_PROJECT_ID`) |
| Read a file at a branch/tag/commit | `mcp__mcp-gateway__gitlab__get_file_contents` | `{ "project_id": "grp%2Fproj", "file_path": "path/to/f", "ref": "main" }` |
| Browse the repo tree | `mcp__mcp-gateway__gitlab__get_repository_tree` | `{ "project_id": "1234", "path": "src", "ref": "main", "recursive": true }` |
| List jobs of a pipeline | `mcp__mcp-gateway__gitlab__list_pipeline_jobs` | `{ "project_id": "1234", "pipeline_id": "555" }` |
| Read a job's log | `mcp__mcp-gateway__gitlab__get_pipeline_job_output` | `{ "project_id": "1234", "job_id": "99887", "limit": 200 }` |
| See why an MR isn't merging (approvals) | `mcp__mcp-gateway__gitlab__get_merge_request_approval_state` | `{ "project_id": "1234", "merge_request_iid": "42" }` |
| Read the diff of an MR | `mcp__mcp-gateway__gitlab__get_merge_request_diffs` | `{ "project_id": "1234", "merge_request_iid": "42" }` |
| Create an issue *(WRITE — approval-gated)* | `mcp__mcp-gateway__gitlab__create_issue` | `{ "project_id": "1234", "title": "…" }` |
| Create a working branch *(WRITE)* | `mcp__mcp-gateway__gitlab__create_branch` | `{ "project_id": "1234", "branch": "agent/topic", "ref": "main" }` |

---

## 7. Guardrails

- **Reads are safe; writes are approval-gated.** All `create_*` / `update_*` / `push_*` /
  `cancel_*` / `retry_*` / `play_*` / `resolve_*` tools change GitLab state and require
  **explicit owner approval** before use. `delete_merge_request_discussion_note` is
  destructive — treat with extra care.
- **Branch discipline.** Do work on `agent/<topic>` branches. **Never commit to `main`**
  and never merge without an explicit "merge it" from the owner.
- **Official product repo (D-042).** `SDWAN_LAB` / GitLab `prisma-sdwan-lab` accepts no
  unapproved files, commits, or AI scratch. Only push there when fully tested and asked.
- **Secrets by name only.** Never print, log, or invent the GitLab token or any secret value.
- **Naming.** Always call tools as `mcp__mcp-gateway__gitlab__<tool>`; bare names are rejected.
- **`project_id`.** Pass the numeric ID or the URL-encoded `group/project` path
  (`%2F` for the slash). Rely on `GITLAB_PROJECT_ID` only where a tool marks `project_id` optional.
