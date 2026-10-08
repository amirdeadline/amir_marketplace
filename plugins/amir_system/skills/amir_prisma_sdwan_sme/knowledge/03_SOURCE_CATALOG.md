# 03 — Source catalog (traceable references)

Every citation in later notes points to an entry here. **SRC-nnnnnn** IDs are the KB registry IDs (`palo-alto-knowledge-base/source-registry.json`, 105 entries, generated 2026-07-16) or the IDs the KB product tree uses beyond the registry (SRC-000120+). **WS-nnn** IDs are workspace IDs for material the registry does not cover. Paths are relative to the KB root `E:\PC3_Shared\Palo\COE\Prisma_SASE_KB\`.

Classification date: 2026-10-08. "Rank" is the KB authority rank (1 official docs, 2 OpenAPI, 3 release notes, 4 official code/SDK, 9 internal). Internal (rank 9) sources are never customer-facing.

---

## A. Official PDFs inside `prisma_sdwan.md` (SRC-000002; mirror `palo-alto-knowledge-base/corpus/containers/prisma_sdwan.md`)

How to locate: `### Source PDF: <name>` opens a section; `#### <name> - Page N` marks each PDF page. Read with offset/limit; never load whole (100,806 lines).

| ID | Title | Rank | Doc version / date | Pages | Container lines | SHA-256 (first 12) | Original PDF (outside KB) |
|---|---|---|---|---|---|---|---|
| SRC-000029 | Prisma SD-WAN Administrator's Guide | 1 | Last Revised 2025-05-13 | 696 | 37581–58806 | c2140a1687fa | `E:/PC3_Shared/Palo/Documents/selected/prisma-sd-wan-administration.pdf` |
| SRC-000032 | Prisma SD-WAN ION Device CLI Reference | 1 | Last Revised 2021-06-24 | 444 | 63413–82456 | 15604c26be95 | `.../selected/prisma-sd-wan-ion-cli-reference.pdf` (duplicate `IONS/prisma-sd-wan-ion-wcli-reference.pdf`) |
| SRC-000030 | Prisma SD-WAN CloudBlade Integrations | 1 | (read in B8/B12) | 176 | 58807–62857 | 63408e8aecd1 | `.../selected/prisma-sd-wan-cloudblades-cloudblade-integrations.pdf` |
| SRC-000031 | Prisma SD-WAN Instant-On Network (ION) Device Specifications | 1 | datasheet (date to confirm in B2) | — | 62858–63412 | cfa84e8bd683 | `.../Ref architect/prisma-sd-wan-instant-on-network-ion-device-specifications_dps.pdf` |
| SRC-000021 | 00ION_data (compendium: quick starts, hardware references, CLI) | 1 | mixed | 708 | 59–26659 | 23aaecd171d6 | `.../IONS/00ION_data.pdf` |
| SRC-000022 | ION 1200-S 4G Quick Start Guide | 1 | — | — | 29678–29826 | 8f456c07cfd0 | `.../IONS/ion-1200-s-4g-quick-start-guide.pdf` |
| SRC-000023 | ION 1200-S Hardware Reference | 1 | — | — | 29827–31170 | 025294d375b1 | `.../IONS/ion-1200-s-hardware-reference.pdf` |
| SRC-000024 | ION 3200 Hardware Reference | 1 | — | — | 31171–32353 | 7990ba3a34b5 | `.../IONS/ion-3200-hardware-reference.pdf` |
| SRC-000025 | ION 5200 Hardware Reference | 1 | — | — | 32354–32843 | f04a80d09fbc | `.../IONS/ion-5200-hardware-reference.pdf` |
| SRC-000026 | ION 9200 Hardware Reference | 1 | — | — | 32844–33385 | dceb617ea407 | `.../IONS/ion-9200-hardware-reference.pdf` |
| SRC-000033 | ION Device Release Notes 6.3 | 3 | © 2023 | 26 | 82457–83296 | ab79c163762f | `.../IONS/prisma-sd-wan-ion-release-notes-6-3.pdf` |
| SRC-000034 | ION Device Release Notes 6.4 | 3 | — | — | 83297–83864 | c9cbcfab9c00 | `.../IONS/prisma-sd-wan-ion-release-notes-6-4.pdf` |
| SRC-000035 | ION Device Release Notes 6.5 | 3 | — | — | 83865–86353 | 60283c1de2a0 | `.../IONS/prisma-sd-wan-ion-release-notes-6-5.pdf` |
| SRC-000036 | Prisma SD-WAN Best Practices ("SDWANN best practice.pdf", earlier edition) | 1 (registry) — treat as **CORROBORATED-grade**: internal-looking, undated | undated; mentions SCM and legacy portal | 59 | 86354–95684 | 082cf4b3ba0e | `.../selected/SDWANN best practice.pdf` |
| SRC-000037 | Secure and Resilient Enterprise Connectivity Using Prisma SD-WAN — Deployment Guide | 1 | Oct 2025 | — | 95685–98402 | afb6fec50e08 | `.../Ref architect/... Deployment Guide - Oct25.pdf` |
| SRC-000038 | Secure and Resilient Enterprise Connectivity Using Prisma SD-WAN — Design Guide | 1 | Oct 2025 | — | 98403–100806 | 5242dba6c7b4 | `.../Ref architect/... Design Guide - Oct25.pdf.pdf` |
| SRC-000009 | Extending SD-WAN into AWS for Private Application Access — Solution Guide | 1 | Nov 2023 | — | 26660–27615 | 0a1939104056 | `.../Ref architect/...Nov23.pdf` |
| SRC-000010 | Extending SD-WAN into Azure for Private Application Access — Solution Guide | 1 | Sep 2023 | — | 27616–28646 | c6606c1bec82 | `.../Ref architect/...Sep23.pdf` |
| SRC-000011 | extending-sdwan-into-azure-for-private-apps-solution-guide (duplicate copy of SRC-000010: identical content, only file name/path/SHA differ; KG-030 CLOSED 2026-10-08) | 1 | undated | — | 28647–29677 | 452d7d908e42 | `.../selected/extending-sdwan-into-azure-for-private-apps-solution-guide.pdf` |
| SRC-000027 | On Premises Network Security and SD-WAN for the Branch — Design Guide (**PAN-OS SD-WAN**) | 1 | Oct 2022 | — | 33386–36812 | e8bcf470e277 | negative routing only |
| SRC-000028 | On-Premises Network Security for the Branch — Overview (**PAN-OS**) | 1 | Oct 2022 | — | 36813–37580 | ac0ce93a6881 | negative routing only |

