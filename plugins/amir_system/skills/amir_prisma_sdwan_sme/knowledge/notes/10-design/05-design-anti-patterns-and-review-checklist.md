# Design anti-patterns and design-review checklist

Domain: 9 (design) | Sources: official design/deployment guides SRC-000037/038/045 (Oct 2025), admin guide SRC-000029, internal best-practices guide WS-001 (May 2026), TSE playbooks | Status: mixed; every row labelled | Last updated: 2026-10-08

## Explanation (plain words)

An SME reviewing a Prisma SD-WAN design looks for a known set of mistakes. This note lists them with the documented consequence and the source quality, so the skill can say "this is an official caution" versus "this is internal field guidance". The checklist at the end is the set of inputs a reviewer must collect before judging a design.

## Anti-patterns (what, why, label)

| # | Anti-pattern | Documented consequence / correct practice | Label, source |
|---|---|---|---|
| 1 | Binding network or security policy to data-center sites, or using DC IONs for anything but aggregation | Not possible; DC↔branch traffic uses branch policy; use DCs only to interconnect branches | VERIFIED, SRC-000038 pp.24, 54 |
| 2 | Binding a security stack before every network/subinterface has a zone | ZBFW drops traffic on zone-less interfaces ("one of the most common ZBFW mistakes") | VERIFIED SRC-000038 p.48 / SRC-000045 p.14; UNVERIFIED-internal emphasis WS-001 |
| 3 | Site-level and device-level zone bindings at the same time | Device-level wins on conflict; mixing complicates troubleshooting; prefer device-level | VERIFIED (recommendation) SRC-000038 p.48; detail UNVERIFIED WS-001 |
| 4 | Security rules with empty source or destination zones | Huge policy tables at compile time → OOM/instability on ION 1000/1200/2000; always set both zones | UNVERIFIED (internal) WS-001; consistent with WS-001 OOM guidance in note 04-security/01 |
| 5 | Mixing application matching with port/prefix matching in one security rule; large /32 prefix lists in custom apps paired with broad port ranges | Hard to audit; policy-table bloat (each /32 multiplies across zones and ports) | UNVERIFIED (internal) WS-001 |
| 6 | Destination NAT without a matching ZBFW allow rule | Default deny drops the translated traffic | UNVERIFIED (internal) WS-001 |
| 7 | Extra catch-all path rules duplicating the built-in default / enterprise-default | Complexity, shadows specific rules | UNVERIFIED (internal) WS-001 |
| 8 | Metered cellular inside default or enterprise-default rules | Unplanned billing; put LTE in a dedicated rule or as **L3 failure** path only; "Minimize Cellular Usage" covers only inbound/control traffic | UNVERIFIED (internal) WS-001; L3-failure semantics VERIFIED SRC-000038 p.43 |
| 9 | Same circuit category on two circuits at one site | Cannot distinguish them in policy; one category per circuit per site | UNVERIFIED (internal) WS-001; "one network per category" VERIFIED SRC-000038 p.31 |
| 10 | Active/Backup for two internet circuits expecting legacy behaviour | Backup is used on reachability/LQM breaches too; idle bandwidth; prefer Any Public active (Best Available Bandwidth), or use L3 Failure for true last-resort | VERIFIED semantics SRC-000038 p.43; recommendation UNVERIFIED WS-001 |
| 11 | No DC service groups/domains when a DC is a transit point; branches not assigned to domains | ION has no transit decision without a more specific route; per-domain primary/secondary needed | VERIFIED SRC-000037 pp.76–77, SRC-000038 p.23; UNVERIFIED detail WS-001 |
| 12 | No explicit path rule for Prisma SD-WAN control applications (paloalto-prisma-sdwan-base; pan-db-cloud, paloalto-dns-security with Branch Security) above the defaults; SSL decryption on the control path | Controller connectivity and probes interrupted by policy; add the rule allowing all paths; exclude controller FQDN/IPs from decryption | UNVERIFIED (internal) WS-001; official analogue: Prisma Access bypass set for HA sites SRC-000037 pp.117–120 |
| 13 | Default path set bound to a site lacking either a public or a private circuit | Major alarm; clone and trim the default set | VERIFIED SRC-000037 p.70 |
| 14 | Leaving 192.168.0.0/16 in enterprise prefixes while the Prisma Access infrastructure subnet is 192.168.255.0/24 | Users cannot reach addresses in that range correctly; remove the summary unless used | VERIFIED SRC-000037 p.24 |
| 15 | Direct Ethernet cable between HA control interfaces | Backup never becomes active when the active is powered off | VERIFIED SRC-000038 p.38 |
| 16 | ION 1000/1200 as HA backup with a /30 WAN subnet | Internet ports are not suppressed; need ≥ /29 per WAN circuit | VERIFIED SRC-000038 p.38 |
| 17 | DC ION pair without a default/WAN summary route to the core | Branches homed on different DC IONs cannot reach each other | VERIFIED SRC-000038 p.41, SRC-000037 p.76 |
| 18 | Undersized DC ION pair (each cannot carry all branches) | Degraded mode during failure | VERIFIED SRC-000038 p.40 |
| 19 | Assigning a DC device via the device view in a multi-cluster design | Lands in the default cluster; must unassign and reassign via DC clusters view | VERIFIED SRC-000038 p.42 |
| 20 | Switching between simple and advanced policy stacks repeatedly | Toggle affects all four policy types and is time-consuming | VERIFIED SRC-000037 p.71 |
| 21 | Assigning a device whose software state is "Software Unknown" | Site assignment fails; recheck SW version first | VERIFIED SRC-000037 p.29 |
| 22 | Using default circuit bandwidth values | QoS shapes to wrong values; set carrier values, 1–2 % below rated; DC values informational only | UNVERIFIED (internal) WS-001 |
| 23 | Editing CloudBlade-managed objects; using the Prisma Access CloudBlade for new integrations | Inconsistencies/breakage; use SASE Easy Onboarding for new deployments | UNVERIFIED (internal) WS-001; Easy Onboarding is the official path SRC-000038 p.54 |
| 24 | Cloud DC vION without site-level prefixes / Global scope, or BGP multihop ≠ 2 | Prefixes not advertised; peering fails (cloud router never adjacent) | UNVERIFIED (internal) WS-001 (KG-083) |
| 25 | Both DC IONs behind NAT with dual tunnel initiators (cloud-to-cloud or DC-to-DC fabric) | IKE collisions/instability; Initiator-only (TAC) + Passive mode, 6.5.2+, no NATed IP or NLB on the initiator | UNVERIFIED (internal) WS-001 |
| 26 | More than two branch gateways in full mesh, or multiple DCs with branch gateways, without prefix-based steering | Implicit prefix reflection → asymmetry/one-way traffic; workaround prefix path policies | UNVERIFIED (internal) WS-001; see note 02-network/06 |
| 27 | Private L2 bypass insertion for new designs | Legacy model; L3 deployments recommended | VERIFIED SRC-000038 p.30 |
| 28 | Standard VPN (service links) configured on DC IONs for policy-driven use | DC sites cannot carry network policy; configure on branches | VERIFIED SRC-000038 p.30 |
| 29 | Disabling multicast SPT switchover; SNMPv1/v2c in production | RP load/latency; cleartext community strings | UNVERIFIED (internal) WS-001 |
| 30 | Network context used as isolation | Inter-context traffic permitted by default; needs zone + security policy, or VRF for true isolation | VERIFIED SRC-000038 pp.34–35 |
| 31 | Expecting IPv6-only interfaces or IPv6-preferred fabric | IPv4 required first; IPv4 path preferred | VERIFIED SRC-000038 p.33 |
| 32 | Trace-level FC debug left enabled, probe-table floods, single heavy flow per core | Datapath starvation, "monitor files", FC restarts | UNVERIFIED (internal) notes 09-datapath/01–02 |

