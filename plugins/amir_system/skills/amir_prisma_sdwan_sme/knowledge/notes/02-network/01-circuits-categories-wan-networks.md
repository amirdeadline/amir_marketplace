# Circuits, circuit categories, circuit labels, WAN networks

Domain: 2 (Network) | Applies to: Admin Guide May 2025 navigation; ION 5.4.1+ for VPN keep-alives | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

A **circuit** is one WAN link at a site (for example "Chicago Internet from Verizon"). Every circuit has a **circuit category** (its type, such as Internet Cable or MPLS; the category is what path policy rules refer to), a **circuit label** (the category applied at the site, attached to the interface so the device knows which port is which WAN link), and a **WAN network** (the carrier, such as AT&T). The circuit also carries its speed, which drives QoS shaping, and a set of monitoring switches (bandwidth monitoring, link quality monitoring, application reachability probes, controller connections) that feed path selection.

## Documented behavior

- Circuit categories are pre-defined and editable; **64 categories exist, at most 32 public and 32 private** (`Manage > Resources > Circuit Categories`). Settings at circuit level override circuit-category level.
- Circuit creation (`Workflows > Sites/Data Centers > Configuration > Internet Circuits / Private WAN Circuits > Add/Change Circuits`): pick circuit and provider, name, **Link Down / Link Up speed (used for QoS shaping rates)**, BW Configuration = manual (default), BW Monitoring (on by default), QoS yes/no, Use for Application Reachability Probes, LQ Monitoring (on by default on branch-to-DC paths), **BFD mode Aggressive (default, recommended) or Non-aggressive** (less probe traffic, for lossy links), VPN Keep-Alive Failure Count and Interval (devices 5.4.1+), L3 reachability probe configuration (profile, probe configs, endpoints, or element default), **Cost default 128** (lower = preferred).
- Circuit category options: Use For Controller Connections, Use for Application Reachability Probes, QoS, LQM settings (LQ Monitoring; **Use LQM for Non Hub Paths**), probe config, VPN keep-alive failure count 3–30 (default 3) and interval 100–600,000 ms (default 1,000 ms).
- **Internet underlay link quality aggregation:** LQM-based path selection works for underlay, VPN and standard VPN paths; the ION aggregates overlay LQM values toward one or more data centers, branch gateways, or Prisma Access remote-network hubs to compute the underlay value. "Use LQM for Non Hub Paths" is off by default; enable per circuit or (recommended) per category; choose DCs (default all) and aggregation Minimum (default) / Maximum / Average. Same aggregation choice exists for private WAN underlay.
- **Device-initiated connections** (MRL, statistics, flows, logs, remote toolkit access) and application probes can be excluded from a circuit or category (metered LTE). Source preference order: controller port, LAN port, any unlabeled interface with an IP, then labeled interfaces by circuit cost (higher cost = lower preference). Alarm `DEVICESW_INITIATED_CONNECTION_ON_EXCLUDED_PATH` fires when an excluded path had to be used as last resort.
- Enterprise prefixes: built-in policies forward and prioritize enterprise prefixes; add public IP LAN ranges at `Manage > System > Enterprise Prefixes` (IPv4 and IPv6).
- Static SGT (Security Group Tag) value per site (1–65533) tags ION-initiated traffic with Cisco metadata so downstream Cisco devices can apply role-based policy.

## Internal best-practice guidance (TME, May 2026; strong internal)

