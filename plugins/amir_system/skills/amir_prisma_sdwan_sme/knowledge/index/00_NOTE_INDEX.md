# Index — one line per note (Phase 5, 2026-10-08)

Label mix counts rows of each note's claims register: **V** VERIFIED, **C** CORROBORATED, **I** INFERRED, **U** UNVERIFIED (internal), **X** CONFLICTED, **O** OBSOLETE. "Floor" = oldest release or document date the note's facts apply to. Gaps = KG IDs the note carries (see `04_KNOWLEDGE_GAPS.md`, consolidated in `05_UNRESOLVED_QUESTIONS.md`).

## Domain 1 — Fundamentals (`notes/01-fundamentals/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-architecture-and-planes | controller, ION, management/control/data planes, controller connections, certificates, on-prem controller mention | ION 6.x; SCM; admin guide May 2025 | 8/1/0/4/0/0 | KG-060, KG-061 |
| 02-deployment-modes-and-insertion | Analytics / Control / Disabled; insertion models; DC-capable models | ION 6.x | 5/0/0/3/0/0 | KG-062 |
| 03-tenancy-tsg-activation | tenants, TSG ("a tenant is just a TSG"), activation, regions | Common Services docs 2024–2025 | 8/0/0/1/0/1 | KG-040 (closed), KG-046 |
| 04-licensing-and-subscriptions | subscription model, tiers, add-ons (ZBFW, DVR, WCR), usage; Design Guide Table 13 addendum | 2024–2025 docs | 10/0/0/1/0/0 | KG-005, KG-126 |
| 05-ion-models-hardware-virtual | current and older models, cellular variants, vIONs, throughput conflicts; Gen-1 lifecycle addendum | datasheet 2025-11-17; Design Guide Oct 2025 | 9/0/0/2/1/0 | KG-003, KG-063 |
| 06-sites-and-object-model-overview | sites, domains, clusters, object scopes, branch creation, branch gateway prerequisites | admin guide May 2025 | 5/1/0/2/0/0 | KG-064 |
| 07-controller-releases-and-maintenance | controller release cadence, maintenance, who upgrades what | admin guide May 2025 | 2/1/0/0/0/0 | KG-065 |
| 08-device-onboarding-claim-assign | connect/claim/assign, states, shells, offline OTP, toolkit roles | admin guide May 2025 | 5/1/0/1/0/0 | KG-046, KG-066 |
| 09-lifecycle-rma-templates-msp | unassign/return/RMA, site templates, MSP roles and device lifecycle | admin guide; API 6.6.2 state names | 12/0/0/2/0/0 | KG-067, KG-068 |

## Domain 2 — Network (`notes/02-network/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-circuits-categories-wan-networks | circuits, 32/32 categories, labels, WAN networks, monitoring switches, cost, excluded paths | ION 5.4.1+ keep-alives | 7/1/0/3/1/0 | KG-070, KG-071 |
| 02-ports-and-interfaces | port roles, bypass pairs, sub-interfaces, loopback, virtual, port channel, PoE, LLDP, PPPoE, L3 LAN | floors 5.1.1…6.6.1 | 15/0/0/3/1/0 | KG-072, KG-073, KG-074 |
| 03-cellular-interfaces | LTE/5G modems, SIM/APN/PIN, switchover, firmware, monitoring | network selection 6.5.1 | 8/0/0/1/0/0 | KG-075 (closed) |
| 04-standard-vpn-ipsec-gre | standard VPN to third parties, DC-to-DC standard VPN, passive mode, 4500→4501 | admin guide May 2025 | 4/0/0/0/0/0 | KG-076 |
| 05-vpn-keepalives-bfd-lqm-settings | keep-alive ranges/precedence, BFD mode, LQM/BW monitoring switches | 5.4.1+ | 3/0/1/1/0/0 | KG-011, KG-071 |
| 06-fabric-topologies-dc-clusters-branch-gateway | DC clusters, inter-DC/inter-branch fabric (6.5.1), prefix filters, ciphers (GCM 6.5.1), branch gateway (6.4.1), full mesh (6.8.1 internal); Design Guide matrices addendum | 6.4.1 / 6.5.1 / 6.8.1 | 7/1/0/3/0/1 | KG-064, KG-077 |
| 07-branch-ha-and-dc-redundancy | HA groups, priorities, tracking, topologies per generation, DC active-active | used-for-HA 6.3.1; SVI auto-op 6.4.1 | 7/0/0/3/0/0 | KG-011, KG-078 |
| 08-routing-static-bgp-ospf | branch/DC routing models, static probes, BGP defaults, peer types, route maps, OSPF (6.4.1); prefix-splitting addendum | LAN routing 5.2.1; OSPF 6.4.1 | 7/1/0/4/0/0 | KG-079, KG-080 |
| 09-vrf-segmentation | VRF profiles, leaking, per-VRF DIA NAT, 6.3.1 limits (internal), 6.8.1 loopbacks | VRF 6.3.1 | 3/0/0/3/1/1 | KG-081 |
| 10-multicast | LAN/WAN multicast, RP, profiles, SPT | 5.6.1 / 6.0.1 / 6.1.1 / 6.2.1 | 5/0/0/1/0/0 | — |
| 11-nat-policies | NAT stacks/sets/rules/zones/pools, use cases, branch-only | admin guide May 2025 | 4/1/0/2/0/0 | KG-082 |
| 12-cloud-deployments-and-cloudblades | AWS TGW / Azure vWAN / GCP NCC CloudBlades, Zscaler, lifecycle rules; Azure guide identity addendum | CloudBlades guide 2025-04-02 | 6/0/0/2/0/0 | KG-030 (closed), KG-083 |

