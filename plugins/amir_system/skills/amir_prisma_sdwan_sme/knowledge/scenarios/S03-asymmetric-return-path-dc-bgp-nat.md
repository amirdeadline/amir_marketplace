# S03 — Asymmetric return path through a data center with BGP route injection and NAT

Domains: 2, 8 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Branch (ION 3200, MPLS + Internet) talks to a server in DC-East (ION 5200 pair, core peers to two core routers). Users report intermittent failures to the server; Flow Browser shows "path change: asymmetry" and some flows on an L3 failure path. The DC firewall between core and servers performs source NAT for branch traffic. A Prisma Access service connection also peers with the core.

## 2. Question

Why does return traffic take a different path, where does it break, and how is it diagnosed and fixed?

## 3. Reasoning chain

1. DC IONs are off-path; they attract return traffic by injecting branch prefixes into the core via BGP core peers. Only the DC ION that is the branch's active hub advertises that branch prefix (internal: prevents asymmetry); the DC enforces routing symmetry for sessions from a branch. [VERIFIED for injection and the symmetry statement — 02-network/08 (SRC-000029 pp.372–373), 10-design/01 (SRC-000038 pp.43, 52); UNVERIFIED (internal) for "only the active DC ION advertises" — WS-001]
2. Known asymmetry causes: (a) both DC IONs advertise the **same aggregate** (manual aggregation) so the core may ECMP to the ION without the active VPN — the official fix is the **Intra Cluster Tunnel** (misrouted traffic forwarded to the peer ION); (b) a static/summary route on the core pointing at one ION regardless of which has the active VPN; (c) the core prefers a prefix learned from another peer (e.g. MPLS CE or the Prisma Access service connection) over the ION's — the ION handles the equal-prefix case with **prefix splitting** towards longer matches, but a more specific route from elsewhere still wins; (d) branch-to-DC traffic sent via Prisma Access (remote network → service connection → core) returning over the fabric (internal CGSDW-14689; automated correction listed for 6.5.1). [VERIFIED for (a), (b) partly and prefix splitting — 02-network/08 (SRC-000029 pp.392–393), addendum (SRC-000038 pp.52–53); UNVERIFIED (internal) for (d) — 04-security/06 deck]
3. NAT effect: if the DC firewall source-NATs branch traffic, the server replies to the firewall, which must have a consistent return route to the correct ION; stateful NAT and the firewall's own asymmetry checks drop packets when the reply arrives on a different interface, which is where "intermittent" comes from. Branch-side NAT is not involved for enterprise traffic over the fabric (NAT policy is branch-only and the default rule targets the Internet zone). [INFERENCE from documented NAT and routing behaviour; VERIFIED for the default NAT rule — 02-network/11 (SRC-000029 pp.594–595)]
4. Branch reaction: path re-evaluation is triggered when the return path differs from the forward path; the flow may be moved, and the L3 failure path is used "on network asymmetry". Flow Browser markers "Asymmetry path change"/"Asymmetry bridge" explain it. [VERIFIED — 03-application-traffic/02 (SRC-000029 pp.455–456, 467); UNVERIFIED (internal) for the marker names — 09-datapath/02]
5. Core-peer health: if a DC ION's core peer drops, all its fabric links are marked unusable and branches switch; if only a classic peer exists (e.g. the Prisma Access service connection peer) the VPN can stay active while traffic black-holes — host tracking (6.5.1 internal; official host-tracking chapter) flips the VPN when the tracker IP via the core is unreachable. [VERIFIED for core-peer gating and host tracking — SRC-000038 p.52, SRC-000029 pp.400–401; UNVERIFIED (internal) for the classic-peer black-hole statement]

## 4. Answer

Return traffic is asymmetric because the core sends it to a DC ION (or to Prisma Access) that is not the branch's active hub or not the forward path; the stateful NAT firewall then drops replies it did not see leave. Fix in order: make sure each DC ION advertises only its connected branches (no identical manual aggregate on both IONs, or configure the Intra Cluster Tunnel peer); ensure the core prefers the ION's prefixes over the service-connection/MPLS copies (prefix splitting handles equal prefixes; longer or preferred routes from other peers need policy on the core); use core peers (not classic only) and host tracking so a dead core path takes the VPN down; set the Prisma Access deployment mode to Internet-Only if private access must stay on the fabric; add the default/WAN-summary route on both DC IONs for branch-to-branch transit.

## 5. What to check / collect next

`dump routing peer advertised-routes` and `received-routes` on both DC IONs; core routing table entries for the branch prefix (which next hop, which mask); `inspect flow detail` for the flow (PATH, asymmetry flags); Flow Decision Data; `inspect wanpaths <site>`; host-tracking status; Prisma Access service-connection BGP advertisements. [VERIFIED command names — 02-network/08, 08-troubleshooting/02]

## 6. Gaps exposed

KG-078 (active DC ION selection), KG-079 (community/prefix length), new **KG-135** — official description of the 6.5.1 "automated asymmetry correction" for Prisma Access ↔ fabric return paths (internal deck only).

## 7. Validation status

**SCENARIO PARTIAL** — the routing mechanics and official fixes are VERIFIED; the Prisma Access return-path case and the active-ION advertisement rule rest on internal material.
