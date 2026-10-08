# Reference architecture: "Secure and Resilient Enterprise Connectivity Using Prisma SD-WAN" Design Guide (Oct 2025)

Domain: 9 (design) | Applies to: SRC-000038 Design Guide Oct 2025 (77 pp; validated with SCM 2025.r3.0, Prisma Access 6.0.0 Preferred, ION 6.5.2 per the companion Deployment Guide SRC-000037 p.15); Azure solution guide SRC-000010 Sep 2023 | Status: VERIFIED (official reference architecture, rank 1) | Last updated: 2026-10-08

## Explanation (plain words)

Palo Alto Networks' own reference design for a Prisma SD-WAN enterprise WAN is simple: **data-center sites are pure aggregation hubs** (no network or security policy can be bound to them), **every branch is a spoke** in a hub-and-spoke overlay that the controller builds automatically, policies live on branches, and **direct internet access (DIA) is secured by Prisma Access** reached as a standard VPN endpoint, not by a default route. Resiliency at the hub comes from a pair of independent IONs plus fast BGP, not from an HA protocol; at the branch it comes from an HA group with hardware bypass pairs. This note records the design rules and numbers the guide states, so that a design review can say "matches the reference architecture" or "deviates, here is the documented consequence".

## Constructs and global design inputs (pp.22–23, 34, 50)

- Elements: cloud management (per-tenant controller hosted in SCM, pushes config to devices via APIs), sites (data-center and branch), modes (analytics, control), devices, interfaces, secure fabric links and service links, traffic classes (enterprise vs non-enterprise), endpoints/domains/service groups, HA and scaling, network/performance policies, security (ZBFW), circuits.
- **Global parameters to settle before any site**: enterprise prefixes (default RFC 1918; enterprise traffic = destination inside the list), domains, circuit categories, service providers, bandwidth per site, IP addressing, NAT and security zone assignments (p.50).
- **Endpoints, domains, service groups** (p.23): a Prisma SD-WAN endpoint is a data-center site (auto-created); a standard VPN endpoint (e.g. Prisma Access) is created manually, can carry IP ranges/FQDNs, liveliness probes and an "allow enterprise traffic" choice. A domain is any grouping of sites (typically regions; preset domain catches unmapped sites). A service group's membership is per domain, so one policy ("Primary-DC / Secondary-DC") resolves to different data centers per region (Table 1).

## Sites and modes (pp.23–24)

- Data-center sites aggregate and transit (including between discontiguous regional MPLS networks). Policies bind to branches only; DC↔branch traffic uses the branch's policy. Recommendation: use data-center sites **only** to interconnect branches.
- Routing between sites comes from **site prefixes** propagated by the controller, not from inter-site dynamic routing.
- Default topology is hub-and-spoke with branch-to-branch via hubs; direct branch-to-branch secure fabric links are optional. **Branch gateway** = branch that also acts as regional hub; branches in the region auto-build links to it; an existing branch can be converted.
- Analytics mode (monitor only, no DC needed) vs control mode (builds fabric VPNs to all DC sites over all WAN paths; policies enforced). Brownfield: analytics first; greenfield: control (p.74).

## Devices and platforms (pp.25–27)

- Hardware IONs authenticate by serial number, virtual IONs by SCM-generated token; ZTP through a controller port or a **ZTP-capable port** (ports 1–2, DHCP internet by default). Unclaimed device shows **online-restricted**; claim, then assign to a site before full configuration.
- Table 2 (branch hardware): ION 1200 and 1200-S "up to 250 Mbps" recommended range; 1200-S has 4 WAN/internet + 6 LAN ports, one bypass pair (3/4), PoE ports 7–10, SFP/RJ-45 combo ports 1–2, LTE/5G variants (1200-C-NA/ROW, 1200-S-C-NA/ROW, 1200-S-C5G-WW); neither has a controller port.
- Table 3 (DC-capable hardware): ION 3200 and 3200H (temperature-hardened) up to 600 Mbps DC mode / 500 Mbps branch mode, 10 or 8 ports, one bypass pair; ION 5200 up to 1.5 Gbps DC / 1 Gbps branch, 15 ports, 4 bypass pairs, 4×10GE SFP+; ION 9200 up to 6 Gbps DC / 3 Gbps branch, 15 ports, 4 bypass pairs, 10×10GE SFP+, PoE 9–12. All have ZTP ports 1–2.
- Table 4 (virtual): 3102v up to 700 Mbps (2 vCPU/8 GB/40 GB), 3104v 1.1 Gbps (4 vCPU), 3108v 1.8 Gbps (8 vCPU), 7108v 3 Gbps, 7116v 10 Gbps; 3100v series up to 9 interfaces with virtual bypass pair support. **These numbers conflict with the Nov 2025 datasheet** (KG-063; see note 01-fundamentals/05).
- Controller port: all models except ION 1000 and 1200 have one; use it when connecting into an existing network (p.50). Static controller-port IP at first boot requires console + toolkit (p.27).

