# 04 — Knowledge gaps, uncertainties and contradictions

Seeded 2026-10-08 from the inventory. Phase 2 appends to this file; Phase 4 turns the open items into `05_UNRESOLVED_QUESTIONS.md`. IDs are `KG-nnn`. Status: OPEN, RESEARCHING, PARTIAL, CLOSED, ESCALATE (needs external research or user access).

Imported KB gap IDs (`GAP-nnnnnn`) and terminology issues (`TERM-nnnn`) are noted where they already exist.

---

## A. Missing material (not in the KB)

| ID | Domain | Gap | Why it matters | Evidence in KB | Status |
|---|---|---|---|---|---|
| KG-001 | 7, 8 | No ION release-note PDFs for **6.6** and **6.8**; only cached public HTML (WS-022) and a derived bug list (WS-023). | Target releases for the skill include 6.6.x (WS-001 validated on 6.6.x). Feature floors and known issues must be VERIFIED from official pages. | SRC-000033–035 cover 6.3–6.5 only | OPEN (D2 would close) |
| KG-002 | 8 | **CLI reference dated 2021-06-24** (SRC-000032) predates ION 6.x. Newer commands appear only in release notes and TSE playbooks. (= GAP-000012) | Risk of citing obsolete syntax; `dump`/`debug` families may have changed. | SRC-000032, SRC-000033–035, playbooks | OPEN |
| KG-003 | 1 | Hardware references exist only for ION 1200-S, 3200, 5200, 9200 (plus the 00ION_data compendium). **ION 1000, 2000, 3000, 7000 and virtual 3102v/3104v/3108v** have no dedicated reference. | Hardware selection and port-role answers for those models would rest on the datasheet (SRC-000031) and WS-001/WS-002 tables only. | SRC-000031, SRC-000021 (check contents in B2) | OPEN |
| KG-004 | 5 | No official **Strata Cloud Manager** document for SD-WAN screens newer than the Admin Guide (May 2025). The Aug 2025 navigation change is known only from the Day-2 draft (WS-030, rank 9). | Every GUI path must be version-scoped; current paths are UNVERIFIED without an official source or screenshot. | WS-030, WS-024, WS-037 | OPEN (D1/D2) |
| KG-005 | 1 | No **licensing / subscription** guide (SKU model, subscription usage dashboard semantics, vION licence model). | Licensing claims would be UNVERIFIED or INTERNAL. | SRC-000029 "Subscription Usage" pp. 51–56; SRC-000090 (internal TAC) | OPEN |
| KG-006 | 6 | **API rate limits**, 429 format and retry guidance absent (= GAP-000008). | Needed for idempotent automation guidance. | SDK defaults only | OPEN |
| KG-007 | 6, 7 | **Monitor/metrics endpoint response semantics** (fields, units, intervals) not documented (= GAP-000015). | Day-2 metric interpretation and capacity assessments. | SRC-000046 schemas only | OPEN |
| KG-008 | 6 | No **TypeScript** SDK or examples in the KB. | User asked for Python and TypeScript coverage. | none | OPEN (D2: check pan.dev) |
| KG-009 | 9 | No **on-premises controller administrator guide**; only requirement pages and a DR page (Confluence). | On-prem controller design/DR answers would be INTERNAL. | 78890444, 284295473 | OPEN |
| KG-010 | 9 | No official **scale limits** table (sites per tenant, tunnels per ION, routes, flows, policy rule counts). | Enterprise design needs limits. | WS-002 claims, 74187098 (100k flows alert) | OPEN |
| KG-011 | 2, 7 | **HA failover timers, BFD timers, LQM thresholds** not yet located in official text. | Failover reasoning in Phase 3 needs numbers. | to be searched in SRC-000029, SRC-000101, 74187026 (ports and timers) | RESEARCHING |
| KG-012 | 4 | **Certificate lifecycle on ION** (device identity, TPM, controller trust, PQC rollout) only partly covered. | Security domain completeness. | 237599551, 609207049, TSE PQC | OPEN |
| KG-013 | all | **No lab or tenant** available in this project. | Nothing can reach LAB VALIDATED. | see `00` D4 | ESCALATE |
| KG-014 | 2 | **IPv6** support per release and per feature not consolidated. | Design answers. | 78890403 (requirements page), 867868115 (test plan, converged) | OPEN |
| KG-015 | 7 | Official **backup/restore** statement beyond API export and `cloudgenix_config` not found yet. | Day-2 operations. | SRC-000058, SRC-000029 (to search) | RESEARCHING |

