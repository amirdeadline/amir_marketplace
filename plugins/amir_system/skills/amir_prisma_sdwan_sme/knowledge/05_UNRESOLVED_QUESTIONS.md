# 05 — Consolidated unresolved questions (Phase 4)

Date: 2026-10-08. Source: `04_KNOWLEDGE_GAPS.md` KG-001..141 after Phases 2–3. Every OPEN, PARTIAL, CONFLICTED or ESCALATE item is placed in exactly one group by **who can answer it**. CLOSED and NOTED items are listed at the end for completeness. Nothing here changes a note; notes keep their labels until a question is answered and the answer is recorded in `04` and in the note.

## A. Questions only the user (Amir) can answer — decisions and access

| # | Question | Why it matters | Gap IDs |
|---|---|---|---|
| A1 | When will lab access (tenant and/or devices) be granted, and under which rules (read-only? change windows?) | Without it nothing reaches LAB VALIDATED; 7 of 14 scenarios stay PARTIAL; CLI spellings and timers cannot be confirmed. | KG-013 (ESCALATE), KG-068, KG-078, KG-090, KG-096, KG-100, KG-104, KG-105, KG-110, KG-137 |
| A2 | Should the skill cover **legacy CloudBlade** Prisma Access integration (FIC/PIC) or only SASE Easy Onboarding? | Decides whether KG-098 (integration guides not in KB) must be fetched. | KG-098 |
| A3 | Should the skill answer **Converged SD-WAN** (PAN-OS NGFW as DC hub) questions, given only internal material exists? | Scope and label policy for an internal-only feature line. | KG-045 |
| A4 | Should the skill include **TypeScript** API examples (none in the KB) or Python only? | Phase 7 content. | KG-008 |
| A5 | Skill folder name and relation to the existing `amir_prisma_sdwan` skill (`prisma_sdwan_sme` vs `amir_prisma_sdwan_sme`; reuse `kbq.py` or fork). | Phase 7 construction; already deferred to Phase 7 by decision. | KG-051 |
| A6 | May the project **render** PDF figures and the 87 base64 images in WS-001 (HA topologies, RMA table) locally to verify figure-only facts? | Closes figure-dependent gaps without any external transfer. | KG-023, KG-024, KG-067 |
| A7 | Is the Live Community (Palo Alto Networks community site, login may be required) an allowed public source under D2? | KG-065 and KG-103 both point at Live Community PDFs. | KG-065, KG-103 |

## B. Questions a lab or live tenant must answer (cannot be closed from documents)

| # | Question | Gap IDs |
|---|---|---|
| B1 | Live SCM menu sub-labels and deep links (Policies/Resources), Insights group label variance, click-verification of inferred links. | KG-046, KG-104 |
| B2 | Unassign/declaim asynchrony and the full set of blockers (hub cluster, spoke HA) as observed on a tenant. | KG-068 |
| B3 | DC-side active/backup selection per branch and measured failover time; ION re-homing time after a DC ION loss. | KG-078 |
| B4 | TACACS+ vs local user precedence when both exist (guide contradicts itself). | KG-096 |
| B5 | ZBFW scale behaviour per platform (OOM thresholds) and Flow Browser limits / export latency. | KG-090, KG-105 |
| B6 | Whether Easy Onboarding tunnels count against standard-VPN limits; Aggregate vs Site-Based licensing interaction. | KG-100 |
| B7 | API error codes beyond the bundle examples (e.g. `INTERFACE_REFERRED_IN_SNMP_TRAP_CONFIG`). | KG-110 |
| B8 | CLI spellings and availability on current releases (`dump spoke ha status` vs `dump spoke-ha status`; 2021 CLI reference vs 6.x). | KG-002, KG-119, KG-137 |
| B9 | Jitter default for the media SLA as shown in current SCM (40 vs 75 ms). | KG-088, KG-127 |
| B10 | Default actions of the built-in performance policy rules; default QoS rule class. | KG-134, KG-140 |

## C. Questions public documentation can answer (D2 allowed; fetch, cache in `inventory/public/`, record URL/date/SHA-256 in `03`)

