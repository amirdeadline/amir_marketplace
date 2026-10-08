# S14 — "Where is it in SCM?" across the three UI generations

Domains: 5 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Three users ask in one week: (a) "the admin guide says `Workflows > Prisma SD-WAN Setup > Devices > Claimed Devices` but I don't have Workflows"; (b) "where do I see a site's VPN status and flows?"; (c) "where are incident policies and audit logs now?" Their tenants: one migrated to SCM in 2025, one on an older SCM look, one MSP child.

## 2. Question

Answer each with a dated path and the right confidence.

## 3. Reasoning chain

1. **Three generations.** Stand-alone portal (Manage / Workflows / Monitor); early SCM (`Workflows > Prisma SD-WAN Setup > …`, `Manage > Prisma SD-WAN > …`, some `Configuration > Prisma SD-WAN > …`); Nav 3.0 from August 2025 (Insights / Incidents / Reports / Log Viewer / Configuration / System Settings). The May 2025 Administrator's Guide mixes the first two; the deployment/solution guides of Oct 2025 use `Configuration > …` paths. [VERIFIED for the guide's mixed wording and the Command Center landing — 05-scm/01 (SRC-000029 p.30 + counts); CORROBORATED for the Nav 3.0 regrouping — WS-024/WS-030]
2. **(a) Claimed devices / device configuration.** Current: `Configuration > Prisma SD-WAN > ION Devices > Claimed / Unclaimed` → device → Configure the device (Oct 2025 deployment guide writes `Configuration > ION Devices`); May 2025 guide: `Workflows > Prisma SD-WAN Setup > Devices > Claimed Devices`. Confidence: deployment-guide path VERIFIED for Oct 2025; deep link inferred. [VERIFIED — 10-design/02 (SRC-000037 pp.28–29); INFERRED deep link — 05-scm/01]
3. **(b) Site VPN status and flows.** Current: `Insights > Prisma SASE > Branch Sites` → Prisma SD-WAN tab → Map / List / Activity / Flows (URL verified 2026-09-11 by the KB owner, not by this project); site → Overlay Connections tab for VPN/standard-VPN peers (`Configuration > Prisma SD-WAN > Branch Sites > site > Overlay Connections`, Oct 2025 guide); May 2025 guide: `Monitor > Branch Sites`, `Monitor > Branch Sites > Prisma SD-WAN > Flows`. Note the Insights group may be labelled Prisma Access on some tenants. [VERIFIED for Overlay Connections — SRC-000037 p.79; UNVERIFIED by this project for the live URL (owner-verified) — 05-scm/01]
4. **(c) Incident policies and audit logs.** Current: `Incidents > Prisma SD-WAN` → Overview / Incidents / Alerts / Settings (incident policies under Settings), consolidated `Incidents > Incidents` (verified 2026-09-12 by the owner); audit logs `System Settings > Audit Logs` and per site in Site Summary → Recent Site Audit Logs; May 2025 wording `Incidents & Alerts > Prisma SD-WAN > Incidents`, `Manage > System > Audit Logs`. [CORROBORATED/INFERRED — 05-scm/01; incident-policy fields VERIFIED — 07-operations/01]
5. **MSP child tenant.** Same SCM paths inside the child after switching tenant; the multitenant pages (`Manage > Devices`, `Manage > Services`, dashboards) live in the Strata Multitenant Cloud Manager, not in the child's SCM. [VERIFIED — 10-design/04 (SRC-000044 pp.9, 79–92)]
6. **How to phrase.** Function first, then path with date and source; mark inferred links; fall back to guide wording for pre-Nav-3.0 tenants. [VERIFIED method — 05-scm/01 §How the skill should quote navigation]

## 4. Answer

Tell (a) that Workflows became Configuration in the August 2025 navigation update: use `Configuration > Prisma SD-WAN > ION Devices > Claimed` → device → Configure the device. Tell (b) to open `Insights > Prisma SASE > Branch Sites`, Prisma SD-WAN tab, pick the site for Activity/Flows, and the site's Overlay Connections tab for VPN peers. Tell (c) incident policies are under `Incidents > Prisma SD-WAN > Settings` and audit logs under `System Settings > Audit Logs` (per-site logs in Site Summary). Add that these are the August 2025 menus; tenants on the older SCM still show Workflows/Manage/Monitor, and only the Branch Sites and consolidated Incidents URLs were click-verified (by the KB owner, 2026-09).

## 5. What to check / collect next

Ask which menu root the user sees (Workflows vs Configuration) to date their UI; confirm the Insights group label; use the advanced SD-WAN UI link from the deployment guide when a page is missing. [05-scm/01]

## 6. Gaps exposed

KG-046, KG-103 (Nav 3.0 mapping PDF), KG-104 (sub-labels under Configuration > Prisma SD-WAN > Policies/Resources).

## 7. Validation status

**SCENARIO PARTIAL** — generation model and Oct 2025 guide paths are VERIFIED; most current deep links are inferred and need a live click-test (D4).
