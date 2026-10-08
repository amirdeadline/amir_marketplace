# Branch high availability (HA groups) and data center redundancy

Domain: 2 | Applies to: Admin Guide May 2025; used-for-HA naming from 6.3.1; SVI auto operational state from 6.4.1 | Status: EVIDENCE REVIEWED | Last updated: 2026-10-08

## Explanation (plain words)

At a branch, two IONs form an **HA group**: one is **active** and forwards everything, the other is **backup** and just bridges traffic through its fail-to-wire ports to the active box. Because each WAN circuit is wired through both boxes, the active box keeps using **all** circuits even when its partner is dead. The two boxes talk over an **HA control interface** (a port, sub-interface or VLAN interface marked "Used for HA") using VRRP-style advertisements; priorities, preemption and interface tracking decide who is active. Data centers do not use this model: two DC IONs are both active, and the controller spreads branches across them.

## Key concepts (official pp. 603–605)

- One HA group per branch site, up to two devices. Active: forwarding, path selection, BGP, usable VPNs, routes, full statistics. Backup: bridges to the active device; no path selection, no routing; limited statistics; may hold VPNs that are "not usable".
- HA control interface: any L3 interface with a **static** IP; controller port recommended when both are in the same subnet; otherwise a dedicated pair in one subnet. Synchronizes some state (DHCP leases).
- **Priority** 1–254 (highest 255 mentioned in concepts; the Add Spoke HA screen accepts 1–254); recommended gap **≥ 40** between active and backup. **Preempt** (group level): forces re-election when the active's priority drops below the backup's; if disabled, no election unless the active hits a catastrophic failure (priority 0: power loss, critical process failure, HA control link loss, tracking to 0).
- **Advertisement interval** 1–10 s (VRRP); backup takes over after **3 consecutive missed advertisements**; recommended 1 s (3-second detection).
- **Interface tracking**: HA control interface failure ⇒ immediate failed state; up to **four** tracked non-HA interfaces, each with a priority decrement; WAN tracking = Layer 3 reachability of WAN circuits (middle-mile failures), only with unique IPs per WAN interface, **not supported in bypass configurations**; not recommended on a private WAN interface with BGP peering or on devices sharing a single circuit; switchover reverses when reachability returns. Process crashes (deck and internal guide): non-critical process −25, critical −255.
- Administration: a device can be disabled in the group (RMA, upgrades). HA status shows last switchover time and reason. Site-level policies apply to both devices; **device-level settings (NAT port forwarding, interface security zone binding, etc.) must be configured on both**.
- CLI names: `dump spoke ha config`, `dump spoke ha status`.

## Topologies (official pp. 606–619)

| Topology | Models | Wiring pattern (from the examples) | Notes |
|---|---|---|---|
| Gen-1 | 2000, 3000, 7000, 9000 | Internet on ION1 bypass pair (4 WAN / 5 LAN), MPLS on ION2 bypass pair; cross-connect port 5 of each to port 1 of the other | controller port carries heartbeat; needs a southbound switch |
| Gen-2 | 3200, 5200, 9200 | ION1: two Internet bypass pairs (3/4, 5/6); ION2: MPLS bypass pair (3/4); cross-connects 4→1, 4→1, 6→3; HA via sub-interface on port 7 (VLAN 130); LAN sub-interface VLAN 150 | HA connection must go through a southbound switch (not back-to-back) |
| Gen-2 embedded switch | 1200-S, 3200 in L2 mode | bypass pairs 3/4; HA SVI 130 and LAN SVI 100 on trunk port 5 | back-to-back allowed only with no southbound switch (split-brain note: both become active/active for outbound; inbound stays down until HA re-forms); neighbor switches must run MSTP/RSTP, not PVST; enable tracking on trunk ports with decrement = device priority |
| Software cellular bypass | 1200-S-C-5G | cellular bypass pair with port 4 on each; cross-connect 4→1; WAN peer ports on port 1 mirror the other device's cellular config | both cellular circuits usable concurrently by the active device |
| No bypass pairs | 1000, 1200, any model | circuits terminate on both devices with unique IPs (northbound switch likely); HA sub-interface VLAN 130, LAN VLAN 100 on port 3 | WAN interfaces stay active on both |
| Hybrid Gen-1 + Gen-2 | 3000 (active) + 3200 (backup) | ION1 Internet 2 / Internet Bypass 2 pair; ION2 ports 3/4; controller 1 on 3000, port 5 as controller on 3200 | creating a bypass pair disrupts that interface; keep an alternate controller path |

