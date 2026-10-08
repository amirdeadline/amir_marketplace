# S11 — Guest Wi-Fi segmentation request

Domains: 4, 9 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Retail customer, 60 branches on ION 1200-S (6.5.x), existing ZBFW stack with PRIVATE/PUBLIC/VPN zones and Prisma Access DIA for corporate traffic. They want guest Wi-Fi: Internet only, no access to corporate or other branches, the same guest subnet at every store, and guest traffic must **not** consume Prisma Access bandwidth.

## 2. Question

Design and configure it; state the traps.

## 3. Reasoning chain

1. Isolation tool choice: a **network context** tags the LAN segment for differentiated policy but does not isolate (inter-context traffic is permitted by default); a **VRF** gives true isolation but is heavier and (per internal 6.3.1 notes) constrains standard-VPN use. The official guest pattern is context + zone + security rules. [VERIFIED — 10-design/01 (SRC-000038 pp.34–35), 10-design/03 (SRC-000045 pp.34–42); UNVERIFIED (internal) for VRF limits — 02-network/09]
2. Same subnet everywhere: set the guest interface **Scope Local** (not advertised into the fabric), so 192.168.255.0/24 (example) can repeat per site. [VERIFIED — SRC-000045 pp.40–41; SRC-000038 p.35]
3. Path: path set "Guest Access" with one rule matching the Guest network context, active **Direct on Any Public**, **no backup** (so guests never fall back to the fabric or Prisma Access); insert as Policy Set 1 above the Prisma Access bypass set; context rules always beat rules without a context. Default NAT rule source-NATs on the Internet port. [VERIFIED — SRC-000045 pp.35–37; 03-application-traffic/03 (SRC-000029 p.476); 02-network/11]
4. Security: zone GUEST; set "ZBFW RuleSet Guest": GUEST→PUBLIC allow (dns-base, web-browsing, ssl, ping), GUEST→Any deny, Any→GUEST deny; add as Policy Set 2 of the existing stack; bind GUEST to the guest LAN port on every device (unbound interfaces drop everything). [VERIFIED — SRC-000045 pp.37–40; 04-security/01]
5. DHCP for guests from the ION with public DNS; guest domain name separate. [VERIFIED — SRC-000045 pp.41–42]
6. Traps: (a) the Internet-bound Prisma Access rule in the default set would catch guest traffic without the context rule above it; (b) forgetting the zone binding on the guest port drops all guest traffic; (c) site-level and device-level bindings mixed; (d) "deny" is silent — use Reject only if clients should get a reset; (e) guests on an interface in the Global VRF still share the ION's NAT and Internet circuits — bandwidth fairness needs QoS (guest class Bronze or a lower share). [VERIFIED for (a)–(d) — SRC-000045, SRC-000038 p.48; INFERENCE for (e) from QoS defaults — SRC-000038 p.45]

## 4. Answer

Create the Guest network context, a GUEST zone, the three-rule guest security set, a one-rule guest path set (context match, Direct Any Public, no backup) placed above the Prisma Access rules, configure the guest port as LAN / context Guest / Scope Local with a static IP and DHCP scope, bind GUEST to that port on each device, and bind the updated stacks to the stores. Guests then exit locally, never reach the fabric, and never use Prisma Access.

## 5. What to check / collect next

Flow Browser for a guest client: path = Direct public, zone pair GUEST→PUBLIC; `inspect flow detail` SEC-ACTION; confirm the guest subnet is not visible in `inspect wanpaths` at other sites (Local scope). [VERIFIED command names — 08-troubleshooting/02]

## 6. Gaps exposed

KG-130 (network-context chapter wording). New: **KG-138** — whether a per-context QoS rule or a circuit sub-allocation is the documented way to cap guest bandwidth.

## 7. Validation status

**SCENARIO VALIDATED** — the configuration path is fully VERIFIED (official solution guide); bandwidth capping is an open design question.
