# Path liveness and quality settings: VPN keep-alives, BFD mode, LQM, bandwidth monitoring, probes

Domain: 2 / 3 | Applies to: Admin Guide May 2025; VPN keep-alives on devices 5.4.1+ | Status: DOCUMENTED (settings); mechanism details deferred to B10 | Last updated: 2026-10-08

## Explanation (plain words)

The device must know quickly whether a path is dead and how good it is. **VPN keep-alives** detect a dead fabric tunnel. **BFD** (Bidirectional Forwarding Detection) is the fast liveness check named on the circuit screen (internal material says it covers the private WAN underlay). **Link Quality Monitoring (LQM)** measures latency, loss and jitter (and a MOS voice score) so path policy can move applications when quality drops. **Bandwidth monitoring** measures how much of the link is really usable. **Application reachability probes** confirm whether a given application is really reachable over a given path when connections start failing.

## Documented settings

| Setting | Where | Values and defaults |
|---|---|---|
| VPN keep-alive failure count | circuit category, circuit (with "Override VPN Keep-Alive"), secure fabric link | 3–30, default **3** |
| VPN keep-alive interval | same three levels | 100–600,000 ms, default **1,000 ms** |
| Precedence | — | secure fabric link > circuit > circuit category; on mismatch between endpoints the larger interval wins, then the higher failure count |
| BFD mode | circuit | Aggressive (default, recommended, fast detection) or Non-aggressive (less probe traffic, lossy links) |
| BW Monitoring | circuit | on by default |
| LQ Monitoring | circuit / category | on by default on branch-to-DC paths; "Use LQM for Non Hub Paths" off by default; aggregation min/max/avg over chosen DCs |
| App reachability probes | device Basic Info and per circuit/category | on by default (except ION 1000); excludable per circuit/category |
| Controller connections | per circuit/category | on by default; excludable |
| L3 reachability probes | circuit / category | profile, probe configs, endpoints; "Use Element Default" |

Internal guide: Aggressive = 1,000 ms × 3 = 3-second detection; higher keep-alive intervals on LTE reduce cost but slow failover. Deck: LQM is used for VPN and private WAN path performance; PCM measures usable bandwidth; BFD determines VPN liveness and private WAN underlay reachability.

## Mechanism (to be documented in B10 from the path-selection and performance sections and the LQM internal note SRC-000101)

Open: how LQM thresholds trigger path moves; the exact meaning of BFD aggressive timers; how app probes interact with the flow controller ("path NA" troubleshooting).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Keep-alive ranges, defaults, three levels, precedence, mismatch resolution | VERIFIED | DOC | SRC-000029 pp.260–263 |
| BFD mode options and recommendation | VERIFIED | DOC | SRC-000029 p.68 |
| LQM default scope and non-hub option | VERIFIED | DOC | SRC-000029 pp.69–72 |
| 3-second detection arithmetic | INFERRED from the documented defaults; stated by WS-001 | DOC | WS-001 §VPNs Configs |
| BFD = private WAN underlay reachability; LQM for VPN and private WAN; PCM = bandwidth | UNVERIFIED (deck glossary) | DOC | WS-033 slide 30 |

## Open questions

- KG-071 (shared with note 01): official definition of what BFD aggressive/non-aggressive changes (timers) and its relation to VPN keep-alives.
- KG-011 remains: HA failover timers.
