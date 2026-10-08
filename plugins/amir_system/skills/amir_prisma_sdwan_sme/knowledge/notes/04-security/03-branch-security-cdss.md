# Branch Security: Cloud-Delivered Security Services on the ION (Security Profile Groups, SLS logging)

Domain: 4 | Applies to: Admin Guide May 2025 pp. 570–577; WS-001 §Branch Security; internal PRDs 407968262, 825491997 | Status: DOCUMENTED with a version-floor CONFLICT | Last updated: 2026-10-08

## Explanation (plain words)

Branch Security adds PAN-OS style threat inspection to the ION itself: Anti-Spyware, Vulnerability Protection, DNS Security and URL Access Management, bundled into a **Security Profile Group** that is attached to a ZBFW rule. Profiles are built in Strata Cloud Manager (SCM) under the Global scope, pushed to Prisma SD-WAN, grouped, then referenced by security rules. Threat, URL and DNS logs can go to Strata Logging Service (SLS) or to syslog. It is a separate subscription.

## Documented facts (official pp. 570–577)

- Requires SCM, a Prisma Access license and the **Branch Security license**; an SLS license is needed to log to SLS. "Branch security capabilities are officially supported starting with the **6.5.1-I** release" (p.570).
- Supported services: Anti-Spyware (Inline Cloud Analysis not supported), Vulnerability Protection, DNS Security, URL Access Management (Advanced URL Inline Categorization and EDLs not supported).
- Workflow: `Manage > NGFW and Prisma Access`, Configuration Scope **Global**, Security Services profiles, **Push** Global config with Prisma SD-WAN as target, check sync status on the overview, then `Manage > Prisma SD-WAN > Policies > Security > Security Profile Groups > Add Profile Group`, then attach the group to a security policy rule in a set bound to the site. A default best-practice group is created automatically; a group in use cannot be deleted; only groups, never individual profiles, attach to rules.
- Logging: SLS for sites with a SASE Site license or standalone devices with an SLS license; logs in `Incidents & Alerts > Log Viewer` (Traffic under Network > Prisma SD-WAN Traffic; Threat, URL, DNS under Network); connection status for Cloud Security Services and Logging Service by hovering Device State under `Workflows > Prisma SD-WAN Setup > Devices > Claimed Devices`; Syslog Profiles (`Manage > Resources > Configuration Profiles > Syslog`) with Threat/DNS/URL checkboxes; Flow Browser filter **Session End Reason** and per-flow threat ID/category/severity/action, URL category, DNS security details.

## Internal (WS-001 §Branch Security; PRDs)

- WS-001 states support "starting with ION device software release **6.5.3-I**", which **conflicts** with the guide's 6.5.1-I. Add path policy rules for `pan-db-cloud` and `paloalto-dns-security` above the default rule, allowed on all paths, or enforcement fails silently. Verify Cloud Security Services and Logging Service connection status on Claimed Devices.
- PRD 407968262 (target 6.6.1, April 2025): SD-WAN traffic and security records to SLS, Log Viewer correlation, Activity Insights pages, Command Center scope "Prisma SD-WAN"; motivation is the "ML7" security engine. PRD 825491997 (May 2026): maintenance release for **threat/appdef content compilation failures** (state stuck Pending, duplicate triggers), commit failures, licensing issues and **Thermite certificate** issues; rule: appdef version must stay at or below the threat version; customer cases include CIE group mapping not reaching the ION and ION-to-SLS connectivity.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Licenses, supported/unsupported services, SCM Global-scope workflow, profile-group-only attachment | VERIFIED | DOC | SRC-000029 pp.570–574 |
| Logging destinations and Flow Browser fields | VERIFIED | DOC | SRC-000029 pp.574–577 |
| Release floor 6.5.1-I (guide) vs 6.5.3-I (WS-001) | CONFLICTED | DOC | SRC-000029 p.570; WS-001 |
| Path rules for pan-db-cloud / paloalto-dns-security | UNVERIFIED (internal, strong) | DOC | WS-001 |
| Content compilation / Thermite certificate failure modes | UNVERIFIED (internal engineering PRD) | DOC | Confluence 825491997 |

## Open questions

- KG-094: which release first supports Branch Security (6.5.1-I vs 6.5.3-I) and whether "-I" images are a distinct image train; the extracted 6.5 release notes contain no "branch security" entry; check public docs under D2.
- KG-095: platform support and throughput impact of Branch Security per ION model (not in the guide).

## Addendum 2026-10-08 (public pages cached under D2; see 03_SOURCE_CATALOG.md §J)

- The 6.8 release notes (PUB-008, VERIFIED) state that Branch Security "requires a subscription license and is supported starting with the release 6.5.3-I", and that SLS logging needs an SLS licence. This agrees with WS-001 and contradicts admin guide p.570 (6.5.1-I). Recommend 6.5.3-I as the floor; record the admin-guide value as the older official statement (KG-094).
