# VRF (WAN segmentation)

Domain: 2 / 4 | Applies to: VRF from ION 6.3.1; L3 mode only; custom-VRF L3 loopback from 6.8.1 (internal) | Status: EVIDENCE REVIEWED | Last updated: 2026-10-08

## Explanation (plain words)

A VRF is a separate routing table. Prisma SD-WAN lets you define VRFs once for the tenant, bind them to sites through a **VRF profile**, and then put LAN interfaces, static routes, BGP/OSPF peers into a VRF. Traffic entering a VRF interface only sees destinations in that VRF; across the fabric the packet carries a VRF identifier so the far-end ION delivers it into the same VRF. **Route leak rules** let specific prefixes cross between VRFs. Direct Internet Access from a VRF works with ordinary path policy because the ION NATs per VRF.

## Documented behavior (official pp. 433–437; interface pages)

- Segments are defined in global **VRF profiles** (`Manage > Resources > Configuration Profiles > VRF`; also from a site's Configuration tab); a Global VRF context exists by default and cannot be changed or deleted; the default Global profile is assigned to all sites; a **rule with a VRF context always takes precedence over one without**; switching a site to a new profile is allowed only when the new profile's definitions match the default context in use.
- **Route leak rules**: name, source VRF, destination VRF, IPv4 prefix; **the leaked prefix must exactly match the prefix configured on the interface**.
- Interfaces: VRF selectable on LAN-type ports, sub-interfaces (settings do not inherit from the parent), port channels and L3 LAN interfaces; "Currently, VRF supports LAN"; IPv6 only in the Global VRF; DC side uses "Peer with the Network" interfaces per VRF. Static routes, BGP peers and OSPF configurations carry a VRF field. Standard VPNs carry a VRF field with constraints (two standard VPNs in different VRFs cannot share the overlay endpoint IP; Global-VRF standard VPN carrying custom-VRF LAN traffic needs a NO-NAT rule). Host tracking: Global VRF only.
- **Simplified DIA** (pp. 436–437): define path policy rules for Internet-bound traffic; the ION applies stateful NAT with VRF and session awareness so return traffic lands in the right VRF; no inter-VRF leaking needed.

## Internal details (TSE VRF playbook 717731234, updated 2026-07-29; deck slides 233–252)

- 6.3.1 introduced VRF; L3 mode only; VRF is a tenant-level resource enabled per site.
- Packet handling: LAN→WAN lookup on the incoming interface gives the VRF; the VRF is encoded in the VNI field of the VXLAN/Geneve header over the native VPN; WAN→LAN extracts the VNI; for Internet access the flow controller marks packets with the interface VRF ID (SO_MARK) for iptables, restored by conntrack on return.
- **Limitations stated for 6.3.1** (the playbook may predate later improvements): per-VRF Internet NAT **not supported** in 6.3.1 (workaround: leak to Global); explicit NAT policies in Global only (implicit masquerade for VRFs via Global lookup); VRF BGP only over **core** peers (edge/classic in Global); route leaking exact match only, non-overlapping addresses, LAN-to-LAN and LAN-to-WAN on branches; spoke-to-spoke needs secure fabric and both sites in the VRF; standard VPN (and guest-to-Prisma-Access over standard VPN) Global only; the hub must be a member of **all** VRFs for end-to-end connectivity; multicast, IPv6, app reachability probes, SNMP/syslog/IPFIX Global only. **CONFLICTED with the official May 2025 "Simplified DIA" page**, which states per-VRF NAT for DIA works with path policy alone: treat the playbook limit as applying to 6.3.1 and the official page to later releases (OBSOLETE for current releases; confirm the exact release in B9/B17).
- Deck: isolated routing table at branch; route leaking on hub/DC; spoke-to-spoke VRF traffic; DIA from VRF; VRF profiles; VRF attachment; VRF static routes and BGP; VRF information in Flow Browser; "broadest support for segmentation" with network contexts (policy per segment, same application) plus VRFs (overlapping IPs).
- CLI (playbook): `dump vrf info [vrf-id|all]`, `dump routing vrf [<vrf-id>|all]`, `inspect system vrf`, `inspect vrf`, `inspect flow brief|detail [vrf <id>]` (look for VRF, FWD_VRF, RX_VRF, VNI, LEAK_VRF), `dump routing static-route config [vrf <id>]`, `dump routing prefix-reachability prefix=<p> [vrf <id>]`, `dump dhcp-server config`.
- **6.8.1 L3 loopback VRF support** (TSE playbook 918315006, 2026-08-21): custom-VRF loopback on spoke (used_for LAN) and hub (Peer with Network) as source for SNMP, SSH, syslog, NTP, BGP update source, OSPF/BGP router ID; Internet/Private-WAN loopbacks stay default VRF; loopback-sourced traffic is classified as LAN traffic; hub-side tcpdump on a loopback is one-directional (capture on the physical interface).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| VRF profile model, Global VRF immutable, precedence of VRF-context rules, exact-match leak rule | VERIFIED | DOC | SRC-000029 pp.433–436 |
| Simplified DIA with per-VRF stateful NAT | VERIFIED (May 2025) | DOC | SRC-000029 pp.436–437 |
| VRF selectable on LAN interfaces/sub-interfaces/port channels; IPv6 Global only; host tracking Global only | VERIFIED | DOC | SRC-000029 pp.208, 241, 251, 401 |
| 6.3.1 introduction; VNI encoding; 6.3.1 limitation list | UNVERIFIED (internal); NAT limitation CONFLICTED/OBSOLETE vs official DIA page | DOC | SRC-000091 pageId 717731234 |
| 6.8.1 custom-VRF loopback matrix and services | UNVERIFIED (internal; 6.8.1 release notes to check under D2) | DOC | SRC-000091 pageId 918315006 |
| Network context vs VRF positioning | UNVERIFIED (deck) | DOC | WS-033 slides 233–241 |

## Open questions

- KG-081: which release introduced per-VRF Internet NAT (simplified DIA) and VRF support on edge/classic peers; needed to date the playbook limitations.

## Addendum 2026-10-08 (public pages cached under D2; see 03_SOURCE_CATALOG.md §J)

- **Release floors now VERIFIED** (PUB-011, PUB-010, PUB-008): Standard VPN, NTP, Syslog and SNMP inside a VRF from **6.4.1** ("put a standard VPN in any VRF, for example Guest"; path policy steers; a route leak gives basic reachability when all VRFs share one tunnel); **Direct Internet Access for VRF-based segments from 6.4.2**; **VRF Service Link Multiplexing from 6.6.1** (custom-VRF internet traffic over Global service links to Prisma Access without manual leaks; VNI encoded in connection marks for symmetric return; failover between Global service links; native custom-VRF service links preferred); VRF-aware IPFIX and multi-VRF DNS service from 6.6.1; custom-VRF L3 loopbacks (LAN side) from 6.8.1. The TSE 6.3.1 limitation list (standard VPN Global only, per-VRF NAT unsupported) is OBSOLETE from 6.4.x (KG-081 CLOSED; KG-133 CLOSED).
