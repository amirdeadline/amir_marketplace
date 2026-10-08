# Cloud deployments (AWS, Azure, GCP) and CloudBlades

Domain: 2 / 9 (batch B8) | Applies to: CloudBlade Integrations guide rev 2025-04-02; AWS solution guide Nov 2023; Azure solution guide Sep 2023; internal best practices May 2026 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

To bring the SD-WAN into a public cloud you deploy **virtual IONs** (vIONs) as a data center site inside the cloud and peer them with the cloud's router. **CloudBlades** are controller-side integrations that automate this: for AWS they build a Connect VPC with two ION 7108v and GRE/BGP to the Transit Gateway; for Azure they deploy a vION pair into a transit VNet attached to the Virtual WAN hub with BGP; for GCP they build VPCs, Cloud Routers and a Network Connectivity Center hub. Other CloudBlades integrate Zscaler, ServiceNow, Slack/Teams chat, Zoom QSS and LAN switching (Shasta). CloudBlades own what they create; you pause them to freeze changes and disable them to tear down.

## CloudBlade catalog (official guide rev 2025-04-02; internal list May 2026)

AWS Transit Gateway; Azure Virtual WAN with vION; Azure Virtual WAN (older, no vION deployment); Chatbot for Slack; Chatbot for MS Teams; GCP-NCC; ServiceNow; Shasta LAN; Zoom QSS; Zscaler Internet Access (ZEN). Internal list adds PagerDuty Notifier, LiveAction, and the Prisma Access CloudBlade (cloud-managed and Panorama-managed), with the note that **SASE Easy Onboarding replaces the Prisma Access CloudBlade for new deployments; do not run both on one tenant** (see note 04-security/… in B12). CloudBlades are configured at `Strata Cloud Manager > Manage > Prisma SD-WAN > CloudBlades` (May 2025 wording); missing tiles mean the CloudBlade is not entitled: contact support.

## Lifecycle rules (official pp. 175–176 for Zscaler; same model elsewhere)

- **Enabled**: runs every **60 seconds**, applies tags, reverts manual drift to the known-good state.
- **Paused**: stops future runs, keeps objects (does not stop removal of untagged objects).
- **Disabled**: removes everything the CloudBlade created (IPsec/IKE profiles, endpoints and service groups are not auto-deleted for Zscaler). Service impact if policy has no other path.
- **Uninstall**: removes the CloudBlade configuration only; to clean up completely, **disable for 2–3 run periods (about 180 s) before uninstalling**. Internal guide: AWS TGW needs 5–6 periods (about 30–36 minutes) or orphaned VPCs, EC2, EIPs and Connect attachments remain; Azure needs 2–3 periods and an empty Monitor tab or redeployment into the same region may fail.
- Internal guide: never edit CloudBlade-managed configuration; use Paused, not Disabled, to stop changes; every interface must be in a security zone when using the Prisma Access CloudBlade (unbound interfaces block traffic).

## AWS Transit Gateway CloudBlade (official pp. 5–22)

- Prerequisites: licenses for **2× ION 7108v per region**; AWS account with CloudFormation and VPC permissions (IAM policy JSON provided); access keys; marketplace subscription to the ION virtual appliance (new deployments from CloudBlade 2.1.0); **2 Elastic IPs per region**; existing TGW per region. The customer configures routing from application VPCs and their TGW attachments.
- Automates: Connect VPC per region; vION pair in separate availability zones; claim and assign to a DC site per region; TGW Connect attachment per vION; GRE tunnels and BGP on both sides; activates the DC site.
- Inputs: access key ID/secret; `Region:TGW-ID` (one region per TGW, comma-separated); **VPC CIDR** (RFC 1918, /16–/26; four subnets carved per vION; same CIDR reused across regions); **TGW GRE CIDR** (non-overlapping; /8, /16 or /24); **BGP peer CIDR** (one /29 in 169.254.x.x/29 as AWS requires; incremented per region); Install. Then path policy rules (p. 16) to steer traffic to the AWS DC.
- Solution guide (Nov 2023): AWS site is a DC site; DC IONs have no HA groups; resilience comes from pairs plus BGP; **each DC ION is independent, a branch builds secure fabric links to both and the active one is typically the first link established**; size each ION to carry all branches alone or run degraded; Internet port on the public subnet with DHCP, peering port on the private subnet as **BGP core peer** to the TGW (auto-generated route maps); TGW ASN is 64512 and the vIONs must use a different ASN (guide example 65412); TGW route-table design (spokes, security, prisma-access, sd-wan tables) forces inspection through VM-Series; **BGP prefix limit 100 per virtual gateway** (route table limit 10,000); Direct Connect/VPN alternatives.
- Internal guide: HA pair in different availability zones; marketplace "HA Greenfield" CloudFormation template when the CloudBlade does not fit (for example AWS Cloud WAN); Cloud WAN manual integration uses the **Tunnel-less Connect attachment** (no GRE standard VPN needed).

## Azure (official pp. 23–58; solution guide Sep 2023; internal)

- **Azure Virtual WAN with vION CloudBlade**: licenses for 2× 7108v per region; Azure account able to create resource groups, VNets, VMs (API list provided); programmatic access enabled; marketplace subscription; brownfield needs read access to VNets and read/write to vWAN/hub (explicit when resources sit in another subscription); **Azure must enable BGP peering with the vWAN hub on request (Resource ID)**; VM size **Standard D8s v3** in all regions. Automates: vION pair in a transit VNet across availability zones, attached as a spoke to the hub, claim/assign to a DC site per region, three subnets (private/LAN, public/Internet, controller), static route to the hub, BGP both sides, activate the DC site. App registration: client ID, tenant ID, client secret, subscription ID, **Contributor** at subscription scope.
- Internal guide: brownfield (existing vWAN/hub) is the common and recommended mode; greenfield only when no Virtual WAN exists; marketplace "Prisma SD-WAN vION HA" solution template when the CloudBlade does not fit.
- Solution guide (Sep 2023, SRC-000010; near-duplicate SRC-000011 undated): design using Azure Route Server and user-defined routes with vION DC sites (not read in detail; both copies to diff in B20 — KG-030).

