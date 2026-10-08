# Zone-Based Firewall (ZBFW) and stacked security policies

Domain: 4 | Applies to: Admin Guide May 2025 pp. 487–504 (stacked), 561–569 (constructs, Original), 578–579; WS-001 §Security Policy (ZBFW); internal ZBFW debugging pages (2016) | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Every ION carries a stateful, application-aware firewall organised by **zones**. A zone is a label you bind to interfaces or networks (LAN VLANs, WAN circuits, VPNs). Rules say what may pass between a source zone and a destination zone, optionally narrowed by application, IP prefixes, protocol and ports. Nothing is filtered until a **security stack is bound to the site**; once it is, the three built-in rules (Intra-Zone allow, Self-Zone allow, Default deny) make the posture deny-by-default for traffic between zones. Security policy always wins over path policy: a denied flow is dropped no matter where path policy would send it.

## Documented facts (official)

- **Stacked vs Original**: new tenants from Release 6.0.1 only see stacked security policies; legacy (Original) policies must be migrated before upgrading a device to 6.0.1 (upgrade is blocked with an error). Stacked policies need ION 5.6+ to take effect (p.488).
- **Stacks**: simple (one set, same name as the stack, rules added directly) or advanced (≤4 ordered sets + one default set; left-most highest). One stack per site; bind under `Manage > Policies > Bindings`, optionally to many sites at once (p.490).
- **Sets**: Normal sets have no implicit rules; the **Default set** holds the implicit Intra-Zone, Self-Zone and Catch-All Deny rules. Sets can be cloned from stacked or Original sets (p.491).
- **Rules** (p.494–495): order 1–65535 (1 highest; blank = lowest); actions **Allow**, **Deny** (silent drop, no RESET/ICMP) or **Reject** (TCP RESET to both ends); Disable Rule flag; Services tab: protocol, ≤16 source and ≤16 destination port ranges; Zones & Prefixes tab: source/destination zone and prefix; Applications tab: **≤16 applications per rule**, with filters "sites 6.0.1 or above" (PANW system apps, common apps, custom), "below 6.0.1" (legacy CGX apps) and "any site" (common + custom).
- **Default rules** (p.563–564): Default denies all inter-zone traffic; Self-Zone allows traffic to/from the ION on trusted L3 interfaces (L3 LAN, controller, L3 private WAN); on an untrusted L3 public WAN interface only ION-initiated traffic is permitted, and **unsolicited inbound traffic to a public WAN port is dropped regardless of ZBFW policy**; Intra-Zone allows traffic within a zone. "There is no limit on the number of security policy rules" (p.564).
- **Zones** (p.496, 498–499): created under `Manage > Policies > Security > Security Zones`; **SYN EXCEPTION** per zone lets the ION pass TCP sessions in that zone without having seen the handshake (asymmetric or long-lived sessions); a zone must be bound to a site or interface, otherwise all traffic is blocked; typical model: guest, one or more corporate LAN, outside (Internet underlay), corporate WAN (private WAN + VPN). Bindings at site level (circuits) or device level (interfaces); both are merged and **device-level wins on conflict**; each network/interface belongs to exactly one zone; all VPNs bind to a single zone.
- **Bindable interfaces** (p.499): WAN-labelled L3 standalone, sub-interface, PPPoE, L3 bypass-pair WAN member, L2 bypass-pair WAN member, loopback bypass pairs; LAN-side standalone L3, L3 bypass pair LAN member, L3 sub-interface, non-parent interface with Used_for NONE, standard tunnel interface. **Not bindable**: controller interfaces, LAN member of an L2 bypass pair, parent interfaces of sub-interfaces/PPPoE.
- **Prefixes** (p.501–502): global (same values everywhere) or local (per-site values attached by Bind Site); created for policy type NGFWSECURITY with optional copies for Path, QoS and NAT policy types.
- **Monitoring** (p.503–504): View Summary Stats (hits per rule per site; default past 1 hour; total can exceed the sum because unbound-site matches are counted) and Monitor Rules per site; audit logs per rule.
- Original-policy extras still documented: policy stance Optimum / Conservative / Standard when creating an Original set (p.568); rule reorder by drag and drop with Save Ranking (p.578).
- CLI names: `inspect security policy lookup|size`, `inspect policy manager status`, `inspect policy mix lookup flow`, `dump security policy config policy rules|policy set|policy set stack|prefix filters|zones` (p.488–489; CLI reference spells it `dump security-policy config zones`).

