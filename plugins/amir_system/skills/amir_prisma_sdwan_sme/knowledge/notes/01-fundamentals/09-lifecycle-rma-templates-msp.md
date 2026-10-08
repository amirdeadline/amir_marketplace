# Device lifecycle (unassign, return, RMA), site templates, and MSP device management

Domain: 1 / 7 (completes batch B3) | Applies to: Admin Guide May 2025; Unified API 6.6.2 for state names | Status: EVIDENCE REVIEWED (official procedures plus API-derived state machine) | Last updated: 2026-10-08

## Explanation (plain words)

An ION moves through a fixed set of states: in the tenant's inventory but unclaimed; claimed; assigned to a site; unassigned again; put back in inventory ("declaimed"); and finally returned to Palo Alto Networks or re-allocated by a service provider. Replacing a broken device uses the **RMA wizard**, which copies the old device's configuration to a new one. To build many sites quickly you use **site templates**: a Jinja text template plus a CSV with per-site values, and the controller deploys each site as a background job, creating device shells when the hardware is not there yet.

## Lifecycle states (official UI names; API enum names from the KB research package WS-020, derived from the OpenAPI 6.6.2 bundle)

| UI state | API (machine / element) | Allowed next step |
|---|---|---|
| Unclaimed (Offline / Online / Online-Restricted) | machine `MACHINE_ALLOCATED`; no element | Claim (needs connected device); allocate to shell; MSP return/revoke |
| Claiming | `MACHINE_CLAIM_PENDING` → CIC issue states → `MACHINE_CLAIMED`; failure `MACHINE_CLAIM_FAILED` | wait; "Recover the device" for stuck claiming/claim_failed (official p. 324) |
| Claimed, not assigned | element exists with `site_id = "1"`, state `ACTIVE_READY` | Assign (PUT `site_id`); change device mode; software upgrade; Put back in inventory (declaim); assign to shell |
| Assigning | `ACTIVE_BOUND_IN_PROGRESS`; failure `ACTIVE_BOUND_TO_SITE_FAILED` | wait |
| Assigned | `ACTIVE_BOUND_TO_SITE` | all element configuration |
| Unassigning | `ACTIVE_UNBOUND_IN_PROGRESS` (UI "Unassigning", official p. 324) | wait; site delete fails until done |
| Put back in inventory (declaim) | `ACTIVE_DECLAIM_IN_PROGRESS` → element removed; device reboots (official p. 324) | Return to Prisma SD-WAN |
| To Return / Returned | machine `MACHINE_TO_BE_RETURNED` → `MACHINE_RETURNED` (UI "To Return", official p. 325) | leaves the tenant |

Official rule before unassigning: remove configuration from the device first, in particular circuit labels attached to WAN interfaces; the message "Site WAN interface id exists in this element" means circuits are still attached (p. 324–325). The API research adds further blockers (spoke HA membership, hub cluster membership, stale `_etag`) and the fact that the unassign PUT returns success immediately while the device is still unbinding; these are API-derived and labelled accordingly.

Return procedure (official pp. 324–325): confirm replacement online and RMA device offline → Unassign device from site → (remove circuits if prompted) → Put back in inventory (unclaim) → Unclaimed tab shows "To return" → Return to Prisma SD-WAN → device removed from inventory.

## RMA (official pp. 314–325)

Before you start: the replacement must reach the controller (DHCP on Internet/used-for-public or controller port works automatically; static IP needs console); it must be claimed and online (older wizard) or unclaimed and online (SCM flow, p. 317); same model with matching bypass pairs and the same software version (older wizard), or a different model with support involvement (SCM flow).

Configuration items the wizard does **not** transfer (p. 314–315): a replacement's pre-configured static Internet/used-for-public interface (and any bypass pair or virtual interface it would belong to); pre-configured PPPoE interfaces; decoupled bypass pairs whose WAN port and controller port were DHCP on the failed device; IPv6 interface addresses (admin down/up the interface; alarm `DEVICEIF_IPV6_ADDRESS_DUPLICATE` appears as a reminder); Advanced UI (Extension API) settings that reference a VPN ID: BFD, LQM media thresholds (`thresholds/lqm/media`), application performance thresholds with a VPN path ID — contact support for these.

Wizard behavior: snapshot of the old device → unassign old → add new to the site → copy configuration → list of items needing manual work; download the snapshot and any warnings before exiting. Service may be affected temporarily during the swap. With a different build the replacement takes 10–15 minutes and reboots.

Cross-model replacement table (p. 317–318; official): 1000 → 1000, 1200; 1200 → 1200; 1200-S → 1200-S; 2000 → 2000, 1200, 1200-S, 3200 L2, 3200 L3, 7000, 9000 (list as printed; the flattened table is ambiguous for the 3000/7000/9000 rows, so verify the PDF page before citing a specific pair); FIPS mode not supported by the RMA flow. ION 2000 → 1200-S specifics: VLAN IDs above 4000 must be changed first; sub-interfaces beyond available ports map to SVIs; all SVIs/VLANs attach to all switch ports as trunk; loopbacks are not transferred (1200-S has no loopback support).

Device claiming issues (p. 324): if stuck in a non-assigned state, Put back in Inventory (device reboots); a SHELL holding the saved configuration appears under Claimed Devices; assign the new unclaimed device to the shell (10–15 minutes).

## Site templates (official pp. 75–84)

