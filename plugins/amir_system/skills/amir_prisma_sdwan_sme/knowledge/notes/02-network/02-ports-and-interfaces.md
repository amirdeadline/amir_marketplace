# Ports and interfaces: controller, Internet, WAN/LAN, bypass pairs, sub-interfaces, loopback, virtual interface, port channel, PoE, LLDP, PPPoE, L3 LAN, DHCP relay, switching

Domain: 2 | Applies to: Admin Guide May 2025; feature floors as noted (5.1.1, 5.2.1, 5.5.1, 6.0.2, 6.3.1, 6.5.1, 6.5.2, 6.6.1) | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

An ION has physical **ports** and logical **interfaces** built on top of them. Each port is given a **use**: Controller (talk to the cloud), Internet, Private WAN, LAN, HA, or Private L2 (a transparent bridge). A **bypass pair** joins a LAN port and a WAN port so the box can fail to wire. **Sub-interfaces** split a port by VLAN. A **virtual interface** bonds two ports for redundancy. A **loopback** is a logical address used for management or as a tunnel source. Newer boxes also have Layer 2 **switch ports** with PoE.

## Physical ports

| Port use | Documented facts |
|---|---|
| Controller | One or two controller ports; two allowed from 5.2.1 (can form a virtual interface for redundancy, same subnet). Default source for controller connections; without a controller port the device picks any L3 port. Devices without a dedicated controller port use port 1 or 2 on a DHCP network with Internet. Gen-2 (from 6.3.1): any main or virtual L3 interface can be **Used-for-Controller** (MRL connectivity, HA heartbeat, management). Deck: controller port also sources dynamic probes, LQM/PCM/BFD for private-L2-only designs, SSH, SNMP, NTP; ION 1000 has none. |
| Internet | Use = Internet (or Private WAN); Scope Local (default, route not advertised to DC) or Global (advertised; branch only); circuit label; IPv4 DHCP/Static; IPv6 AutoConf (SLAAC)/Static; advanced: MAC, IP MTU (≥1280 for IPv6), **External NAT Address and Port (IPv4/IPv6)**. **Internet ports are hardened: only UDP 4500, UDP 500 (ISAKMP, reserved for standard VPNs) and ESP are accepted; unsolicited inbound traffic is blocked.** Deck: exceptions can be added for SSH, ping, traceroute, BGP, DHCP, SNMP, spoke HA sync; automatic NAT boundary for direct Internet traffic; BGP to provider possible. |
| WAN/LAN (bypass pair) | Hardware Relay – Fail to Wire yes/no; Use = Private WAN; circuit label; IPv6; **Attached Networks**: router VLAN ID and IP, optional **Network Context** (segment a subnet for separate policy, for example guest Wi-Fi), Scope Local/Global ("Prisma SD-WAN does not control traffic if a prefix/subnet is not defined on the ION device"); optional routing, SNMP, syslog export, NTP client. |

## Bypass pairs (branch only)

- Hardware bypass pair (relay-backed, strict port pairing) or virtual bypass pair (no relay; no virtual interface on it). Not allowed on controller interfaces or members of other logical interfaces. Can be broken into two ports.
- Uses: Internet / Private WAN (WAN side gets static or DHCP IP), **Private L2** (L2-only toward core/peer edge routers; no IP), **LAN** (LAN side only; used for branch HA clustering).
- Bringing a bypass pair down leaves ports individually down; bring ports up individually afterwards or software upgrades may be affected.
- **Propagate LAN State**: LAN port down also brings the paired WAN port down (LAN-to-WAN direction only).
- Default hardware bypass ports: ION 2000 4/5; ION 3000 all LAN/WAN; ION 7000 5/6 and 7/8; ION 9000 1/2, 3/4, 5/6, 7/8 (p. 148). Current models: see datasheet note (1200-S/3200/3200H 3/4; 5200 1–2, 3–4; 9200 four pairs).
- **Cellular software bypass pair** (for HA with cellular models): cellular interface is always the WAN side, Ethernet peer is LAN; circuit label must match the peer device's directly attached cellular interface; on the other ION set "Peer Bypass Pair WAN Port Type = Cellular" on the Ethernet WAN port to inherit the cellular configuration; MTU IPv4 552–1500, IPv6 1280–1500 for the pair.

## Sub-interfaces

- Parent: Ethernet port, virtual port, or an unconfigured bypass pair; not on controller ports, nor on interfaces/bypass pairs that have loopback members, PPPoE or standard VPNs. On a bypass pair, WAN-use sub-interfaces go on the WAN port, LAN-use on the LAN port. VLAN ID required when multiple; one native-VLAN sub-interface per parent. DNS servers required for Internet/Private WAN, not LAN.
- Before 5.1.x LAN sub-interfaces served only branch services (DHCP server/relay, SNMP, ping, SSH); from 5.1.1 they forward user traffic. No virtual interface on a sub-interface; DHCP relay and server cannot share a sub-interface. VRF selectable (Global or custom; VRF supports LAN; sub-interface settings do not inherit from parent). Uses: Internet, Private WAN, LAN, HA.

