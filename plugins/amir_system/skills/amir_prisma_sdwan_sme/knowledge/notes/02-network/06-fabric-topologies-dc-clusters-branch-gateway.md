# Secure fabric topologies: DC clusters, inter-DC and branch-to-branch fabric tunnels, prefix filters, ciphers, branch gateway and full mesh

Domain: 2 | Applies to: Admin Guide May 2025; inter-DC/inter-branch fabric tunnels need ION 6.5.1+; branch gateway 6.4.1+; branch gateway full mesh qualified in 6.8.1 (internal) | Status: EVIDENCE REVIEWED | Last updated: 2026-10-08

## Explanation (plain words)

By default every branch builds tunnels to the data center IONs in its **DC cluster**; a data center can have several clusters to spread branches across pairs of IONs. Since release 6.5.1 you can also build fabric tunnels **between data centers** and **between branches** from the controller, with prefix filters to control what each DC advertises onward. A **branch gateway** is a branch that also acts as a small hub for other branches in its domain (regional data center use case). Release 6.8.1 adds "full mesh" rules so chains of branch gateways and data centers choose the shortest path and keep traffic symmetric.

## Data center clusters (official pp. 85–89)

- First cluster is created automatically with the DC site; one cluster is the **default** (new branches map to it; the first cluster is default until changed). Peer sites = branches mapped to the cluster. A branch maps to exactly one cluster (or none = no VPN to that DC).
- Cluster fields: name, description, tags, **Maximum Branch Site Count (soft limit)** (alarm "Hub Cluster Branch Count Limit Exceeded" when crossed; not blocking). **Two devices per cluster by default; a third is allowed when one device is locked for maintenance.**
- Operations: assign device, edit, view branch sites (Overlay Connections filtered by cluster; VPNs up vs configured), unset default, **lock device** (branches stop building VPNs to it), manage branches on cluster (move/remove; VPN outage during moves), move branches between devices (procedure: lock the device → assign a third device → attach site WAN interfaces → move peer sites one by one → unassign the locked device), view cluster status (VPNs added/removed/up), replace device (wizard), unassign device, delete cluster (choose a new default), audit log.
- Internal deck: controller selects one DC ION as Primary and another as Backup per branch; different branches may use different IONs; "clustering config is done via backend today, plan to expose in UI" (older slide; the official guide now documents the UI).

## Secure fabric tunnels between data centers (official pp. 89–92; ION 6.5.1+ both ends)

- Connect DCs across clouds (AWS, Azure, Equinix, GCP) and physical sites without third-party solutions; `Workflows > Data Centers > Overlay Connections > Add Secure Fabric Link`: source cluster and circuit, destination DC site, hub cluster and hub circuit; multiple destinations allowed; tunnels are created between all devices in the clusters; active by default based on core peering status (core peer down ⇒ controller marks the VPN inactive).
- Use either standard VPN or fabric tunnels between two DCs, not both; in a hybrid, add a prefix list on the first DC denying the second DC's prefixes on the standard VPN path to avoid loops.
- **After upgrading to 6.5.1 all existing BGP peers are set to Local scope** so inter-DC-learned prefixes are not redistributed by default; change to Global if needed.
- **Overlay prefix filters** (`Workflows > Data Centers > Overlay Prefix Filters`, order / prefix / permit-deny): eligible for fabric distribution: global static routes, WAN path prefixes from branches and branch gateways (hop count 1), site prefixes, BGP/OSPF global learned prefixes. Prefixes learned over inter-DC VPNs are **not** distributed further to other DCs nor to branches/branch gateways (loop prevention). If two DC IONs share a core peer, distribute through the core, not over the fabric.

## Secure fabric tunnels between branch sites (official pp. 92–93; 6.5.1+)

`Workflows > Branch Sites > Overlay Connections > Add Secure Fabric Link`: source circuit, destination branch site and circuit, multiple destinations; tunnels between all devices in a branch cluster; active on the active HA device, inactive on standby.

## Site prefixes (official p. 94)

Advertise reachability from a site into the fabric; preferred for DC sites (`Workflows > Data Centers > site > IP Prefixes`); for branches prefer global-scope interfaces and static routes. IPv4 and IPv6.

## Ciphers for fabric tunnels (official pp. 95–96)

