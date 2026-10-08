# Sites, domains, clusters and the basic object model

Domain: 1 (overview; details in domain 2 batches) | Applies to: Admin Guide May 2025, ION 6.x | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Everything in Prisma SD-WAN hangs off **sites**. A site is a branch or a data center (or a branch gateway, which is a branch that also acts as a small hub). Each site has **circuits** (its WAN links, each tagged with a circuit category such as MPLS or Internet), one or more **ION devices** (or placeholders called device shells), and the policies that apply there (path, QoS, security, NAT, performance stacks). Branches belong to a **domain** that says which data centers they talk to, and data centers can be grouped into **clusters** for scale.

## Object model (from the QA export contract and the admin guide; API names in parentheses)

- Tenant-scoped: WAN networks (`wannetworks`), circuit categories/labels, policy stacks and sets, security zones, profiles, application definitions (`appdefs`), service and DC groups, prefix filters, network contexts, SASE connectivity.
- Site-scoped (`/sites/{site_id}/...`): circuits (`waninterfaces`), LAN networks, DHCP servers, spoke clusters (HA), hub clusters, Prisma Access connections.
- Element-scoped (`/sites/{site_id}/elements/{element_id}/...`): interfaces, static routes, BGP, OSPF, SNMP, NTP, IPFIX, DNS, switch configuration.
(Scope model from SRC-000004, internal QA contract; the admin guide confirms the same hierarchy in its navigation.)

## Site types (official)

| Type | Role | Where |
|---|---|---|
| Branch | where users are; ION is the WAN gateway; path selection, QoS, app recognition, telemetry | `Workflows > Prisma SD-WAN Setup > Branch Sites > Add Site` |
| Data center | hub hosting applications; terminates branch VPNs (active/active per deck); integrates with existing DC routing; injects branch routes into the core so return traffic is symmetric | `Workflows > Prisma SD-WAN Setup > Data Centers > Add Site` |
| Branch gateway (6.4.1+) | branch that also offers hub services (policy transit, LQM server) for regional sites; one-click enable; tunnels form automatically to branch sites in the domain | branch site setting "Configure as a Branch Gateway site" |

## Creating a branch (official steps, May 2025 navigation)

1. General: name, city, country (address search recommended); optional Branch Gateway; Static SGI value 1–65533 (Security Group Information, default enabled).
2. Domain and policies: pick a domain (a preset domain is offered); "Associate Branch With Default Data Center Cluster" is checked by default; select the default Path, Performance, QoS, Security and NAT policy stacks.
3. Circuits: add Internet and Private WAN circuits; predefined circuit categories exist and can be edited under Circuit Categories in Stacked Policies.
4. Devices: assign claimed devices or create up to two device shells to pre-provision.
Sites can be created before devices arrive; a new site is off by default. At least one branch site and one ION are needed to start. The DC needs activation only for Control mode; tunnels form automatically once both branch and DC are active.

## Branch gateway conversion prerequisites (official)

Site in Control mode; L3 Direct Private WAN Forwarding enabled; L3 LAN Forwarding enabled; no existing branch-to-branch VPN tunnels (they are deleted during conversion); conversion reboots the ION.

## Device defaults when configuring a branch ION (official p. 148)

- "Enable L3 Direct Private WAN Forwarding" on by default: Layer 3 forwarding over the private WAN underlay without extra encapsulation.
- "Enable L3 LAN Forwarding" on by default; only applicable when the above is enabled.
- "Application Reachability Probe" on by default: probes a path only when an application/destination is deemed unreachable; the probing interface is configurable.

## Fabric defaults (internal deck, consistent with official)

- Branches automatically establish zero-touch tunnels to all DC (hub) nodes; full or partial mesh is possible; DC sites do active/active VPN termination, horizontal scaling by clustering, off-path insertion, BGP with the DC core with flow symmetry.
- Official: "Configure Secure SD-WAN Fabric Tunnels between Data Centers" (p. 89) and "between Branch Sites" (p. 92); "Manage Data Center Clusters" (p. 85). Details in B5.

## Terms (internal deck slide 30, use for navigation only)

ION, App-Fabric, MIC, CIC, TPM, HA, fail-to-wire, claiming, scope (global/local) of inner tunnel IP advertisement, Control mode vs Monitor (Analytics) mode, Link Quality Monitoring (LQM) for VPN and private WAN path performance, bandwidth monitoring (PCM), BFD for VPN liveness and private-WAN underlay reachability, Classic / Core / Edge BGP peer types, LLDP, Virtual Interface.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Site definitions; branch vs DC roles; DC injects branch routes for symmetry | VERIFIED | DOC | SRC-000029 pp.12, 57 |
| Branch creation steps, defaults, SGI range, shells (max 2) | VERIFIED | DOC | SRC-000029 pp.58–59 |
| Branch gateway definition, platforms, 6.4.1 minimum, conversion prerequisites, reboot | VERIFIED | DOC | SRC-000029 pp.60–62 |
| Device defaults (L3 Direct Private WAN Forwarding, L3 LAN Forwarding, App Reachability Probe) | VERIFIED | DOC | SRC-000029 p.148 |
| Object scopes (tenant/site/element) and API families | UNVERIFIED (internal QA contract) → to be VERIFIED against SRC-000046 in B15 | DOC | SRC-000004 §0 |
| Branches auto-tunnel to all hubs; DC active/active termination | CORROBORATED (official p.59 says tunnels form automatically; internal deck gives detail) | DOC | SRC-000029 p.59; WS-033 slide 42 |
| LQM, PCM, BFD, peer-type terms | UNVERIFIED (internal glossary) | DOC | WS-033 slide 30 |

## Open questions

- KG-064: what "domain" exactly controls (which DCs a branch tunnels to) and defaults; read admin guide "Service and Data Center Groups" pp.470–476 and "Understand Service and Data Center Groups" p.674 in B5/B9.
