# S05 — API automation: idempotent site build-out and safe teardown order

Domains: 6 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

An operations team must create 25 branch sites per month from a CSV (site, address, two circuits, LAN prefix, device serial) on an SCM-managed tenant (controller 6.6.x), using a service account, and must also be able to decommission a site cleanly. They ask for the call sequence, how to make it re-runnable, and why their first teardown script failed with `DELETE_FORBIDDEN_SITE_WAN_EXISTS` and `SITE_WAN_INTERFACE_ID_EXISTS`.

## 2. Question

Design the automation flow against the unified API; explain idempotency and the teardown order.

## 3. Reasoning chain

1. **Authentication.** Service account (SCM `System Settings > Identity & Access Management > Add Identity > Service Account`, SD-WAN role) → `POST https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token` (Basic client_id:secret; `grant_type=client_credentials`, `scope=tsg_id:{TSG} email profile`) → JWT ≈15 min → **mandatory `GET /sdwan/v2.1/api/profile`** or every call returns 403. The `prisma-sase` SDK does this in `login_secret()` and refreshes the JWT 60 s before expiry. [VERIFIED — 06-api-automation/01 (WS-011, SRC-000046), 06-api-automation/03 (WS-012)]
2. **Scopes.** Tenant objects (WAN networks, circuit labels, policy stacks, zones) → site objects (`/sites/{id}`: `waninterfaces` = circuits, `lannetworks`, `dhcpservers`, `spokeclusters`) → element objects (`…/elements/{id}`: interfaces, static routes, BGP). Build in that order; tear down in reverse. [VERIFIED — 06-api-automation/02 (SRC-000046; WS-020 §02)]
3. **Idempotency.** Discover before create with `POST …/query` (`BaseQueryDTO`) by name/serial; update with PUT carrying the current `_etag` (stale → `INVALID_JSON_COMMON_ATTR_MISMATCH`: re-GET and retry); treat `*_NOT_FOUND` on DELETE as success; never key on `id` from a previous run. [VERIFIED — 06-api-automation/01–02]
4. **Build order (per site).** (a) ensure tenant prerequisites exist (WAN networks v2.1, circuit labels, policy stacks); (b) `POST sites` (v4.13; admin_state disabled until ready); (c) `POST sites/{id}/waninterfaces` (v2.10) one per circuit with label, network, speeds; (d) `POST lannetworks`, `dhcpservers`; (e) claim the machine (`machines/{id}/operations` inventory_op CLAIM) and poll `machine_state` → MACHINE_CLAIMED; (f) assign the element (`PUT elements/{id}` with `site_id`) and poll `state` ACTIVE_BOUND_IN_PROGRESS → ACTIVE_BOUND_TO_SITE; (g) element interfaces (v4.21: `used_for`, `site_wan_interface_ids`, IP config, scope Global on LAN), static routes, BGP; (h) bind stacks (site PUT fields for path/qos/security/nat stacks) and zones (`securityzones` bindings); (i) switch admin_state to active (control mode) and verify `elements/{id}/status` `config_and_events_connected` and VPN status. A 200 means persisted on the controller, not programmed on the device: poll the GET. [VERIFIED (bundle versions, enums) and CORROBORATED (polling targets) — 06-api-automation/02 (WS-020 §18)]
5. **Why the teardown failed.** The site delete is refused while circuits exist (`DELETE_FORBIDDEN_SITE_WAN_EXISTS`), and a circuit cannot be deleted while an interface still references it; unassigning an element fails while any interface carries a circuit label (`SITE_WAN_INTERFACE_ID_EXISTS`). Other blockers: `DELETE_FORBIDDEN_ELEMENT_OR_ELEMENT_SHELL_EXISTS`, `DELETE_FORBIDDEN_SITE_WAN_LQM_CONFIG_EXISTS` (another site's circuit lists this site in `lqm_config.hub_site_ids`), `SITE_CONFIG_DELETE_NOTALLOWED_SERVICEENDPOINT_EXISTS`, `DELETE_FORBIDDEN_INVALID_STATE` (disable the site first), `ENABLED_CIRCUITS_NOT_REMOVED` (SASE connection), `WAN_INTERFACE_CONFIG_IN_ZONE`, `LANNETWORK_IS_USED_IN_SECURITY_ZONES`. [CORROBORATED — 06-api-automation/02 (WS-020 §17 from the bundle's 400 examples)]
6. **Safe teardown order.** Disable the site (admin_state) → delete the Prisma Access connection (`prismasase_connections`) and wait for circuits to be released → remove zone bindings and NAT/zone references → clear routing children (BGP peers, static routes) → reset interfaces (remove `site_wan_interface_ids`, used_for) → unassign the element (`PUT` site_id='1', poll ACTIVE_UNBOUND_IN_PROGRESS → ACTIVE_READY; `cloudgenix_config` retries etag mismatches every 10 s up to 600 s here) → delete spoke cluster, DHCP servers, LAN networks → delete circuits (`waninterfaces`) → remove this site from other sites' `lqm_config.hub_site_ids` if present → delete the site. Declaim only if the hardware leaves the tenant (`operations` declaim → element 404). [CORROBORATED — WS-020 §17–18; VERIFIED for operations enums]
7. **Tooling choice.** `prisma-sase` SDK or Terraform `prismasdwan` (115 resources, service-account auth) for SCM tenants; `cloudgenix_config` only through legacy tokens and without post-2023 features (VRF, SASE connections). Never embed email/password. [VERIFIED for tool facts; INFERRED for the recommendation — 06-api-automation/03]

## 4. Answer

Authenticate with a service account and call `GET /sdwan/v2.1/api/profile` first; build tenant → site → circuits → claim/assign → element children → bindings → activate, polling the state enums after every asynchronous step; make it re-runnable by querying by name/serial, PUT-ing with fresh `_etag`s and treating NOT_FOUND deletes as success. Tear down strictly in reverse, releasing every referrer (SASE connection, zones, interface circuit labels, LQM hub references) before deleting circuits and the site; the two errors seen are exactly the referrer checks for circuits and for interfaces still bound to circuit labels.

## 5. What to check / collect next

`GET elements/{id}` state, `GET machines/{id}` machine_state, `GET elements/{id}/status`, `POST elements/bulk_config_state/query`; dependency error codes from `_error[]`; SDK `sdk_status`/`sdk_errors`. [VERIFIED — 06-api-automation/01–03]

## 6. Gaps exposed

KG-044 (state casing), KG-107 (token lifetime page), KG-110 (exhaustive error catalog), KG-111 (unified-API successor to cloudgenix_config). New: **KG-139** — official field list for binding policy stacks and zones per site/element in the unified API (which object carries the stack IDs; which endpoint binds zones) — currently inferred from the export model, not from a documented procedure.

## 7. Validation status

**SCENARIO VALIDATED** for authentication, conventions and the dependency reasoning (VERIFIED/CORROBORATED); the exact binding endpoints are PARTIAL (KG-139).
