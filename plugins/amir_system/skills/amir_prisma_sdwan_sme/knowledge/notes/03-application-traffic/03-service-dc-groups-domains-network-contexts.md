# Service and DC groups, endpoints, domains, network contexts, policy prefixes

Domain: 3 / 2 | Applies to: Admin Guide May 2025 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

A **service endpoint** is a label for a place traffic can be sent through: a Prisma SD-WAN data center (for transit) or a third-party service reached by a standard VPN (for example Prisma Access or Zscaler). Endpoints are collected into **groups**; groups are mapped to endpoints inside **domains**; each site is bound to exactly one domain. A path policy rule names the group, and the site's domain decides which concrete endpoints that means, so one policy works everywhere with region-specific endpoints. A **network context** tags a LAN segment (guest, corporate, IoT) so the same application can have different rules per segment. **Prefixes** (global or local) let rules match addresses.

## Documented facts (official pp. 470–476, 480–481)

- Endpoints: `Manage > Resources > Service & DC Groups > Manage Endpoints`. Standard VPN endpoints: name, **Admin Up** (required to be used in path selection), **Allow Enterprise Traffic** (let enterprise traffic transit the cloud security service), **Prisma Access** checkbox (set automatically by Easy Onboarding; set manually for hand-made Prisma Access endpoints; drives Site Configuration and Overlay Connections pages), address, **IPs & hostnames** (the ION probes each and builds the tunnel to the lowest-latency endpoint, fails over to the next, and re-optimizes when latency changes unless "Disable Tunnel Reoptimization" is set), **liveliness probes** (ICMP ping: interval, failure count, IP, up to four; HTTP: interval, failure count, status codes, URL, up to four; **Enable DNS Liveliness in Tunnel** resolves probe names over the service link instead of WAN DNS). All Prisma SD-WAN DC sites appear as endpoints automatically when admin up and cannot be deleted (only admin-downed).
- Groups: Standard VPN groups or Prisma SD-WAN (DC) groups; referenced in policy. Domains: collections of groups; several domains, **one domain per site**; endpoints in the same group within a domain are equal in path selection. Bind domains per site on the same page.
- Policy combinations (p. 474–475): active and backup groups may be Standard or Palo Alto Networks (DC) in any pairing; only one Palo Alto group or one non-Palo Alto group per active/backup slot. Examples: cloud security service active with DC backup, DC active with cloud backup, primary/backup cloud services, primary/backup DC groups.
- **Network contexts** (`Manage > Resources > Network Contexts`): a rule with a context always precedes one without; a LAN network belongs to one context; attach to LAN segments on interfaces (example given with a Private L2 bypass pair and attached VLAN networks).
- **Path and QoS prefixes** (`Manage > Policies > Path > Path Prefixes`; QoS equivalent): global (same prefixes at all sites) or local (site-specific values; attach to a site); prefixes created under Path apply only to Path sets, under QoS only to QoS sets; IPv4 and IPv6.

## Internal guidance (WS-001 §DC Group for Transit Traffic; §Network Context)

Define primary and secondary DC per branch; DC groups are needed whenever a rule uses a DC as transit; create DC groups and domains when multiple DCs exist and assign every branch to a domain; summarize DC prefixes at site level. **Required** = always transit via the DC (no direct underlay); unchecked = preference (direct first, DC transit when direct is unavailable or breaches SLA). The ION uses the DC group only when it lacks a more specific route; a DC advertising its prefixes makes the group redundant for those prefixes; a default route (0.0.0.0/0) is advertised over all fabric VPNs so Internet-bound traffic always finds a path, but DC-only enterprise destinations need the group in the rule. Guest vs corporate network contexts example (DIA for guests, DC backhaul for corporate).

## Relation to branch gateways and domains (notes 02-network/06)

Auto-VPNs between branches and branch gateways form only within the same domain; DC targets ignore domains (every branch builds overlays to all mapped DC cluster destinations); changing a site's domain tears down its VPNs (internal TSE playbook).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Endpoint fields incl. admin up, allow enterprise traffic, Prisma Access flag, latency-based endpoint selection and reoptimization, liveliness probes (4 ICMP + 4 HTTP), DNS in tunnel | VERIFIED | DOC | SRC-000029 pp.470–472 |
| DC endpoints auto-created, undeletable; groups; one domain per site; equal endpoints within a group | VERIFIED | DOC | SRC-000029 pp.471–474 |
| Active/backup group combination rules | VERIFIED | DOC | SRC-000029 pp.474–475 |
| Network context precedence and single-membership | VERIFIED | DOC | SRC-000029 p.476 |
| Prefix scoping (global/local; Path vs QoS) | VERIFIED | DOC | SRC-000029 pp.480–481 |
| Required vs preference semantics; group used only without a more specific route; default route advertised over fabric VPNs | UNVERIFIED (internal, strong; partially VERIFIED by p.452 "Required" text) | DOC | WS-001 §DC Group; SRC-000029 p.452 |

## Open questions

- KG-064 progress: domain = site-to-group/endpoint mapping (official); its role in auto-VPN formation is only stated internally. Official confirmation still wanted.
