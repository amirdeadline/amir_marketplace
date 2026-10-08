# Applications: identification, custom applications, system application overrides

Domain: 3 | Applies to: Admin Guide May 2025; unified App-ID from 6.0.1 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Every policy decision in Prisma SD-WAN starts with "which application is this flow". The ION recognizes more than 4,000 **system applications** (Palo Alto Networks App-ID plus the legacy CloudGenix set, unified since 6.0.1) using prefixes, ports, signatures and SaaS knowledge, and keeps an application map cache so the first packet of a flow can usually be matched. You add **custom applications** for your own traffic, either by Layer 3/4 (port plus prefix) or Layer 7 (domain name from TLS Server Name Indication). You can also **override** attributes of system applications (category, transfer type, path affinity, idle timeout, ingress share, reachability detection).

## Documented facts (official pp. 463–469)

- Application types shown under `Manage > Resources > Applications`: System (PANW), System (CGX), System (PANW, CGX), Custom. Policy rule app pickers filter by site version (6.4.1+, 6.0.1–6.4.1, below 6.0.1, any).
- **L3/L4 custom app**: UDP rules (port mandatory; DSCP 0–63 optional; prefix filter optional), TCP rules (server port, DSCP, server prefix), IP rules (protocol such as GRE/ICMP, DSCP, up to eight destination and eight source prefix filters). Prefix filters with their ports are required; prefix filters can be reused but ports must be unique per custom app. DSCP decimal/hex table given (EF = 46, CS6 = 48, AF41 = 34 …).
- **L7 custom app**: up to 16 domain names, case-sensitive, must match the SNI; parent domain acts as wildcard for sub-domains; app category; **transfer type** Transactional / Bulk / Real-Time Audio / Real-Time Video (queue service order within a priority: real-time audio, real-time video, transactional, bulk); **ingress traffic percentage** (share of WAN-to-LAN bytes; weights bandwidth capacity and utilization in path selection, 50% = equal weight); **connection idle timeout**; **path affinity** Strict (subsequent sessions from the same client stay on the originally selected path) or None; **Use Unreachability Detection** (on by default for all TCP apps; LAN-initiated TCP only); **Network Scan App** flag (disabled by default; applies to new flows only; when enabled, deselect unreachability detection and set affinity None).
- Palo Alto Networks recommends defining port scanners as scanning applications: their sessions age out first near session capacity, and probe generation is suppressed.
- **System application overrides**: category, path affinity, transfer type, **Use Parent App Network Policy** (child apps inherit parent policy; Google apps only), ingress traffic capacity, connection idle timeout (new flows only), unreachability detection.
- Unreachability detection mechanism: the ION watches LAN-to-WAN TCP sessions; when a server stops responding on a path it probes the server on that path; an unreachable path is not used for that application; if all paths are unreachable one of the active paths from the policy is used.

## Internal guidance (WS-001 §Custom Applications)

Custom apps always win over system apps on conflict; custom definitions cost memory at policy compilation: avoid long /32 lists combined with wide port ranges (each /32 multiplies across zones and ranges; aggregate to subnets; avoid 1–65535), remove unused custom apps (or detach them from policy to keep visibility); define scanners (Nessus, Qualys) as Network Scan App with the two companion settings. Internal guide lists **three** affinity modes (None, Required with configurable timeout, Required Strict with 8-hour inactivity default) and says HTTP, SSL, IPsec and Ariba default to Required; the official guide exposes only Strict/None in these screens. **CONFLICTED/UNVERIFIED** until the affinity field options are confirmed on a current tenant or newer documentation (KG-084).

## Deck (internal)

Unified App-ID (slides 120–122) and application-defined fabric framing; App-ID services for both SD-WAN and PAN-OS applications from 6.0.1 (consistent with the official guide).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| 4,000+ system apps; identification techniques; unified App-ID from 6.0.1; app type labels | VERIFIED | DOC | SRC-000029 p.463 |
| L3/L4 and L7 custom app fields and limits (16 domains, 8+8 prefix filters, unique ports) | VERIFIED | DOC | SRC-000029 pp.464–467 |
| Transfer type queue order; ingress percentage semantics; idle timeout; affinity Strict/None; unreachability detection default on for TCP | VERIFIED | DOC | SRC-000029 pp.466–467 |
| Network Scan App recommendation and companion settings | VERIFIED | DOC | SRC-000029 pp.464, 467 |
| System app override fields; Google-only parent policy inheritance | VERIFIED | DOC | SRC-000029 p.468 |
| Custom beats system on conflict; memory hygiene guidance | UNVERIFIED (internal) | DOC | WS-001 §Custom Applications |
| Three affinity modes with Required / Required Strict and app defaults | CONFLICTED with official two-option screen | DOC | WS-001 §Application Probes; SRC-000029 p.467 |

## Open questions

- KG-084: current path-affinity options and defaults (Strict/None vs Required/Required Strict); check newer admin guide revision under D2 or the API schema `appdefs` in B15.