## B. Official PDFs inside `prisma_sase_architecure.md` (SRC-000003; mirror `corpus/containers/prisma_sase_architecure.md`, 83,593 lines)

| ID | Title | Rank | Date | Container lines |
|---|---|---|---|---|
| SRC-000045 | SASE Network Segmentation — Solution Guide | 1 | Oct 2025 | 76412–77445 |
| SRC-000017 | SASE for Securing Private Applications — Deployment Guide | 1 | Jun 2024 | 68888–73096 |
| SRC-000018 | SASE for Securing Private Applications — Design Guide | 1 | Jun 2024 | 73097–76411 |
| SRC-000044 | Prisma SASE Multitenant Platform | 1 | Oct 2024 (per TERM-0001 note) | 64707–68332 |
| SRC-000041 | Identity-Based and Posture-Based Security for SASE — Solution Guide | 1 | Dec 2025 | 54627–57533 |
| SRC-000042 | Managing Risk in Connected Assets by Using Device Security — Solution Guide | 1 | Oct 2025 | 57534–59911 |
| SRC-000043 | Network Security for Public Cloud — Overview | 1 | Nov 2025 | 59912–60511 |
| SRC-000039 | aws-vpc-tgw (AWS documentation; background only) | 1 | — | 56–6391 |
| SRC-000040 | azure-virtual-wan (Microsoft documentation; background only) | 1 | — | 6392–51608 |
| dup | SRC-000009/010/011 at 51609–54626; SRC-000027/028 at 60512–64706; SRC-000031 at 68333–68887; SRC-000037/038 at 77446–82567 | | | use section A ranges |

## C. Internal best-practices and summaries (not in registry)

| ID | Path | Rank | Version / date | Notes |
|---|---|---|---|---|
| WS-001 | `palo-alto-knowledge-base/prisma-sd-wan/Prisma SD-WAN Best Practices - May 2026.md` | 9 (strong internal; TME-authored, version-stamped) | v2.0, 2026-05-30; validated on ION 6.6.x/6.5.x/6.4.x/6.3.x, SCM April 2026 | 2,013 lines; headings carry `{#anchor}` ids usable as section pointers; 87 base64 images (image refs `[imageN]`). Identical copies: `prisma-sdwan/Prisma SD-WAN Best Practices - May 2026.md`, `prisma-sd-wan/research/...` |
| WS-002 | `prisma-sdwan/Prisma SD-WAN Best Practices - May 2026 (1).md` | unknown (looks AI-generated) | undated | 18 KB "Comprehensive Best Practices Guide"; hardware table (ION 1000–9200 throughput). UNVERIFIED until cross-checked |
| WS-036 | `playbooks/sdwan/Prisma SD-WAN Low-Level Playbook.md` (mirror `corpus/prisma-sd-wan/playbooks-root/`) | 9 | — | topic route `sdwan-low-level-playbook` |

