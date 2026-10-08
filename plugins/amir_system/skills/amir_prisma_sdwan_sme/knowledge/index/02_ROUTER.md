# Router — where to look, by question type (Phase 5, 2026-10-08)

Designed for the future `prisma-sdwan-sme` skill. Each row: the intent → notes to open first → primary sources behind them (SRC/WS IDs from `03_SOURCE_CATALOG.md`) → the label ceiling the answer can reach today. Rules at the end apply to every answer.

## By intent

| Intent | Open first | Then | Primary sources | Label ceiling today |
|---|---|---|---|---|
| Design review / new deployment | 10-design/01, 05, 02 | 02-network/06, 07, 08; 03-application-traffic/02, 03; 04-security/01, 06 | SRC-000038, SRC-000037, SRC-000045, SRC-000029 | VERIFIED (official reference architecture) |
| Segmentation (zones, VRF, guest, IoT) | 10-design/03; 02-network/09 | 04-security/01; 03-application-traffic/03 | SRC-000045, SRC-000029 pp.433–437, 487–504 | VERIFIED; VRF release limits internal |
| Prisma Access integration (DIA, Easy Onboarding) | 04-security/06; 10-design/02 §2, §5.7 | 10-design/01 (Prisma Access facts); 03-application-traffic/03 | SRC-000029 pp.663–680; SRC-000037/038 | VERIFIED; CloudBlade legacy internal |
| Path selection behaviour / "why did it take that path" | 03-application-traffic/02, 06, 05 | 02-network/01, 05; scenarios S02, S07 | SRC-000029 pp.439–468, 540–549 | VERIFIED mechanics; evaluation order CORROBORATED |
| QoS / voice quality | 03-application-traffic/04, 05; scenario S07 | 02-network/01 | SRC-000029 QoS chapter; SRC-000038 p.45 | VERIFIED structure; tuning internal |
| Routing (BGP/OSPF/static, DC injection, asymmetry) | 02-network/08; scenario S03 | 02-network/06; 10-design/01 §Routing | SRC-000029 pp.370–401; SRC-000038 pp.51–54 | VERIFIED; /25 and community internal |
| HA (branch pairs, DC redundancy) | 02-network/07; scenario S09 | 10-design/01 §HA, 10-design/02 §7 | SRC-000029 pp.603–632; SRC-000038 pp.36–42 | VERIFIED |
| Circuits, cellular, metered links | 02-network/01, 03; 03-application-traffic/02 (metered LTE) | 08-troubleshooting/04 (cellular) | SRC-000029 pp.68–75, 188–207, 456–459 | VERIFIED |
| Security policy (ZBFW) | 04-security/01; scenario S08 | 10-design/03; 02-network/11 | SRC-000029 pp.487–504, 561–569 | VERIFIED; scale/OOM internal |
| Identity (User-ID, CIE, Device-ID, RBAC, SSO) | 04-security/02, 05, 09 | — | SRC-000029 pp.333–367, 688–691 | mixed; Cloud User-ID internal |
| Branch Security (CDSS on ION) | 04-security/03; 08-troubleshooting/05 | 07-operations/03 ("-I" image) | SRC-000029 pp.570–577 | VERIFIED basics; floor CONFLICTED; troubleshooting internal |
| Device offline / onboarding | 08-troubleshooting/03; 01-fundamentals/08; scenario S06 | 07-operations/01 (`DEVICESW_DISCONNECTED_FROM_CONTROLLER`) | WS-041 p.14; SRC-000029 pp.40, 140–146 | official steps VERIFIED; recipe internal |
| Incidents, alerts, notifications | 07-operations/01 | 05-scm/01 (where), 07-operations/02 (syslog/SNMP) | WS-041 | VERIFIED |
| Upgrades and lifecycle | 07-operations/03, 04; scenario S10 | 01-fundamentals/05 | RN 6.3/6.4/6.5 (SRC-000033–035), public 6.6/6.8 pages | VERIFIED; recommended-release policy UNKNOWN |
| API / automation | 06-api-automation/01, 02, 03; scenario S05 | 01-fundamentals/09 (state machine) | SRC-000046 (OpenAPI 6.6.2), WS-012 (SDK), WS-013 (Terraform), WS-020 | VERIFIED bundle facts; async/dependency CORROBORATED |
| SCM navigation / "where is it" | 05-scm/01, 02; scenario S14 | 10-design/02 (Oct 2025 paths) | SRC-000029 (May 2025), SRC-000037 (Oct 2025), WS-024 | dated paths VERIFIED; deep links INFERRED |
| Troubleshooting method and CLI | 08-troubleshooting/01, 02 | domain note for the layer; 09-datapath/02 for escalation | WS-048 CLI reference 2025; TSE playbooks | CLI syntax VERIFIED (2025 ed.); method internal |
| Datapath internals, packet drops | 09-datapath/01, 02; scenario S12 | 08-troubleshooting/02 | PAEE/TSE (internal only) | UNVERIFIED (internal) — present as TAC territory |
| MSP / multitenant / on-prem controller | 10-design/04; 01-fundamentals/09, 03; scenario S13 | 06-api-automation/01 (TSG scope) | SRC-000044, WS-046, WS-044 | VERIFIED |
| Licensing | 01-fundamentals/04; 10-design/01 §Licensing | 05-scm/02 (usage) | SRC-000029 pp.51–56; SRC-000038 pp.55–56; WS-046 | VERIFIED with tier-naming gap KG-126 |
| Cloud deployments (AWS/Azure/GCP) | 02-network/12; 10-design/01 (Azure) | 02-network/08 (classic peer) | SRC-000030, SRC-000010 | VERIFIED; multihop/Global-scope rule internal |
| Converged SD-WAN, PQC, roadmap items | 04-security/07, 08; 02-network/06 §Converged | 07-operations/04 | internal PRDs; public 6.8 page for PQC | INTERNAL / roadmap except PQC 6.8.1 |

## Negative routing (never used as Prisma SD-WAN evidence)

- PAN-OS SD-WAN material: Oct 2022 branch design/deployment guides (SRC-000027/028), "Strata Playbook: Secure SD-WAN" Panorama-plugin pages.
- Legacy CloudGenix API docs for current authentication (use unified API notes; legacy only for migrated-token caveats).
- AWS/Azure vendor documentation (SRC-000039/040) — background only.
- Confluence requirement/PRD pages — roadmap unless corroborated (KG-050).
- WS-002 "Comprehensive Best Practices" — UNVERIFIED until cross-checked (KG-031).

## Answer rules carried into the skill

1. Label every product claim (VERIFIED / CORROBORATED / INFERRED / UNVERIFIED / CONFLICTED / OBSOLETE) and state DOC vs SCENARIO vs LAB; nothing is LAB today (D4).
2. Quote SCM paths with their date and generation (05-scm/01 §How the skill should quote navigation).
3. Numbers (throughput, timers, limits) always with source and mode; CONFLICTED numbers are listed, never averaged (05_UNRESOLVED_QUESTIONS §E).
4. Internal-only material (TSE/PAEE/WS-001) is "field guidance", never "Palo Alto Networks requires".
5. When a question hits an OPEN gap, say so and point to `05_UNRESOLVED_QUESTIONS.md` group (A user, B lab, C public docs, D local read).
6. Scenarios S01–S14 are worked examples of the reasoning chain; reuse their structure (situation → question → labelled chain → answer → checks → gaps).
