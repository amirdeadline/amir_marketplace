# MSP design: Strata Multitenant Cloud Manager, device and licence allocation, bulk configuration; On-Premises Controller option

Domain: 9 (design) / 1 | Applies to: SRC-000044 "Strata Multitenant Cloud Manager" Oct 2024, last revised 2025-01-30 (148 pp); WS-044 On-Premises Controller for Prisma SD-WAN Deployment Guide, last revised 2025-06-12 (48 pp) | Status: VERIFIED (official) | Last updated: 2026-10-08

## Explanation (plain words)

A managed service provider (MSP) or a large enterprise with separate business units runs **one parent tenant above a hierarchy of child tenants** in the Strata Multitenant Cloud Manager. The parent activates and shares licences, creates identities and roles, **allocates physical IONs and virtual-ION licences to child tenants**, watches all tenants' incidents and health, and (for Prisma Access only) pushes common security configuration snippets. Customers who cannot use a cloud controller for regulatory reasons can run the **On-Premises Controller**, a self-hosted controller with the same ION functions, sized by site count and optionally clustered in nine nodes.

## Multitenant platform (SRC-000044)

- Capabilities (p.7): Common Services (licence activation and subscription management; **tenant management** — hierarchy, share/allocate subscriptions; identity and access — roles for users and API access), aggregated monitoring across tenants, open APIs.
- Access (p.9): `stratacloudmanager.paloaltonetworks.com/msp/dashboard` or `sase.paloaltonetworks.com/msp/dashboard`; from the hub tenant view or from SCM `Tenants and Services > tenant > Available Apps`.
- Tenants (p.23): each tenant has a name and a business vertical; licences are assigned per tenant through Common Services Tenant Management; identities and service accounts through Identity & Access Management (p.25).
- Monitoring chapters (TOC pp.27–78): SASE summary, Prisma Access and **Prisma SD-WAN summary dashboards**, tenant threats, applications, service connectivity, service-provider backbones and IP pools, **tenant branches, devices, licences, upgrades**, incidents (Prisma Access and Prisma SD-WAN), ASC support view.
- **Manage > Services** (pp.80–81): per tenant: licence edition, vertical, setup journey/status, expiry, allocated licences (remote-network speed, service connections, mobile users, SLS space), **Support IDs: TSG ID, SLS ID, Cloud Management ID, Prisma Access ID**. Roles needed: Multitenant Superuser, Multitenant IAM Administrator, IAM Administrator or Auditor.
- **Manage > Devices** (pp.82–87): regions tabs; states; summary widgets (available for allocation, return requested, revoked, claimed, unclaimed). Lifecycle: **Allocate** (device appears Unclaimed in the child tenant; bulk allowed) → child claims in Prisma SD-WAN; **Return** (from state "Available for Client Allocation"; back to Palo Alto inventory for re-allocation or RMA); **Re-allocate** (child must first mark the device **To Return**); **Revoke** (non-renewing child keeps the device → Revoked state; child may mark Return or "Put device back in use").
- **Virtual ION licences** (pp.88–92): parent allocates a number of vION licences per model to a child (Total Counts / Allocated to Clients / Used by Tenant; "Allocated By" shows the allocating TSG ID); the child **instantiates** via `System > License Management > Manage Tokens > Generate Token`, deploys the VM with the token, then claims; the parent can **revoke** only licences not yet used to instantiate.
- **Bulk configuration** (pp.107–112): Prisma Access licence at the parent; snippets of global security policy assigned and pushed to selected child tenants; tenant config status (in sync / update available / unassigned / failed, with Push, Revert, Retry, Remove); **cloud-managed tenants only, not Panorama-managed**; roles Multitenant Superuser or Superuser. Not an SD-WAN configuration mechanism.
- Also: multitenant notification profiles (announcements/upgrades, incidents) and multitenant reports (pp.113–131).

Related: note 01-fundamentals/09 §MSP covers the Prisma SD-WAN admin guide view of the same model (esp_* roles, MSP dashboard thresholds, device lifecycle); note 06-api-automation/01 covers service accounts and TSG scopes.

## On-Premises Controller (WS-044, June 2025)

- Purpose (p.5): same functions as the cloud controller for customers with data-sovereignty or regulatory needs (government, finance); FIPS-CC mode from 6.5.1 is tied to it per internal guidance (note 01-fundamentals/01).
- Prerequisites (pp.6–7): qcow2 image (Ubuntu 20.04.5) on **KVM or ESXi**; one static management IP; password-less sudo Ubuntu user; NTP; DNS optional (private preferred); do not modify OS/packages; **fully air-gapped installation supported**; backups at `/mnt_ebs/backup_config`. Ports: admin → controller TCP 443/9443 and 22; **ION → controller TCP 443**. **API limit 20 concurrent calls**.
- Sizing (pp.8–10): 10 sites/20 devices: 8 cores, 64 GB, 500 GB SSD, 500 IOPS, 1 GE. 500 sites/1,000 devices: 64 cores, 256 GB, 4 TB SSD, 1,200 IOPS (assumption 65 flows/10 s per device). **9-node HA** (3 app nodes 32c/128 GB/400 GB, 3 stats nodes 24c/160 GB/3.6 TB, 3 ops nodes 8c/16 GB/300 GB) on at least 3 servers with a network load balancer (HAProxy chapter); 3-node non-HA (app 16c/64 GB, stats 6c/40 GB/800 GB, ops 4c/8 GB). **Single-node cannot be converted to HA**; reinstall.
- Licensing and image (p.11): no separate controller licence, but ION usage and support licences are required; image downloaded from the Customer Support Portal `Assets > IONs > Controller > Download` after a Common Services "magic link" activation that binds the CSP account holding the ION serial numbers.
- Other chapters (TOC): ZTP service to connect IONs, allocate devices to the controller, SAML authentication, VFF licence management, SCEP, controller upgrade, device software upgrade via Operator/Administrator consoles, appdef download, pre-owned device upgrade, tech-support dump, error scenarios.

## Design implications

- MSP hierarchies: plan tenant naming/verticals, which roles the MSP holds inside each child, and whether ION hardware is MSP-owned (allocate/revoke lifecycle) or customer-owned; vION licences are allocated as counts per model.
- Prisma Access bulk snippets do not reach Prisma SD-WAN policy; SD-WAN standardisation across tenants relies on site templates (note 01-fundamentals/09) and API tooling (note 06-api-automation/03).
- On-premises controller changes the operating model: customer-run upgrades, API rate limit of 20 concurrent calls, LAN-reachable controller for ZTP, and sizing by sites/devices; SCM-only features (Nav 3.0 Insights, Prisma Access integration workflows) are not documented for it in this guide (KG-131).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Multitenant capabilities, device/vION lifecycle, bulk configuration scope | VERIFIED (official Oct 2024, rev Jan 2025) | DOC | SRC-000044 pp.7–9, 23–26, 79–92, 107–109 |
| On-premises controller prerequisites, ports, sizing, HA, licensing | VERIFIED (official June 2025) | DOC | WS-044 pp.5–11 |
| FIPS-CC requires the on-premises controller | UNVERIFIED (internal WS-001) | DOC | note 01-fundamentals/01 |

## Open questions

- KG-131: feature parity of the On-Premises Controller with SCM (which SCM/Insights features, Prisma Access onboarding, CloudBlades are available); not covered in WS-044 pp.5–11.