## B. Extraction failures (material exists but is not readable as text)

| ID | Item | Impact | Status |
|---|---|---|---|
| KG-020 | WS-033 slide deck "Prisma SD-WAN Technical Deep-Dive 2025 — TDM" (89 MB) has no text extraction. | Likely the richest architecture diagrams in the KB. | OPEN → B0 |
| KG-021 | WS-034 DS/S&O playbook spreadsheet; WS-035 AI transparency datasheet PDF. | Unknown content. | OPEN → B0 |
| KG-022 | 116 of 307 TSE playbook images failed to mirror; PAEE documents keep only remote Confluence image links; Life of Packet and Route Manager `.doc` figures (4 MB and 0.8 MB of images) were not extracted. | Datapath diagrams unavailable offline. | OPEN (needs live Confluence or `.doc` image extraction, read-only) |
| KG-023 | PDF tables flattened in all container extracts; SRC-000036 best-practice text is one word per line in places. | Numeric tables (specs, limits) may be misread; figure-dependent facts stay UNVERIFIED. | OPEN (D1 would close) |
| KG-024 | WS-001 embeds 87 base64 images (HA topology drawings, screenshots). Readable only by rendering. | HA topology notes depend on them. | OPEN (render in B7 if needed) |
| KG-025 | Confluence page content is not semantically extracted (= GAP-000029); 572 of 750 `sd_wan` pages are uncurated "reference". | Coverage may hide useful pages; must sample by title and headings. | OPEN |

## C. Duplicates and version ambiguity

| ID | Item | Resolution plan | Status |
|---|---|---|---|
| KG-030 | SRC-000010 (Azure Sep 2023) vs SRC-000011 (undated Azure guide, different SHA) (= GAP-000013). | Diff done 2026-10-08 (B20): the two extracts are byte-identical apart from file name/path/SHA (883 normalised lines, 6 metadata diffs). SRC-000011 is a duplicate copy of the Sep 2023 guide, not a revision. | CLOSED |
| KG-031 | WS-002 (18 KB "Comprehensive Best Practices") vs WS-001 (TME v2.0) vs SRC-000031 datasheet: hardware throughput and port tables may disagree. | Cross-check in B2; WS-002 is UNVERIFIED by default. | OPEN |
| KG-032 | Registry (105 sources, 2026-07-16) does not contain SRC-000120–000153 used by the product tree. | Keep both numberings in `03`; never cite a SRC above 105 without its path. | NOTED |
| KG-033 | Same TSE playbook pages appear under `prisma_access` Confluence space and in the curated SD-WAN tree. | Cite the curated tree path with the pageId. | NOTED |
| KG-034 | Day-2 draft exists in 12 `.docx` variants plus 3 Markdown versions across 4 trees, filed under Prisma Access. | Use `day2_ops/day2_ops.md` (WS-030) only; treat as draft (CORROBORATED at best). | NOTED |
| KG-035 | vION ingested docs copied 3 times with non-conforming names (= GAP-000028). | Cite `source-material/ingested/` copies. | NOTED |

## D. Contradictions and terminology to resolve