## Loopback interfaces

- **L2 loopback** (from 4.5.3): emulates a WAN port to free a physical port; only on ports without hardware bypass circuitry (ION 1000 all; 1200 all; 2000 ports 1–3; 7000 ports 1–4, 9–14; virtual IONs all non-controller ports); max **4** per device (older text); paired with a physical LAN port as a bypass pair with use **Private L2** only; the site's network policy must not use "Direct on private WAN" (traffic dropped); valid paths Direct on public or VPN on public.
- **L3 loopback** (from **6.5.2**): for SSH and syslog management over the overlay, and as a **VPN tunnel source** when MPLS WAN IPs are not routable; max **12** per device (all platforms); /32 only; **no IPv6**; cannot be used for Standard VPN. Fields: use Internet / Private WAN / LAN (DC: Public), circuit label, **Associate Interface** (port or sub-interface without a circuit label; the loopback must be advertised only on it; tunnels form only over it; if NAT is on the associate interface the loopback is NATted to its IP), Scope Global to advertise to BGP peers and fabric. DC advertisement: new route map with the loopback prefix list (edge peers: loopback only; core peers: loopback plus existing; classic peers: automatic when Global).

## Virtual interface (VI)

- Bonds **max two** physical ports of the same type (controller with controller; data with data) that have default configuration; Up if at least one member is up. Controller VI cannot be admin down; circuit label cannot attach to a controller VI; data VI supports LAN/Internet/Private WAN, IPv4/IPv6, scope, circuit label, DHCP relay. Topologies: controller port redundancy to two L2 switches; branch LAN redundancy (VLAN sub-interface on the VI); branch Internet redundancy to an active/backup firewall pair (port tracking on the firewalls); DC two core peers in one subnet (BGP to both, active/active); DC Internet via L2 switches to a firewall pair. Deck: controller VIs supported on ION 3000/9000 and are not cleaned up on unassign; LAN VIs are.

## Port channel (LAG/LACP)

- Official (May 2025): **ION 3200 (L3 mode), 5200, 9200; LAN side only; "currently we don't support WAN side LAG/LACP"**. LACP on (dynamic) or off (static); transmission mode Slow (30 s, default) or Fast (1 s); members must not belong to other interfaces or be used by SNMP trap, syslog, AAA, DNS service; port-channel MAC = lowest member interface; uses LAN, HA, None (DC: Peer with the Network); VRF; NAT zone/pool; IoT SNMP discovery source.
- Internal guide (May 2026): LAN L3 port channel from **6.5.2**; **WAN port channel (Internet and Private WAN) from 6.6.1**; fabric VPN automation does not support IPv6 on WAN port channels. Deck says 6.5.1. **Version floor CONFLICTED** (6.5.1 deck vs 6.5.2 internal guide; official guide gives no version) and WAN support is newer than the official guide read.

## PoE

- ION 1200-S (all variants) and ION 3200: ports 7–10, 60 W per port (802.3bt, 4-pair or 2-channel), 90 W system, classes 0–6, first-come-first-served; PoE disabled by default; port alarm threshold 50–100% (default 100% = 60 W); system threshold 50–100% (default 100%); incident when exceeded; monitor under System > PoE.

## LLDP / LLDP-MED

- Receive-only default on non-PoE ports, transmit-and-receive on PoE ports; up to 10 neighbors per interface (oldest ages out); entries cleared on interface down or PD disconnect; TLVs: Chassis ID, Port ID, TTL, system name/description/capabilities; MED: capabilities, extended power-via-MDI, inventory (hardware/software/firmware revision, serial, manufacturer, model).

## PPPoE

- WAN physical ports only (not sub-interfaces, bypass pairs, or interfaces with L3 config); the logical PPPoE interface is the underlay for all features; without a circuit label the port only talks to the controller and policy ignores it; IPv4 Negotiated or Static (static overrides server); IPv6 AutoConf/Static (link-local from server).

## L3 LAN interface, secondary IPs, static ARP, DHCP relay, directed broadcast