## Internal guidance (WS-001 §Security Policy, May 2026; strong)

- With **no stack bound**, nothing is filtered except unsolicited inbound on public WAN interfaces (always dropped).
- Use device-level binding and give **every interface a zone**; an unbound interface silently drops traffic (most common deployment mistake). Do not run site-level and device-level bindings together.
- Never leave source or destination zone empty: it explodes the compiled policy table and causes **Out-of-Memory (OOM)** on ION 1000/1200/2000, especially from 6.3.6, 6.4.3 and 6.5.3; large prefix lists, many /32s, full port ranges (1–65535 becomes 65,535 entries) and stale custom apps compound it. Aggregate prefixes, use exact ports, audit custom apps, check memory under `Insights > ION Devices > Device Activity` first, change incrementally in maintenance windows.
- Top-down first-match; specific above general; keep app-based and port/prefix-based rules separate; inbound DNAT needs a matching ZBFW allow from the Internet zone; validate with Monitor Rule and Flow Browser (`Insights > Prisma SD-WAN > Branch Sites > Flows`).
- **OOM recovery**: unbind the stack in SCM, wait about 30 s, reapply a smaller policy; else power-cycle; for a reboot loop use console 115200/8/N/1, unbind the policy, run `debug process stop name=fc` (about 5 min), confirm controller reconnect, run `debug process start name=fc`, reapply the last known-good policy.
- Deck slide 197: reserved system zone named `internet` (lowercase) cannot be modified. Release notes 6.5: fix CGSDW-16172 for ZBFW first-packet block handling LAN-to-LAN vs LAN-to-WAN (fixed in 6.3.1/6.1.7).

## Internal debugging (2016 CGXKB pages 74187121 / 74187067; commands OBSOLETE, mechanics useful)

Flow-controller trace shows the sequence per first packet: app lookup (dst ip/port, src ip/port, port-only, ip-only, 5-tuple custom app, off-path app map), then network policy lookup with the most granular app and then app 0 default, then WAN path candidates pruned by active/backup, then a **security lookup per candidate path's destination zone** (`wan_security_check`), then the path is chosen among paths that are both available and allowed. Continuous detection re-runs the security lookup when the app changes (for example http-l4 to http) and the rule hit can change mid-flow. Security data lives in the device Redis DB 10 (`active_security_policyset_id`, `security_zones`, `prefix_filters`); only one security set is active per site. The `cglog_ctl` trace commands are 2016-era and absent from the current CLI reference, so they are OBSOLETE.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Stacked-only from 6.0.1, migration gate, ION 5.6 floor for stacked | VERIFIED | DOC | SRC-000029 p.488 |
| Stack/set structure, ≤4 sets, one stack per site | VERIFIED | DOC | SRC-000029 pp.490–491 |
| Rule fields: order 1–65535, Allow/Deny/Reject semantics, ≤16 port ranges each, ≤16 apps | VERIFIED | DOC | SRC-000029 pp.494–495 |
| Default rules; unsolicited inbound on public WAN dropped regardless of policy | VERIFIED | DOC | SRC-000029 pp.563–564; WS-001 |
| Zone binding rules, device-level precedence, unbound = blocked, bindable interface list | VERIFIED | DOC | SRC-000029 pp.496–499, 566 |
| SYN EXCEPTION per zone | VERIFIED (PRD 185806733 targets 6.5.1, DRAFT) | DOC | SRC-000029 p.496 |
| Security policy supersedes network (path) policy | VERIFIED | DOC | SRC-000029 pp.565, 568; WS-001 |
| "No limit on number of rules" vs platform OOM risk | VERIFIED both; practical limit is memory | DOC | SRC-000029 p.564; WS-001 |
| OOM symptoms, affected releases and recovery procedure | UNVERIFIED (internal, strong) | DOC | WS-001 §Security Policy |
| Reserved zone `internet` | UNVERIFIED (deck) | DOC | WS-033 slide 197 |
| Security lookup per candidate WAN path; re-evaluation on app change | UNVERIFIED (internal 2016 trace; commands OBSOLETE) | DOC | Confluence 74187121 |

## Open questions

- KG-090: current official statement of ZBFW rule/zone/prefix scale limits per platform (only "no limit" plus internal OOM guidance exist).
- KG-091: ZBFW behaviour for VPN-to-VPN transit at a DC/hub ION and for IPv6 (roadmap slide mentions IPv6 ZBFW; no official floor).
