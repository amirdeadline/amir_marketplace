# S13 — MSP allocates devices and virtual-ION licences to a child tenant

Domains: 1, 9 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

An MSP runs a parent tenant with 14 child tenants in the Strata Multitenant Cloud Manager. A new customer needs 6 × ION 1200-S (MSP-owned stock) and 2 × ION 3108v in Azure. A departing customer has 4 devices it will not return.

## 2. Question

Walk the allocation, instantiation and revocation flows and the roles involved; name what the child tenant does itself.

## 3. Reasoning chain

1. **Hierarchy and licences.** Parent creates child tenants (name, vertical) and allocates licences through Common Services Tenant Management; identities/service accounts through Identity & Access Management; roles for Manage pages: Multitenant Superuser / Multitenant IAM Administrator / IAM Administrator / Auditor. [VERIFIED — 10-design/04 (SRC-000044 pp.7, 23–26, 80)]
2. **Hardware allocation.** `Manage > Devices`, choose the region tab, select devices, **Allocate** to the child tenant (bulk allowed) → devices appear **Unclaimed** in the child; the child's Prisma SD-WAN admin claims and assigns them (claim installs tenant certificates; device briefly offline). [VERIFIED — SRC-000044 pp.82–84; 01-fundamentals/08 (SRC-000029 pp.140–143)]
3. **vION licences.** Parent `Manage > Devices > Virtual ION Devices` → per model Allocate N licences to the child; the child instantiates with a token (`System > License Management > Manage Tokens > Generate Token`), deploys the VM in Azure (vION DC site: internet port on the public subnet, peering port to the SD-WAN private subnet, classic BGP peer to Azure Route Server), then claims; the parent can revoke only licences not yet used. [VERIFIED — SRC-000044 pp.88–92; 10-design/01 Azure variant (SRC-000010 pp.7–14)]
4. **Departing customer.** Devices not returned: parent **Revokes** them → Revoked state (child may mark "Return the device" or "Put device back in use"). Returned devices: child marks **To Return**, parent **Re-allocates** or **Returns** them to Palo Alto inventory (RMA path). [VERIFIED — SRC-000044 pp.85–87; 01-fundamentals/09 §MSP (SRC-000029 pp.681–696)]
5. **Monitoring across tenants.** MSP dashboard (`Summary > Prisma SD-WAN`, 5-minute refresh): tenants by open incidents, branch/link health thresholds (Good > 80, Fair 60–80, Poor < 60), devices-to-controller connectivity; incidents per tenant; licences and upgrades per tenant. [VERIFIED — 01-fundamentals/09; SRC-000044 TOC pp.27–78]
6. **What bulk configuration cannot do.** Bulk configuration snippets are Prisma Access security policy for cloud-managed child tenants only; SD-WAN standardisation uses site templates and the API per child tenant (service account per TSG). [VERIFIED — SRC-000044 pp.107–109; 06-api-automation/01]
7. **Roles inside the child.** MSP identities are added into the child tenant (`System Settings > Identity & Access Management > Add Identity`) with roles defined there; MSP roles esp_root/esp_super/esp_iam_admin/esp_machine_admin/esp_user; an MSP cannot delete tenants. [VERIFIED — 01-fundamentals/09 (SRC-000029 pp.681–696)]

## 4. Answer

Parent: allocate the six 1200-S from regional stock to the child (bulk), allocate two 3108v licences, and revoke the four unreturned devices of the departing customer (or return them once the customer marks To Return). Child: claim and assign the hardware, generate vION tokens, deploy the Azure vIONs as a DC site with a classic peer to Azure Route Server, claim them. The MSP watches all tenants from the multitenant dashboards; SD-WAN configuration standardisation is per tenant via templates/API, not via bulk snippets.

## 5. What to check / collect next

Device states in `Manage > Devices` (Available for allocation, To Return, Revoked), vION licence counts (Total/Allocated/Used), child claim status, TSG IDs for support cases. [VERIFIED — SRC-000044 pp.80–92]

## 6. Gaps exposed

None new; KG-046/KG-103 (navigation generations) apply to the child-tenant paths quoted from the admin guide.

## 7. Validation status

**SCENARIO VALIDATED** — every step is VERIFIED from the official multitenant guide and admin guide.
