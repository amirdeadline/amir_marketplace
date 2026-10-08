# How the ION measures paths: LQM, application reachability probes, L3 reachability, service health probes, VPN keep-alives, standard VPN liveliness

Domain: 3 / 8 | Applies to: Admin Guide May 2025 (pp. 540–549, 252–253, 260–263); internal LQM runbook SRC-000101 | Status: EVIDENCE REVIEWED | Last updated: 2026-10-08

## Explanation (plain words)

The ION builds its picture of every path from five kinds of evidence. **Real user traffic** gives TCP handshake failures, retransmissions, round-trip times, server response times, DNS times and voice/video quality. **Application reachability probes** are synthetic copies of a failed TCP SYN sent on the suspect path. **L3 reachability** checks whether a circuit can still reach the Internet when all its VPNs are down. **Service health probes** (6.4.1+) are always-on ICMP/DNS/HTTP(S) checks to chosen endpoints over any path type. **Link Quality Monitoring (LQM)** measures latency, loss, jitter and MOS on fabric VPNs toward data centers and branch gateways. Fabric VPN **keep-alives** and standard VPN **liveliness probes / DPD** decide whether a tunnel is up at all.

## Documented mechanisms (official pp. 547–549 unless noted)

| Source | What it measures | Behavior |
|---|---|---|
| Real user traffic | init success/failure (TCP 3-way handshake), transaction success/failure (retransmissions), RTT, SRT (server response time), NTTn (TCP window completion), DNS transaction time, voice MOS, voice/video loss and jitter | passive; only some are SLA-usable (init failure, RTT, UDP-TRT); others for visibility (deck) |
| App reachability probe (pp. 252–253, 547) | per app / path / prefix | on a LAN-initiated TCP handshake failure the ION crafts a synthetic SYN on that path; failure marks the path unusable for that app/prefix; re-probes every **1 minute** until success; **UDP DNS probing from 6.3.2** (once a minute for three probes, then every 5 minutes); source interface: controller port by default, LAN port configurable; **Gen-2 models need a configured source interface**; ION 1000 must configure a LAN port; excludable per circuit/category |
| L3 reachability (p. 548) | circuit usable at Layer 3 | triggered when all VPNs on a WAN interface are down and no inbound traffic; defaults: ping 8.8.8.8, 8.8.4.4, 208.67.222.222; HTTPS GET captive.apple.com and captive.google.com; **from 6.4.1 can use service health probe results instead** (customizable endpoints); failing circuits are removed from path selection even if physically up (captive portal, upstream ISP fault) |
| Service health probes (pp. 540–543, 549; 6.4.1+) | ICMP latency/loss/jitter; DNS transaction time/failure rate; HTTP/S transaction time (incl. content download), failure rate, response code, content validation, allow-invalid-certificate | probe profiles (global, ≤8 probe configs each; default profile cannot be removed) bound to circuit categories/circuits; probe config: IP/FQDN/URL, cycle duration 1 s–60 min, probe count ×1/2/3, path type (Direct, Prisma SD-WAN VPN, Standard VPN), protocol; **up to 8 endpoints per circuit**; results feed Probe SLAs (failover as low as 1,000 ms) and L3 reachability; viewed per circuit under Branch Sites and in Flow Decision Data |
| LQM (p. 548–549; circuit settings note 02-network/01) | latency, loss, jitter, link MOS on branch-to-DC and branch-to-branch-gateway VPNs | automatic and continuous; visible in UI; SLA criteria; disable per category/circuit; "Use LQM for Non Hub Paths" extends to Internet underlay, branch-to-branch and Prisma Access paths by aggregating DC-side values (min/max/avg) |
| Fabric VPN keep-alives (pp. 260–263, 548) | VPN up/down | default 1 s interval, 3 failures; tunable to 100 ms × 3 = **300 ms detection**; precedence secure fabric link > circuit > category |
| Standard VPN liveliness (p. 548; p. 472) | tunnel to third party | ICMP: interval 1–30 s, failure count 3–300; HTTP: interval 10–3600 s, failure count 3–300, status codes, URL; up to four of each; IKE DPD for IPsec; "Enable DNS Liveliness in Tunnel" |
| ADEM (p. 549) | always-on synthetic monitoring for business-critical apps | ION acts as a remote-network sensor; non-actionable for path selection (deck) |

## Internal LQM runbook (SRC-000101, PAEE; internal)

- LQM client on the spoke opens a **UDP session to the hub on destination port 443** (random source port); probe packets are RTP-style UDP sent in both directions, **100 ms apart** during a measurement phase.
- Branch samples every **1 minute** (600-probe sample) and sends to the controller; hub samples every **10 seconds**; so branch and hub values can differ (hub may show 0 while branch shows loss).
- Diagnostic sequence: `dump vpn summary RemoteSite=<hub>` → `dump vpn status VpnID=<id>` (note `vpnlink_id`) → `inspect lqm stats path-id=<vpnlink_id>` (RTT, uplink/downlink jitter, loss, MOS, health scores) → on the hub `inspect lqm-server session-stats vpn-link-ids=<id>`; check circuit egress loss on the controller and other VPNs on the same underlay first. Health score fields: uplink/downlink/tunnel/packet-loss/RTT health scores (0–100). Example in the runbook shows 2% uplink loss marking the link unhealthy.

## Verification (UI)

Monitor > Branch Sites > circuit > probe health; Flow Browser → Advanced Info → **Flow Decision Data** (SLA violations, actions, forced-move reason); Application Site Details (path performance, app reachability per transport); incidents `APPLICATION_PERFORMANCE_DEGRADED`, `CIRCUIT_PERFORMANCE_DEGRADED`.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Real-traffic metric list; app reachability probe mechanism and 1-minute cadence; DNS probing 6.3.2 | VERIFIED | DOC | SRC-000029 pp.252, 547–548 |
| L3 reachability defaults (3 pings, 2 HTTPS GETs) and 6.4.1 probe option | VERIFIED | DOC | SRC-000029 p.548 |
| Service health probe parameters, 8 per circuit, 1,000 ms failover claim | VERIFIED | DOC | SRC-000029 pp.540–542, 549 |
| Keep-alive 100 ms × 3 = 300 ms tuning | VERIFIED | DOC | SRC-000029 p.548 |
| Standard VPN liveliness ranges | VERIFIED | DOC | SRC-000029 p.548 |
| LQM transport (UDP 443, 100 ms spacing), 1-minute vs 10-second sampling, CLI sequence | UNVERIFIED (internal PAEE) | DOC | SRC-000101 |
| LQM scope: branch-to-DC and branch-to-branch-gateway VPNs | VERIFIED | DOC | SRC-000029 p.548 |

## Open questions

- KG-071 progress: the official text now ties fabric VPN liveness to keep-alives; the BFD mode selector on circuits still lacks an official timer definition. KG-011 (HA) separate.