| ID | Topic | Side A | Side B | Status |
|---|---|---|---|---|
| KG-040 | **TSG vs tenant** (TERM-0001). | SRC-000044 (multitenant platform) uses parent/child tenants and Common Services, not "Tenant Service Group". | SCM API (`/tenancy/v1/tenant_service_groups`), SDK scope `tsg_id`, Admin Guide "Allocate ION Devices for an Existing TSG-enabled User", internal FAQ: TSG is the tenancy identifier. | OPEN — needs official Common Services/IAM doc |
| KG-041 | **"Cloud Manager" vs "Strata Cloud Manager"** (TERM-0004). | Older solution guides and SRC-000036 say "Cloud Manager" / legacy portal. | Admin Guide 2025 and WS-001 say Strata Cloud Manager. | Resolve by labelling legacy-portal paths OBSOLETE |
| KG-042 | **PAN-OS SD-WAN vs Prisma SD-WAN** (TERM-0002). | SRC-000027/028 (Oct 2022) describe PAN-OS SD-WAN. | Everything else. | CLOSED by negative routing |
| KG-043 | **Feature chronology conflicts** already recorded in WS-021 `2026-09-30-feature-source-conflicts.md` (public pages disagree on when some features appeared). | — | — | OPEN — import item by item in B17 |
| KG-044 | **State-string casing**: OpenAPI enums upper-case vs `cloudgenix_config` lowercase (WS-020 unknown). | SRC-000046 | SRC-000058 | OPEN |
| KG-045 | **Converged SD-WAN (CSDWAN)**: many `prisma_access`-space pages describe a converged controller/path-selection design; unclear which parts are shipped versus planned. | internal FS/test plans | TSE playbook "Converged SD-WAN (CSDWAN)" 867864901 suggests shipped support | OPEN — INTERNAL until official doc found |
| KG-046 | **Admin Guide (May 2025) menu paths vs SCM navigation after Aug 2025** (WS-030 says Insights / Incidents / Reports / Configuration / System Settings). | SRC-000029 | WS-030 | OPEN — record both with dates |

## E. Process risks noted during inventory

- Rank-1 label in the registry is applied to some documents that look internal or undated (SRC-000036). The catalog downgrades them to CORROBORATED-grade; this is a judgment and is recorded as such.
- Confluence `sd_wan` pages are mostly product requirement documents; they describe intent, not shipped behavior. Any claim from them is UNVERIFIED unless corroborated.
- The 2026-09-30 web cache was collected by a previous agent; this project has not re-fetched. Content is official (rank 1) but freshness is 2026-09-30.
- Several KB files reference a test tenant and a credentials file path. Credentials must never be read, copied or used.

## F. Updates 2026-10-08 (after authorization)

| ID | Change |
|---|---|
| KG-001 | PARTIAL: release notes 5.6 (WS-042) and 6.1 (WS-043) PDFs found; 6.6 and 6.8 still only in cached HTML (WS-022). Public docs now authorized (D2 = yes): fetch 6.6/6.8 release notes in B17. |
| KG-005 | RESEARCHING: WS-046 (Common Services licensing/subscription/tenant management, 140 pp) and WS-040 (SD-WAN activation and onboarding) found. |
| KG-009 | PARTIAL: WS-044 On-Premises Controller deployment guide (Jun 2025, 48 pp) found. |
| KG-013 | Lab exists; access not yet granted (user, 2026-10-08). Status stays ESCALATE until access. |
| KG-020, KG-021 | CLOSED: WS-033/034/035 extracted (text only; deck diagrams still images). |
| KG-023, KG-024 | PARTIAL: original PDFs accessible; figures can be inspected on demand from the PDFs. WS-001 base64 images still need rendering. |
| KG-040 | RESEARCHING: WS-046 is the official Common Services document the TSG question needed. |
| KG-050 | NEW: WS-033 deck (Feb 2026) is confidential and includes forward-looking statements (disclaimer on slide 2). Roadmap items must be labelled UNVERIFIED and never presented as shipped. |
| KG-051 | NEW: skill folder naming for the amir marketplace (`prisma_sdwan_sme` vs `amir_prisma_sdwan_sme`) and its relation to the existing `amir_prisma_sdwan` skill: user decision in Phase 7. |

## G. Updates after batches B1–B3 (2026-10-08)