AES-256-GCM, AES-256-CBC, AES-128-GCM, AES-128-CBC; selection order 256-GCM > 256-CBC > 128-GCM > 128-CBC; **GCM requires 6.5.1 on both devices**, otherwise CBC only; all four enabled by default for new sites; the controller picks the best common cipher per site pair and pushes it to both; no common cipher ⇒ "None" and no tunnel. Standard VPNs use IKE/IPsec profiles instead (AES-GCM only with IKEv2).

## Branch gateway (official pp. 60–62; TSE playbooks 794506392 and 917197340, internal)

- Official: single-click site setting (6.4.1+); supported ION 3200/5200/9200/3000/7000/9000 and all virtual; creates hub services (policy transit, LQM server) plus branch visibility and path selection; tunnels form automatically to branch sites in the same domain; interfaces: port, bypass pair, sub-interfaces, virtual interfaces, standard VPN; IPv4/IPv6 static/DHCP and secondary addresses; conversion requires Control mode, L3 Direct Private WAN Forwarding, L3 LAN Forwarding, no existing branch-to-branch VPNs (deleted on conversion); conversion reboots the ION.
- TSE playbook adds: exactly one spoke cluster and one branch gateway cluster are created; no "Peer with network" interface use (hub-only); routing uses **classic peering** only (no off-path core/edge peering); by default distributes WAN-BGP-learned prefixes to branches and DC hubs; LQM client toward DCs, LQM server toward branches, element-ID-based election between two gateways; reversion blocked while DC groups, WAN default route advertisements, cross-domain VPNs or service-group memberships remain; **model change (enable or revert) reboots the spokes**; VPNs auto-form only within the same domain; large domains pause auto-mesh creation with a confirmation; changing a site's domain tears down VPNs; gateway-to-gateway cross-domain links are manual; **no BFD on gateway-to-gateway underlay**; incident when mapped spoke count exceeds the threshold; VPN scale equals the branch platform scale but may be bound by LQM server capacity. Verification: `dump overview` shows `Branch Gateway: Enabled` and both L3 forwarding flags true; `dump vpn status VpnID=…` shows `peer_site_branch_gateway: true`; `inspect wanpaths site-id=…`. (Internal term "Model-3" = both L3 forwarding toggles on; not for customer use.)
- Deck positioning (internal): branch gateway < 8 Gbps, no scale-out, full app/link visibility, app-based path selection, automated hub-to-hub; DC < 15 Gbps; DC with cluster > 15 Gbps with scale-out but without branch-style visibility. Roadmap items listed on slide 117 (OSPF on gateway, cloud HA, multicast, FEC/packet duplication, scale-out) are UNVERIFIED and may have shipped since.

## Branch gateway full mesh (TSE playbook 917197340, updated 2026-08-21, internal; feature "QA-qualified in 6.8.1")

- Topologies Branch–BGW–DC, BGW–BGW, DC–BGW–DC become production-qualified in 6.8.1; earlier (6.4.1–6.7.x) basic full mesh existed but was not validated. Platforms: ION 9000, 3200, 5200, 9200, vION 3108v, 7116v, 7132v. No new CLI.
- **Hop-aware routing**: lowest hop count wins and can override Active/Backup (a Backup path with hop count 1 beats an Active path with hop count 2; ties broken by media type, public vs private).
- **Symmetry**: the DC element with the direct branch overlay advertises the branch prefix to the core with metric 0; a DC element learning it through a branch gateway (hop count 2) uses metric 30 (implicit FRR route maps). Branch gateways prune WAN paths back to the originating site (loop prevention) and move asymmetric flows to the optimal path.
- **Prefix filtering on Anynet links** (BGW↔BGW and BGW↔DC only; implicit deny; VRF-bound; commit rejected on empty action or missing VRF).
- Interconnection types: intra-domain auto-VPN; cross-domain manual Internet links; DC targets ignore domains (every branch and active gateway builds overlays to all mapped DC cluster destinations).
- Diagnostic commands listed: `inspect wanpaths all|<site_id>|<path_id>`, `inspect fib vpn|lan`, `dump vpn summary RemoteSite=…`, `dump vpn ha RemoteSite=…`, `inspect flow brief|detail`, `inspect path summary`, `inspect path id …`, `inspect site id …`, `inspect network routing table vrf …`, `inspect network advertised-prefixes path id …`.

