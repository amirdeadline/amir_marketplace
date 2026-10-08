# SDKs and automation tooling: prisma-sase SDK, legacy cloudgenix SDK, cloudgenix_config, Terraform provider

Domain: 6 | Applies to: prisma-sase SDK 6.6.2b1 (WS-012 source; SRC-000052–056 derived docs), legacy cloudgenix SDK 6.6.2b1 (SRC-000057), cloudgenix_config 1.9.0b2 (SRC-000058; last release notes Jan 2023), Terraform provider prismasdwan 6.6.1-beta.3 (WS-013, retrieved 2026-08-29), pan.dev pages WS-011 | Status: DOCUMENTED (official code, rank 4) | Last updated: 2026-10-08

## Explanation (plain words)

Palo Alto Networks publishes two Python SDKs with the same method surface: **`prisma-sase`** for the unified SASE API (service accounts, TSG scope) and **`cloudgenix`** for the legacy API (email/password or static token). The SDK version tracks the controller release (6.6.2 = February 2026 controller). **`cloudgenix_config`** is a YAML export/import utility built on the legacy SDK (pull a site, edit, push; create or destroy whole sites). The **Terraform provider `prismasdwan`** covers about 115 resources through the unified API and is community-supported. Every SDK method maps one-to-one to a REST endpoint and accepts an `api_version` override.

## prisma-sase SDK (official source WS-012; derived docs SRC-000053/054)

- Install `pip install prisma-sase`; Python 3.7+; outbound HTTPS to `api.sase.paloaltonetworks.com` and `auth.apps.paloaltonetworks.com`. Package: `get_api.py` 305 GET, `post_api.py` 369 POST, `put_api.py` 156 PUT, `patch_api.py` 3 PATCH, `delete_api.py` 134 DELETE, `interactive.py`, `ws_api.py` (2 WebSocket methods: toolkit session) = **969 methods**; pinned CA bundle; retry adapter (default 8 retries, ~0.7 s backoff, tunable with `modify_rest_retry`).
- Login: `sdk.interactive.login_secret(client_id, client_secret, tsg_id)` performs the OAuth client-credentials exchange, sets the Bearer header, calls `GET /sdwan/v2.1/api/profile` then `GET /sdwan/v2.12/api/tenants`, and derives `X-PANW-Region` from the telemetry region for monitor calls; JWT auto-refresh when within **60 s** of expiry (`_refresh_jwt`). Interactive `login()` handles SAML browser flow, region redirect and MSP (`is_esp`) client selection (`client_login` / `client_logout`; static tokens cannot switch clients). QA environments use a different OAuth URL (`sase_qa_env`).
- Responses are extended `requests.Response` objects: `sdk_status` (True on 200/201/204 with valid JSON), `sdk_content`, `sdk_errors` (from `_error`), `sdk_warnings`; errors inside a 200 body still set `sdk_errors`. Helpers `extract_items`, `build_lookup_dict`, `jd/jdout`, `set_debug(1–3)`.
- Pitfalls listed by the SDK docs: always check `sdk_status`; POST/PUT take dict payloads; use `*_query` POST for large tenants; monitor calls need the region header; IAM calls use `{controller}/iam/v1/service_accounts` and `/iam/v1/access_policies`.

## Legacy cloudgenix SDK (SRC-000057)

Same structure for `https://api.elcapitan.cloudgenix.com` (default controller; region redirect on login); `interactive.login(email, password)` or `interactive.use_token(token)`; the pan.dev SDK page still documents `pip install cloudgenix` and token creation under `System Administration > Auth Tokens` (legacy portal). Version table maps SDK builds to controller releases from 4.6.1 (Mar 2018) to 6.6.2b1 (Feb 2026); 6.5.2b4 added the DigiCert CA.

## cloudgenix_config (SRC-000058; pan.dev prismasdwanconfig.md)

- `pull_site -S <site|ALL_SITES> [--output|--multi-output DIR] [--leave-implicit-ids] [--strip-versions] [--force-parents] [--normalize]` exports site configuration to YAML; `do_site <file> [--destroy] [--force-update] [--site-safety-factor N] [--timeout-offline|claim|upgrade|state] [--wait-upgrade] [--interval-timeout 10–180]` applies it (create/update/destroy site, circuits, LAN networks, elements, interfaces, routing, NTP …), waiting for claim/assign/upgrade state changes. Uses the **legacy `cloudgenix` SDK** and `cloudgenix_settings.py` (auth token or email/password); no `prisma_sase` or TSG support in the code. Last release notes 1.9.0b2 (2023-01-26): SDK 6.1.x support, hub cluster YAML, elements v3.0 / interfaces v4.14. Use cases: ION replacement by swapping `serial_number`, config in Git with CI, rollback, templates for many sites. Its unassign loop retries on etag mismatch every 10 s up to 600 s (WS-020).

## Terraform provider prismasdwan (WS-013)

Separate from the `scm` and `panos` providers; same OAuth service-account pattern (`client_id`, `client_secret`, `scope = "tsg_id:<TSG_ID>"`, optional `host`, `auth_url`, `auth_file`; env vars `SCM_CLIENT_ID`, `SCM_CLIENT_SECRET`, `SCM_SCOPE`, `SCM_HOST`); **115 resources, 1 data source**, including `prismasdwan_site`, `_element`, `_element_interface`, `_element_bgp_peer`, `_element_static_route`, `_path_policy_rule/_set/_stack`, `_qos_policy_*`, `_nat_policy_*`, `_security_policy_*`, `_performance_policy_*`, `_probe_config/_profile`, `_ipsec_profile`, `_event_correlation_policy_*`, `_sdwanapps_config`, `_element_toolkit`; `prismasdwan_resource_locator` looks up existing objects by property. Pinned version example 6.6.1-beta.3; support is best-effort for the provider.

## Choosing a tool (INFERRED from the above)

New automation on SCM tenants: unified API via `prisma-sase` or Terraform with a service account. Existing `cloudgenix_config` pipelines: still work through legacy tokens on migrated tenants, but the login endpoint is deprecated and the tool's last release predates 6.3+ features (VRF, performance policy stacks, SASE connections), so coverage gaps must be expected. Never embed email/password in automation.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| SDK method counts, package layout, login sequence, 60-s JWT refresh, X-PANW-Region | VERIFIED (official source code) | DOC | WS-012; SRC-000054 |
| Response attributes and helpers | VERIFIED | DOC | WS-012; SRC-000053 |
| Legacy SDK default controller and version/controller mapping | VERIFIED | DOC | SRC-000057 README, `__init__.py` |
| cloudgenix_config CLI options, use cases, legacy-SDK dependency, last release 1.9.0b2 | VERIFIED | DOC | SRC-000058; WS-011 prismasdwanconfig.md |
| Terraform provider auth, 115 resources, best-effort support | VERIFIED (upstream docs clone) | DOC | WS-013 |
| Coverage gap of cloudgenix_config for post-2023 features | INFERRED | — | release-notes dates vs feature chronology |

## Open questions

- KG-111: whether a maintained successor to `cloudgenix_config` exists for the unified API (the KB's own exporter project is internal); check pan.dev / GitHub under D2.
