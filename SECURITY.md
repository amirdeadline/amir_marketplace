# Security Model — amir-marketplace 1.0.0

This marketplace ships exactly two plugins, both surfacing commands under `/amir:`:

- **amir_system** (user scope) — project creation/onboarding/orchestration, Graphify wrappers, Asana MCP, Playwright MCP, system rules, deterministic tooling (`amirctl`).
- **amir_project** (project scope) — component groups enabled only via a project's `.amir/project.yaml`. Never auto-enabled.

## Secrets

- No secret values live in this repository, in project manifests, or in generated files — ever.
- Credentials are referenced by environment-variable NAME only. Machine-local values belong in
  `%USERPROFILE%\.amir\secrets\*.env` (e.g. `asana.env` → `ASANA_ACCESS_TOKEN`).
- Authoritative per-component credential names: `catalog/catalog.json` (`required_credentials`).
  Key examples: `ASANA_ACCESS_TOKEN`; `ELASTIC_BASE_URL`/`ELASTIC_AUTH_HEADER`; `SPLUNK_BASE_URL`/`SPLUNK_TOKEN`;
  `QRADAR_BASE_URL`/`QRADAR_SEC_TOKEN`; `PANOS_HOST`/`PANOS_API_KEY`; `XDR_API_KEY`/`XDR_API_KEY_ID`/`XDR_FQDN`;
  `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` (litellm); `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`/`LANGFUSE_HOST`;
  `CONTEXT7_API_KEY` (optional).
- A pre-push secrets scan (`plugins/amir_project/tools/secrets_scan.js` + pattern sweep) gates every release.

## Permission model

System-scope availability never equals project authorization. Every project-facing command checks
`.amir/project.yaml` first (component gate). Activation is refused when a dependency, executable,
credential, host, or permission requirement is unmet (`amirctl` resolver — see
`schemas/component-metadata.schema.json`). Network and secret access default to **deny** per project.
Destructive actions (delete/replace/force-reset/push/publish/external writes incl. Asana writes)
require explicit confirmation — see `plugins/amir_system/rules/destructive-action.mdc` and the other
six system rules in `plugins/amir_system/rules/`.

## Supply chain

Official sources and package identity are recorded per component in `catalog/catalog.json`
(`official_source`). Verify identity before installing anything (worked example: PyPI `graphifyy`
was verified against the Graphify-Labs/graphify repository redirect before use; unaffiliated
`graphify*` packages exist). Pin versions in `.amir/components.lock.json` (per-file SHA256).

Full model: `%USERPROFILE%\.amir\docs\security-model.md`.
