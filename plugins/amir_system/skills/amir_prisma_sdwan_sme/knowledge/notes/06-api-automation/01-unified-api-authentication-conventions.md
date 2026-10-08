# Prisma SD-WAN APIs: unified (SASE) vs legacy, authentication, request conventions

Domain: 6 | Applies to: unified OpenAPI bundle SRC-000046 (6.6.2, bundled 2026-07-05, rank 2), legacy bundle SRC-000047, pan.dev pages WS-011, SRC-000036 (older best-practices PDF, §Tenant Access Using APIs), Admin Guide p.340–341, SDK docs SRC-000053/054 (6.6.2b1) | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

There are two API front doors to the same controller. The **unified SASE API** (`https://api.sase.paloaltonetworks.com/sdwan/v{x.y}/api/...`) uses a **service account** created in Strata Cloud Manager: client ID and secret are exchanged for a short-lived **JWT bearer token** scoped to a **TSG**. The **legacy CloudGenix API** (`https://api.<region>.cloudgenix.com/v{x.y}/api/tenants/{tenant_id}/...`) uses an **auth token** (static token from the portal, or a login call) in the `x-auth-token` header. Resources, version numbers and error codes are the same in both; only the prefix, host and authentication differ. Tenants migrated to SCM can still use legacy tokens but the login endpoint is slated for deprecation.

## Documented facts

- **Two API sets** (pan.dev WS-011): unified APIs integrate with the other SASE APIs and became available **2022-06-06**; legacy APIs are identical to the pre-unified offering and use login-issued tokens. Legacy base URL `https://api.<region>.cloudgenix.com:443`; the login response may carry `api_endpoint` for the tenant's region; static tokens are created under `System > Access Management > Site Access > Auth Tokens` (legacy portal). Legacy versions in the bundle match the unified ones (v2.0 … v4.21).
- **Unified authentication** (OpenAPI `00 - Authentication`, SDK docs, SRC-000036): `POST https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token`, HTTP Basic with client_id:client_secret, form fields `grant_type=client_credentials` and `scope=tsg_id:{TSG_ID} email profile`; token lifetime about **15 minutes** (SRC-000036 says 15 minutes; the OpenAPI note says "~15 minutes"); then **`GET /sdwan/v2.1/api/profile` is mandatory** before any other SD-WAN call, otherwise subsequent calls return **403** (pan.dev api/home.md). The SDK additionally calls `GET /sdwan/v2.12/api/tenants` to learn the telemetry region.
- **Service account creation**: SCM `System Settings > Identity & Access Management > Add Identity > Service Account` (Admin Guide p.691; Terraform docs WS-013 and SRC-000036 agree), assign the Prisma SD-WAN app role; the secret is shown once.
- **Legacy tokens and IP Session Lock** (Admin Guide p.341; SRC-000036): user profiles have IP Session Lock enabled by default and tokens inherit it, so a token used from another IP is rejected; disable it (or set an IP/prefix allow list) before creating tokens for VMs or shared automation. Migrated tenants manage this at `Manage > Prisma SD-WAN > Access Management > Tenant Access > Auth Token Session Lock` and create tokens under `… > Tenant Access > Auth Tokens`. "Do not use username/password authentication for automation"; the login API endpoint "will be deprecated after migration to Strata Cloud Manager".
- **Monitor APIs** live under `/sdwan/monitor/v{x}/api/monitor/...` (28 families, e.g. `metrics`, `aggregates`, `sys_metrics`, `flows`, `aiops`, `topn`, `lqm_point_metrics`, `app_acceleration`); the SDK adds an **`X-PANW-Region`** header for them from the tenant telemetry region (SDK source; not declared as a parameter in the OpenAPI bundle).
- **Request/response conventions** (OpenAPI schemas; WS-020 §02): every persisted object carries `id`, `_etag`, `_schema`, `_created_on_utc`, `_updated_on_utc`; **PUT requires the current `_etag`** (stale → `400 INVALID_JSON_COMMON_ATTR_MISMATCH`); error envelope `{"_error":[{"code","message"}]}` (several codes at once); list GETs return `{count, items[]}`; **`POST …/query`** (207 endpoints) accepts `BaseQueryDTO` (`query_params`, `limit`, `dest_page`, `next_query`, `total_count`, `retrieved_fields`, `getDeleted`, `sort_params`, `aggregate`, `group_by`) and is the preferred tenant-wide discovery; response codes are almost always 200 or 400 (1 × 202, 1 × 203); DELETE returns the deleted object and a repeat DELETE returns `*_NOT_FOUND`.
- **Per-resource versions are independent**: 924 paths spread over v2.0 (561) … v4.21; both versions of a resource stay live (WS-020 §02). The SDK pins a default `api_version` per method and lets callers override it.
- Bundle shape: 1,509 operations, 1,528 schemas, 40 tags (largest: System Administration 186, Routing 126, Security Policy 119, Device Configuration 102, Site Configuration 92, Metrics 70, Path/QoS Policy 54 each, Multicast 50, Performance Management 49, Event Policy 48, NAT Policy 48, IPFIX 46, Cellular 43, Applications 41).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Unified vs legacy API sets; 2022-06-06; legacy token header and base URL | VERIFIED (rank 1 pan.dev) | DOC | WS-011 sdwan.md, legacy_getstarted.md |
| Mandatory GET profile after token, else 403 | VERIFIED | DOC | WS-011 api/home.md; OpenAPI description |
| OAuth endpoint, Basic auth, scope format, ~15-minute JWT | VERIFIED (OpenAPI rank 2) / CORROBORATED (SRC-000036 "15 minutes") | DOC | SRC-000046; SRC-000036 §Tenant Access |
| IP Session Lock inheritance and menu paths | VERIFIED | DOC | SRC-000029 p.341; SRC-000036 |
| Login endpoint deprecation after SCM migration | CORROBORATED-grade (SRC-000036 undated) | DOC | SRC-000036 |
| X-PANW-Region header on monitor calls | VERIFIED in SDK source (rank 4); not in OpenAPI | DOC | WS-012 `prisma_sase/__init__.py` lines 1132–1141 |
| Envelope, etag, query DTO, response-code distribution | VERIFIED (bundle inspection) | DOC | SRC-000046 components; WS-020 §02 |

## Open questions

- KG-107: official statement of access-token lifetime and refresh guidance (pan.dev "access tokens" page referenced but not in the KB; fetch under D2).
- KG-108: official documentation of the `X-PANW-Region` requirement and the telemetry-region mapping for monitor APIs.
- KG-109: date and scope of the legacy login-API deprecation for migrated tenants.
