# Network segmentation design: zone model, subinterfaces, intra-site security rules, guest access (SASE Network Segmentation Solution Guide Oct 2025)

Domain: 9 (design) / 4 | Applies to: SRC-000045 Oct 2025 (44 pp; validated SCM 2025.r3.0, Prisma Access 6.0.0 Preferred, ION 6.5.2); builds on SRC-000037/038 | Status: VERIFIED (official) | Last updated: 2026-10-08

## Explanation (plain words)

Local segmentation on a branch ION means: one LAN port carries several VLAN subinterfaces, each VLAN is one subnet and one **security zone**, and the zone-based firewall decides which applications may cross between zones. The guide's method is a **zone matrix** (sources down the side, destinations across the top, applications in each cell, built-in rules filling the rest) turned into **one-directional rules**. Guest access adds a **network context** with Local scope (same guest subnet at every site), a direct-internet path rule with no backup, and deny rules both ways between GUEST and everything else.

## Zone model (pp.13–16)

PRIVATE (general users), PRIVILEGED (site operators), IOT, SERVICES (shared services), PUBLIC (internet circuits), PRIVATEWAN (MPLS/leased), VPN (fabric tunnels), GUEST. Fewer or more zones as the organisation's policy needs. Link types: port, **subinterface (LAN port + VLAN + zone)**, lan (site prefixes), privatewan, publicwan, service_link, vpn. **Bind zones to all subinterfaces before binding the stack; device-level binding recommended** (same text as the design guide).

## Rule semantics worth remembering (pp.14, 22–23)

- Actions Deny (silent), Reject (TCP reset to both ends), Allow. Match: order, zones, global/local prefix filters, users/groups, services, applications.
- Built-in rules self-zone / intra-zone / default (deny all); more specific rules win.
- **enterprise-http and enterprise-ssl match only when the destination is inside the enterprise prefixes** (default RFC 1918; edit under `Configuration > System > Enterprise Prefixes`) — use them for internal browsing, web-browsing/ssl for internet.
- App-ID dependencies: allow dependent App-IDs or the application breaks.

## Example rule sets (Tables 2, 3)

- Inter-site/internet additions (orders 6–12): PRIVILEGED↔VPN, PRIVILEGED→PUBLIC, SERVICES↔VPN, SERVICES→PUBLIC, IOT→PUBLIC with dns-base, enterprise-http/ssl or web-browsing/ssl, ping.
- Intra-site (orders 13–17): PRIVATE→SERVICES (dhcp, dns-base, enterprise-http/ssl, ping), PRIVILEGED→PRIVATE/IOT/SERVICES (enterprise-http/ssl, ping, ssh, plus dhcp/dns-base to SERVICES), IOT→SERVICES (dhcp, dns-base, ping). The guide labels these as examples, not a complete policy.
- Stack: clone the existing set ("ZBFW RuleSet Local Segmentation"), stack "ZBFW SecurityStack Local Segmentation" with DefaultSet as default-rule set; bind on Stacked Bindings only to sites needing segmentation.

## Subinterfaces (pp.29–31)

Reset the physical port to defaults first (`ION Devices > device > Interfaces > Port > Reset to defaults`), Admin Up; **Sub Interfaces > Add**: VLAN, **Native VLAN only on the first subinterface**, use LAN, **Application Reachability Probe Source enabled only on the first**, **Scope Global** (needed for BGP advertisement towards Prisma Access), static IP = default gateway of that VLAN on the switch. Example VLANs 151/152/153/160 → 10.130.0–3.0/24. Then bind zones per subinterface (2.151 → Private, 2.152 → Privileged …).

## Guest access (pp.34–42)

1. Network context "Guest" (`Configuration > Resources > Network Contexts`).
2. Path set "Guest Access" with rule "Guest DIA": Network Context Guest, active **Direct on Any Public**, **no backup path**; default NAT rule covers DIA. Insert as Policy Set 1 in both stacks (Prisma Access Bypass moves to Policy Set 2; MPLS Direct to Set 2 where used).
3. Zone GUEST; security set "ZBFW RuleSet Guest": **GUEST→PUBLIC allow (dns-base, web-browsing, ssl, ping)**, **GUEST→Any deny**, **Any→GUEST deny**; add as Policy Set 2 of the existing stacks. "--" in a zone list means Any.
4. Bind GUEST to the guest LAN interface (example Port 4 on an ION 1000); interface: LAN, Network Context Guest, **Scope Local** (same 192.168.255.0/24 at every site), static IP; DHCP scope guest.example.com with public DNS.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Zone model, link types, rule semantics, enterprise-http/ssl behaviour | VERIFIED (official, Oct 2025) | DOC | SRC-000045 pp.12–23 |
| Subinterface procedure constraints (reset, native VLAN first, probe source first, Global scope) | VERIFIED | DOC | SRC-000045 pp.29–31 |
| Guest design (context + Local scope + direct-only path + two deny rules) | VERIFIED | DOC | SRC-000045 pp.34–42 |

## Open questions

- KG-130: whether a network context alone (without GUEST zone rules) leaks between contexts is stated as "inter-context traffic permitted by default" (SRC-000038 p.34); confirm against the admin guide network-context chapter wording (note 02-network/09 covers VRF, not contexts).