## Design-review checklist (inputs to collect)

1. Sites: count by type (DC, branch, branch gateway), regions/domains, planned DC clusters and soft limits, brownfield vs greenfield (analytics first?).
2. Circuits per site: categories, providers, bandwidth up/down, metered links, "use for controller connections", NAT in front of internet ports (external NAT IP/port 4500).
3. Platforms: model per site vs recommended throughput range (carry the KG-063 conflict), controller port presence, bypass pairs, HA pairs same model, licence tier per branch device, DVR/WCR/ZBFW add-ons.
4. Addressing: enterprise prefixes (non-RFC-1918 additions, Prisma Access infrastructure subnet overlap), site prefixes per DC, global vs local scope on LAN interfaces and static routes, guest subnet reuse.
5. Routing: DC peer types (core/edge/classic), BGP timers 1/3 at DC, MD5, default/summary route to core on each DC ION, prefix splitting expectations, branch default gateways vs BGP/static, L3 Direct Private WAN / L3 LAN forwarding flags, probe source interface.
6. Overlay: default hub-and-spoke vs branch-to-branch links, MPLS direct override, inter-DC fabric (6.5.1+), branch gateway count and mesh.
7. Policy: stack mode (simple/advanced), per-site-type path sets, DC groups on enterprise-default, DIA model (direct, DC backhaul, Prisma Access as standard VPN with All/Backup Regions), control-app rule, cellular placement, QoS class budgets, performance SLAs and actions.
8. Security: zone model and matrix, device-level bindings incl. auto-created service links, built-in rule reliance, User-ID/CIE needs, Branch Security licensing and supported models.
9. Prisma Access: deployment mode (Internet-Only vs Private-App-Access vs with mobile users), local AS, tunnel pool, compute-location bandwidth (≥50 Mbps), ECMP circuits, location pairs, security policy for DIA apps.
10. Operations: management path (controller port vs ZTP port), HA control interface design, syslog/SNMP/IPFIX targets, upgrade path to the target release (6.5.x or 6.8.x), on-premises controller or MSP hierarchy if applicable.

## Claims register

See per-row labels above; rows marked UNVERIFIED (internal) must be presented as field guidance, not as Palo Alto Networks requirements.

## Open questions

- KG-132: official statements for rows 4–9, 12, 22 (internal only today); candidates under D2: Live Community best-practice articles and the admin guide policy chapters.
