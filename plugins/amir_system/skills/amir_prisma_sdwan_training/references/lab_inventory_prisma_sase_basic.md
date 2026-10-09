# Lab inventory — Prisma SASE Basic lab (documentation-derived, 2026-10-08)

Source of this inventory: read-only inspection of `E:\PC3_Shared\Palo\COE\Prisma_SASE_LAB\` (`README.md`, `project.md`, `CLAUDE.md` audited 2026-08-18, `labs/labs.json`, `labs/designs/prisma-sase-basic/{design.json,docs/HLD.md,docs/LLD.md,docs/lab_guide.md,docs/lab_guide2.md}`, `labs/lab_docs/General Lab User Guide.md`) and the lab-operations skills under the KB `.ai/.cursor/skills/lab-*`. **Nothing was observed live; no lab was changed; no credential, token or tenant identifier is reproduced here.** Re-verify before any course run (the lab tree changes often; `labs.json` and `doc-v2/`/`CLAUDE.md` win on conflict).

## Platform

| Item | Documented state |
|---|---|
| Hosting | One GCP VPC per lab ("POD"): 4 GNS3 server VMs + a per-lab web app (labapp: Lab Detail / Devices / Terminal / GNS3 proxy, lifecycle REST `/lab/start`, `/lab/day0`, `/lab/day1`, `/lab/destroy`, `/lab/status`) |
| Booking | Corporate Lab Hub (App Engine, other team); scenario chosen at booking; Terraform builds the POD from golden snapshots; end-of-booking cleanup wipes the SCM tenant back to Day0 and tears the POD down |
| Fleet (`labs.json`) | `dev` active (LAB_ID 0); `lab1` documentation-cook; `lab2`, `lab3` active-build; `lab4`–`lab20` planned skeletons. Each lab maps to its own Prisma SASE tenant (TSG); the parent TSG is hard-refused by automation |
| Student access | Lab App (SSO), Devices table (console/SSH/RDP/web through Guacamole), GNS3 web UI (topology, consoles, **link delay / packet loss / suspend** for failover tests), Windows PCs at BOS and DAL (RDP) |
| Baselines | **Day0** = restored golden baseline: legacy AT&T-MPLS hub-and-spoke through NGFWs, dual Internet, enterprise addressing `10.{site_id}.0.0/16`, OOB `10.10.99.0/24`; **Day1** = post-Day0 configuration layer pushed by automation per scenario |
| Scenarios (`labs.json`) | 10 Prisma SASE Basic (disabled in catalog), 11 Prisma SDWAN Basic (**enabled**; CLAUDE.md: its config files are 0-byte stubs), 12 Prisma Access Basic (enabled), 13 Complete Prisma SASE Basic (enabled). Designs: `prisma-sase-basic` (the only real one), `prisma-sase-advance` and `prisma-sase-nhrp` (disabled shells) |
| Automation status (CLAUDE.md 2026-08-18) | Day0 licensing of NGFW + vION, SCM wipe, GCP snapshots work; Day1 Prisma Access scripts partly implemented; one live cleanup failed to reclaim two vION licences (manual clear); Mobile Users / Explicit Proxy / ADEM / Remote Networks (SASE Connectivity) / DC CPE tunnels "specified but not fully implemented" |

## Topology (design `prisma-sase-basic`, GNS3 project `Prisma-SASE-Basic-v3.2`, 48 nodes / 128 links)

| Site | site_id | Prefix | IONs | NGFW | Other | WAN |
|---|---|---|---|---|---|---|
| DC1 New York (Method A: IONs on switch pair, L3 to firewalls over VLANs) | 11 | 10.11.0.0/16 | DC1-ION1/2 = 2× vION 3108 active/active hub cluster; **BGP** ION↔core on VLAN 40 (10.11.40.0/24) | DC1-FW1/FW2 HA pair | DC1-SW1/SW2, DC1-PE (VyOS MPLS), Server1 (Windows AD/DNS/DHCP/NTP/PKI 10.11.20.11), Server2 (Ubuntu Grafana/InfluxDB/Telegraf/snmpd/file 10.11.20.12) | AT&T DIA 201.1.11.0/24, Verizon DIA 202.1.11.0/24, MPLS handoff 172.16.11.0/24 |
| DC2 Los Angeles (Method B: IONs cross-connected to firewalls on physical L3) | 12 | 10.12.0.0/16 | DC2-ION1/2 = 2× vION 3108 A/A; **OSPF** ION↔core on VLAN 40 (10.12.40.0/24) | DC2-FW1/FW2 HA | DC2-SW1/SW2, DC2-PE, Server1 (AD replica 10.12.20.11), Server2 (10.12.20.12) | AT&T + Verizon DIA, MPLS 172.16.12.0/24 |
| BOS Boston | 101 | 10.101.0.0/16 | BOS-ION1/2 = 2× vION 3102, HA **with bypass** | BOS-FW1 | BOS-SW1/SW2, BOS-PE, **BOS-PC** (Windows 11) | dual DIA (AT&T + Verizon), MPLS |
| DAL Dallas | 102 | 10.102.0.0/16 | DAL-ION1/2 = 2× vION 3102, HA **without bypass** | DAL-FW1 | DAL-SW1/SW2, DAL-PE, **DAL-PC** | DIA AT&T + Broadband Verizon, MPLS |
| ATL Atlanta | 103 | 10.103.0.0/16 | ATL-ION1 = 1× vION 3102 (single) | ATL-FW1 | ATL-SW1, ATL-PE | Broadband AT&T + **LTE** Verizon (203.1.103.0/24), MPLS |
| Shared | — | — | — | — | Internet node (VyOS), AT&T-MPLS node, MGMT switch fabric, GCP-Router (OOB 10.10.99.1), DCI 10.10.12.0/24 (NGFW BGP), shared multihoming 10.10.0.0/16 | IPv6 /64s per provider also defined |

Counts from the lab guide: 9 ION devices, 7 NGFWs. Branch VLANs: 10 Users, 20 Servers, 30 Voice (DHCP relay to both Server1s), 100 IoT (ION DHCP, advertised), 666 Guest (192.168.0.0/24 at every branch, ION DHCP, local-only). DC VLANs 10, 20, 40; no DC voice VLAN.

## Design intent the lab implements (HLD/LLD, authoritative for the lab)

- Hub-and-spoke overlay to DC1/DC2; BOS↔DAL direct tunnel only after both are migrated; ATL spoke-only. MPLS is **excluded** from SD-WAN path policy; migrated sites decommission MPLS after acceptance. Migration waves: Wave 0 DCs → BOS → DAL → ATL.
- Path policy: enterprise DIA → Broadband → LTE; internet equal across circuits; User (VLAN 10) default internet via Prisma Access (Remote Networks / SASE Connectivity) with a local-DIA allow-list (Teams/Zoom media, CDN); Guest local DIA only; IoT limited to DC infra. Performance policy at Basic depth (Real-Time Media 150 ms / 2 % / 40 ms jitter; All Apps 500 / 5 % / 100).
- Zones: trust, iot, guest, infra, untrust (+ transit on Day0 NGFWs). LTE hardening at ATL: no controller use, no probes, no LQM, keep-alive 1,740,000 ms × 3, cost 129.
- Prisma Access: SC1 US East ↔ DC1, SC2 US West ↔ DC2 (two tunnels each), Remote Networks via SASE Connectivity, Mobile Users with LDAP + CIE. Out of scope for the lab design: MSP/VRF, DNS-on-ION, cloud vION hubs, CASB/DLP/RBI, DNAT, deep QoS, deep RBAC/SAML, Colo-Connect, ZTNA Connector.
- Acceptance tests ATC-01..32 (MPLS coexistence, failover, hybrid internet, zones, decrypt) and the VAL open-items register (BGP ASNs, OSPF areas, SC/RN crypto, **ION software train VAL-008**, bypass as-built, etc.) are written but unresolved.

## What this means for training labs

| Capability | Documented support | Status for courses |
|---|---|---|
| Legacy Day0 state to start a migration from (MPLS + NGFW) | Day0 as-built configs exist (`labs/designs/prisma-sase-basic/day0_config/`) | READY (documented) |
| ION claim/assign, site/circuit/interface build, control mode, overlay formation | vIONs exist in the topology; scenario 11 configs are stubs → learners build the SD-WAN configuration themselves | PARTIAL (lab-build by learners; vION licensing and claim flow handled by Day0 automation per CLAUDE.md) |
| Branch HA with bypass (BOS), HA without bypass (DAL), single ION + LTE (ATL) | Designed and wired per HLD/LLD; VRRP/bypass as-built values are VAL items | PARTIAL / UNVERIFIED |
| DC BGP (DC1) and OSPF (DC2) ION↔core, MPLS coexistence via NGFW | Designed; ASNs/areas VAL | PARTIAL |
| Failover and impairment tests | GNS3 link suspend / delay / loss documented in the General Lab User Guide | READY (mechanism) |
| Monitoring targets (Grafana/InfluxDB/Telegraf/snmpd on Server2) | Documented as-built on DC1-Server2 | READY (documented), UNVERIFIED live |
| Prisma Access integration (SASE Connectivity, SCs, Mobile Users) | Specified; automation "not fully implemented"; scenario 12 enabled | PARTIAL / UNVERIFIED |
| VRF segmentation, branch gateway, DNAT, deep QoS, Branch Security (CDSS), API automation against the lab tenant | Out of scope of the lab design or absent | MISSING (API: tenant per lab exists, so read-only API labs are plausible → UNVERIFIED) |
| Multi-tenant / MSP | Each lab has its own tenant; MSP hierarchy not documented | MISSING |
| ION software version | VAL-008 unresolved | UNVERIFIED (ask the owner) |

Credentials, port numbers and tenant identifiers live in the lab documents and the Lab App; curriculum files refer to them by role only.
