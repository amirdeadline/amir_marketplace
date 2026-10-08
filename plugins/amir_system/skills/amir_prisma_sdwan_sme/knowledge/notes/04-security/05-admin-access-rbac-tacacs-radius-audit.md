# Administrative access: RBAC and roles, device toolkit users, 802.1X/MAC on switch ports, audit logs, TACACS+

Domain: 4 / 6 | Applies to: Admin Guide May 2025 pp. 333–367 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Who may do what splits into four layers. **Tenant RBAC** governs the web UI and API (system roles, custom roles). For SCM-migrated tenants, users live in the TSG and are managed in Common Services Identity and Access; the legacy page only edits the API IP session lock. **Device toolkit users** govern CLI/SSH access to IONs, optionally via **TACACS+**. **802.1X/MAC authentication** governs end devices on ION 1200-S switch ports via RADIUS. **Audit logs** record every configuration change and login attempt.

## Documented facts (official)

- **System roles** (pp.337–339; IdP group names in parentheses): Root `cloudgenix_tenant_root` (single fallback account), Super Administrator `cloudgenix_tenant_super`, IAM Administrator `cloudgenix_tenant_iam_admin`, Network Administrator `cloudgenix_tenant_network_admin` (sites, devices, interfaces, network policies, custom apps, prefix filters, BGP, SNMP/Syslog/DNS/IPFIX; no security), Security Administrator `cloudgenix_tenant_security_admin` (zones, security rules, bindings; no network), View-only `cloudgenix_tenant_viewonly`. Permissions are API call sets; **custom roles** combine roles plus or minus permissions; a disallowed permission overrides an allowed one; Root cannot be a base; roles in use cannot be deleted; make sure GET permissions exist or UI workflows fail (pp.343–345).
- **Users** (pp.340–341): migrated tenants use SCM Identity and Access; the legacy page `Manage > Prisma SD-WAN > System > Access Management > Tenant Access > Auth Token Session Lock` is the only remaining control. Stand-alone tenants: `Manage > System > Access Management > User Access > User Management > Add User` with Access toggle (default disabled), roles, **IP Session Lock** (default enabled; auth tokens bound to the source IP; disable for tokens used from several systems), IP/Prefix Access List.
- **Device toolkit users** (p.347): roles Super (read/write), Read Only, Monitor; tenant-level (max **10**) or device-level (any number, but only **40** device-level users can be assigned devices); unlimited devices per user.
- **802.1X / MAC authentication** (pp.350–356): from **6.0.2**; closed mode and single-host only; all ports of the ION 1200-S L2 switch; up to **two RADIUS servers** per device (priority 1–255, lower wins; ports 1812/1813; shared secret 8–64 chars; global source interface) configured under `Claimed Devices > Configure the Device > AAA`; RADIUS AVPs: dynamic VLAN (RFC 3580 Tunnel-Type=VLAN(13), Tunnel-Medium-Type=802, Tunnel-Private-Group-ID; the VLAN must pre-exist as an SVI or an incident is raised and the port stays unauthorized), Termination-Action / Session-Timeout re-authentication, Idle-Timeout (0 or absent = static never-ages client; non-zero = dynamic entry aged by the global switch timer, AVP value discarded). Monitoring under AAA > Stats, Auth Clients and device charts.
- **Audit logs** (pp.358–361): filter by time (at least 6 months back), site, device, type; login attempts per user/IP; **auto-expire after two years, last two actions per resource kept forever**; visible to ROOT, SUPER, IAM ADMIN or custom roles with GET+POST on the audit log resource; regex queries; version compare (rewind/fast-forward); CSV export; filter fields Resource Key/ID/Type/Status/Ver, URI Ver, URI, Session Key, Source IP, Operator ID, dates; status 400 records show bad requests.
- **TACACS+** (pp.363–366): AAA profile with up to **four servers** tried sequentially; protocol CHAP or PAP; IPv4/IPv6/FQDN; server response time up to 10 s; associate the profile to a device under `Manage > Setup > Devices > AAA` with a source interface and optional customized values. Allowed usernames: alphanumeric, underscore, hyphen. Accounting records; critical alert if no server accepts accounting. **Conflict inside the guide**: p.363 says that when a user exists in both TACACS+ and the local database **local** authentication is used; p.365 says **AAA server** authentication is used. p.365 lists local fallback when all four servers are unreachable, for the offline-device user menu, when the user is absent from TACACS+, or when the user exists only locally.
- CLI names: `dump auth config|status`, `dump radius config|statistics|status`, `dump device accessconfig`, `clear device account login`, `inspect switch mac address table`, `config banner`.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| System role names and responsibilities; custom-role rules | VERIFIED | DOC | SRC-000029 pp.337–345 |
| SCM-migrated tenants manage users in Common Services; session-lock page only | VERIFIED | DOC | SRC-000029 p.340 |
| IP Session Lock semantics | VERIFIED | DOC | SRC-000029 p.341 |
| Toolkit user limits 10 tenant-level / 40 device-level assignable | VERIFIED | DOC | SRC-000029 p.347 |
| 802.1X/MAC from 6.0.2 on ION 1200-S; two RADIUS servers; AVP handling | VERIFIED | DOC | SRC-000029 pp.350–356 |
| Audit log retention (2 years; last two actions forever) and access roles | VERIFIED | DOC | SRC-000029 p.358 |
| TACACS+ four servers, CHAP/PAP, 10 s, fallback conditions | VERIFIED | DOC | SRC-000029 pp.363–365 |
| Precedence when a user exists in both TACACS+ and the local DB | CONFLICTED (guide p.363 vs p.365) | DOC | SRC-000029 |

## Open questions

- KG-096: TACACS+ vs local precedence (the guide contradicts itself).
- KG-097: Common Services role mapping for Prisma SD-WAN in SCM (which SCM roles map to the legacy cloudgenix_* roles); check the Common Services guide in B13/B14.