- L3 LAN (5.1.1+): forwarding plus services; static routing supported; needs "Enable L3 Direct Private WAN Forwarding"; no default gateway/DNS needed for LAN use; IPv6 only in Global VRF; IPv6 prefix distribution option.
- Secondary IPs (5.5.1+, branch): up to **8** per L3 LAN interface; primary must be static; same network context; each with own scope; no DHCP server on secondary IPs; cannot disable LAN forwarding while configured; downgrade blocked.
- Static ARP (5.5.1+): up to **16** entries per L3 LAN interface; downgrade blocked.
- DHCP relay (branch): on controller port, LAN port or static-IP sub-interface; VRF-aware; forwards only when the device is assigned and the site is active; up to **16** server IPs; source interface default controller port; Option 82 (circuit ID, remote ID, reforwarding policy).
- IP directed broadcast: from fabric VPN into an L3 LAN subnet broadcast; not with ZBFW for non-UDP traffic nor with NAT on the LAN interface; disabled by default.
- Application reachability probes: enabled by default except ION 1000 (must configure a LAN port or an alarm is raised); controller port generates probes if no LAN port is set; **1200/1200-S/3200/5200/9200 need a configured source interface** (no dedicated controller port); TCP probing on 3-way handshake failures; **UDP DNS probing from 6.3.2** (retry once a minute for three probes, then every 5 minutes).

## Layer 2 switching (deck, internal; admin guide pp. 163–180 not yet read)

L2 switch ports on ION 1200-S variants and ION 3200 (ports 5–10), two 2.5 Gbps uplinks to the host; access/trunk; VLAN ID 1–4000, max 32 active VLANs; STP 802.1d/1s/1w (RSTP default), root/BPDU guard, portfast default, priority 0–240 step 16 (default 128); minimum 6.0.2 (1200-S) and 6.3.1 (3200), no downgrade; ION 3200 in L2 mode behaves like a 1200-S; 802.1X or MAC authentication (closed mode, single host). To VERIFY against admin guide pp. 163–180 in a follow-up.

## MTU notes (internal guide)

Default MTU 1500; IPv6 needs ≥1280; cellular default 1428; reduce the Ethernet WAN MTU manually when behind a cellular gateway (no auto-detect). Speed/duplex Auto (hard-coding on bypass pairs can break failover through the relay). Configure DNS servers per interface. Behind NAT: set External NAT Address and Port (UDP 4500) and allow TCP 443 and UDP 4500 inbound on the upstream firewall.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Controller port rules; two ports from 5.2.1; Used-for-Controller from 6.3.1 | VERIFIED | DOC | SRC-000029 pp.182–183 |
| Internet port hardening: UDP 4500, 500, ESP only | VERIFIED | DOC | SRC-000029 p.185 |
| Scope Local/Global semantics | VERIFIED | DOC | SRC-000029 pp.185, 187 |
| Bypass pair types and uses; LAN-state propagation; bring-up caveat | VERIFIED | DOC | SRC-000029 pp.233–239 |
| Cellular software bypass pair rules | VERIFIED | DOC | SRC-000029 pp.236–238 |
| Sub-interface rules and 5.1.1 floor | VERIFIED | DOC | SRC-000029 pp.207–210 |
| L2 loopback rules, max 4, eligible ports | VERIFIED (older section; the max-4 vs max-12 statements both appear in the guide) | DOC | SRC-000029 pp.212–214 |
| L3 loopback from 6.5.2, max 12, /32, no IPv6, associate interface, no Standard VPN | VERIFIED | DOC | SRC-000029 pp.214–217 |
| Virtual interface rules and topologies | VERIFIED | DOC | SRC-000029 pp.218–223 |
| Port channel: 3200 L3/5200/9200, LAN only, LACP modes, MAC rule | VERIFIED as of May 2025 | DOC | SRC-000029 pp.239–242 |
| Port channel WAN support from 6.6.1; LAN from 6.5.2 | UNVERIFIED (internal); floor CONFLICTED with deck (6.5.1) | DOC | WS-001 §Ports; WS-033 slide 91 |
| PoE ports/limits/thresholds | VERIFIED | DOC | SRC-000029 pp.243–244 |
| LLDP defaults and TLVs | VERIFIED | DOC | SRC-000029 pp.245–246 |
| PPPoE restrictions | VERIFIED | DOC | SRC-000029 pp.247–248 |
| L3 LAN, secondary IP (8), static ARP (16), DHCP relay (16 servers), directed broadcast | VERIFIED | DOC | SRC-000029 pp.249–259 |
| App probes default on, ION 1000 exception, DNS probing from 6.3.2, source interface needed on Gen-2 | VERIFIED | DOC | SRC-000029 pp.252–253 |
| L2 switching parameters | UNVERIFIED (deck) pending pp.163–180 | DOC | WS-033 slides 78–83 |
| MTU/NAT/DNS best practices | UNVERIFIED (internal) | DOC | WS-001 §Ports and Interfaces |

## Open questions

- KG-072: read admin guide pp.163–180 (switch ports, VLAN/SVI, L2/L3 mode change) to verify the switching parameters.
- KG-073: reconcile loopback maximum (4 in the L2 section vs 12 in the L3 section) — likely 4 applied to L2 loopbacks historically and 12 is the current overall limit; needs official confirmation.
- KG-074: port-channel WAN support and exact release floors (public release notes 6.5.x/6.6.x under D2).
