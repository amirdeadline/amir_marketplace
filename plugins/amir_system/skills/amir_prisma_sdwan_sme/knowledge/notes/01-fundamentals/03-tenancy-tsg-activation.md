# Tenants, tenant service groups (TSG), activation and regions

Domain: 1 | Applies to: cloud-managed tenants on the Prisma SASE platform (Common Services), 2024–2025 documents | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

A **tenant** is your own isolated space in the Palo Alto Networks cloud: your users, devices, licenses and configuration. The platform calls the container that holds tenants a **tenant service group (TSG)**. The official Common Services guide says plainly that "mechanically, a tenant is just a TSG" and the two words are used interchangeably. Every tenant gets a numeric **TSG ID**, which you need for API service accounts and which also decides which tenant you land in when you log in. Managed service providers and large companies build a **hierarchy**: a root TSG with child tenants under it.

This closes the knowledge-base terminology question TERM-0001 / KG-040: the TSG is the tenancy identifier and container; the multitenant platform guide's "parent/child tenants" are TSGs in a tree.

## Activation paths (official, 2024–2025)

- **Magic link** (orders after March 2021): the order fulfillment email contains an activation link. Activate from the email: sign in, pick the Customer Support Portal (CSP) account, pick the recipient tenant, pick a region, accept terms, Activate. Without activating the Bandwidth or Data Center license only a base tenant is created without full functionality.
- **CSP activation** (no magic link, Superuser role, CSP access): `support.paloaltonetworks.com` > Activate Products > find the sales order > Activate.
- **Existing TSG-enabled customer adding devices**: use the magic link; choose the CSP account (use the same CSP ID for all SD-WAN assets in a hierarchy); choose the **TSG ID** to receive devices and subscriptions (recommended: the root tenant, then use the SD-WAN device manager to move devices to sub-tenants); region defaults to the tenant's existing region; devices appear under Unclaimed Devices after 15–60 minutes.
- **Legacy URL customers** (pre-TSG): open a support case to allocate devices or activate child tenants.
- **TSG migration**: when a legacy tenant is migrated to a TSG, users receive an activation email; set password and multi-factor authentication, then log in to Prisma SASE.
- Since December 2023 every stand-alone Prisma SD-WAN order sends an activation email, even for additions to an existing tenant.
- For MSSP/distributed enterprises: a license activated on a child tenant is also provisioned on the top-most root parent tenant (one-time, at activation); tenants created later between child and root are not auto-provisioned; allocate devices at the root so the parent can manage devices for children; after activation, activate the SD-WAN license on every child that should receive devices (`Subscriptions & Add-ons > Actions > Activate Cloud Tenant`).

## Regions

- Admin Guide (May 2025): United States, Canada, UK, Germany, Netherlands, Australia, Singapore, Japan, Israel, Switzerland, France, Saudi Arabia, Qatar, India.
- Activation and Onboarding 6.4 (April 2024): United States, Canada, UK, Germany, Netherlands, Australia, Singapore, Japan, India. (Older list; the 2025 list supersedes it.)
- A tenant previously activated in a region that does not support Prisma SD-WAN cannot activate SD-WAN in that tenant; open a support case for region allocation. There is no cross-region aggregation; keep all tenants of a hierarchy in one region for monitoring.

## Finding the TSG ID

Hub > `Common Services > Tenant Management` > select the tenant; the TSG ID is at the top right. If the application is not visible in "View by Support Account", the application is TSG-migrated.

## Hierarchy limits (Common Services, June 2024 edition)

| Limit | Value |
|---|---|
| Hierarchy depth | 10 (root is depth 1) |
| Child TSGs per TSG (immediate children) | 100 |
| Unused root TSGs | 10 |

## Roles at first login

- CSP Super User becomes Super Administrator in Prisma SD-WAN on first access through the hub; others get View-only until changed by a Super or IAM user. CSP roles and SD-WAN roles do not map to each other; deleting a user in SD-WAN does not delete the CSP user.

## MSP tenant model (official admin guide chapter "Device and Tenant Management" pp. 681–695; internal deck slides 481–491)

- Tenant types (deck): Support tenant (Palo Alto operations), MSP parent tenant (ESP), client child tenant. MSP operators cannot delete tenants; they assume a role inside the client tenant.
- MSP roles (deck): esp_root, esp_super, esp_iam_admin, esp_machine_admin, esp_user. Device lifecycle: allocate to child, return to MSP, re-allocate, return to MSP stock, revoke to Palo Alto Networks. The admin guide chapter covers the same lifecycle (Allocate, Return, Re-allocate, Revoke; pp. 693–695). To be read in detail in B3/B20.

## Verification

- After activation the tenant status shows **Up** in Tenant Management; devices appear in `Configuration > Prisma SD-WAN > ION Devices > Unclaimed Devices` (admin guide p. 24) or `Workflows > Prisma SD-WAN Setup > Devices > Unclaimed Devices` (p. 23). Both paths appear in the same guide; see KG-046 on navigation drift.

## Limitations and gotchas

- Region lists differ between documents by date. Always cite the document date.
- Two paths to the same screen are given in the admin guide (Workflows vs Configuration). The Sep 2026 Day-2 draft reports a navigation change in August 2025; treat menu paths as date-stamped.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| TSG = logical container of tenants and TSGs; a tenant is mechanically a TSG; each tenant gets a TSG ID used for service accounts and default login | VERIFIED | DOC | WS-046 p.107 (Common Services, rev 2024-12-10, section dated June 2024); SRC-000029 p.24 |
| Hierarchy limits 10 / 100 / 10 | VERIFIED | DOC | WS-046 p.119 |
| Activation categories and magic link vs CSP flow | VERIFIED | DOC | SRC-000029 pp.18–23; WS-040 pp.9–21 (rev 2024-04-12) |
| Region list (14 regions) | VERIFIED as of 2025-05-13 | DOC | SRC-000029 p.21 |
| Region list (9 regions) | OBSOLETE (superseded by the 2025 list) | DOC | WS-040 p.14 |
| Child-level activation auto-provisions root; intermediate tenants not auto-provisioned | VERIFIED | DOC | WS-040 p.19; WS-046 p.27 |
| Devices visible 15–60 minutes after activation | VERIFIED | DOC | SRC-000029 p.23 |
| No cross-region aggregation | VERIFIED | DOC | WS-040 p.20 |
| CSP Super User → SD-WAN Super Administrator; others View-only | VERIFIED | DOC | SRC-000029 p.21; WS-040 p.22 |
| MSP role names (esp_root …) and tenant types | UNVERIFIED (internal) until admin guide pp.681–695 are read | DOC | WS-033 slides 482, 490, 491; SRC-000029 TOC pp.681–695 |

## Open questions

- KG-040 can move to CLOSED (official definition found). Remaining nuance: whether the SCM API object `tenant_service_groups` maps one-to-one to a Common Services tenant (expected yes from the definition; INFERRED).
