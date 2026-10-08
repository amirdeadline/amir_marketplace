# Prisma Access integration: SASE Easy Onboarding, legacy FIC/PIC CloudBlades, hub association, API family

Domain: 4 / 2 | Applies to: Admin Guide May 2025 pp. 663–680; ION release notes 6.4 (6.4.2 enhancements) and 6.5 (Panorama-managed support); WS-001 §Integration and §SASE Easy Onboarding; TSE playbooks FIC 175768057, PIC 175768067, hub association 177111562; unified OpenAPI SRC-000046 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

A branch ION reaches Prisma Access over **standard IPsec tunnels** that terminate on Prisma Access **Remote Network** nodes. Today the tunnels, BGP and endpoints are created by **SASE Easy Onboarding** (native integration inside SCM). Before that, a **CloudBlade** did the same job: the Cloud Managed variant (internally "FIC", Fawkes Integration Container) or the Panorama Managed variant ("PIC", Panorama Integration Container), driven by site and interface **tags**. Once tunnels are up, traffic only uses them when path policy names the Prisma Access **service endpoints** through a **Service and DC Group** and a **Domain** bound to the site.

## Easy Onboarding (official pp. 663–680)

- Requirements: SCM; ION software **5.6.x or higher**; Prisma Access **Aggregate Bandwidth** licensing with bandwidth enabled per compute location; knowledge of the IPSec Termination Nodes; **Prisma Access and Prisma SD-WAN in the same TSG**. Panorama Managed: Cloud Services plugin **5.2.0-h24** minimum, a service account with superuser on All Apps and Services, and `request plugins cloud_services prisma-access store-client-details client-id … client-secret … tsg-id …` on Panorama.
- If a CloudBlade already connects the tenant, **deactivate it and contact Customer Support** before using Easy Onboarding (p.663; WS-001: never run both).
- **SASE Connectivity** (`Manage > Resources > SASE Connectivity`, one time per tenant): ION Peering Default Local AS (private 16-bit recommended; enables ECMP onboarding); **Deployment Mode** Private-App-Access (default; private apps and Internet), Internet-Only (BGP no-advertise inside Prisma Access), Internet-Only-With-Mobile-User-Access (BGP no-export out of Prisma Access); mode changes affect only new or modified tunnels; **Tunnel Inner IP Pool** (unique, not the Palo Alto service infrastructure subnet; **each tunnel consumes a /31**, so the pool bounds the tunnel count); optional Security Zone for the tunnels; optional Panorama sub-tenant; optional IPSec profile sync.
- Per site (`Workflows > Prisma SD-WAN Setup > Branch Sites > Connect to Prisma Access`): Prisma Access Location (closest recommended from site latitude/longitude), IPSec Termination Node (**one new node per 1 Gbps allocated to a region**), optional Secondary location and node; multi-site selection supported. **One tunnel per circuit, maximum 4 circuits per site.** Status in the SASE Connection column; peer details under Overlay Connections > Branch-Standard VPN. Disconnect removes tunnels but keeps SASE objects for reconnection.
- After onboarding: standard endpoints for all Prisma Access regions are auto-created with an **ICMP liveliness probe every 10 s, failed after 3 misses**, and the **Prisma Access check box** set (tells the UI these VPNs go to Prisma Access; set it manually on hand-made endpoints). The default group **"Prisma Access: All Regions"** is created; add the region endpoints to it per Domain, bind Domains to sites (one domain per site); endpoints in one group are equal in path selection; a rule uses one active and one backup group. Policy patterns: blanket suspect list, suspect list with safelist, Internet-only exceptions. CLI `dump service end points`.
- Release chronology: deck notes say Easy Onboarding arrived in **6.4.1** (SCM tenants only); 6.4.2 release notes list enhancements (site templates, automated BGP deployment modes, region redundancy, IPSec profile changes); **6.5 release notes add Panorama Managed Prisma Access**. Fixes: standard VPN path not listed after easy onboarding (6.3.1/6.1.7), ADEM not working after easy onboarding (6.3.1/6.4.1).

## WS-001 additions (internal, strong)

Same-TSG is a hard prerequisite; configure a secondary location; size the inner pool from total circuits; endpoints auto-created as **Prisma Access Remote Networks High Performance (RN-HP)**; enable the RN-HP **LQM liveliness probe** on the endpoint and **Use LQM for Non-Hub Paths** on the Internet circuit categories so performance policy can compare Prisma Access tunnels with other paths; Site-Based Licensing tiers 25 Mbps / 50 / 250 / 1 Gbps / 2.5 Gbps.

## Legacy CloudBlades (internal TSE playbooks; the integration guides 2.1.2/3.1.5 are not in the KB)

