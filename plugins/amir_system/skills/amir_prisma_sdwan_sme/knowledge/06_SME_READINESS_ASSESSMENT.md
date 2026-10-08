# 06 — SME readiness assessment (Phase 6)

Date: 2026-10-08. Basis: 58 notes (Phase 2), 14 scenarios (Phase 3), gap register KG-001..141 (Phase 4), index (Phase 5). Practical-test status is stated honestly: **no claim in this project has reached LAB VALIDATED** (lab exists, access not granted — decision D4). "Reading documentation is not expertise"; the test applied here is whether the notes let a reader reason through realistic SME tasks with every step labelled, which the scenarios exercised.

## 1. Readiness scale

| Level | Meaning |
|---|---|
| **R4 Ready (official)** | Core behaviour VERIFIED from official rank-1/2 sources; scenario(s) in the domain closed on VERIFIED claims; residual gaps are edge cases. |
| **R3 Ready with caveats** | Core behaviour VERIFIED; important practical details only CORROBORATED or internal; scenarios PARTIAL because of those details. |
| **R2 Field-guidance only** | Mechanism and procedures come mainly from internal material (TSE/PAEE/WS-001); official coverage thin; must be presented as field guidance. |
| **R1 Not ready** | Internal-only or roadmap; cannot be presented as product behaviour. |

## 2. Per-domain assessment