| ID | Change |
|---|---|
| KG-040 | **CLOSED.** Common Services guide (WS-046 p.107, June 2024 section): "A tenant service group (TSG) is used to provide a logical container that contains tenants and other TSGs… mechanically, a tenant is just a TSG." Same sentence in SRC-000029 p.24. |
| KG-060 | NEW (domain 1/8): official list of destinations and ports an ION must reach for the cloud controller (firewall allow-list) not yet located; candidate SRC-000029 p.155 "Allow IP Addresses in Firewall Configuration". |
| KG-061 | NEW: internal deck says an offline ION operates and buffers statistics for 3 days; official text only says session keys rotate for up to 72 h. Need official confirmation of the statistics claim. |
| KG-062 | NEW: fail-to-wire / bypass behavior ("fail open or closed") per model; read SRC-000029 p.233 Bypass Pair in B4. |
| KG-063 | NEW, CONFLICTED: vION throughput. Datasheet (SRC-000031, Nov 2025): 3102V 100 Mbps, 3104V 200, 3108V 350, 7108V 3 Gbps, 7116V 10 Gbps. Internal guide (WS-001, May 2026): 700 Mbps / 1.1 Gbps / 1.8 Gbps, 7108V 3.2/4.2 Gbps, 7116V 10–11 Gbps, plus ION 7132V. Also ION 5200 branch throughput 3.2 Gbps (datasheet) vs 2 Gbps (WS-001). Resolve with public datasheet/hardware pages under D2. B20 adds a third official set (Design Guide Oct 2025, SRC-000038 pp.26–27): 3102v 700 Mbps, 3104v 1.1 Gbps, 3108v 1.8 Gbps, 7108v 3 Gbps, 7116v 10 Gbps (matches WS-001 for the 3100v series); ION 3200/3200H 600 Mbps DC / 500 Mbps branch; ION 5200 1.5 Gbps DC / 1 Gbps branch (vs datasheet 3.2 Gbps vs WS-001 2 Gbps); ION 9200 6 Gbps DC / 3 Gbps branch. Three-way CONFLICT for ION 5200. |
| KG-064 | NEW: exact semantics of "domain" and DC cluster association for branch tunnels; read SRC-000029 pp.85–94, 470–476, 674–680 in B5. |
| KG-065 | NEW: Live Community "Prisma SD-WAN ION Software Release Guidelines" (recommended release policy) referenced by the admin guide but not in KB; fetch under D2 in B17. |
| KG-066 | NEW: confirm device-level roles (Monitor/Read-Only/Super), `elem-admin` default, TACACS+ from 6.5 in official text (SRC-000029 pp.333–368; SRC-000035). |
| KG-046 | Evidence added: the May 2025 admin guide itself mixes `Workflows > Prisma SD-WAN Setup > …` and `Configuration > Prisma SD-WAN > …` paths (pp.23–24); the internal 2026 guide uses `Configuration > Prisma SD-WAN > ION Devices`. Keep every GUI path date-stamped. |
| KG-003 | Partial: the datasheet lists current models only (1200, 1200-S, 3200, 3200H, 5200, 9200) and marks 3000 and 9000 end-of-sale; ION 1000/2000/7000 remain documented in the admin guide but without hardware references in the KB. |

## H. Updates after batches B3–B11 (2026-10-08)

Gap IDs below are the ones cited in the notes' "Open questions" sections (KG-069 is unused). Domain and note pointers tell where the gap was raised. "D2" means resolvable from public docs under decision D2; "LAB" means it needs tenant access (D4).