## D. API specifications and SDKs

| ID | Path | Rank | Version | Notes |
|---|---|---|---|---|
| SRC-000046 | `api/prisma_sdwan_unified.json` | 2 | 6.6.2; bundled 2026-07-05 | 924 paths, 1,509 ops; servers `https://api.sase.paloaltonetworks.com`, `https://auth.apps.paloaltonetworks.com`; paths `/sdwan/v{n}/api/...`, `/sdwan/monitor/v2.0/api/monitor/...`, `/auth/v1/oauth2/access_token` |
| SRC-000047 | `api/prisma_sdwan_legacy.json` | 2 | legacy | 925 paths, 1,513 ops; `https://api.us.cloudgenix.com`, paths `/v{n}/api/tenants/{tenant_id}/...` |
| SRC-000051 | `api/generation_stats.json`, `api/prisma_sdwan_legacy_generation_stats.json` | 9 | 2026-07-05 | bundle provenance (source root `pan.dev-master/openapi-specs`) |
| SRC-000050 | `api/Prisma SASE.postman_collection.json` | 2 | — | 69 MB; sample with jq-style scripts only |
| — | `api/scm.json` | 2 | 1.0.0 | 513 paths, 1,065 ops; tenancy/IAM endpoints (`/tenancy/v1/tenant_service_groups/...`) |
| WS-010 | `pan-dev/repos/pan.dev/openapi-specs/sdwan/unified/open_api_unified.json`, `.../legacy/open_api_legacy.json` | 2 | — | raw upstream specs |
| WS-011 | `pan-dev/repos/pan.dev/products/sdwan/docs/sdwan.md`, `sdwan_gsg_sdk.md`, `legacy_getstarted.md`, `prismasdwanconfig.md`; `products/sdwan/api/home.md`, `api/legacy/home.md` | 1 | — | states unified APIs became available 2022-06-06 and legacy APIs use login tokens |
| SRC-000052 | `SDKs/prisma_sase_sdk/index.md` | 9 (derived from rank-4 source) | SDK 6.6.2b1, generated 2026-06-28 | module map |
| SRC-000053 | `SDKs/prisma_sase_sdk/user_guide.md` | 9 | 6.6.2b1 | install, auth, pitfalls |
| SRC-000054 | `SDKs/prisma_sase_sdk/architecture.md` | 9 | 6.6.2b1 | class layout, auth flows, regions |
| SRC-000055 | `SDKs/prisma_sase_sdk/api_reference.md` | 9 | 6.6.2b1 | 969 methods: verb, API version, URL pattern |
| SRC-000056 | `SDKs/prisma_sase_sdk/_methods_extracted.json` | 9 | 6.6.2b1 | raw method extraction |
| WS-012 | `SDKs/prisma-sase-sdk-python-master/prisma_sase/*.py`, `docs/*.html`, `example.py` | 4 | 6.6.2b1 | official source |
| SRC-000057 | `SDKs/sdk-python-master/` (legacy `cloudgenix` SDK) | 4 | 6.6.2b1 | legacy lineage |
| SRC-000058 | `SDKs/cloudgenix_config-master/` (`pull_site.py`, `do_site.py`, `cloudgenix_config/`, `release_notes/`) | 4 | — | only vendor-written teardown order |
| WS-013 | `terraform/docs/prismasdwan/overview.md`, `resource-inventory.md`, `provider-index-from-repo.md`; `terraform/repos/terraform-provider-prismasdwan/docs/**` (117 files) | 4 | provider 6.6.1-beta.3 example; retrieved 2026-08-29 | service-account setup steps in SCM quoted from upstream README |
| SRC-000004 | `ai_prisma_sdwan.md` (mirror `corpus/containers/ai_prisma_sdwan.md`) | 9 | — | QA export contract; object scopes; field shapes seen live on `tenant1` |

## E. Confluence export (SRC-000091, exported 2026-07-24, internal)

- Page files: `confluence/<space>/<pageId>_<Title>.md` (mirror `corpus/confluence/...`). YAML frontmatter has `id`, `title`, `url`, `product`.
- Cite as `SRC-000091 pageId <id>`; URL pattern `https://confluence-dc.paloaltonetworks.com/pages/viewpage.action?pageId=<id>`.
- Index: `palo-alto-knowledge-base/confluence-index/sd_wan-index.md` (type-grouped) and `pages-index.jsonl` (machine; grep only).
- Workspace table of all 938 SD-WAN-relevant pages with processing status: `inventory/confluence_sdwan_pages.tsv`.
- Default exclusions: `confluence-index/retrieval-exclude.txt` (67 of the 750 `sd_wan` pages).