## Domain 3 — Application traffic (`notes/03-application-traffic/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-applications-and-identification | 4,000+ apps, custom L3/L4 and L7 apps, overrides, unreachability detection, scan apps | unified App-ID 6.0.1 | 5/0/0/1/1/0 | KG-084 |
| 02-path-policy-and-path-selection | stacks (6.0.1), rule fields, SLA-compliant vs best path, active/backup/L3 failure, metered LTE recipe, selection inputs | 6.0.1; IPv6 rule 6.2.1 | 9/1/0/2/0/1 | KG-085, KG-086 |
| 03-service-dc-groups-domains-network-contexts | endpoints, groups, domains, network contexts, path/QoS prefixes | admin guide May 2025 | 6/0/0/1/0/0 | KG-064 |
| 04-qos-circuit-capacities-dscp | QoS classes/queues, bandwidth allocation, DSCP, HFSC note | admin guide May 2025 | 3/1/0/0/0/0 | — |
| 05-performance-policy-fec-packet-duplication | SLAs, Move Flows, FEC, duplication, system health; Best Path 6.4.2 addendum | perf policy 6.3.1; 6.4.1 additions | 10/0/0/1/1/0 | KG-087, KG-088 |
| 06-measurement-lqm-probes-reachability | real-traffic metrics, app probes, L3 reachability, service health probes (6.4.1), LQM runbook | admin guide pp.540–549 | 6/0/0/1/0/0 | KG-011, KG-071 |
| 07-app-acceleration | L4 optimisation (6.4.2), SaaS L7 acceleration (6.5.2), licence | 6.4.2 / 6.5.2 | 3/0/0/1/0/0 | KG-089 |

## Domain 4 — Security (`notes/04-security/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-zbfw-stacked-security-policies | zones, stacks, rules, default rules, bindings, OOM guidance | stacked 6.0.1; ION 5.6+ | 8/0/0/3/0/1 | KG-090, KG-091 |
| 02-user-id-cie-device-id | User-ID agent model, Cloud User-ID (6.6.1 internal), CIE groups, Device-ID | 6.2.1 / 6.5 / 6.6.1 | 3/0/0/3/0/0 | KG-092, KG-093 |
| 03-branch-security-cdss | CDSS on ION, Security Profile Groups, SLS logging, model list, floor conflict | 6.5.1-I vs 6.5.3-I | 2/0/0/2/1/0 | KG-094, KG-095 |
| 04-iot-device-visibility | DHCP/ARP logging, SNMP/LLDP discovery (6.3.1) | 6.2.1 / 6.3.1 | 4/0/0/1/0/0 | — |
| 05-admin-access-rbac-tacacs-radius-audit | roles, toolkit users, 802.1X/MAC (6.0.2), audit logs, TACACS+ (6.5) | admin guide pp.333–367 | 7/0/0/0/1/0 | KG-096, KG-097 |
| 06-prisma-access-integration-easy-onboarding | Easy Onboarding, SASE Connectivity, legacy FIC/PIC, hub association, API family | ION 5.6.x+; 6.4.2 / 6.5 | 7/0/0/4/0/0 | KG-098, KG-099, KG-100 |
| 07-converged-sdwan-ngfw-hub | PAN-OS NGFW as SD-WAN DC (internal only) | PAN-OS 12.1.2 + ION 6.5.2 (internal) | 0/0/1/1/0/0 | KG-045 |
| 08-post-quantum-cryptography | PQC design intent; **shipped 6.8.1** (addendum) | 6.8.1 | 0/1/0/1/0/0 | KG-101 (closed) |
| 09-sso-saml-service-accounts-tpm-cli-access | SAML SSO, service accounts, CLI access, elem-admin, TPM | admin guide pp.335–340, 688–691 | 2/0/0/3/0/1 | KG-066b, KG-096, KG-097, KG-102 |

## Domain 5 — SCM (`notes/05-scm/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-navigation-map-version-scoped | three UI generations, mapping table, quoting rules | May 2025 guide vs Aug 2025 Nav 3.0 | 2/1/1/2/0/0 | KG-046, KG-103, KG-104 |
| 02-dashboards-monitoring-screens | dashboards, thresholds, licences, time ranges, freshness | admin guide pp.30–56, 633–640 | 6/1/0/2/0/0 | KG-105, KG-106 |