- A template is a Jinja blueprint with variables; Site Variables CSV (variables and original values) and Site Data CSV (per-site values). Compatible with ION 5.6.x and later; day-one deployments only; FIPS mode and CloudBlades not covered (planned).
- Create at `Manage > Resources > Site Templates > Add Site template` from an existing site (recommended) or import Jinja + CSV (at least one data row; after import the template cannot be edited, download/edit/re-import instead). Jinja conditionals (if, comparisons, replacements) are supported; the CSV is validated against the generated YAML.
- Mandatory variables: `site_name`, `ion_sw_version`, `ion_serial_number_1` (`ion_serial_number_2` for HA). Policy abstraction (path, QoS, NAT, security) keeps the variable count small.
- Deploy: select template → Deploy Site with Template → upload CSV or enter manually → review rows (alert, existing, new, duplicate markers) → Deploy Sites; one job per site in Job History. Serial numbers are optional; missing serials create device shells. After deployment the template is frozen; download the site configuration YAML for backups.
- Day-2 updates through templates: existing site/device resources are updated, unmatched ones created; software version and serial are not updated; device name cannot change after deployment; L2↔L3 device mode change requires unassigning first.
- Internal deck (slides 318–336) covers the same flow with a "Site Data Source" validation step and a "Device Requirements and Pre-provisioning" slide (not read in detail).

## MSP device management and multi-tenancy (official pp. 681–696)

- Multi-tenancy serves MSPs and enterprises with independent lines of business. The MSP tenant is a super-tenant over its client tenants but cannot delete tenants; it assumes a role inside a client tenant. Client authorization for MSP management goes through Palo Alto Networks support.
- MSP roles: esp_root (fail-safe root), esp_super, esp_iam_admin, esp_machine_admin (device allocation/deallocation), esp_user. SSO through an IdP; IdP group names can map to custom roles.
- MSP dashboard (`Summary > Prisma SD-WAN`, refreshed every 5 minutes): tenants by open incidents, top tenants with open incidents, open incidents by code, branch health (poor below 60; branch score = best link score), branch link health (Good >80, Fair 60–80, Poor <60), top tenants with poor links, devices to controller connectivity. Health widgets need the tenant on the new data-lake infrastructure.
- Device lifecycle (physical devices only, not virtual): allocate to client (device appears Unclaimed in the client tenant), return to Palo Alto (from "Available for Client Allocation"), re-allocate (client must first mark the device "To Return"), revoke (device moves to Revoked; client can mark Return or Put device back in use). Path: `Manage > Devices > ION Devices`, per region; bulk actions available; sales order number groups devices.
- Add a user or service account into a child tenant: `System Settings > Identity & Access Management > Add Identity`; roles offered are those configured in the child tenant.

## Related material

- Common Services "Device Associations" (WS-048, Mar 2024) applies to firewalls and Panorama appliances associated with a TSG for SCM, AIOps, IoT Security, CASB-X, SaaS Security Inline, Strata Logging Service. It does not cover ION devices; keep it out of SD-WAN answers except as context for mixed TSGs.
- Confluence "ZTP Onboarding Rules" (788071694, draft PRD, updated 2026-03-31, target release November 2026 "Ceres MR1"): a **planned** converged SD-WAN/SCM onboarding workflow (site-based onboarding rules with SD-WAN fabric toggle, fabric domain, circuit-to-interface binding, Prisma Access onboarding, HA pairing, site address mandatory, parallel provisioning of 5 sites/10 devices). Roadmap only: UNVERIFIED, never present as shipped.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Return flow: unassign → remove circuits → put back in inventory → To return → Return to Prisma SD-WAN | VERIFIED | DOC | SRC-000029 pp.324–325 |
| "Site WAN interface id exists" means circuits still attached | VERIFIED | DOC | SRC-000029 p.324 |
| Recover the device for claiming/claim_failed; Put back in Inventory reboots the device | VERIFIED | DOC | SRC-000029 p.324 |
| API state names and transitions; unassign PUT returns before unbind completes; additional blockers | UNVERIFIED (derived from OpenAPI enums and vendor tool; not lab-observed) | DOC | WS-020 `09_ION_LIFECYCLE.md` (2026-09-14) built on SRC-000046/058 |
| RMA prerequisites and non-transferred items | VERIFIED | DOC | SRC-000029 pp.314–315 |
| RMA wizard steps (snapshot, swap, warnings) | VERIFIED | DOC | SRC-000029 p.316, 319–320 |
| Cross-model replacement allowed and FIPS not supported in RMA | VERIFIED (table pairs need PDF-page check) | DOC | SRC-000029 pp.317–318 |
| 2000 → 1200-S caveats (VLAN >4000, SVI mapping, no loopback) | VERIFIED | DOC | SRC-000029 pp.322–323 |
| Site template concepts, mandatory variables, 5.6.x+, FIPS/CloudBlades excluded, Jinja conditionals | VERIFIED | DOC | SRC-000029 pp.75–79 |
| Deploy flow, job per site, shells for missing serials, frozen template, day-2 update rules | VERIFIED | DOC | SRC-000029 pp.80–83 |
| MSP roles, tenant types, lifecycle actions, physical-only | VERIFIED | DOC | SRC-000029 pp.683, 689, 693–696 |
| MSP dashboard health thresholds (60/80) | VERIFIED | DOC | SRC-000029 pp.685–688 |
| ZTP Onboarding Rules capabilities | UNVERIFIED (roadmap PRD, Nov 2026 target) | DOC | SRC-000091 pageId 788071694 |
| Device Associations is firewall/Panorama only | VERIFIED | DOC | WS-048 pp.5–9 |

## Open questions

- KG-067: verify the RMA cross-model table pairs from the rendered PDF page (SRC-000029 pp.317–318) before the skill cites any specific pair.
- KG-068: official confirmation that unassign is asynchronous and of the blockers beyond circuit labels (hub cluster, spoke HA); lab validation needed (D4).