High-value `sd_wan` pages pre-selected for Phase 2 (all rank 9):

| pageId | Title | Words | Domain |
|---|---|---|---|
| 78890282 | (path selection — see shortcut in `kb_use.md`) | — | 3 |
| 78890365 | Performance Management | 4,104 | 3 |
| 78890478 | FEC and Packet Duplication — Digital Experience Assurance | 6,734 | 3 |
| 78890494 | Forward Error Correction (FEC) | 6,153 | 3 |
| 645427428 | SD-WAN Fabric and Routing | 5,769 | 2 |
| 852957299 | DC and Branch Routing Enhancements | 5,283 | 2 |
| 78890403 | IPv6 | 4,998 | 2 |
| 78890501 | Advanced Native Security with Prisma SD-WAN | 4,969 | 4 |
| 515613585 | Advanced URL Filtering for SD-WAN Branch Security | 4,124 | 4 |
| 906563250 | Advanced DNS Security (ADNS) Integration | 4,234 | 4 |
| 609207049 | Post-Quantum Cryptography for Prisma SASE | 6,719 | 4 |
| 516234737 | Prisma SD-WAN context-aware policy | 4,525 | 3 |
| 78889893 | Bulk Site Creation & Templates (Profiles) | 4,277 | 5/7 |
| 788071694 | ZTP Onboarding Rules | 2,418 | 7 |
| 719437975 / 447524772 | Converged SASE Seamless Branch Onboarding / SASE Seamless Branch Onboarding | 4,015 / 3,270 | 4/7 |
| 78890444 | On-premise Controller Requirements | 4,279 | 1/9 |
| 284295473 | On-Premise Controller Release 6.3.2 — Disaster Recovery | 1,656 | 9 |
| 78890027 | Prisma SD-WAN MSP 1.0 Requirements (6.0.1) | 6,349 | 9 |
| 78890517 | Brownfield Tenant and User Data (2022, huge) | 31,067 | 9 |
| 78890296 / 78890382 | ION WWAN support (LTE, 5G) | 5,947 / 4,642 | 2 |
| 78890436 | ION-NG Switching Requirements | 6,379 | 2 |
| 74187030 | Debug / Troubleshoot Device statistics connection | 3,991 | 8 |
| 74187049 | Troubleshoot Device Services: DHCP/SNMP/Syslog | 3,243 | 8 |
| 74187077 | Route Manager Debugging | 2,798 | 8 |
| 74187067 | Zone Based Firewall Debugging | 2,202 | 8 |
| 74187092 | Device offline issue troubleshooting steps (TPM) | 1,433 | 8 |
| 74187094 | Troubleshoot VPN issues | 754 | 8 |
| 74187102 | Debugging Flows with path as "NA" | 185 | 8 |
| 156632234 | Prisma SD-WAN Release Dashboard | 2,846 | 7 |
| 223448007 | Element SW Release Analytics and Actions | 2,315 | 7 |
| 545328803 | 6.8.1 Release Reference Page | 775 | 7 |
| 74187097 | How to Setup SSO via SAML | 1,041 | 4 |
| 237599551 | How to check TPM on the new generation devices x2xx | 463 | 4/8 |

SD-WAN pages in the `prisma_access` space (converged SD-WAN, internal specs): 717747608, 779858436, 795627824, 156636897, 852689419, 169084622, 795149129 (TSE Performance playbook), 719262115 (converged path selection FS), 718649824 (network policy FS), 374588395 and 176817615 (Strata playbooks: management plane, data plane), 156631532 (branch security better-together), 795617715 (topology route injection), 175767835 (brownfield onboarding use case). Full list in the TSV.

## F. Curated TSE playbooks (tree ID SRC-000153; retrieved 2026-09-28; rank 9)

Root `palo-alto-knowledge-base/prisma-sd-wan/playbooks/` (mirror `corpus/prisma-sd-wan/tse-playbooks-curated/`). Index `README.md`; hub `index/prisma-sd-wan-playbooks-hub.md` (pageId 175767979); machine index `manifest.jsonl`; images `_assets/<pageId>/`.