## Interfaces, bypass pairs, standard VPN, L2/L3 interfaces (pp.27–30)

- DC device ports: **internet** or **peering** (private LAN/WAN). Branch ports: internet, private WAN, LAN. Behind NAT: supply the external NAT IP on the internet port (DC always; branch when it will terminate branch-to-branch links).
- Per-interface FIB: different default gateways per interface; static routes rarely needed to build links. All internet ports need a default gateway; on branches a default gateway on the private WAN port simplifies routing.
- Bypass pairs (branch only): hardware (relay, strict port pairing) or virtual; usages Internet/Private WAN (ION routes), **Private L2 (legacy, transparent, not recommended)**, LAN (HA cluster only). Controller ports cannot join a virtual bypass pair.
- Standard VPN (IPsec or GRE) with default third-party IPsec profiles; recommended only on branch devices because DC sites cannot carry policy.
- VLAN vs SVI (IP assigned), loopback (always-up address for BGP peering, VPN termination, SSH, syslog source), port channel (L3 LAN LAGs on ION 3200/5200/9200).

## Circuits and link matrices (pp.31–33)

- **32 public and 32 private circuit categories**; category holds VPN keep-alive interval and failure count. One network per category; two providers of the same type → rename an unused category. Per-site circuit settings: bandwidth, LQM, QoS, BFD mode.
- DC port: one public circuit, or **one or more private WAN circuits** (Table 5). Branch port: exactly one circuit (Table 6).
- Secure fabric links (Table 7): branch public ↔ DC public = all-to-all, automatic; branch private ↔ DC private = all-to-all **within the same circuit category**, automatic; branch public ↔ DC private not applicable; branch public↔branch public and private↔private selectively enabled; **never between data-center sites** (this guide; inter-DC fabric from 6.5.1 is in the admin guide, note 02-network/06). Table 8: same pattern towards an in-region branch gateway; other-region branch gateway only selectively.

## Protocols (p.33)

IPv4 everywhere; IPv6 only after IPv4 on the same interface (IPv6-only unsupported); dual-stack fabric links prefer IPv4 and fail over to IPv6. Multicast: branch LAN senders/receivers, WAN receive only; DC receives from peers and sends to branches over public VPNs; RP + multicast on one L3 interface for LAN, WAN multicast profile per branch + enable on DC ION.

## Segmentation constructs (pp.34–36)

- **Network contexts**: policy differentiation per interface community; **no isolation by themselves** (inter-context traffic permitted by default) → add a zone and security policy. Uses: guest (Local scope lets every site reuse one guest subnet), per-source application policy, differentiated QoS for a shared app.
- **VRF instances**: true isolation, VRF ID carried across the fabric, Global VRF default; route leaking off by default and configured in the VRF profile with paired rules plus routing changes; uses: business units, overlapping address ranges (acquisitions).

## High availability and scaling (pp.36–43)