| # | Question | Target document(s) | Gap IDs |
|---|---|---|---|
| C1 | 6.6 and 6.8 release notes (features, considerations, retired codes), 6.6.x considerations page, 6.4.1 notes (Easy Onboarding floor). | ION release notes 6.4.1, 6.6.x, 6.8.x | KG-001, KG-113, KG-116, KG-099, KG-087 (confirm), KG-080, KG-074 |
| C2 | ION Software Release Guidelines (recommended/preferred release policy). | Live Community (see A7) | KG-065 |
| C3 | SCM Nav 3.0 UI mapping (before/after menus). | Live Community PDF (see A7); SCM release notes | KG-103, KG-004, KG-046 |
| C4 | Current datasheet / hardware pages: vION and ION 5200/9200 throughput (three-way conflict), ION 7132V, Blackhawk 3545R-D-C5G-WW, hardware references for ION 1000/2000/3000/7000. | Datasheets, hardware references | KG-063, KG-031, KG-003, KG-120 |
| C5 | EOL summary and compatibility matrix as text; controller release identifiers. | EOL / compatibility pages; controller release notes | KG-115, KG-117 |
| C6 | Cloud User-ID / User Context page and floor; Device-ID GA and licence; Branch Security first release and "-I" image meaning, platform support and throughput impact; Intra-VLAN Segmentation. | Admin guide (newer rev), Branch Security pages | KG-092, KG-093, KG-094, KG-095, KG-122 |
| C7 | Common Services Identity and Access (roles, `accessPolicies`, service accounts), role mapping SCM vs legacy roles; access-token lifetime; `X-PANW-Region`; legacy login deprecation. | Common Services docs; pan.dev | KG-102, KG-097, KG-107, KG-108, KG-109 |
| C8 | Official API rate limits / 429 handling; monitor metrics semantics; error-code reference; maintained successor to `cloudgenix_config`; unified-API procedure for binding stacks and zones. | pan.dev, OpenAPI docs | KG-006, KG-007, KG-110, KG-111, KG-139 |
| C9 | Event-code tables as HTML (clean names). | Incidents and alerts docs | KG-112, KG-141 |
| C10 | Prisma Access CloudBlade integration guides (only if A2 = yes). | CloudBlade guides 2.1.2 / 3.1.5 | KG-098 |
| C11 | PQC configuration details after 6.8.1; path affinity options; "drop but track" and Best Available Bandwidth; soft/hard failure semantics; app-map expiry and QUIC; L7 acceleration list. | Admin guide newer rev; 6.8 docs | KG-101 (follow-up), KG-084, KG-085, KG-086, KG-121, KG-089 |
| C12 | On-Premises Controller administrator guide and feature parity. | On-prem controller docs | KG-009, KG-131 |
| C13 | Branch gateway limits and 6.8.1 full-mesh behaviour (hop-aware, metric 0/30, Anynet filters); BGW max per domain. | 6.8 release notes / admin guide | KG-077, KG-136 |
| C14 | VRF: release introducing per-VRF Internet NAT and VRF on edge/classic peers; custom VRF over standard VPN (Prisma Access). | Admin guide VRF chapter (newer), release notes | KG-081, KG-133 |
| C15 | Prisma Access ↔ fabric asymmetry correction (6.5.1); Internet-Only mode behaviour. | Prisma Access / SD-WAN integration docs | KG-135 |
| C16 | Official scale limits table (sites, tunnels, routes, flows, rules); analytics retention per licence; licensing/subscription model text (tiers, DC subscription). | Scale/limits page; subscription guide (WS-046 partly) | KG-010, KG-106, KG-005, KG-126 |
| C17 | IPv6 support per feature; certificate lifecycle (MIC/CIC, TPM, renewals); offline-statistics buffering claim; fail-to-wire semantics per model. | Admin guide chapters; release notes | KG-014, KG-012, KG-061, KG-062 |
| C18 | Controller allow-list destinations/ports; controller-interface selection and MRL behaviour; safety of FC debug/trace logging; datapath statements (DPDK, 32-VLAN SVI). | Admin guide "Allow IP Addresses in Firewall Configuration"; KB articles | KG-060/118, KG-124, KG-125, KG-123 |
| C19 | Official sources for internal-only best practices (anti-pattern rows 4–9, 12, 22 in note 10-design/05; DC bandwidth informational; NAT branch-only; multihop 2 / Global scope in cloud DCs). | Live Community best-practice articles; admin guide | KG-132, KG-070, KG-082, KG-083 |

## D. Reads still pending inside the KB (no new source needed)