## Hub-to-hub third-party tunnels (legacy CGXKB 74187137, 2023; OBSOLETE in part)

Older workaround: fabric VPN listens on UDP 4500 and strongSwan (standard VPN) on 4501; when a DC ION is behind NAT, DNAT 4500→4501; one end set non-initiator from the support shell (reset on upgrade). The official guide now provides **Passive Mode** for DC-DC standard VPN and documents the 4500→4501 DNAT (note 04), so the support-shell step is OBSOLETE.

## Converged SD-WAN direction (Confluence 645427428 "SD-WAN Fabric and Routing", PRD draft updated 2026-02-04, internal roadmap)

Describes a future converged Prisma SD-WAN / PAN-OS SD-WAN fabric (fabric clusters/domains with up to 16 DCs per domain, hub-and-spoke default, optional full mesh, DCI tunnels, overlay types Direct / Secure Fabric / Prisma Access / Standard VPN, three fixed DC groups, failback timers, CMEK/CSEK keys). **Roadmap only**; never present as current behavior.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| DC cluster concepts, default cluster, soft limit alarm, two devices (+1 when locked), operations and outage warnings | VERIFIED | DOC | SRC-000029 pp.85–89 |
| Inter-DC fabric tunnels 6.5.1+, created between all cluster devices, core-peer gating, not both standard and fabric, BGP peers set Local after 6.5.1 upgrade | VERIFIED | DOC | SRC-000029 pp.89–90 |
| Overlay prefix filter eligibility and non-redistribution of inter-DC prefixes | VERIFIED | DOC | SRC-000029 p.91 |
| Branch-to-branch fabric tunnels 6.5.1+, active on active HA device only | VERIFIED | DOC | SRC-000029 pp.92–93 |
| Site prefixes guidance | VERIFIED | DOC | SRC-000029 p.94 |
| Cipher list, order, 6.5.1 GCM floor, best-common selection | VERIFIED | DOC | SRC-000029 pp.95–96 |
| Branch gateway official facts | VERIFIED | DOC | SRC-000029 pp.60–62 |
| Branch gateway internals (classic peering only, LQM roles, reboot on mode change, no BFD BGW-BGW, verification flags) | UNVERIFIED (internal TSE playbook, 2026-04-15) | DOC | SRC-000091 pageId 794506392 |
| Full mesh 6.8.1 behaviors (hop-aware override, metric 0/30, loop pruning, prefix filters) | UNVERIFIED (internal TSE playbook, 2026-08-21); release notes 6.8 to be checked under D2 | DOC | SRC-000091 pageId 917197340 |
| Primary/backup DC ION per branch | CORROBORATED (deck + WS-001 note that only the Active DC ION advertises the branch prefix) | DOC | WS-033 slide 104; WS-001 §High Availability |
| Hub-to-hub support-shell non-initiator workaround | OBSOLETE (replaced by Passive Mode) | DOC | 74187137; SRC-000029 p.232 |
| Converged fabric requirements | UNVERIFIED (roadmap PRD) | DOC | SRC-000091 pageId 645427428 |

## Open questions

- KG-077: official documentation of hop-aware path selection, metric 0/30 symmetry, and Anynet prefix filters (expected in ION 6.8 release notes or admin guide revisions after May 2025).
- KG-064 (domain semantics) still open; "Service and DC groups" sections pp.470–476, 674–680 to read in B9.

## Addendum 2026-10-08 (B17/B20 findings)

- 6.8.1 release considerations (note 07-operations/04, VERIFIED official): branch-gateway **hop-count / prefix-filter** behaviour changes in 6.8.1 (branch gateway prefix filters) — read before advising on multi-BGW designs; WS-001 (internal) warns that more than two branch gateways in full mesh, or several DCs with branch gateways, can produce asymmetry until the native fix ships (workaround: prefix-based path policies).
- Design Guide Oct 2025 (SRC-000038 pp.32–33, VERIFIED) link matrices: branch↔DC public all-to-all automatic; private all-to-all **within the same circuit category**; branch↔branch and branch↔other-region branch gateway only selectively; the guide still states "never between data-center sites", which the admin guide supersedes from 6.5.1 (inter-DC fabric tunnels).