| ID | Domain / note | Gap | Route | Status |
|---|---|---|---|---|
| KG-066 | 4 / 04-security/05 | Device toolkit roles Super / Read Only / Monitor and TACACS+ confirmed in SRC-000029 pp.347, 363–366. `elem-admin` default account not mentioned in the guide (stays open under KG-066b). | — | **CLOSED** (roles, TACACS+); KG-066b OPEN for `elem-admin` |
| KG-067 | 1 / 01-fundamentals/09 | RMA cross-model replacement table (pp.317–318) is an image; pairs must be verified from the rendered page before the skill cites any pair. | render PDF | OPEN |
| KG-068 | 1 / 01-fundamentals/09 | Official confirmation that unassign is asynchronous and of blockers beyond circuit labels (hub cluster, spoke HA). | LAB | OPEN |
| KG-070 | 2 / 02-network/01 | Official source for "DC circuit bandwidth is informational only (no shaping at DC)"; WS-001 §QoS corroborates internally. | D2 | OPEN (CORROBORATED internally) |
| KG-071 | 2 / 02-network/01, 05; 03-app/06 | What the BFD aggressive / non-aggressive selector changes versus VPN keep-alives; p.457 says BFD mode is for devices 5.3.x and earlier that lack keep-alives. | D2 | PARTIAL |
| KG-072 | 2 / 02-network/02 | Switching parameters: read SRC-000029 pp.163–180 (switch ports, VLAN/SVI, L2/L3 mode change). | read | OPEN |
| KG-073 | 2 / 02-network/02 | Loopback maximum 4 (L2 section) vs 12 (L3 section). | D2 | CONFLICTED |
| KG-074 | 2 / 02-network/02 | Port-channel WAN support and exact release floors (6.5.1 vs 6.5.2 LAN; WAN 6.6.1 internal). | D2 release notes | OPEN |
| KG-075 | 3 / 03-app/02 | "Minimize Metered LTE Usage" (p.456–457) read in B10: clear BW and LQ monitoring, keep-alive 600,000 ms override, cost 129, no controller connections, no app probes. | — | **CLOSED** |
| KG-076 | 2 / 02-network/04 | Read WS-001 §Standard VPN (lines 917–995) and the Zscaler CloudBlade playbook for field practice. | read (B12) | OPEN |
| KG-077 | 2 / 02-network/06 | Official documentation of hop-aware full-mesh path selection, metric 0/30 symmetry and Anynet prefix filters (6.8.1 internal). | D2 release notes 6.8 | OPEN |
| KG-078 | 2 / 02-network/07 | Official statement of DC-side active/backup selection per branch and failover time. | D2 / LAB | OPEN |
| KG-079 | 2 / 02-network/08 | /25 more-specific injection and `no-advertise` community for core peers (DC routing design guide SRC-000038). B20: SRC-000038 pp.52–53 documents **prefix splitting** (connected-branch prefix equal to an edge-learned prefix → two longer prefixes, e.g. /21 → 2×/22) as the official mechanism; the /25 length and the no-advertise community on core peers remain internal-only. | read (B20) | PARTIAL |
| KG-080 | 2 / 02-network/09 | Confirm 6.6.1 per-VRF BGP router ID. | D2 release notes 6.6 | OPEN |
| KG-081 | 2 / 02-network/09 | Release that introduced per-VRF Internet NAT (simplified DIA) and VRF support on edge/classic peers. | D2 | OPEN |
| KG-082 | 2 / 02-network/11 | Official statement that NAT policies apply only to branch sites. | read admin guide NAT chapter | OPEN |
| KG-083 | 2 / 02-network/12 | Source for "multihop limit 2" and Global scope requirement in cloud DC sites (CloudBlade validation pages pp.13–16, 34–38, 103–108). | read | OPEN |
| KG-084 | 3 / 03-app/01 | Current path-affinity options and defaults (Strict/None vs Required/Required Strict). | D2 or API schema `appdefs` (B15) | CONFLICTED |
| KG-085 | 3 / 03-app/02 | Official statement of "drop but track and re-evaluate" and the Best Available Bandwidth algorithm name. | D2 | OPEN |
| KG-086 | 3 / 03-app/02 | Which failures move existing flows versus only new flows (soft vs hard) in current releases; partly answered by Move Flows Graceful/Forced (03-app/05). | — | PARTIAL |
| KG-087 | 3 / 03-app/05 | Release that introduced Best Path Selection (deck: 6.4.2 vs 6.5.1) and Move Flows Forced. | D2 release notes 6.4/6.5 | CONFLICTED |
| KG-088 | 3 / 03-app/05 | Media SLA jitter default 40 ms (p.505) vs 75 ms (p.510; WS-001). | D2 newer guide / LAB | CONFLICTED |
| KG-089 | 3 / 03-app/07 | Current L7-accelerated application list; license coverage of private-app acceleration through Prisma Access. | D2 | OPEN |
| KG-090 | 4 / 04-security/01 | Official ZBFW rule/zone/prefix scale limits per platform (guide says "no limit"; WS-001 documents OOM on ION 1000/1200/2000). | D2 / LAB | OPEN |
| KG-091 | 4 / 04-security/01 | ZBFW behaviour for VPN-to-VPN transit at a hub ION and for IPv6 (roadmap). | D2 | OPEN |
| KG-092 | 4 / 04-security/02 | Public documentation and release floor of Cloud User-ID / User Context in Prisma SD-WAN (playbook: 6.6.1). | D2 | OPEN |
| KG-093 | 4 / 04-security/02 | Device-ID enforcement GA status and license dependency (6.5 release notes: "contact Support"). | D2 | OPEN |
| KG-094 | 4 / 04-security/03 | Branch Security first supported release: 6.5.1-I (guide p.570) vs 6.5.3-I (WS-001); meaning of the "-I" image suffix. | D2 | CONFLICTED |
| KG-095 | 4 / 04-security/03 | Platform support and throughput impact of Branch Security per ION model. | D2 | OPEN |
| KG-096 | 4 / 04-security/05 | TACACS+ vs local precedence when a user exists in both (guide p.363 says local, p.365 says AAA server). | D2 / LAB | CONFLICTED |
| KG-097 | 4 / 04-security/05 | Common Services role mapping for Prisma SD-WAN in SCM versus legacy `cloudgenix_*` roles. | read WS-046 (B13/B14) | OPEN |