- Branch HA group: two IONs, priority 1–254 (higher = preferred active; example 50/45), same platform; **HA control interface** = controller port if present, else any static L3 interface; same IPv4 subnet, unique static IPs, via external switch(es) on a common VLAN (SVI control needs trunk ports allowing the VLAN); **never a direct cable** (a powered-off active leaves the backup's link down so it never goes active). Backup suppresses IP config on LAN/internet/private-WAN ports (up, no IP, no traffic); duplicate static IPs allowed; **ION 1000/1200 as backup do not suppress internet ports → /29 minimum per WAN circuit**; complete HA setup before cabling LAN/WAN when IPs are duplicated. Bypass pairs: active device WAN port active and LAN port isolated; backup device WAN inactive and bridged to its LAN port → cross-connected design keeps both WAN links active without an external WAN switch.
- Data-center HA: no HA groups; SCM auto-creates one DC cluster; devices independent (no state sharing); each branch picks the DC ION whose link came up first; size each DC ION to carry **all** branches alone; unique IPs; BGP session from every core router to every ION with **keepalive 1 s / hold 3 s**; each DC ION needs a **default or WAN summary route to the core** so branches active on different IONs can reach each other.
- Scaling: multi-cluster DC design to distribute branches (regions) and bound failure impact; **cluster soft limit** only notifies; first cluster is the default cluster; assign devices via the DC clusters view (advanced site settings) or they land in the default cluster; branch can be mapped to a specific cluster or to **no cluster** (no VPNs to that DC); migrating a branch between clusters causes a brief disruption.

## Policies (pp.43–49)

- Stacks: default set + up to four sets for path, QoS, security, NAT; applied to branches only; DC IONs enforce **routing symmetry** (return on the ingress path).
- Path hierarchy: WAN networks at the site → filtered by policy and reachability → active paths with automatic best-path per application; **backup only when no active path can be used; L3 failure path only when all active and backup lost L3 reachability**. Path types: Direct, Prisma SD-WAN VPN, Standard VPN; generalise by circuit category (Any Public/Any Private) or pin to circuits.
- Path/QoS match: order 1–65535 (same order → most specific wins), network context, users/groups (needs User-ID + CIE), source/destination prefixes global or local (**non-default sets only**), applications (system or custom; transfer type real-time audio/video, transactional, bulk drives queueing). Actions: paths (active/backup/L3 failure) and service/DC groups (active/backup).
- QoS Table 10 defaults: Platinum 50 % / Gold 25 % / Silver 15 % / Bronze 10 % of circuit bandwidth; within a class real-time audio 20 %, video 30 %, transactional 30 %, bulk 20 %; DSCP mark/remark.
- Performance policy: SLAs on application metrics (init failure rate, RTT, UDP TRT), link-quality metrics (latency, loss, jitter, MOS, probe) and system/flow metrics (CPU, memory, disk, circuit and flow utilisation); actions Create Incident, Visibility, Move Flows (graceful honours link affinity; forced ignores it), Packet Duplication (**up to three VPN paths**), FEC. Built-in SLAs Table 12: All Apps 500 ms / 5 % / 100 ms; Media Apps 150 ms / 2 % / 40 ms (jitter) — supports the 40 ms side of KG-088.
- Security: default + 4 sets; **branches only**; example zones PRIVATE/PUBLIC/WAN/VPN/GUEST; link types port, subinterface, lan, privatewan, publicwan, service_link, vpn; **bind zones to every network before binding a stack (unbound = dropped); bind at device level**; actions Deny (silent), Reject (TCP reset both ways), Allow; match includes services (protocol/ports) and users/groups.
- NAT: up to 4 sets; default internet zone bound to all internet interfaces with a default source-NAT-to-egress rule; match on zones, prefixes, up to 16 port ranges each side, protocol; up to 4 actions per rule: No NAT, Source, Destination (optional port), Static Source, Static Destination, ALG Disable (SIP).

## Routing design (pp.51–54)

- DC: ION off-path; **eBGP only**; one "peer with network" port towards both private WAN and LAN in brownfield, separate ports in greenfield; internet port needs a default gateway but the DC ION never forwards internal users to the internet.
- Branch router replacement: direct internet/private WAN/LAN ports; default gateway on internet; static, BGP or default gateway towards private WAN; static or BGP for other internal networks.
- Peer types: **Classic** (both site types; no auto route-maps; branch router replacement), **Core** (DC only; auto route-maps; advertises only prefixes of currently connected branches; **core peer down → all fabric links to that DC marked unusable and branches drop flows through it; with several peers at least one up keeps them usable**; if the core also learns the same prefix from an MPLS CE, prefer the ION's advertisement), **Edge** (DC only, listen-only, learns from e.g. MPLS CE). **Prefix splitting**: when a connected branch prefix equals an edge-learned prefix the DC ION advertises longer matches (10.130.0.0/21 → /22 + /22) so the core prefers the SD-WAN path without extra configuration. This is the official description behind KG-079 (internal playbook spoke of /25 injection with a no-advertise community; the /25 length and the community remain unconfirmed).
- Options: **Force VPN to VPN Traffic to Local Next Hop** (send branch-to-branch transit via an external DC device); branch **L3 Direct Private WAN Forwarding** (needed without a bypass pair and for L3 LAN forwarding), **L3 LAN Forwarding**, **Application Reachability Probe source** (controller port by default; any L3 LAN interface otherwise).

## Prisma Access connectivity (pp.54–55, 59–68)

- SASE Connectivity settings: ION Peering Default Local AS (RFC 6996 private range, **default 65024**, must differ from the Prisma Access tenant AS), Tunnel Inner IP Pool (/31 per tunnel, **default 172.16.0.0/22**, must not overlap the Prisma Access infrastructure subnet), Deployment Mode **Private-App-Access** (default, no communities, routes advertised to backbone and external), **Internet-Only** (BGP no-advertise), **Internet-Only-With-Mobile-User-Access** (no-export), Security Zone auto-bound to the auto-created tunnel interfaces.
- Onboarding uses all internet circuits, recommends the closest location from the site address, ECMP automatic for 2–4 circuits.
- Prisma Access facts the SD-WAN design depends on: remote-network connections = IPsec to an RN-SPN; **aggregate bandwidth** per compute location (minimum allocation 50 Mbps; shared and bidirectional); **max 250 sites or 250 tunnels per RN-SPN**; NAT on by default; ECMP up to 4 links, session-level, same RN-SPN and location, BGP required, unique BGP peer IP per tunnel, RN-SPN round-robin; **BGP keepalive 10 s / hold 30 s recommended** (Prisma Access default hold 90 s); IKEv2 liveness 5 s × 10 = about 50 s to declare a tunnel down; infrastructure subnet /24 minimum (/23 recommended), RFC 1918, must not overlap 169.254.169.253–254, 100.64.0.0/10, 169.254.201.0/24, 169.254.202.0/24; two zones trusted/untrusted; policy identical on all RN-SPNs; large DIA-only sites up to 4 × 500 Mbps to separate RN-SPNs (overlapped subnets, SE review).
- Licensing (pp.55–56): Prisma SD-WAN subscriptions are data-center (ION 7000, 7100V, 9000, unlimited bandwidth) or bandwidth (branch). Table 13 bandwidth tiers: 1200-S 25/50/250 Mbps; 3200 250/1000; 5200 250 Mbps/1/2.5 Gbps; 9200 1/2.5 Gbps; 3102V and 3104V 25/50/250; 3108V 250/1000; 7108V and 7116V 1/2.5 Gbps. Optional per-branch-device licences: ZBFW, DVR (90 days of statistics), WAN Clarity Reports; DVR and Reports are enabled at customer level but purchased per branch device. Prisma Access **site licence** tiers (Very Small 25 Mbps … X-Large 2,500 Mbps; min 2 sites; includes Interconnect and SD-WAN add-ons; new tenants only; no Panorama, IPv6, inbound) vs remote-network units (1 Mbps), not mixable.

## Design model (pp.69–74) and Azure variant (SRC-000010 pp.7–14)

- Two regions, each with a DC pair in one cluster integrated (not inline) into the existing network, static IPs, BGP to core; branches dual-internet or MPLS+internet, DHCP on internet ports, static on private WAN; small-site HA with hardware bypass; hub-and-spoke default with optional branch-to-branch links; Prisma Access as standard VPN endpoints with application policies rather than a default route; Prisma Access security policy must allow the DIA applications.
- Azure (Sep 2023): vIONs as a DC site in the Transit VNet; internet port on the public subnet, peering port on an SD-WAN private subnet; **BGP classic peer to Azure Route Server** (ASN fixed 65515, eBGP so vION routes beat VNG iBGP routes unless AS-prepended); VNGs in the same VNet must be active-active with ASN 65515; UDRs steer VNet traffic to an internal load balancer in front of VM-Series; Azure has no ECMP via UDRs; DC HA rules identical to on-premises. SRC-000011 is a byte-identical copy of this guide (KG-030 closed).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| All design rules, tables and limits above | VERIFIED (official reference architecture Oct 2025) | DOC | SRC-000038 pp.21–75 |
| Validation environment SCM 2025.r3.0 / PA 6.0.0 / ION 6.5.2 | VERIFIED | DOC | SRC-000037 p.15; SRC-000045 p.17 |
| vION and 5200/9200 throughput values | CONFLICTED with datasheet SRC-000031 (Nov 2025) and WS-001 | DOC | SRC-000038 pp.26–27 (KG-063) |
| Prefix splitting as the official core-peer behaviour | VERIFIED; /25 length and no-advertise community for core peers remain UNVERIFIED (internal) | DOC | SRC-000038 pp.52–53 (KG-079 PARTIAL) |
| Azure design (ARS classic peer, ASN 65515) | VERIFIED (official, Sep 2023; check currency) | DOC | SRC-000010 pp.7–14 |
| "Secure fabric links are never created between data-center sites" | OBSOLETE in part: admin guide (May 2025) documents inter-DC fabric tunnels from ION 6.5.1 | DOC | SRC-000038 p.32 vs SRC-000029 pp.89–92 |

## Open questions

- KG-126: the Design Guide licensing text (DC subscription for ION 7000/7100V/9000; Table 13 tiers) vs note 01-fundamentals/04 tiers (Small/Medium/Large) and ION 9200 placement; reconcile with the subscription guide.
- KG-127: Design Guide Table 12 jitter 40 ms for Media Apps vs other sources (KG-088) — now two official values exist; confirm which is current in SCM.