| Folder | Files | Page IDs (title → id) |
|---|---|---|
| `official/` | 30 | element-troubleshooting 700294090; aws-tgw-cloudblade 175768041; bgp-troubleshooting 645960289; blackhawk-cellular 891623273; branch-gateway 794506392; branch-gateway-full-mesh 917197340; cellular-connectivity 294805872; converged-sd-wan 867864901; dns-security 646388120; element-connectivity-to-controller 175768105; general-isolation 175768189; ivs 891621909; ion-fc-dpdk-stats-life-of-packet 700294454; l3-loopback-vrf-6-8-1 918315006; performance-troubleshooting 795149129; pqc 917847611; prisma-access-fic-cloudblade 175768057; prisma-access-pic-cloudblade 175768067; hub-association 177111562; rma 175768010; sd-wan-datapath-5-6-x 175768166; tsf-download 916738378; threat-prevention 645404167; url-filtering 645960986; user-id 645959526; zen-integration-cloudblade 175768088; debugging-app-detection 719443384; dhcp-snmp-syslog 700294438; ospf-troubleshooting 717730978; vrf-troubleshooting 717731234 |
| `support/` | 12 | capture-packet-on-kernel 645415316; debugging-app-detection-on-ion 559435576; fc-crash-checks 560410331; ion-fc-dpdk-stats 645969914; lens 645373930; license-activation-verification 607978252; life-of-packet-in-ion 645969919; interface-to-dpdk-port-mapping 445985041; remove-rmaed-element-shell 645388964; tenant-deletion 559039291; garuda-element-logs 609206678; vion-licenses-allocation 825506113 |
| `legacy/` | 17 | alert-100k-flows 74187098; basic-connectivity 74187081; cellular-refresh-training 373684159; runbook-prisma-access 373684246; bgp 373684186; device-allocation 373684132; element-processes-and-logs 74187112; hub-to-hub-3rd-party-tunnels 74187137; l3-reachability-detection 74187069; media-av-call 74187035; dit-playbook 295179659; playbooks 74187242; taxonomy-playbook 236810084; route-manager-debugging 74187077; services-ports-and-timers 74187026; snmp-troubleshooting 74187105; troubleshoot-device-services 74187049 |

## G. Internal PAEE datapath documents (rank 9; retrieved 2026-10-04)

Folder `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/`; sources are `.doc` exports in `confluence/` (not modified).

| ID | File | Source `.doc` |
|---|---|---|
| SRC-000098 | `data-collection-6wind-dpdk-fpvi.md` | `Data+Collection+For+6wind+Issues+(...).doc` (11 KB) |
| SRC-000099 | `data-collection-mbuf-exhaustion.md` | `Data+Collection+for+mbuf+exhaustion.doc` (9 KB) |
| SRC-000100 | `life-of-packet-datapath-on-prisma-sdwan-ion.md` | `Life+of+Packet+-+Datapath+on+Prisma+SDWAN+ION.doc` (4.08 MB; figures not extracted) |
| SRC-000101 | `lqm-uplink-pkt-loss.md` | `LQM+Uplink+Pkt+Loss.doc` (27 KB) |
| SRC-000102 | `mrl-troubleshooting.md` | `MRL+Troubleshooting.doc` (22 KB; duplicate `(1).doc`) |
| SRC-000103 | `packet-flow-in-dpdk-release.md` | `Packet+flow+in+dpdk+release.doc` (183 KB) |
| SRC-000104 | `prisma-sd-wan-troubleshooting-playbook.md` | `Prisma+SD-WAN+Troubleshooting+Playbook.doc` (35 KB) |
| SRC-000105 | `route-manager.md` | `Route+Manager.doc` (823 KB; figures not extracted) |

## H. Derived research in the KB (rank 9/10 — reasoning aids, cite the underlying SRC where possible)