| KG-098 | 4 / 04-security/06 | Prisma Access CloudBlade integration guides (Cloud Managed 2.1.2, Panorama Managed 3.1.5) are not in the KB; the CloudBlades guide (May 2025) has no Prisma Access chapter. | D2 | OPEN |
| KG-099 | 4 / 04-security/06 | Release that introduced SASE Easy Onboarding (deck: 6.4.1; 6.4 release notes describe only the 6.4.2 enhancements). | D2 release notes 6.4.1 | OPEN |
| KG-100 | 4 / 04-security/06 | Whether Easy Onboarding tunnels count against per-platform standard VPN limits; Aggregate vs Site-Based licensing interaction with bandwidth allocation. | D2 / LAB | OPEN |
| KG-101 | 4 / 04-security/08 | Shipped post-quantum capability (RFC 8784 PPK, hybrid KEM, TLS 1.3) in ION 6.7/6.8; KB holds only PRDs. | D2 release notes 6.7/6.8 | OPEN (roadmap) |
| KG-102 | 4 / 04-security/09 | Official Common Services Identity and Access documentation (role list, `accessPolicies` SAML attribute, service accounts and client secrets) not in the KB. | D2 (B15) | OPEN |
| KG-045 | 9 / 04-security/07 | Converged SD-WAN: TSE playbook v44 (2026-07) documents requirements (PAN-OS 12.1.2, ION 6.5.2, PA-5440) and procedures; still no official document in the KB. | D2 | OPEN (INTERNAL, strong) |

