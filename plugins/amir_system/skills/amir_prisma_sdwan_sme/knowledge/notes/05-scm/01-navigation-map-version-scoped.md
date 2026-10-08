# Strata Cloud Manager (SCM) navigation for Prisma SD-WAN, scoped by generation and date

Domain: 5 | Applies to: Admin Guide May 2025 (SRC-000029), Incidents and Alerts guide Nov 2023 (WS-041), WS-024 `monitoring/scm-navigation-links.md` (Aug 2025 menu, recorded 2026-09-11/12), WS-030 Day 2 Operations draft §3.1 (checked against a live tenant 2026-09-11, SCM 2026.r2.3), WS-033 deck slides 406–434 | Status: DOCUMENTED with explicit verification levels | Last updated: 2026-10-08

## Explanation (plain words)

Prisma SD-WAN has had three user-interface generations and the written sources mix them. The **stand-alone portal** (CloudGenix lineage) used top menus **Manage / Workflows / Monitor**. The first SCM integration kept those words inside SCM (`Workflows > Prisma SD-WAN Setup > …`, `Manage > Prisma SD-WAN > …`) and added **Configuration > Prisma SD-WAN > …** paths. The **August 2025 navigation update ("Nav 3.0")** reorganised SCM into **Insights / Incidents / Reports / Log Viewer / Configuration / System Settings**: everything that was Monitor or Dashboards is now under Insights, Incidents & Alerts became Incidents, and Workflows and Manage became Configuration. The May 2025 Administrator's Guide predates that update, so a skill must never quote its menu paths as current without a date.

## Path counts in the May 2025 Administrator's Guide (evidence of the mixed generation)

| Top-level word | Occurrences | Example |
|---|---|---|
| Manage > | 128 | `Manage > Policies > Security > Security Stacks` |
| Workflows > | 112 | `Workflows > Prisma SD-WAN Setup > Devices > Claimed Devices` |
| Monitor > | 18 | `Monitor > ION Devices > Device Activity` |
| Configuration > | 9 | `Configuration > Prisma SD-WAN > Policies > NAT > NAT Stacks > Simple` |
| System Settings > | 2 | `System Settings > Identity & Access Management` |
| Insights > | 2 | `Insights > Prisma SD-WAN > Branch Sites > Flows` |
| Incidents & Alerts > | 1 | `Incidents & Alerts > Prisma SD-WAN > Incidents` |

The guide itself says SASE customers land on the **Command Center** and reach the SD-WAN dashboard via `Insights > Prisma SASE > Prisma SD-WAN Dashboard` (p.30), while the same chapter still writes `Monitor > Sites`, `Monitor > Applications`, `Monitor > Predictive Analytics`, `Monitor > ION Devices > Device Activity Dashboard` (pp.34–45). Treat the guide's paths as **May 2025 wording**.

## Mapping table: May 2025 guide wording → August 2025 SCM navigation (WS-024 / WS-030)