| ID | Path | Date | Notes |
|---|---|---|---|
| WS-020 | `prisma-sdwan/00_EXECUTIVE_SUMMARY.md` … `23_IMPLEMENTATION_HANDOFF.md`, `07b_COMPUTED_DELETE_LAYERS.md`; JSON: `prisma_sdwan_object_catalog.json`, `prisma_sdwan_relationships.json`, `prisma_sdwan_dependency_graph.json`, `prisma_sdwan_dependency_errors.json`, `prisma_sdwan_async_operations.json`, `prisma_sdwan_all_error_codes_by_operation.json`; `prisma_sdwan_unified_api_paths.txt`. Mirror `palo-alto-knowledge-base/prisma-sd-wan/research/` (tree IDs SRC-000120–000151) | 2026-09-14 | built from SRC-000046/047, SRC-000029, SRC-000058, SDK; 14 unknowns and 6 conflicts listed in `22_UNKNOWN_GAPS.md` |
| WS-021 | `prisma-sdwan/2026-09-30-feature-review-index.md`, `-feature-release-matrix.md` (86 records), `-announcement-calendar.md`, `-feature-prerequisites-and-boundaries.md`, `-feature-source-conflicts.md`, `-feature-baseline-and-release-families.md`, `-feature-review-sources.md` (150 URLs + SHA-256), `-release-selection-lifecycle-evidence.md`, `-software-recommendation-implementation.md`, `-research-continuation-index.md` | 2026-09-30 | public docs read on that date; cite the URL and SHA from the sources file |
| WS-022 | `prisma-sdwan/research-2026-09-30/<sha12>.html|.txt` (155 HTML, 151 TXT, 4 JSON, `deliverables/`) | 2026-09-30 | cached official pages (release notes 5.6–6.8, monthly new-features Feb 2024–Sep 2026, revision history, on-prem controller) |
| WS-023 | `prisma-sdwan/prisma_sdwan_ion_bugs.json` (581 bugs; fields id, title, symptoms, conditions, workaround, affected_software, fixed_in, status, sources) and `ion-bugs/raw/{known,addressed}_{5.6,6.1,6.3,6.4,6.5,6.6,6.8}.md` | 2026-09-30 | derived from public release-note pages; cite the `sources` URL per bug |
| WS-024 | `palo-alto-knowledge-base/prisma-sd-wan/{operations,reference,configuration,automation,monitoring}/*.md` (+ `.meta.json`) | 2026-09 | authored notes: cleanup delete order, ION lifecycle state machine, site delete prerequisites, interface dependency tree, cleanup engine handoff, configuration dependency model, dependency errors and async, SCM navigation links |
| WS-025 | `.ai/kb/prisma_sdwan_dependency_research.md`, `.ai/kb/sdwan-playbooks-kb.md` | — | agent summaries |

## I. Day-2 drafts, decks, spreadsheets, screenshots (internal, rank 9, work in progress)

| ID | Path | Notes |
|---|---|---|
| WS-030 | `day2_ops/day2_ops.md` (522 KB), `day2_ops/day2_ops_humanized.md`, `day2_ops/SD-WAN Day2 Ops doc - WIP.md` (9.9 MB, images embedded) | Day 2 Operations Guide draft; scope ION 6.3–6.5 on SCM; SCM navigation checked on a live tenant 2026-09-11; contains `<<NOTE>>`/`<<VERIFY>>` markers |
| WS-031 | `new/day2_operations/day2-regeneration/06_Prisma_SDWAN_Day2_Operations_Guide.md`, `01_Review_Report.md`, `02_Gap_Analysis.md`, `04_SME_Attention_List.md`, `05_Screenshot_Capture_List.md`, `07_QA_Report.md`, `assets/` (37 PNG), `.docx` | regenerated edition and its QA trail |
| WS-032 | `day2_ops/*.docx` (12 variants) and copies under `corpus/prisma-access/day2-operations/`, `palo-alto-knowledge-base/prisma-access/operations/day2-ops/`, `.../internal-ops/day2_operations/` | duplicates; do not use |
| WS-033 | `new/day2_operations/ref/Prisma SD-WAN Technical Deep-Dive 2025 - TDM .pptx` (89 MB) | slide deck; extraction pending (B0) |
| WS-034 | `playbooks/sdwan/Prisma SD-WAN- Playbook for DS and S&O (1).xlsx` | sheets "Prisma SD-WAN Playbook", "_donottouch"; extraction pending (B0) |
| WS-035 | `day2_ops/new_docs/sd-wan-ai-transparency-datasheet.pdf` | extraction pending (B0) |
| WS-037 | `day2_ops/images/*.png` (5), `.ai/scm/reports/*.png` (96), `new/day2_operations/day2-regeneration/assets/` (37) | SCM screenshots, Sep 2026; check each for screen and version |
| WS-038 | `securecrt/commands/IONs/{Alarms,HA,Interfaces,Policy,Route,System,VPN}/__Commands__.ini` | user-authored ION CLI command packs; verify each command against SRC-000032 / release notes before citing |
| SRC-000088 | `palo-alto-knowledge-base/source-material/ingested/vff-generic-v2-test-strategy.md` (copy `prisma-sd-wan/licensing-and-requirements/VFF+Generic+V2+-+Test+Strategy.doc.md`) | internal QA |
| SRC-000089 | `.../ingested/vion-cloud-platform-automation-regression-handoff.md` (copy in `licensing-and-requirements/`) | internal QA |
| SRC-000090 | `.../ingested/prisma-sdwan-vion-licenses-allocation.md` (copy in `licensing-and-requirements/`; also TSE support page 825506113) | CONFIDENTIAL TAC runbook; licence names only, never ticket details |

