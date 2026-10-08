# Phase 3 — Scenario validation index

Purpose: prove that the Phase 2 notes support SME-grade reasoning, not just recall. Every scenario is worked through on paper against the notes and their sources. Evidence type for everything here is **SCENARIO** (D4: no lab access, nothing reaches LAB). A scenario is **SCENARIO VALIDATED** when the reasoning chain closes using labelled claims only; it is **SCENARIO PARTIAL** when a step depends on an UNVERIFIED/CONFLICTED/OPEN item, which is then listed for Phase 4.

## File format (every `S<nn>-*.md`)

1. **Situation** — what the user describes (releases, platforms, topology, symptoms, constraints).
2. **Question** — what an SME is asked to decide or explain.
3. **Reasoning chain** — numbered steps; each step cites the note(s) and the claim label it relies on.
4. **Answer** — what the SME says, with labels inline.
5. **What to check / collect next** — only steps a source supports.
6. **Gaps exposed** — KG IDs touched; new gaps opened here (continue numbering from `04_KNOWLEDGE_GAPS.md`).
7. **Validation status** — SCENARIO VALIDATED / SCENARIO PARTIAL, with the domains it covers.

## Scenario set (plan §5 items 1–5 plus coverage scenarios so every domain is exercised)

| ID | Title | Domains exercised | Plan origin |
|---|---|---|---|
| S01 | Multi-site enterprise: 40 branches (MPLS+Internet+LTE), 2 DCs with clusters, BGP to core, VRF segmentation, Prisma Access DIA; packet paths and failovers | 1, 2, 3, 4, 9 | plan §5.1 |
| S02 | Policy conflict: path policy prefers Internet for SaaS while the performance SLA fails on Internet | 3 | plan §5.2 |
| S03 | Asymmetric return path through a DC with BGP route injection and NAT | 2, 8 | plan §5.3 |
| S04 | Brownfield migration from a legacy WAN with a branch-gateway topology | 1, 2, 9 | plan §5.4 |
| S05 | API automation: idempotent site build-out and safe teardown order | 6 | plan §5.5 |
| S06 | Branch offline after cut-over (controller connectivity) | 1, 8 | coverage |
| S07 | Poor voice quality on an MPLS+Internet branch | 3, 8 | coverage |
| S08 | ZBFW drops an inbound destination-NAT service | 4 | coverage |
| S09 | HA pair never fails over | 2, 8 | coverage |
| S10 | Upgrade planning for a mixed Gen-1/Gen-2 fleet to 6.5.x | 7 | coverage |
| S11 | Guest Wi-Fi segmentation request | 4, 9 | coverage |
| S12 | Datapath drop escalation: what to collect, how incidents map | 7, 8, 9 (datapath) | coverage |
| S13 | MSP allocates devices and vION licences to a child tenant | 1, 9 | coverage |
| S14 | "Where is it in SCM?" across the three UI generations | 5 | coverage |

Domains: 1 fundamentals, 2 network, 3 application traffic, 4 security, 5 SCM, 6 API, 7 operations, 8 troubleshooting, 9 design/datapath.

## Status

| ID | Status | Date | File |
|---|---|---|---|
| S01 | SCENARIO PARTIAL (KG-133 new) | 2026-10-08 | `S01-multisite-enterprise-two-dcs-vrf-prisma-access.md` |
| S02 | SCENARIO VALIDATED (KG-134 new) | 2026-10-08 | `S02-policy-conflict-path-vs-performance-sla.md` |
| S03 | SCENARIO PARTIAL (KG-135 new) | 2026-10-08 | `S03-asymmetric-return-path-dc-bgp-nat.md` |
| S04 | SCENARIO PARTIAL (KG-136 new) | 2026-10-08 | `S04-brownfield-migration-branch-gateway.md` |
| S05 | SCENARIO VALIDATED (KG-139 new) | 2026-10-08 | `S05-api-idempotent-site-buildout-and-teardown.md` |
| S06 | SCENARIO PARTIAL | 2026-10-08 | `S06-branch-offline-after-cutover.md` |
| S07 | SCENARIO PARTIAL (KG-140 new) | 2026-10-08 | `S07-poor-voice-quality-mpls-internet-branch.md` |
| S08 | SCENARIO VALIDATED | 2026-10-08 | `S08-zbfw-drops-inbound-dnat-service.md` |
| S09 | SCENARIO VALIDATED (KG-137 new) | 2026-10-08 | `S09-ha-pair-never-fails-over.md` |
| S10 | SCENARIO VALIDATED | 2026-10-08 | `S10-upgrade-planning-mixed-gen1-gen2-fleet.md` |
| S11 | SCENARIO VALIDATED (KG-138 new) | 2026-10-08 | `S11-guest-wifi-segmentation.md` |
| S12 | SCENARIO PARTIAL (KG-141 new) | 2026-10-08 | `S12-datapath-drop-escalation-and-incident-triage.md` |
| S13 | SCENARIO VALIDATED | 2026-10-08 | `S13-msp-allocates-devices-and-vion-licences.md` |
| S14 | SCENARIO PARTIAL | 2026-10-08 | `S14-where-is-it-in-scm-ui-generations.md` |

Domain coverage after S01–S14: every domain 1–9 is exercised at least twice. Domains whose scenarios are only PARTIAL: 8 (troubleshooting) and 9-datapath — both because the evidence is internal-only (no lab, D4). Domains 5 (SCM) is PARTIAL because deep links are inferred.

Totals: 7 VALIDATED, 7 PARTIAL. New gaps opened by Phase 3: KG-133..141 (recorded in `04_KNOWLEDGE_GAPS.md` §I).
