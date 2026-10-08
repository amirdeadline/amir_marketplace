# Portal SSO (SAML), SCM identities and service accounts, ION CLI access and the default account, TPM checks

Domain: 4 / 6 | Applies to: Admin Guide May 2025 pp. 335, 340, 688–691; WS-001 §Access and Authorization (May 2026); Confluence 223905802 (2024-08), 74187097 (2018, OBSOLETE procedure), 237599551 (2024-06), 78890355 (2019 PRD) | Status: DOCUMENTED (portal access); INTERNAL (TPM, legacy SAML) | Last updated: 2026-10-08

## Explanation (plain words)

Three different "logins" exist. **Portal users** sign in to Strata Cloud Manager (SCM) with a local Customer Support Portal account or through the company's **SAML identity provider**; their rights come from roles (see note 05). **Service accounts** are non-human identities created in SCM Identity and Access Management and used for API automation. **ION CLI users** are separate device accounts (toolkit users or TACACS+) and every ION ships with a default local account whose password is randomised at claim time. Underneath, each ION proves its identity to the controller with a certificate stored in its **TPM** chip; a failed or full TPM keeps the device offline.

## Documented facts (official)

- Roles can be system or custom and are "enabled for SSO through an enterprise IdP"; system roles map to IdP groups named `cloudgenix_tenant_*` (p.335–339). MSP accounts are regular users with extra `esp_*` roles and SSO; an IdP group name can be mapped to a custom role of the same name (p.688).
- SCM-migrated tenants manage identities in Common Services: `System Settings > Identity & Access Management > Access Management > Add Identity`, Identity Type **User** or **Service Account** (name, contact, description), then Assign Role per Apps & Services; a parent (MSP) tenant can add a user into a child tenant and the child's configured roles determine what can be assigned (p.691). The legacy SD-WAN user page only keeps the Auth Token IP Session Lock for API tokens (p.340).
- Common Services guide (WS-046): tenant hierarchy and identity-and-access inheritance; the activating user receives the **Superuser** role; multitenant operations need **Multitenant Superuser**.

## Internal guidance

- **WS-001 §Portal Access**: Chrome or Prisma Browser preferred; use SAML 2.0 with the enterprise IdP (Okta, PingID…) and MFA; role mapping from IdP groups to Prisma SD-WAN roles is mandatory before a federated user gets access; local accounts need a Customer Support Portal account.
- **Confluence 223905802 (TAC note, 2024)**: greenfield and TSG-migrated tenants enable SAML themselves in SCM (TAC no longer loads metadata); the IdP must send attributes `firstname`, `lastname`, `email`, and for IdP-driven role assignment **`accessPolicies`** (replaces the old `memberOf`), value format like `tenant_super@prn:<tenant_id>:cgx:::`; full role list at pan.dev "All roles"; escalation via DIT component `scm-settings`; SCM or CSP login problems go to an IT ticket. Non-migrated tenants with existing SAML still need TAC for metadata changes.
- **Confluence 74187097 (2018)**: legacy SAML setup through the internal `etna` tooling (`tenants.py create_idp/update_idp`, role-map keys/values, session timeout, auto-provision operators/roles) → **OBSOLETE** for current tenants; useful only to understand that role mapping and auto-provisioning existed in the legacy portal.
- **Confluence 78890355 (2019 PRD)**: controller as OAuth2 authorization server / SAML IdP for external CloudGenix services (support portal, ticketing) → historical design intent, UNVERIFIED.
- **WS-001 §CLI access**: device roles Monitor (dump/inspect/file), Read-Only (adds debug/search), Super (configure); default account **`elem-admin`** whose password becomes a random string at claim; rotate every 60–90 days; prefer the portal Device Toolkit (SSH over the TLS control connection, audited) over direct SSH; SSHv2 only, no Telnet; direct SSH is blocked on public-circuit IPs by default; CLI configuration is overwritten by the controller; TACACS+ from 6.5 with role attribute `super|readonly|monitor` (default read-only if absent) — WS-001 says local wins when a user exists in both stores (matches guide p.363, contradicts p.365; KG-096); Device Offline Access OTP for offline devices (see note 01-fundamentals/08).
- **Confluence 237599551 (TPM check, 2024)**: on legacy models (1000/2000/3000/7000/9000) `tpm_selftest` from the shell, or mrl_agent log "ENGINE load_private_key:failed loading private key"; on x200 models use **`cgtpmtool -l`** (no output = dead TPM); TPM key slots are limited (roughly 8–10); an ION that moves between tenants stores a new MIC per allocation and a **full TPM blocks claiming** (device stays offline); delete middle keys with `cgtpmtool -d -k <handle>`, never `0x81010005`, `0x81fffffe`, `0x81ffffff`; `debug controller reachability 1` shows "TPM command not responding"; kernel log `tpm_transmit: tpm_recv: error -5` means hardware failure → reboot, then RMA if repeated.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Roles SSO-enabled; IdP group names; MSP esp_* roles | VERIFIED | DOC | SRC-000029 pp.335–339, 688 |
| SCM Identity & Access: User vs Service Account identities, role assignment, child-tenant access | VERIFIED | DOC | SRC-000029 p.691; WS-046 |
| accessPolicies attribute format and self-service SAML in SCM | UNVERIFIED (internal TAC note; points to official Common Services docs not in KB) | DOC | Confluence 223905802 |
| elem-admin default account, password randomised at claim, role command scopes, public-IP SSH blocked | UNVERIFIED (internal, strong) | DOC | WS-001 §CLI access |
| TPM diagnostics and key-slot limit | UNVERIFIED (internal KB article) | DOC | Confluence 237599551 |
| Legacy etna SAML procedure | OBSOLETE | DOC | Confluence 74187097 |

## Open questions

- KG-102: official Common Services "Identity and Access" documentation (role list, accessPolicies format, service-account creation and client-secret handling) is not in the KB; fetch under D2 for B15 (API authentication) and to close KG-097.
- KG-066b (from note 05): `elem-admin` default account is internal-only so far; look for it in the CLI reference or activation guide.