## J. Governance files (routing aids; not evidence for product claims)

| Path | Use |
|---|---|
| `palo-alto-knowledge-base/source-registry.json` | SRC IDs, ranks, hashes (stale after SRC-000105) |
| `palo-alto-knowledge-base/knowledge-map.json` | product indexes, dependency graph, negative routing, topic routes |
| `palo-alto-knowledge-base/prisma-sd-wan/manifest.json` | 102 planned work units (topic checklist) |
| `palo-alto-knowledge-base/global-gap-register.json` | 31 gaps |
| `palo-alto-knowledge-base/terminology.json` | 26 terms, term issues TERM-0001..0004 |
| `palo-alto-knowledge-base/corpus/COPY_MANIFEST.jsonl` | mirror freshness |
| `.ai/prompts/kb_use.md` | retrieval specification |
| `graphify-out/graph.json`, `GRAPH_REPORT.md` | knowledge graph (built 2026-10-02) |
| `C:/Users/amir/.claude/skills/amir_prisma_sdwan/` (`SKILL.md`, `scripts/kbq.py`, `references/sdwan_topic_map.md`, `references/evidence_policy.md`) | existing skill; retrieval helper |

## K. Official public URLs (from WS-021 source inventory; not fetched in this project yet — see `00` D2)

- `https://docs.paloaltonetworks.com/prisma-sd-wan` (TechDocs root)
- `https://docs.paloaltonetworks.com/prisma-sd-wan/release-notes/<5-6|6-1|6-3|6-4|6-5|6-6|6-8>/...` (6-2 returned 404 on 2026-09-30)
- `https://docs.paloaltonetworks.com/prisma-sd-wan/new-features/by-date/prisma-sd-wan/<month-year>` (Feb 2024–Sep 2026 probed)
- `https://docs.paloaltonetworks.com/prisma-sd-wan/release-revision-history`
- `https://pan.dev/sdwan/api` (unified), `https://pan.dev/sdwan/api/legacy`
- `https://github.com/PaloAltoNetworks/terraform-provider-prismasdwan`, `https://registry.terraform.io/providers/paloaltonetworks/prismasdwan/latest/docs`
- `https://github.com/CloudGenix/sdk-python`, `https://github.com/CloudGenix/cloudgenix_config`

## L. Added 2026-10-08 after authorization: original PDFs and extracted texts

Extracted text lives in `inventory/extracted/official/<name>.txt` (pdftotext layout mode; form-feed characters separate pages, so page N is the N-th form-feed block). Cite as `[LABEL — WS-04x p.N (<title>, rev <date>)]`.