| Function | Guide wording (May 2025) | Current menu (Aug 2025+, recorded 2026-09) | Verification |
|---|---|---|---|
| Tenant dashboard | Dashboard / `Insights > Prisma SASE > Prisma SD-WAN Dashboard` | `Insights > Prisma SASE > Prisma SD-WAN Dashboard` | inferred URL `/insights/operational/sdwan-dashboard` |
| Applications | `Monitor > Applications` | `Insights > Prisma SASE > Prisma SD-WAN Applications` | inferred |
| Branch sites map/list/activity/flows | `Monitor > Branch Sites`, `Monitor > Branch Sites > Prisma SD-WAN > Flows` | `Insights > Prisma SASE > Branch Sites` → Prisma SD-WAN tab → Map / List / Activity / Flows | **verified 2026-09-11** (`/insights/operational/sase-branch-sites/sdwan`) |
| Site Summary | `Monitor > Sites` → site | Branch Sites (Map/List) → site → Site Summary tab; also `Configuration > Prisma SD-WAN > Branch Sites` → site → Site Summary | inferred (`…/site/<site-id>`) |
| Data centers | `Monitor > Data Centers` | `Insights > Prisma SASE > Data Centers` | inferred |
| Device list / Device Activity | `Monitor > ION Devices > Device Activity`, `Manage > Devices > ION Devices` | `Insights > Prisma SASE > ION Devices` → Device List / Device Activity | inferred |
| Predictive Analytics | `Monitor > Predictive Analytics` | Prisma SD-WAN Dashboard → Predictive Analytics widget → View All | inferred |
| Link Quality | `Dashboard > Overall Link Quality` | Prisma SD-WAN Dashboard → Overall Link Quality → View All | inferred |
| Claimed / unclaimed devices, device configuration | `Workflows > Prisma SD-WAN Setup > Devices > Claimed Devices > Configure the device > …`, `Manage > Setup > Devices` | `Configuration > Prisma SD-WAN > ION Devices > Claimed / Unclaimed` → device → Configure the device → Interfaces / Routing / … | inferred (`/configuration/sdwan/devices/<device-id>/routing`) |
| Sites (configuration) | `Workflows > Sites`, `Workflows > Data Centers`, `Workflows > Prisma SD-WAN Setup > Branch Sites` | `Configuration > Prisma SD-WAN > Branch Sites` / `Data Centers` → site tabs Configuration / Site Summary / Overlay Connections / Experience (branch) / Overlay Prefix Filters (DC) | inferred |
| Policies (path, QoS, security, NAT, performance, bindings) | `Manage > Policies > …`, `Manage > Prisma SD-WAN > Policies > …` | `Configuration > Prisma SD-WAN > Policies` (sub-labels to confirm) | inferred; sub-labels unconfirmed |
| Resources (circuit categories, apps, groups, probes, profiles, templates, SASE connectivity) | `Manage > Resources > …` | `Configuration > Prisma SD-WAN > Resources` (label to confirm) | inferred |
| Incidents, alerts, incident policies | `Incidents & Alerts > Prisma SD-WAN > Incidents`, `Incidents & Alerts > Settings` | `Incidents > Prisma SD-WAN` → Overview / Incidents / Alerts / Settings; consolidated `Incidents > Incidents` → Summary / Notification Profiles / Settings / Informational Alerts | consolidated pages **verified 2026-09-12**; SD-WAN page redirected on an out-of-sync lab tenant |
| WAN Clarity Reports | Prisma SD-WAN Clarity Reports chapter | `Reports > WAN Clarity Reports` | inferred (not licensed on the test tenant) |
| Audit logs | `Manage > System > Audit Logs` | `System Settings > Audit Logs`; per site: Site Summary → Recent Site Audit Logs | inferred |
| Subscription usage | `Monitor > Subscription Usage` | `System Settings > Subscription Usage` | inferred |
| Users, roles, service accounts | `Manage > System > Access Management` (legacy) | `System Settings > Identity & Access Management` | inferred |
| Activity Insights (threat/URL/DNS from Branch Security) | — | `Insights > Activity Insights` → Prisma SD-WAN tabs (needs SLS) | inferred |
| Advanced SD-WAN configuration UI | — | direct URL `https://sase.paloaltonetworks.com/sdwan/manage/advanced` | documented (deployment guide, per WS-024) |

Observed variance (WS-024/WS-030, 2026-09-12): the Insights group holding the SD-WAN items is labelled **Prisma SASE** on most tenants and **Prisma Access** on at least one; children identical. `Insights > Prisma SASE > SASE Health` appeared in the Aug 2025 mapping but was not present on the customer tenant. Overlay status is read from the site's Overlay Connections tab (and the Experience tab with ADEM).

## How the skill should quote navigation

1. Give the function first, then the path with its date and source, e.g. "Device configuration: `Configuration > Prisma SD-WAN > ION Devices > Claimed` → device → Configure the device (SCM navigation of Aug 2025; the May 2025 Administrator's Guide writes `Workflows > Prisma SD-WAN Setup > Devices > Claimed Devices`)."
2. Mark URLs as inferred unless the row above says verified; never present an inferred deep link as certain.
3. When the user's tenant pre-dates the Nav 3.0 update or uses the stand-alone portal, fall back to the guide wording and say so.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Command Center default landing for SASE customers; Insights path to the SD-WAN dashboard | VERIFIED | DOC | SRC-000029 p.30 |
| Guide mixes Manage/Workflows/Monitor with Configuration/Insights paths (counts above) | VERIFIED (counted in extracted text) | DOC | SRC-000029 |
| Aug 2025 Nav 3.0 regrouping (Insights, Incidents, Reports, Log Viewer, Configuration, System Settings) | CORROBORATED (two internal notes citing the Live Community mapping PDF; PDF itself not in KB) | DOC | WS-024; WS-030 §3.1 |
| Branch Sites URL and consolidated Incidents URLs verified on a live tenant | UNVERIFIED by this project (owner-verified 2026-09-11/12; no lab access, D4) | DOC | WS-024 |
| All other deep links | INFERRED (routing pattern) | DOC | WS-024 |
| Insights group label variance; SASE Health absent | UNVERIFIED (owner observation on one tenant) | DOC | WS-024 verification notes |

## Open questions

- KG-046 (existing): keep both generations date-stamped; close only after a live click-test (D4).
- KG-103: the "SCM Nav 3.0 UI Mapping Preview" PDF (Live Community) is referenced but not stored in the KB; fetch under D2 so the before/after mapping is first-hand.
- KG-104: exact sub-labels under `Configuration > Prisma SD-WAN > Policies` and `> Resources` in the current SCM (WS-030 marks them "confirm").