| KG-103 | 5 / 05-scm/01 | "SCM Nav 3.0 UI Mapping Preview" PDF (Live Community, Aug 2025) referenced by WS-024/WS-030 but not stored in the KB. | D2 | OPEN |
| KG-104 | 5 / 05-scm/01 | Exact sub-labels under `Configuration > Prisma SD-WAN > Policies` and `> Resources` in current SCM. | LAB / D2 | OPEN |
| KG-105 | 5 / 05-scm/02 | Official Flow Browser limits (1000 flows per page, one-hour range) and flow export latency (10 s–3 min) are internal observations only. | D2 / LAB | OPEN |
| KG-106 | 5 / 05-scm/02 | Official retention table per analytics licence (Base vs DVR; deck says 7 d / 90 d data, 30 d / 1 y audit and events). | D2 | OPEN |
| KG-107 | 6 / 06-api/01 | Official access-token lifetime and refresh guidance (pan.dev access-tokens page not in KB). | D2 | OPEN |
| KG-108 | 6 / 06-api/01 | Official documentation of the `X-PANW-Region` header for monitor APIs and the telemetry-region mapping (only in SDK source). | D2 | OPEN |
| KG-109 | 6 / 06-api/01 | Date and scope of the legacy login-API deprecation for SCM-migrated tenants (SRC-000036 undated). | D2 | OPEN |
| KG-110 | 6 / 06-api/02 | Official API error-code reference; the bundle's 400 examples are not exhaustive (`INTERFACE_REFERRED_IN_SNMP_TRAP_CONFIG` observed live but absent). | D2 / LAB | OPEN |
| KG-111 | 6 / 06-api/03 | Maintained successor to `cloudgenix_config` for the unified API. | D2 | OPEN |

| KG-112 | 7 / 07-operations/01 | Clean machine-readable event-code table; PDF columns split about 15 code names in the derived TSV. | D2 (public event-code HTML pages) | OPEN |
| KG-113 | 7 / 07-operations/01 | Codes retired or renamed after 6.3.2 (6.4–6.8 release notes). | D2 | OPEN |
| KG-114 | 7 / 07-operations/02 | Official DHCP server scale (256 subnets) and relay server count (16) wording in the DHCP chapter pp.252–258. | read | OPEN |
| KG-115 | 7 / 07-operations/03 | Full EOL and compatibility matrix tables (per model, per train) as first-hand text; only WS-021's summary exists (cached HTML not extracted). | D2 | OPEN |
| KG-116 | 7 / 07-operations/03 | 6.6.x upgrade/downgrade considerations page (not cached). | D2 | OPEN |
| KG-117 | 7 / 07-operations/04 | Controller release identifiers behind each monthly announcement. | D2 | OPEN |
| KG-087 | 3 / 03-app/05 | **PARTIAL**: public 6.4.2 notes give Best Path Selection an explicit 6.4.2 minimum; 6.5.1 notes list graceful/forced Move Flows. Deck labels explained. | — | PARTIAL (resolve in note revision) |
| KG-101 | 4 / 04-security/08 | **CLOSED**: 6.8.1 release notes (public, cached 2026-09-30) ship PQC for Standard VPN IPsec (RFC 8784 PPK, RFC 9370/9242 ML-KEM hybrids) and TLS 1.3 hybrid groups for ION-to-controller; fabric tunnels unchanged. Note 08 must be updated from "roadmap" to "shipped in 6.8.1". | — | CLOSED |
| KG-077 | 2 / 02-network/06 | **PARTIAL**: 6.8.1 notes confirm hop-count forwarding for Branch Gateway mode (DC mode since 6.5.1); metric 0/30 and Anynet prefix filters still internal. | D2 | PARTIAL |

| KG-118 | 8 / 08-troubleshooting/01, 03 | Official controller allow-list (destinations/ports per service) not yet read (Admin Guide "Allow IP Addresses in Firewall Configuration"; same as KG-060). | read | OPEN |
| KG-119 | 8 / 08-troubleshooting/02 | Per-release CLI availability matrix (needs a full pass over the ~290 "Introduced in" entries). | derive | OPEN |
| KG-120 | 8 / 08-troubleshooting/04 | Official documentation for ION 3545R-D-C5G-WW (Blackhawk) and dual-modem cellular. | D2 | OPEN |
| KG-121 | 8 / 08-troubleshooting/04 | Official statement of app-map 10-hour expiry and no QUIC domain detection. | D2 | OPEN |
| KG-122 | 8 / 08-troubleshooting/05 | Official documentation of Intra-VLAN Segmentation (release, platforms). | D2 | OPEN |