| ID | Original PDF (`E:\PC3_Shared\Palo\Documents\`) | Rank | Rev | Pages | Extracted text |
|---|---|---|---|---|---|
| WS-040 | prisma-sd-wan-activation-and-onboarding.pdf | 1 | 2024-04-12 | 30 | `official/prisma-sd-wan-activation-and-onboarding.txt` |
| WS-041 | prisma-sd-wan-incidents-and-alerts.pdf | 1 | 2023-11-04 | 92 | `official/prisma-sd-wan-incidents-and-alerts.txt` |
| WS-042 | prisma-sd-wan-ion-release-notes-5-6.pdf | 3 | 2024-01-13 | 36 | `official/prisma-sd-wan-ion-release-notes-5-6.txt` |
| WS-043 | prisma-sd-wan-ion-release-notes-6-1.pdf | 3 | 2024-06-03 | 46 | `official/prisma-sd-wan-ion-release-notes-6-1.txt` |
| WS-044 | onpremises-controller-for-prisma-sd-wan-deployment-guide.pdf | 1 | 2025-06-12 | 48 | `official/onpremises-controller-for-prisma-sd-wan-deployment-guide.txt` |
| WS-045 | prisma-sd-wan-privacy.pdf | 1 | — | 5 | `official/prisma-sd-wan-privacy.txt` |
| WS-046 | subscription-and-tenant-management.pdf (Common Services: License Activation, Subscription, and Tenant Management) | 1 | 2024-12-10 | 140 | `official/subscription-and-tenant-management.txt` |
| WS-047 | strata-cloud-manager-activation-and-onboarding.pdf | 1 | 2024-07-31 | 62 | `official/strata-cloud-manager-activation-and-onboarding.txt` |
| WS-048 | device-associations.pdf (Common Services: Device Associations) | 1 | 2024-03-08 | 30 | `official/device-associations.txt` |
| WS-049 | securing-microsoft-azure-vwan-solution-guide.pdf | 1 | — | 50 | `official/securing-microsoft-azure-vwan-solution-guide.txt` |
| WS-050a | adem-activation-and-onboarding.pdf | 1 | 2024-12-11 | 50 | `official/adem-activation-and-onboarding.txt` |
| WS-050b | autonomous-dem-administration.pdf | 1 | 2025-03-03 | 200 | not extracted yet |
| WS-050c | ai-powered-adem-release-notes.pdf | 3 | 2025-05-21 | 34 | `official/ai-powered-adem-release-notes.txt` |
| WS-051 | 00pa_all_pdf.pdf (merged compendium) | 1 | 2025-03-25 | 16,790 | not extracted |
| WS-052 | `Prisma SDWAN day0 Config Snapshots/sdwan-day0.yaml`, `sdwan-day0-raw.json` | 9 (tenant data) | exported 2026-07-11 | — | read in place; never quote identifiers |
| SRC-000029 | prisma-sd-wan-administration.pdf | 1 | 2025-05-13 | 696 | `official/prisma-sd-wan-administration.txt` (24,724 lines) |
| SRC-000032 | prisma-sd-wan-ion-cli-reference.pdf | 1 | 2021-06-24 | 444 | `official/prisma-sd-wan-ion-cli-reference.txt` |
| SRC-000030 | prisma-sd-wan-cloudblades-cloudblade-integrations.pdf | 1 | 2025-04-02 | 176 | `official/prisma-sd-wan-cloudblades-cloudblade-integrations.txt` |
| SRC-000033/034/035 | ION release notes 6.3 / 6.4 / 6.5 | 3 | — | 26 / 18 / 48 | `official/prisma-sd-wan-ion-release-notes-6-{3,4,5}.txt` |
| SRC-000036 | SDWANN best practice.pdf | 1 (treat as CORROBORATED-grade) | — | 56 | `official/SDWANN best practice.txt` |
| SRC-000031 | ION device specifications datasheet | 1 | — | 8 | `official/prisma-sd-wan-instant-on-network-ion-device-specifications_dps.txt` |
| SRC-000037 | Enterprise Connectivity — Deployment Guide Oct25 | 1 | 2025-10 | 122 | `official/Secure and Resilient ... Deployment Guide - Oct25.txt` |
| SRC-000038 | Enterprise Connectivity — Design Guide Oct25 | 1 | 2025-10 | 77 | `official/Secure and Resilient ... Design Guide - Oct25.pdf.txt` |
| SRC-000045 | SASE Network Segmentation — Solution Guide Oct25 | 1 | 2025-10 | 44 | `official/SASE Network Segmentation - Solution Guide - Oct25.txt` |

## M. Extracted binaries (batch B0)

| ID | Extracted file | Source |
|---|---|---|
| WS-033 | `inventory/extracted/WS-033_technical-deep-dive-2025.md` (505 slides + notes; Feb 2026; TME; confidential) | `new/day2_operations/ref/Prisma SD-WAN Technical Deep-Dive 2025 - TDM .pptx` |
| WS-034 | `inventory/extracted/WS-034_playbook-ds-sno.md` | `playbooks/sdwan/Prisma SD-WAN- Playbook for DS and S&O (1).xlsx` |
| WS-035 | `inventory/extracted/WS-035_sd-wan-ai-transparency-datasheet.txt` | `day2_ops/new_docs/sd-wan-ai-transparency-datasheet.pdf` |

## N. Sibling project folders (rank 9, internal; see `01` section 14.3)

`E:\PC3_Shared\Palo\COE\PRISMA_SDWAN_HA\docs\prisma-sdwan-health-assessment.md` (+ `.evidence.md`, `docs/checks/`), `PRISMA_SDWAN_MA\agnets\{evidence-policy,check-contract,lab-handoff}.md`, `PRISMA_SDWAN_DAY2_OPS\.ai\{evidence,review,handoff}`, `PRISMA_SDWAN_SnO\.ai\{evidence_index,final_validation_report}.md`, `PRISMA_SASE_SDK_CONFIG\.ai\design.md`. Never read `PRISMA_SASE_LAB\.env`.

## O. Skill packaging reference (Phase 7)

Marketplace `E:\PC3_Shared\Plugins\amir_marketplace` (`.claude-plugin/marketplace.json`, v1.2.0). Plugin `plugins/amir_system` (v1.1.8 in marketplace; 1.1.7 installed at user scope). Skill folder layout: `skills/<name>/{SKILL.md, README.md, config.json, references/, scripts/, tests/}`. Install: `claude plugin install amir_system@amir-marketplace --scope user`.