| # | What to read | Gap IDs |
|---|---|---|
| D1 | Admin guide pp.163–180 (switching: switch ports, VLAN/SVI, L2/L3 mode, SVI limits). | KG-072, KG-123 (partly) |
| D2 | Admin guide pp.317–318 RMA cross-model table (image; needs A6). | KG-067 |
| D3 | Admin guide DHCP chapter pp.252–258 (256 subnets, 16 relay servers wording). | KG-114 |
| D4 | Admin guide network-context chapter wording; default path set wording; NAT chapter "branch only" wording. | KG-130, KG-128, KG-082 |
| D5 | CloudBlade validation pages pp.13–16, 34–38, 103–108 (multihop 2, Global scope). | KG-083 |
| D6 | WS-001 §Standard VPN (lines 917–995) cross-check into note 02-network/04 (read in B12; amend note, then close). | KG-076 |
| D7 | Loopback maximum 4 vs 12 (two admin-guide sections). | KG-073 |
| D8 | Feature-chronology conflicts file (WS-021) imported item by item into note 07-operations/04. | KG-043 |
| D9 | Confluence image extraction for Life of Packet / Route Manager `.doc` figures (read-only, local). | KG-022 |
| D10 | `elem-admin` default account statement. | KG-066b |
| D11 | Guest bandwidth capping method (QoS chapter). | KG-138 |
| D12 | Backup/restore statement beyond API export (admin guide search). | KG-015 |
| D13 | Semantic sampling of the 572 uncurated `sd_wan` Confluence pages by title/heading. | KG-025 |
| D14 | Deployment-guide Prisma Access infrastructure subnet (192.168.255.0/24) — confirm in current onboarding docs. | KG-129 |

## E. Conflicts recorded (two or more sources disagree) — adjudication rule until resolved

| Conflict | Sources | Rule applied in notes | Gap |
|---|---|---|---|
| vION / ION 5200 / 9200 throughput | datasheet Nov 2025 vs Design Guide Oct 2025 vs WS-001 May 2026 | quote all three with mode and source; never a single number | KG-063 |
| Media SLA jitter 40 vs 75 ms | admin guide p.505 / Design Guide vs admin guide p.510 / WS-001 | state both; prefer the policy screen on the tenant | KG-088, KG-127 |
| Best Path Selection floor 6.4.2 vs 6.5.1 | public 6.4.2 notes vs deck | 6.4.2 (public notes) with note on the deck | KG-087 (PARTIAL) |
| Branch Security first release 6.5.1-I vs 6.5.3-I | admin guide vs WS-001 playbooks | official 6.5.1-I, internal recommends 6.5.3-I | KG-094 |
| TACACS+ vs local precedence | admin guide p.363 vs p.365 | present both; recommend testing | KG-096 |
| Path affinity options Strict/None vs Required/Required Strict | admin guide screen vs WS-001 | official two options; internal three noted | KG-084 |
| Loopback maximum 4 vs 12 | admin guide L2 vs L3 sections | state both with context | KG-073 |
| Circuit categories 32/32 vs "30/30" | admin guide vs WS-001 | official 32 | (in note 02-network/01) |
| `dump spoke ha status` vs `dump spoke-ha status` | admin guide vs deployment guide | quote both spellings | KG-137 |
| "Fabric links never between DCs" vs inter-DC fabric from 6.5.1 | Design Guide Oct 2025 vs admin guide May 2025 | admin guide current; Design Guide sentence OBSOLETE in part | (note 10-design/01) |
| Prefix injection /25 + no-advertise vs prefix splitting | TSE playbook vs Design Guide | prefix splitting official; /25 and community internal | KG-079 (PARTIAL) |
| State-string casing (API enums vs cloudgenix_config) | OpenAPI vs tool | compare case-insensitively | KG-044 |
| TSG vs tenant terminology | resolved: "a tenant is just a TSG" | closed | KG-040 (CLOSED) |

## F. Closed or noted since inventory (for the record)

CLOSED: KG-020, KG-021 (extractions), KG-030 (Azure copies identical), KG-040 (TSG definition), KG-042 (negative routing), KG-066 (device roles, TACACS+), KG-075 (metered LTE recipe), KG-101 (PQC shipped 6.8.1). PARTIAL: KG-001, KG-009, KG-023, KG-024, KG-071, KG-077, KG-079, KG-086, KG-087. NOTED (process rules, no action): KG-032, KG-033, KG-034, KG-035, KG-041, KG-050.

## G. Suggested order of resolution

1. A1 and A7 (access and source permissions) — they unlock groups B and parts of C.
2. C1, C4, C3 (release notes, datasheets, Nav 3.0 mapping) — highest impact on label upgrades across many notes.
3. D1–D14 — cheap local reads.
4. Remaining C items by domain in Phase 7 preparation; B items only when the lab opens.

Count: 114 open questions grouped into 7 user decisions, 10 lab-only items, 19 public-doc fetch groups, 14 local reads, 13 recorded conflicts.