Common properties: LAN addressing identical on both devices (only the active answers ARP); HA/controller addressing unique so the backup reaches the controller through the active; underlay (private MPLS) use requires routing exchange with the PE.

## Configuring (official pp. 620–632)

- HA group: `Workflow > Sites > HA Groups` or device configuration; one group only; preempt, advertisement interval 1–10 s (recommended 1).
- Used-for-HA interface (called used-for-control before 6.3.1): SVI (VLAN 1–4000; **Auto Operational State** default on for new SVIs from 6.4.1: if all member ports are down the device goes to backup; existing SVIs need it enabled after upgrade), sub-interface, or **main interface (6.3.1+)**; static IPs in one subnet, each device's gateway = the peer's IP; scope Global. Downgrade below used-for-HA support needs support.
- Add devices: Spoke Cluster (HA group), Enabled, Priority 1–254, Track Availability (interface physical state; WAN L3 reachability), Reduce Priority value. If preempt is off, the first device added becomes active.

## Switchover triggers (deck, consistent with official)

Loss of HA control interface (physically down or no IP), loss of HA keep-alives, priority decrement (process crash, tracked interface down), HA disabled on active, power loss.

## Internal best practice (WS-001, May 2026)

Terminate each WAN circuit directly on one ION and indirectly via fail-to-wire on the other; static IPs and DNS on HA interfaces; do not use HA interfaces for other services; trunk ports with MSTP/RSTP on embedded-switch platforms; priority gap ≥ 40; advertisement 1 s; consider leaving preempt off to avoid a second disruption on failback; replicate device-level configuration on both; branch gateway HA uses the same model; **upgrade the backup first** (optionally raise its priority to make it active, then upgrade the former active).

## Data center redundancy

- Official (p. 57, 12): DC IONs integrate with core routing and inject branch routes; clusters provide horizontal scaling (note 06).
- WS-001: DC IONs are **active-active**; both forward and peer with the core; put both in the same cluster; each branch builds tunnels to both DC IONs but only the Active DC ION for that branch advertises the branch prefix into the core (prevents asymmetry); fast failover if it fails. Deck: "<4 second failover detection and remediation (tunable)" for branch HA pairs; DC primary/backup per branch.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| One HA group, two devices, active/backup roles | VERIFIED | DOC | SRC-000029 p.603 |
| Priority range, ≥40 gap, preempt semantics, 1–10 s advertisement, 3 missed, 4 tracked interfaces | VERIFIED | DOC | SRC-000029 pp.604, 620, 629–630 |
| WAN L3 tracking restrictions | VERIFIED | DOC | SRC-000029 p.630 |
| Device-level config must be applied to both | VERIFIED | DOC | SRC-000029 p.605 |
| Topology table and wiring | VERIFIED | DOC | SRC-000029 pp.606–619 |
| Back-to-back HA split-brain behavior and MSTP requirement | VERIFIED | DOC | SRC-000029 pp.611–613 |
| Used-for-HA on main interface from 6.3.1; SVI auto operational state 6.4.1 | VERIFIED | DOC | SRC-000029 pp.622, 624 |
| Process crash decrements 25 / 255 | UNVERIFIED (deck and internal guide; not found in official pages read) | DOC | WS-033 slide 98; WS-001 §Branch HA Topologies |
| DC active-active and single Active DC ION advertising per branch | UNVERIFIED (internal, strong); official DC routing chapter pp.369–373 to confirm in B6 | DOC | WS-001 §High Availability |
| Upgrade backup first | UNVERIFIED (internal recommendation) | DOC | WS-001 §ION Software Upgrade |

## Open questions

- KG-011 partially answered: branch HA detection = advertisement interval × 3 (official); process-crash decrements and "<4 s" claims need an official source.
- KG-078: official statement of DC-side active/backup selection per branch and failover time.

## Addendum 2026-10-08 (public pages cached under D2; see 03_SOURCE_CATALOG.md §J)

- **6.6.1 Branch HA optimization** (PUB-010, VERIFIED): application identification maps (UDP app-map) replicated to the standby in real time and pre-installed in its data plane; LAN-side dynamic routes replicated and merged into the forwarding table during role transition (pairs with BGP graceful restart); **readiness-based preempt**: the HA manager checks routing, firewall and interfaces before a device may resume the Active role. Gen-2 and ION 9000 only (6.6.1 platform rule).