- Tag model: site extended tag `prisma_access` (ECMP region selection or Auto Detect), interface tag `prisma_region:<region>[:<spn>]` (SPN needed for Aggregate Bandwidth), `prisma_ecmp_exclude` on circuit labels, `prisma_ha_primary` for ECMP mirroring on HA sites (needs ECMP). Common mistakes: wrong secret on the tile, ECMP Auto Detect left on for Aggregate BW, SPN index beyond available SPNs, `pa_tenant_name` set on a single-tenant Panorama, SD-WAN Integration not enabled on Panorama.
- Mechanics: CloudBlade computes tunnels, creates service links on the controller via the northbound API, then provisions `AUTO_CGX_*` objects on Prisma Access (Fawkes) or Panorama (via the Cloud Services plugin, which polls every **5 min**); the peer IP arrives later and is attached to the service link. Never delete `AUTO_CGX` objects manually. Service links bound to a security zone block deletion (`INTERFACE_IS_USED_IN_SECURITY_ZONES`). Tunnel states: local auth failure (secret mismatch; CloudBlade auto-rekeys), `peer_address_unresolved`, `tunnel_bring_up` (device-side). Untag/retag rebuilds tunnels; remove the site tag rather than one interface tag. Execution types App_config, Timer, Resource Change.
- **Hub association**: the Prisma SD-WAN app can be associated with a Prisma Access tenant **only once** (by design); choosing an eval tenant or the wrong one requires a backend fix (DIT to Cortex Hub / App Portal); eval-to-prod conversion must follow the sales license-conversion process.
- WS-001: CloudBlade-managed config is authoritative; use **Paused** to stop changes, **Disabled** only to offboard (then Uninstall after convergence).

## DC-side interplay (deck slides 213–225, internal)

Asymmetry when a branch sends DC-bound traffic via Prisma Access (Remote Network → Service Connection → DC ION core peer) and the return takes the fabric VPN (CGSDW-14689); automated asymmetry correction is listed under 6.5.1 DC enhancements. **Core peer failover via host tracking (6.5.1)**: VPN stays Active while only a classic peer (for example the Prisma Access service connection peer) is up; host-tracking IPs per hub flip the VPN to standby (CGSDW-14688). DC prefix **Distribution to Fabric** (6.5.1) and DC summarization also listed. These are corroborated by the official routing chapter where read in B6 (host tracking, distribution to fabric).

## API family (SRC-000046, unified OpenAPI 6.6.2)

`/sdwan/v2.0/api/sites/{site_id}/prismasase_connections` (GET, POST) and `/{prismasase_connection_id}` (GET, PUT, DELETE) plus `/status`; v2.1 site-scoped GET/POST/PUT; tenant-wide `/sdwan/v2.0/api/prismasase_connections/query` and `/status/query` (POST); `/sdwan/v3.0/api/prismasase_connections/configs` and `/sdwan/v3.1/api/prismasase_connections/configs` (GET, POST, PUT, DELETE) for the tenant-level SASE Connectivity settings. Nine paths in total. Schema fields to be documented in B15.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Requirements (5.6.x, Aggregate BW, same TSG, Panorama plugin 5.2.0-h24 and CLI) | VERIFIED | DOC | SRC-000029 pp.663–665 |
| SASE Connectivity fields, deployment modes, /31 per tunnel, zone and sub-tenant options | VERIFIED | DOC | SRC-000029 pp.665–666 |
| Location recommendation, one termination node per 1 Gbps, 4 circuits per site, one tunnel per circuit | VERIFIED | DOC | SRC-000029 pp.669–670 |
| Auto-created endpoints with ICMP 10 s / 3 failures; "Prisma Access: All Regions" group; domain rules | VERIFIED | DOC | SRC-000029 pp.676–680 |
| CloudBlade must be deactivated and Support contacted before Easy Onboarding | VERIFIED | DOC | SRC-000029 p.663; RN 6.5 |
| Easy Onboarding introduced 6.4.1 | UNVERIFIED (deck notes); 6.4.2 enhancements and 6.5 Panorama support VERIFIED | DOC | WS-033 slide 149; RN 6.4 p.?; RN 6.5 |
| RN-HP endpoint type, LQM probe, site-based licence tiers | UNVERIFIED (internal, strong) | DOC | WS-001 §SASE Easy Onboarding |
| Tag model, AUTO_CGX objects, 5-minute Panorama poll, tunnel state meanings | UNVERIFIED (internal TSE, 2024) | DOC | Confluence 175768057 / 175768067 |
| One-time app-to-tenant association | UNVERIFIED (internal TSE, 2025) | DOC | Confluence 177111562 |
| prismasase_connections endpoint list | VERIFIED (rank 2 OpenAPI) | DOC | SRC-000046 |

## Open questions

- KG-098: the Prisma Access CloudBlade integration guides (Cloud Managed 2.1.2, Panorama Managed 3.1.5) are not in the KB; fetch under D2 if legacy CloudBlade support is in scope for the skill.
- KG-099: official release that introduced Easy Onboarding (deck says 6.4.1; 6.4 release notes only describe 6.4.2 enhancements); check public 6.4.1 notes under D2.
- KG-100: whether Easy Onboarding tunnels count against the standard VPN limits per platform and how bandwidth allocation per site interacts with Aggregate vs Site-Based licensing (official text).

## Addendum 2026-10-08 (public pages cached under D2; see 03_SOURCE_CATALOG.md §J)

- 6.4.2 release notes (PUB-011, VERIFIED) list "SASE Easy Onboarding Enhancements" (site templates, automated BGP deployment modes, region redundancy, IPsec profile changes); no ION release page names the original introduction (KG-099 PARTIAL). 6.6.1 "VRF Service Link Multiplexing" (PUB-010) routes custom-VRF internet traffic to Prisma Access over Global service links without manual leaks. 6.8.1 Coffeeshop policies (PUB-008) auto-steer Mobile User / Explicit Proxy gateway traffic direct at branches. Compatibility matrix (PUB-007): Easy Onboarding with Panorama-managed Prisma Access 10.2.4 needs plugin cloud_services-5.2.0-h24; Cloud Managed CloudBlade 3.1.6 needs Prisma Access 2.1.2+ with Aggregate Bandwidth.