## Domain 6 — API and automation (`notes/06-api-automation/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-unified-api-authentication-conventions | unified vs legacy, OAuth, profile call, etag, query DTO, monitor header | OpenAPI 6.6.2 | 6/2/0/0/0/0 | KG-107, KG-108, KG-109 |
| 02-api-object-model-scopes-versions-async-errors | scopes, versions, operations, async enums, dependency errors | OpenAPI 6.6.2; WS-020 | 1/2/0/2/0/0 | KG-044, KG-110 |
| 03-sdks-tooling-terraform-config-utility | prisma-sase / cloudgenix SDKs, cloudgenix_config, Terraform provider | SDK 6.6.2b1; TF 6.6.1-beta.3 | 5/0/1/0/0/0 | KG-111 |

## Domain 7 — Operations (`notes/07-operations/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-incidents-alerts-event-codes | model, correlation, site connectivity, incident policies, event-code table | Incidents guide Nov 2023/2025 | 8/1/0/1/0/0 | KG-112, KG-113 |
| 02-external-services-ipfix-syslog-snmp-dns-ntp-dhcp | IPFIX, syslog/flow logs, SNMP, DNS service, NTP, DHCP | admin guide pp.264–313 | 6/0/0/1/0/0 | KG-114 |
| 03-software-upgrades-release-lifecycle | scheduling, upgrade paths 6.5/6.8, considerations, lifecycle | RN 6.3/6.4/6.5; public 6.6/6.8 | 5/1/0/1/0/0 | KG-065, KG-115, KG-116 |
| 04-feature-chronology-6x | feature-release matrix Feb 2024–Sep 2026 with evidence classes | WS-021 public pages | 4/0/0/0/0/0 | KG-077, KG-087, KG-094, KG-101, KG-117 |

## Domain 8 — Troubleshooting (`notes/08-troubleshooting/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-golden-workflow-isolation-escalation | isolation order, evidence, escalation, RMA triage, taxonomy | TSE playbooks 2024–2026 | 2/2/0/5/0/0 | KG-060, KG-079, KG-118 |
| 02-cli-command-reference-by-problem-area | command families, roles, key commands, release deltas | CLI reference 2025 ed.; RN 6.3–6.5 | 5/1/0/2/0/0 | KG-119 |
| 03-controller-connectivity-device-offline-onboarding | offline causes, TPM, MTU, proxy, four connections | playbooks 2024–2026; incidents guide | 3/0/0/3/0/0 | KG-060, KG-118 |
| 04-performance-app-detection-services-cellular | speedtest, SCP test, memory/FC, app detection, DHCP/SNMP/syslog, cellular, Blackhawk | playbooks 2026 | 0/1/0/4/0/0 | KG-120, KG-121 |
| 05-branch-security-troubleshooting | Threat Prevention, DNS Security, URL Filtering, IVS | playbooks 2025–2026 | 0/0/0/6/0/0 | KG-094, KG-122 |

## Domain 9 — Datapath internals (`notes/09-datapath/`) — internal only

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-datapath-architecture-ovs-vs-dpdk | OVS 5.6.x vs DPDK 6.x, queues, 6.3.6 protection, Gen-2 SR-IOV | PAEE 2024–2026 | 0/0/0/3/0/0 | KG-072, KG-123 |
| 02-datapath-diagnostics-fc-debug-dpdk-counters-route-manager-mrl | FC debug, stage counters, cores, VPN internals, route manager, MRL | TSE/PAEE 2016–2026 | 0/0/0/6/0/0 | KG-124, KG-125 |

## Domain 9 — Design (`notes/10-design/`)

| Note | Scope | Floor / basis | V/C/I/U/X/O | Gaps |
|---|---|---|---|---|
| 01-reference-architecture-enterprise-connectivity-design-guide-oct2025 | official reference design, platform tables, link matrices, HA, policies, routing, Prisma Access, licensing, Azure | Design Guide Oct 2025 | 4/0/0/1/1/1 | KG-030, KG-063, KG-079, KG-088, KG-126, KG-127 |
| 02-deployment-blueprint-greenfield-with-prisma-access-oct2025 | validated procedure order, parameters, warnings, HA branch, Prisma Access bypass set | Deployment Guide Oct 2025 (SCM 2025.r3.0, ION 6.5.2) | 3/0/0/0/0/0 | KG-103, KG-128, KG-129 |
| 03-segmentation-zones-subinterfaces-guest-design | zone model, subinterfaces, rule matrix, guest pattern | Segmentation guide Oct 2025 | 3/0/0/0/0/0 | KG-130 |
| 04-msp-multitenant-cloud-manager-and-on-premises-controller | multitenant platform, device/vION allocation, bulk config; on-prem controller sizing | Oct 2024 / Jun 2025 | 2/0/0/1/0/0 | KG-131 |
| 05-design-anti-patterns-and-review-checklist | 32 labelled anti-patterns; review checklist | mixed | per-row labels | KG-063, KG-083, KG-132 |

## Totals

58 notes; claims-register rows: 280 VERIFIED, 23 CORROBORATED, 4 INFERRED, 107 UNVERIFIED (internal), 9 CONFLICTED, 7 OBSOLETE. Internal-only notes (no VERIFIED rows): 04-security/07, 04-security/08 (before the 6.8.1 addendum), 08-troubleshooting/04–05, 09-datapath/01–02, 10-design/05 (per-row).
