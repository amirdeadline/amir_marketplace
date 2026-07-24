# amir — security rules

Guardrails for secrets, production assets, approvals, and mandatory scanning.

## Never without explicit human approval

Agents **must not** edit, create, or commit:

| Category | Examples |
|----------|----------|
| **Secrets / credentials** | `.env`, API keys, tokens, private keys, connection strings with passwords |
| **Production configs** | Prod kube manifests, prod TF workspace, live DNS, prod CI deploy targets |
| **Deployment pipelines** | Release workflows that push to prod, store credentials, or alter infra |
| **Generated secrets output** | Files produced by secret generators intended for secure stores only |
| **Destructive migrations** | Irreversible data drops, column deletes without backup plan, prod DB migrations |

Read-only inspection of redacted samples is allowed; copying secrets into chat or notes is **forbidden**.

## Protected files — PROBLEM then wait

If a task requires modifying a **protected** path:

1. Emit **PROBLEM** with path and reason
2. List safe alternative (env example, stub, feature flag off)
3. **Wait** for human approval recorded in `decisions.json`
4. Do not proceed with edit until approved

Protected patterns include (project may extend via `.ai/state/security.json` if present):

- `**/.env`, `**/.env.*` (except `.env.example`)
- `**/credentials*`, `**/*secret*`, `**/*token*` (case-insensitive, sensible globs)
- `**/prod/**`, `**/production/**` deploy configs
- Cloud provider identity files

## Ignored paths — not source of truth

Paths listed in `.gitignore`, host ignore lists, or `adapters/*/capabilities.md` degrade paths:

- **Not** authoritative for architecture or requirements
- **Not** evidence for VERIFIED claims unless explicitly generated into tracked artifacts
- Scanning may skip ignored paths — document **Impact** in security review

Do not "fix" security by adding sensitive paths to gitignore to hide them from scan.

## secrets_scan — mandatory gate

**secrets_scan** is mandatory before:

| Command / gate | Requirement |
|----------------|-------------|
| `/git_commit` | Scan clean or documented false-positive approval |
| `/security_scan` | Full scan report archived to workspace |
| Task touching auth, crypto, PII | `4-security` review + scan |

Run via project tools (`tools/secrets_scan` or host wrapper). Outcomes:

| Result | Action |
|--------|--------|
| **Clean** | Proceed |
| **Findings** | **FAIL** QA; remove secrets; rotate if leaked; never commit |
| **NOT RUN** | **BLOCKED** for commit; log Reason/Impact per `core/honesty-rules.md` |

## Approval gates

Work **stops** until human approval in `decisions.json` for:

| Gate | Trigger |
|------|---------|
| **Architecture** | New service boundary, database choice, major dependency |
| **Security** | Auth model change, new external data flow, crypto algorithm |
| **Breaking API** | Public API, CLI contract, event schema breaking consumers |
| **Remote device** | SSH, production shell, device farm, customer environment access |
| **Destructive ops** | Data delete, force push, prod rollback, infra destroy |

Orchestrator sets `status.json` gate flags; worker must not bypass.

## Agent responsibilities

| Agent | Security role |
|-------|----------------|
| `4-security` | Threat review, scan interpretation, gate sign-off |
| `qa-<task-id>` | Verify security acceptance criteria; FAIL if scan skipped |
| `1-orchestrator` | Enforce gates before `complete` |
| `dev-<task-id>` | No secrets in code; use env examples; least privilege |

## Safe defaults

- Use `.env.example` with placeholder values
- Mock external services in tests
- Feature flags default **off** for risky paths
- Log redaction for PII

## Cross-references

| Topic | File |
|-------|------|
| Honesty NOT RUN | `core/honesty-rules.md` |
| QA FAIL/BLOCKED | `core/qa-loop.md` |
| Drift / forbidden fixes | `core/no-drift-rules.md` |
| Workspace layout | `core/workspace-rules.md` |

Skills and agents must say **"Follow `core/security-rules.md`"** — do not restate these rules elsewhere.
