# Multicast

Domain: 2 | Applies to: LAN multicast from 5.6.1; WAN multicast from 6.0.1; private-VPN and branch-side sources from 6.1.1; scale change at 6.2.1 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

An ION can act as a PIM sparse-mode router. On the branch LAN it can have senders and receivers; over the WAN, a data center ION replicates multicast to branches through the fabric VPNs, and (from 6.1.1) a branch can be the source with the data center relaying to other branches. Rendezvous points can be static or learned by bootstrap messages. Scale and which VPN types carry multicast depend on the release.

## Documented behavior (official pp. 402–432)

- Branch site: LAN senders and receivers; **receives** WAN multicast only. DC site: transmits to branches over VPNs; no receivers at the DC. 6.0.1: WAN multicast over **public VPN only**; 6.1.1+: DC receives from peers and branches and transmits over **public and private** VPNs; **Branch Side Source (BSS)** from 6.1.1 (receiver branch joins via the DC; DC forwards the join to the source branch; replication only via DCs; no direct branch-to-branch multicast).
- Scale: 6.2.1+: a DC supports **400** branch sites for multicast and 400 per group; 6.0.1–6.2.1: 250 sites and 64 per group. Branch: max **30 PIM interfaces** (incl. VLAN sub-interfaces); not on secondary addresses or virtual interfaces. DC: multicast on "Peer with a Network" ports only without a Private WAN circuit label (with a label you cannot enable multicast; without, the interface can only source multicast from an upstream router); Internet-use ports cannot be configured but the DC still receives/transmits over VPNs. Raise the LTE circuit cost to avoid receiving multicast on metered links.
- Branch prerequisites: L3 Direct Private WAN Forwarding and L3 LAN Forwarding; per LAN interface: Multicast yes, IGMP version (IGMPv2/v3 receivers only), interface DR priority (default 1; 6.0.1+), IGMP static joins (6.0.1+). DC: Peer with a Network port, Multicast yes, DR priority.
- WAN multicast profile ("peer group profile", `Manage > Resources > Configuration Profiles > Multicast`): source DC site; "Receive traffic from branch side sources" (6.1.1+); assign the profile to branch sites (or "No profile" to disable); branch source entries (max **64**: group prefix + source address).
- Global parameters (RFC 4601 PIM-SM; editable from 6.0.1): SPT switchover enabled (recommended), Enable BSM (dynamic RP learning; RP and source must be reachable via specific routes, not default), DR priority 1, PIM hello 30 s, hold 105 s, join/prune 60 s, join hold 210 s, IGMP query 125 s, query response 10 s, last member query count 3, last member query response 1 s, IGMP query max response 100 s (6.0.1+); older parameters (triggered hello delay 4 s, TTL threshold 1, SPT threshold 100 s, querier timeout 380 s) only before 6.0.1.
- Static RP: max **8 RPs and 240 groups**, groups unique across RPs; the ION or an external device can be the RP; Auto-RP and BSR advertisement are not supported (BSM learning is); a branch static RP takes precedence over a DC static RP.
- Views: LAN statistics (PIM neighbors, traffic, PIM and IGMP message counters), WAN statistics (per DC/branch secure fabric link; needs the new data-lake infrastructure), IGMP membership, LAN and WAN multicast route tables (flags S, C, P, R, F, T from 6.0.1), multicast flow statistics (requires a global prefix filter and an L3/L4 custom application created before traffic starts; DC IONs do no flow processing), `Monitor > Activity > Routing`.
- CLI names: `dump routing multicast configuration|igmp|interface|internal vif entries|mroute|pim|sources|statistics|status`, `inspect routing multicast fc site iface|interface|mroute`, `debug routing multicast log|pimd`, `clear routing multicast statistics`.

## Internal guidance

WS-001: never disable SPT switchover. Deck slides 205–207 (not read in detail). Converged PRD (645427428) lists future multicast goals (SSM/ASM, IPv6, LQM best path) — roadmap only.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Release floors (5.6.1 LAN, 6.0.1 WAN public, 6.1.1 private + BSS) | VERIFIED | DOC | SRC-000029 pp.402–404 |
| Scale 400/400 (6.2.1+) and 250/64 (earlier); 30 PIM interfaces; 64 source entries; 8 RPs / 240 groups | VERIFIED | DOC | SRC-000029 pp.402–403, 410, 416 |
| Interface support matrix and DC circuit-label restriction | VERIFIED | DOC | SRC-000029 pp.403–404 |
| Global parameter defaults | VERIFIED | DOC | SRC-000029 pp.413–415 |
| Auto-RP/BSR not supported; BSM supported; branch static RP precedence | VERIFIED | DOC | SRC-000029 pp.416–418 |
| Keep SPT switchover on | UNVERIFIED (internal recommendation, consistent with official "good practice") | DOC | WS-001 §Multicast; SRC-000029 p.412 |