| Domain | Notes | Claims V/C/I/U/X/O | Scenarios | Level | Why | Lab-dependent items |
|---|---|---|---|---|---|---|
| 1 Fundamentals | 9 | 64/4/0/16/1/1 | S04, S06, S13 (+S01) | **R4** | Architecture, modes, tenancy, licensing, models, onboarding, lifecycle, MSP all official; conflicts limited to throughput numbers (KG-063) and a role detail (`elem-admin`). | KG-068 (unassign asynchrony) |
| 2 Network | 12 | 76/4/1/26/3/2 | S01, S03, S04, S09 | **R3** | Circuits, interfaces, HA, routing, VRF, multicast, NAT, CloudBlades official; DC failover timing, branch-gateway full-mesh (6.8.1), /25 injection, VRF release limits are internal; three CONFLICTED numbers (loopbacks, affinity, 5200 throughput). | KG-078, KG-011, KG-096-type timers |
| 3 Application traffic | 7 | 42/2/0/7/2/1 | S02, S07 | **R4-** | Path policy, performance policy, SLAs, measurement, QoS structure official; evaluation order CORROBORATED; defaults of built-in performance rules and QoS default class unconfirmed (KG-134, KG-140); jitter conflict (KG-088/127). | KG-088, KG-134, KG-140 |
| 4 Security | 9 | 33/1/1/18/2/2 | S01, S08, S11 | **R3** | ZBFW, Easy Onboarding, RBAC/TACACS+, IoT visibility, segmentation official; User-ID/Cloud User-ID floor, Branch Security floor and troubleshooting, converged SD-WAN internal; PQC now official (6.8.1) but configuration unread. | KG-090 (OOM limits), KG-096 (precedence) |
| 5 SCM | 2 | 8/2/1/4/0/0 (+ addendum) | S14 | **R3-** (raised 2026-10-08) | Official "First Look" page (PUB-013) now VERIFIES the top-level navigation (Command Center, Insights, Reports, Incidents, Log Viewer, Configuration, System Settings); Prisma SD-WAN sub-labels and deep links still inferred; dashboards official (May 2025). | KG-104, KG-105, KG-144 |
| 6 API and automation | 3 | 12/4/1/2/0/0 | S05 | **R4-** | OpenAPI bundle, SDK source, Terraform docs are official; asynchronous semantics and dependency catalog CORROBORATED (authored from bundle + another project's live observation); binding procedure and error-code completeness open (KG-139, KG-110). | KG-110 |
| 7 Operations | 4 | 23/2/0/3/0/0 | S10, S12 | **R4** | Incidents guide, upgrade mechanics and paths, external services, feature chronology official; missing: recommended-release policy (KG-065), 6.6/6.8 notes as PDFs, EOL tables as text. | — (KG-113 doc fetch) |
| 8 Troubleshooting | 5 | 10/4/0/20/0/0 | S06, S07, S12 | **R2** | CLI syntax official (2025 edition); isolation method, connectivity recipe, performance tests, app-detection internals, Branch Security troubleshooting are TSE playbooks; official per-code steps exist for ~35 incident codes. | KG-119 (CLI per release), KG-137 |
| 9 Datapath internals | 2 | 0/0/0/9/0/0 | S12 | **R2** | Entirely PAEE/TSE; coherent and recent, but no official counterpart; usable only as "what TAC will look at" and escalation preparation. | KG-123, KG-125 |
| 9 Design | 5 | 12/0/0/2/1/1 | S01, S04, S11, S13 | **R4** | Oct 2025 reference architecture, deployment blueprint, segmentation guide, multitenant and on-prem controller all official; anti-pattern list mixes official cautions with internal rows, each labelled. | — |

Overall: **R3** — the skill can act as an evidence-labelled SME for design, configuration, policy, operations, API and MSP questions on official grounds, and as a field-guidance assistant for troubleshooting and internals, provided the label discipline is enforced in the skill text.

## 3. Evidence base quality

- Claims-register rows: 280 VERIFIED (66 %), 23 CORROBORATED, 4 INFERRED, 107 UNVERIFIED internal (25 %), 9 CONFLICTED, 7 OBSOLETE — 430 rows over 58 notes.
- Official sources read in full or in the relevant chapters: Administrator's Guide (May 2025), ION release notes 6.3/6.4/6.5, Incidents and Alerts guide, CLI reference (2025 edition), CloudBlade Integrations guide, datasheet (Nov 2025), Design/Deployment/Segmentation guides (Oct 2025), Multitenant Cloud Manager (Oct 2024), On-Premises Controller guide (Jun 2025), Common Services guide (Jun 2024), Azure solution guide (Sep 2023), OpenAPI 6.6.2 bundle, SDK and Terraform sources, cached public 6.6/6.8 pages.
- Internal sources used with UNVERIFIED labels: WS-001 best practices (May 2026), ~40 TSE playbooks and PAEE pages, deck WS-033, Day 2 draft WS-030, KB research package WS-020/021.
- Known blind spots (not in the KB): 6.6/6.8 release-note PDFs, Live Community release guidelines and Nav 3.0 mapping, Common Services IAM reference, Prisma Access CloudBlade guides, official scale limits, on-prem controller admin guide, hardware references for older models (05_UNRESOLVED_QUESTIONS §C).

## 4. Scenario validation summary

| Status | Scenarios | Reason for PARTIAL |
|---|---|---|
| SCENARIO VALIDATED | S02, S05, S08, S09, S10, S11, S13 | — |
| SCENARIO PARTIAL | S01 (DC failover timing, VRF→Prisma Access), S03 (Prisma Access return path, active-ION advertisement), S04 (multi-gateway limits), S06 (diagnostic recipe internal), S07 (shaping/LQM internals), S12 (datapath internal), S14 (deep links inferred) | each PARTIAL step is tied to a KG ID |

No scenario reached LAB; the lab-only list is `05_UNRESOLVED_QUESTIONS.md` §B (10 items).

## 5. Risks if the skill is built now

1. **Navigation drift**: SCM menus changed in Aug 2025 and the guides lag; the skill must date every path (mitigation already in 05-scm/01 rules).
2. **Number conflicts**: throughput, jitter, loopback counts; the skill must list sources, never pick silently (05 §E).
3. **Internal leakage**: 25 % of claims are internal; the skill must keep the "field guidance" framing and never quote Confluence as Palo Alto Networks requirements.
4. **Release coverage**: 6.4.x, 6.6.1 and 6.8.1 feature pages and the 6.8 considerations page are now cached first-hand (PUB-008..011, 2026-10-08); addressed-issues pages and the EOL summary are still missing, so retired codes and end-of-life dates may be incomplete.
5. **Lab absence**: timers, CLI spellings and UI deep links remain unproven; the skill should say "unverified on a live tenant" where the notes say so.

## 6. Recommendation

Proceed to **Phase 7 (skill construction) after user approval**, with these conditions written into the skill:
- Carry the label scheme, the router (`index/02_ROUTER.md`) and the quoting rules verbatim; ship the notes and scenarios as the skill's reference corpus (or point to them in the research workspace) so every answer can cite a note and a source.
- Before or immediately after construction, execute `05_UNRESOLVED_QUESTIONS.md` C1, C3, C4 (release notes 6.6/6.8, Nav 3.0 mapping, datasheets) — they lift the most labels.
- Keep domains 8 and 9-datapath explicitly tagged "field guidance" in the skill's answer template.
- Reopen Phase 3 items for LAB validation when access is granted (A1): S01 failover timings, S09 CLI spelling, S14 deep links, S06 recipe.

Questions needing the user's answer before Phase 7 are listed in `05_UNRESOLVED_QUESTIONS.md` §A (A1–A7).
