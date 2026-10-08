# NAT policies (stacks, sets, rules, zones, pools, prefixes) and use cases

Domain: 2 / 3 | Applies to: Admin Guide May 2025; branch sites only (internal guide) | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Out of the box, the ION source-NATs everything that goes straight out of an Internet port, using the port's own IP. For anything else (inbound services, one-to-one mappings, SIP without ALG, excluding VPN traffic from NAT) you write NAT policy rules. Rules live in a **policy set**, sets live in a **stack**, and one stack is bound per site. Rules match **NAT zones** (bound to interfaces, separate from firewall zones), prefixes, protocols and ports, and apply actions using **NAT pools** (IP ranges bound to interfaces).

## Documented structure (official pp. 581–593)

- Simple stack = one policy set (same name); advanced stack = up to **four policy sets plus a default-rule set**, evaluated left to right. A simple stack becomes advanced when a second set is added. Paths (May 2025): `Manage > Policies > NAT > NAT Stacks > Simple|Advanced`, also `Configuration > Prisma SD-WAN > Policies > NAT`. Bind one stack per site under `Manage > Policies > Bindings` (multi-site edit supported).
- Rule: name; **Source Zone** or **Destination Zone** rule (direction relative to the ION); NAT zone; **order 1–4** (1 = highest); disable flag; match: protocol (name or 1–255), source/destination prefixes, up to **16 port ranges** (TCP/UDP only); actions (max **four** per rule, one pool per action): **No NAT** (exclusive), Source NAT, Destination NAT, Static Source NAT, Static Destination NAT, ALG Disable.
- NAT zones: created and bound to device interfaces (`View Interface Bindings > Bind Interface(s)`); distinct from security zones. NAT pools: ranges with start/end; bound per device interface; **max four IP ranges per device per interface per pool; max 64 pools per interface**; also addable from the Interfaces tab. NAT prefixes: global (all sites) or local (per site; must be attached to a site), optionally replicated for Path and QoS policies.
- CLI names: `dump nat counters`, `dump nat6 counters`, `dump nat summary`.

## Use cases (official pp. 594–601)

- **Default source NAT**: `Default-NATPolicySet` / `Default-InternetRule` (destination zone Internet, any/any/any, Source NAT, empty pool ⇒ interface IP; source port randomized; the ION ARPs for pool addresses inside the interface subnet).
- **Destination NAT**: source zone Internet rule, destination prefix = local prefix with the public /32, port 443, action Destination NAT with pool of the internal server; the ION sends GARP and answers ARP for the public address. Add a source NAT rule if the server must initiate as the same public IP.
- **Static NAT**: 1:1 range mapping (public range ↔ RFC 1918 range, or overlapping private ranges after a merger): Static Destination NAT inbound with a /28 local prefix and contiguous pool, Static Source NAT outbound.
- **ALG Disable**: SIP ALG off for UCaaS; rule with source prefix = phone network and action ALG Disable (protocol SIP), placed in a separate set alongside the default set within a new stack bound to the target sites.

## Internal guidance (WS-001 §NAT Policy)

Default policy suffices for user-to-Internet; inbound DNAT also needs a **path policy rule permitting the Direct Internet path** and, with ZBFW, a security rule from the Internet zone; use Flow Browser to see which policy drops; disable SIP ALG for Webex, Zoom Phone, RingCentral, Teams Direct Routing; put **No NAT** rules above the default SNAT rule; NAT zones must be bound or NAT silently does not apply; **NAT policy is branch-only** ("Policies apply only to branch sites" at DC setup) so DC DIA NAT must be done upstream; with two Internet circuits the ION keeps a flow on one circuit for its lifetime (flow-level, not packet-level, load balancing), preserving the NAT boundary.

## Related

VRF per-VRF NAT for DIA: note 09. Cellular interface NAT zone = internet (note 03). Behind-NAT WAN interfaces need External NAT Address/Port (note 02). DC-DC standard VPN behind NAT: 4500→4501 DNAT (note 04).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Stack/set/rule structure, limits (4 sets, order 1–4, 16 port ranges, 4 actions) | VERIFIED | DOC | SRC-000029 pp.581–588 |
| Zones separate from security zones; must be bound; pools 4 ranges, 64 per interface | VERIFIED | DOC | SRC-000029 pp.590–591 |
| Global/local NAT prefixes | VERIFIED | DOC | SRC-000029 p.593 |
| Default SNAT behavior and the four use cases incl. GARP | VERIFIED | DOC | SRC-000029 pp.594–601 |
| DNAT also needs path policy (and security policy) | UNVERIFIED (internal, strong; consistent with policy model) | DOC | WS-001 §NAT Policy |
| NAT policy branch-only | UNVERIFIED (internal; UI text quoted) | DOC | WS-001 §NAT Policy |
| Flow-level stickiness on dual Internet | CORROBORATED (WS-001 + TSE BGP playbook "path change: asymmetry" note) | DOC | WS-001; SRC-000091 pageId 645960289 |

## Open questions

- KG-082: official statement that NAT policies apply only to branch sites (admin guide text to locate).