| KG-123 | 9 / 09-datapath/01 | Official statement on DPDK core allocation, queue sizes, or the 32-VLAN SVI limit on Gen-2 (cross-check switching chapter pp.163–180). | read / D2 | OPEN |
| KG-124 | 9 / 09-datapath/02 | Official description of controller-connection interface preference and MRL retry behaviour. | D2 | OPEN |
| KG-125 | 9 / 09-datapath/02 | Official guidance on the safety/impact of FC debug and trace logging for customer-run diagnostics. | D2 | OPEN |

| KG-126 | 9 / 10-design/01 | Design Guide licensing text (DC subscription for ION 7000/7100V/9000; Table 13 bandwidth tiers incl. ION 9200 1/2.5 Gbps) vs note 01-fundamentals/04 tiers; reconcile with the subscription guide. | read | OPEN |
| KG-127 | 9 / 10-design/01 | Design Guide Table 12 media jitter 40 ms is a second official value for KG-088; confirm current SCM default. | D2 | OPEN |
| KG-128 | 9 / 10-design/02 | Default path set: does the current enterprise-default rule still include "Direct on any private" as backup (SRC-000037 p.70)? | read | OPEN |
| KG-129 | 9 / 10-design/02 | Is the Prisma Access infrastructure subnet still set to 192.168.255.0/24 by the SD-WAN onboarding workflow in current SCM? | D2 | OPEN |
| KG-130 | 9 / 10-design/03 | Admin-guide wording for network contexts ("inter-context traffic permitted by default", SRC-000038 p.34). | read | OPEN |
| KG-131 | 9 / 10-design/04 | On-Premises Controller feature parity with SCM (Insights, Prisma Access onboarding, CloudBlades). | D2 | OPEN |
| KG-132 | 9 / 10-design/05 | Official sources for internal-only anti-patterns (empty zones OOM, app/port mixing, DNAT needs ZBFW rule, circuit-category uniqueness, control-app rule, circuit bandwidth values). | D2 | OPEN |

## I. Gaps opened by Phase 3 scenarios (2026-10-08)

| ID | Scenario / note | Gap | Route | Status |
|---|---|---|---|---|
| KG-133 | S01 / 02-network/09 | Can a standard VPN (Prisma Access tunnel) carry traffic from a custom VRF in 6.5.x (official statement)? | D2 / read | OPEN |
| KG-134 | S02, S07 / 03-app/05 | Default actions of the two built-in performance policy rules (Create Incident only vs Move Flows) in current SCM. | D2 / read | OPEN |
| KG-135 | S03 / 04-security/06 | Official description of the 6.5.1 "automated asymmetry correction" for Prisma Access ↔ fabric return paths. | D2 | OPEN |
| KG-136 | S04 / 02-network/06 | Official guidance on maximum branch gateways per domain and gateway↔gateway behaviour on 6.5.x. | D2 | OPEN |
| KG-137 | S09 / 02-network/07 | CLI spelling `dump spoke ha status` (admin guide) vs `dump spoke-ha status` (deployment guide). | read CLI ref / lab | CONFLICTED |
| KG-138 | S11 / 03-app/04 | Documented way to cap guest bandwidth (per-context QoS rule vs circuit sub-allocation). | read | OPEN |
| KG-139 | S05 / 06-api/02 | Unified-API fields/endpoints that bind policy stacks and security zones to a site/element (procedure, not inferred from the export model). | read bundle | OPEN |
| KG-140 | S07 / 03-app/04 | Official statement of the default QoS rule class (Bronze) and whether transfer type alone changes class assignment. | read | OPEN |
| KG-141 | S12 / 07-ops/01 | Official description of `DEVICESW_GENERAL_PROCESSRESTART` sub-reasons / process names in incident text. | D2 | OPEN |

Next free ID: **KG-142**.