- Define all WAN networks (providers) once for the whole estate and reuse them; provider name is the key for incident correlation.
- Name circuits with site, type and provider (for example `CHI-INET-VZN`, `NYC-DC-MPLS-ATT`); add descriptions and tags.
- Set circuit speeds from carrier values, about 1–2% lower than rated so QoS engages before the circuit saturates; DC circuit bandwidth is informational only (no shaping on DC).
- Aggressive mode: 1,000 ms interval, fail count 3, so 3-second failure detection; overridable per circuit or secure fabric link.
- Keep BW Monitoring, LQ Monitoring, App Reachability Probes and Controller Connections enabled except on metered/last-resort circuits. Use "Minimize Metered LTE Usage" (admin guide p. 456) for LTE/5G; it raises cost and stops controller statistics/connections on that circuit; outgoing traffic still needs a path policy that uses the circuit only on L3 failure.
- **You cannot use the same circuit category twice at a site** (the category defines the label used in policy); rename categories into a convention (for example `ACME-INTERNET-1`, `ACME-INTERNET-2`). The guide says "30 Internet categories and 30 public categories" which conflicts with the official 32/32 wording (CONFLICTED; official number preferred).
- Private circuits: the **WAN network must match at branch and DC** for an overlay over a private path, otherwise the VPN does not come up.
- **Always assign a circuit label to every WAN-facing interface**, including Standard-VPN-only designs; without it no WAN interface context exists and no WAN path is selected even though tunnels show up. Symptom: Flow Decision Data shows "Available WAN Networks: empty" with reason "All Active and Backup paths with a route for destination prefix are down or have L3 failures". Check with `dump waninterface summary` (internal spelling; official list shows `dump wan interface summary`).

## Deck (internal, Feb 2026)

Circuit labels define connection type (Internet / Private WAN), circuit category (used in path policy; metered 3G/4G/LTE label for backup), and WAN carrier name. Internet WAN name is informational and any Internet WAN can form a VPN with any other; a Private WAN forms zero-touch tunnels only with IONs that have the same WAN definition, or manually via "Add Secure Fabric Link". Provisioned link speeds drive QoS shaping and load distribution by headroom; BW Monitoring detects usable bidirectional bandwidth; LQ Monitoring measures latency, jitter, loss and a MOS score toward DC nodes; "Auto" bandwidth configuration is reserved for future use.

## Verification

- Flow details show path and circuit names (Flow Browser); Link Quality dashboard shows per-path metrics (admin guide p. 49).
- CLI names from the admin guide: `dump wan interface summary`, `dump wan interface config`, `inspect wan paths`, `dump vpn ka summary`, `dump vpn status`.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| 64 circuit categories, max 32 public and 32 private; circuit settings override category | VERIFIED | DOC | SRC-000029 p.71 |
| Circuit fields: speeds for QoS shaping, BW monitoring default on, LQM default on branch-to-DC, BFD aggressive default and recommended, cost default 128 | VERIFIED | DOC | SRC-000029 pp.68–69 |
| Keep-alive ranges: failure count 3–30 (default 3), interval 100–600,000 ms (default 1,000) | VERIFIED | DOC | SRC-000029 pp.72, 261–262 |
| Use LQM for Non Hub Paths off by default; aggregation min/max/avg, default min; DC selection default all | VERIFIED | DOC | SRC-000029 pp.69–71 |
| Device-initiated connection source order and `DEVICESW_INITIATED_CONNECTION_ON_EXCLUDED_PATH` alarm | VERIFIED | DOC | SRC-000029 pp.72–74 |
| Enterprise prefixes path | VERIFIED (May 2025 navigation) | DOC | SRC-000029 pp.74–75 |
| Static SGT range 1–65533 | VERIFIED | DOC | SRC-000029 pp.58, 67 |
| Same category cannot be used twice per site; "30 categories" | UNVERIFIED (internal); number CONFLICTED with official 32 | DOC | WS-001 §Circuit Settings |
| WAN network must match at both ends for private overlay | CORROBORATED (internal guide + deck; official text on secure fabric links to confirm in B5) | DOC | WS-001; WS-033 slide 88 |
| Circuit label mandatory on WAN interfaces; empty WAN networks symptom | UNVERIFIED (internal, field experience) | DOC | WS-001 §Circuit Settings |
| 1–2% lower speed than rated; DC bandwidth informational only | UNVERIFIED (internal recommendation) | DOC | WS-001 §Circuit Settings |

## Open questions

- KG-070: official source for "DC circuit bandwidth is informational only (no shaping on DC)".
- KG-071: official statement of what BFD mode controls versus VPN keep-alives (the guide shows both on the same screen; internal guide says BFD is used for the MPLS underlay and keep-alives for VPN).