## GCP Network Connectivity Center CloudBlade (official pp. 93–108)

Licenses for 2× 7108v per region; quota for three VPCs; service account with Deployment Manager, Compute Engine, Cloud Router and Network Connectivity APIs (JSON key); marketplace subscription; N1 machine type (from 1.0.0). Automates: NCC hub (global; all vIONs attach as spokes); Controller, Internet and Transit VPCs (controller/internet subnets 255.255.x.0/24 style, transit 10.255.x.0/24 greenfield); two 7K vIONs per region; Cloud Routers per region with BGP to the vIONs; VPC routing; DC site with both devices; port 1/2 interface configuration; **BGP core peers**.

## Cross-cloud rules (internal guide, May 2026)

- Set **DC site prefixes or static/BGP routes to Global** or branches cannot reach the cloud through the overlay; adding the DC to a Service and DC Group remains recommended.
- **BGP on the core/LAN side is required and the Multihop Limit must be 2** on every peer (the cloud router is never directly adjacent: GRE/Connect on AWS, spoke attachment on Azure, transit VPC on GCP); configure on each ION of the pair.
- DC-to-DC across clouds: fabric tunnels from 6.5.1 (note 06); NAT-to-NAT with Passive Mode and an initiator-only side (TAC) using an AWS NLB with UDP 500 and 4500→4501 target groups; 6.5.2+ (note 06, note 04).

## Zscaler Internet Access CloudBlade (official pp. 149–176)

Available from release 5.1.1 (devices 5.1.9+); IPsec and, from CloudBlade 2.0.0, GRE (up to 1 Gbps per GRE tunnel) to Zscaler Enforcement Nodes; tag-driven: site/circuit tags `AUTO-zscaler` (IPsec) and `AUTO-zscaler-GRE`; Zscaler side needs a partner administrator role (Locations, VPN credentials, and from 2.0.0 Static IP and GRE tunnels), a partner admin account, an SD-WAN partner key, activation; default Zscaler limit of 100 static IPs/GRE tunnels (raise via Zscaler support); GRE tunnels require a security zone and security policy stack bound to the site (the CloudBlade places the GRE service link into the zone; two GRE tunnels, primary and secondary DC); disable "IP session lock" on the configuring user; then edit application network policy rules to send traffic to Zscaler. Troubleshooting sections exist (pp. 171–174) for B18.

## Other CloudBlades (official TOC)

Chatbot for Slack (pp. 59–76) and MS Teams (pp. 77–92) with supported commands; ServiceNow incident integration (pp. 109–128; events overview, create/resolve incidents, monitor status); Shasta LAN (pp. 129–142; ZTP onboarding of switches and APs, branch microsegmentation, supported hardware); Zoom QSS (pp. 143–148; application experience data). Read on demand in B17/B20.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| CloudBlade list, lifecycle semantics, 60 s run, 2–3 periods before uninstall | VERIFIED | DOC | SRC-000030 pp.3–6, 175 (rev 2025-04-02) |
| AWS TGW prerequisites, inputs, CIDR rules, 2 EIPs, 7108v pair, /29 169.254 | VERIFIED | DOC | SRC-000030 pp.7–12 |
| AWS DC design: no HA groups, independent DC IONs, first-link active selection, BGP core peer, TGW ASN 64512, 100-prefix BGP limit | VERIFIED (solution guide, Nov 2023) | DOC | SRC-000009 pp.6–16 |
| Azure CloudBlade prerequisites, automation steps, D8s v3, Contributor, hub BGP enablement | VERIFIED | DOC | SRC-000030 pp.24–30 |
| GCP NCC automation steps and prerequisites | VERIFIED | DOC | SRC-000030 pp.93–96 |
| Zscaler CloudBlade mechanics (tags, GRE 1 Gbps, partner key, security zone requirement) | VERIFIED | DOC | SRC-000030 pp.149–158 |
| Global prefix scope requirement; multihop 2; AWS 5–6 periods; Azure brownfield preference; Cloud WAN tunnel-less | UNVERIFIED (internal, strong) | DOC | WS-001 §Public Cloud Deployment |
| SASE Easy Onboarding replaces the Prisma Access CloudBlade for new deployments | UNVERIFIED (internal) until SRC-000029 pp.663–680 are read in B12 | DOC | WS-001 §Integration and CloudBlades |

## Open questions

- KG-030 remains (Azure guide revisions). KG-083: official source for "multihop limit 2" and Global scope requirement in cloud DC sites (CloudBlade validation pages pp.13–16, 34–38, 103–108 to read).

## Addendum 2026-10-08 (B20: KG-030 CLOSED)

The two Azure solution-guide extracts (SRC-000010 "Sep23" and SRC-000011 undated) are **identical in content** (883 normalised lines each; only file name, path and SHA differ). SRC-000011 is a duplicate copy, not a later revision. Design content now summarised in note 10-design/01 (Azure variant): vION DC site in the Transit VNet, BGP **classic** peer to Azure Route Server (ASN 65515, eBGP), active-active VNGs required in the same VNet, UDRs towards an internal load balancer in front of VM-Series, no ECMP via UDRs, DC HA rules identical to on-premises (VERIFIED, SRC-000010 pp.7–14).
