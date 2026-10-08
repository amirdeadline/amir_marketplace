# API object model: scopes, resource families and versions, asynchronous operations, dependency errors

Domain: 6 | Applies to: unified OpenAPI SRC-000046 (6.6.2); WS-020 `02_API_INVENTORY`, `17_DEPENDENCY_ERRORS`, `18_ASYNC_OPERATIONS` (authored 2026-09 from the bundle plus live observation); SRC-000004 QA export contract (2026-07, live tenant1) | Status: DOCUMENTED (bundle) + CORROBORATED (authored analyses) | Last updated: 2026-10-08

## Explanation (plain words)

Objects live at three **scopes**: tenant (`/api/<obj>`: WAN networks, policies, zones, profiles, app definitions, resources, system administration), site (`/api/sites/{site_id}/<obj>`: circuits, LAN networks, DHCP servers, spoke and hub clusters, Prisma Access connections) and element (`…/elements/{element_id}/<obj>`: interfaces, routing, SNMP, NTP, IPFIX, DNS, switch). Every mutation is persisted synchronously in the controller and answered with the new `_etag`, but **device programming and inventory state machines run asynchronously**, so a 200 does not mean the device has converged; the caller polls the authoritative GET. Deletes are refused with named dependency codes until referrers are removed.

## Resource families and preferred versions (WS-020 §02, from the bundle)

sites v4.12/v4.13 (admin_state PUT at v3.0); elements v3.1/v3.2 (PUT = assign/unassign; operations v2.0; status v2.6); machines v2.3/v2.5; elementshells v2.0/v2.1; waninterfaces v2.9/v2.10; wannetworks v2.0/v2.1; waninterfacelabels v2.5/v2.6 (GET/PUT only); interfaces v4.20/v4.21; lannetworks v3.2/v3.3; dhcpservers v2.2/v2.3; staticroutes v2.2/v2.3; bgpconfigs v2.4/v2.5; bgppeers v2.6 (PATCH)/v3.0; ospfconfigs v2.0; routing prefix lists / route maps / AS-path lists / community lists v2.0–v2.3; snmpagents v2.0/v2.1; syslogservers v2.2/v2.3; ntp v2.0/v2.1 (no DELETE); radii, tacacs_plus_* v2.0; dnsservices v2.0; securityzones v2.0/v2.1; networkcontexts, vrfcontexts, vrfcontextprofiles v2.0; probeconfigs/probeprofiles v2.0; perfmgmt threshold profiles v2.0/v2.1, sets v2.0, rules v2.1/v2.2, stacks v2.0; networkpolicy sets v2.0 / rules v2.3–v2.4 / stacks v2.0 / prefixes v2.0–v2.1; prioritypolicy (QoS) sets v2.0 / rules v2.1–v2.2; natpolicy family v2.0; ngfwsecuritypolicy sets v2.0 / rules v2.2–v2.3 / securityprofilegroups v2.0; original securitypolicysets v2.0 and policysets v3.0 (rules v3.1) still exposed; servicelabels v2.0/v2.1, serviceendpoints v3.0/v3.1, servicebindingmaps v2.0/v2.1; hubclusters v3.0/v4.0 (v4 embeds `elements[]` and `peer_sites[]`), spokeclusters v2.0; ipfix family v2.0; appdefs v2.5/v2.6, overrides v2.2/v2.3; pathgroups v2.1, wanoverlays v2.0, anynetlinks v3.4/v4.0; prismasase_connections v2.0 (DELETE only here)/v2.1 site-scoped, configs v3.0/v3.1; bulkconfigurations/sitetemplates v2.0; deviceidprofiles v2.0; multicast v2.0/v2.1; eventcorrelationpolicysets v2.0, rules v2.0/v2.1. Version-dependent differences: hub cluster v3 child `hubclustermembers` vs v4 embedded elements; element v3.2 adds intra-cluster-tunnel interface validations; interfaces v4.21 adds loopback `binding_interface_id` validations.

## Operations endpoints (13) and asynchronous behaviour (WS-020 §18; enums from the bundle)

`elements/{id}/operations` (`{action, parameters[]}`: declaim, change_device_mode …), `machines/{id}/operations` (`inventory_op`: CLAIM, RETURN, REVOKE, REUSE, RETIRE, RECOVER, REMANUFACTURE, ALLOCATE, RECEIVED_STOCK, ESP_*), `sites/{id}/operations`, `spokeclusters/{id}/operations`, `hubclusters/{id}/operations` (v4.0), `bgppeers/{id}/operations`, `interfaces/{id}/operations`, `vpnlinks/{id}/operations`, `events/operations`, `deviceidprofiles/{id}/operations`, `ntp/templates/{id}/operations`, `vfflicenses/{id}/operations`.

| Mutation | What to poll | Pending → done |
|---|---|---|
| Assign element (PUT element with site_id) | GET element `state` | ACTIVE_BOUND_IN_PROGRESS → ACTIVE_BOUND_TO_SITE |
| Unassign (PUT element site_id='1') | GET element `state`, `site_id` | ACTIVE_UNBOUND_IN_PROGRESS → ACTIVE_READY |
| Declaim (POST operations action declaim) | GET element (404 when done) / machine `machine_state` | ACTIVE_DECLAIM_IN_PROGRESS → gone |
| Claim machine | GET machine `machine_state`, `connected` | MACHINE_CLAIM_PENDING, MANUFACTURED_CIC_ISSUE_PENDING/ISSUED/OPERATIONAL → MACHINE_CLAIMED |
| Device mode change | GET element `device_change_mode_state` | ELEMENT_CHANGE_MODE_INIT/IN_PROGRESS → ELEMENT_CHANGE_MODE (failure states exist) |
| Software upgrade | GET elements/{id}/software/status | until `software_version` == target; config changes may be rejected meanwhile |
| Hub cluster changes | GET hubclusters/{id}/status `cluster_state` | cluster_update_in_progress, vpn_update_in_progress, vpn_update_ack_pending → cluster_update_completed |
| Policy set clone | GET set status; rule ops | POLICY_SET_CLONE_IN_PROGRESS → rule ops succeed |
| Topology changes (circuits, anynetlinks) | retry | TOPOLOGY_REBUILD_IN_PROGRESS → accepted |
| Element shell copy config | GET copy_element_configurations/status | INIT … IN_PROGRESS → COMPLETED / ERROR |
| Site template deployment | GET deployments/{id}/status | free-text in progress → success / failed |
| Site snapshot export | GET snapshots/{id}/status | in progress → completed (yaml) / failed; EXPORT_ALREADY_IN_PROGRESS |
| Any PUT | re-GET `_etag` | INVALID_JSON_COMMON_ATTR_MISMATCH on stale etag |
| Config push after child mutation | GET elements/{id}/status (`config_and_events_connected`), POST elements/bulk_config_state/query | eventual |

Element `state` enum (v3.2) includes ACTIVE_INIT, ACTIVE_INVENTORY_*, ACTIVE_READY, ACTIVE_BOUND_IN_PROGRESS, ACTIVE_BOUND_TO_SITE, ACTIVE_UNBOUND_IN_PROGRESS, ACTIVE_DECLAIM_IN_PROGRESS …; `admin_action` ALLOCATE, CLAIM, BOUND, UNBOUND, DECLAIM, RETURN, REVOKE, RETIRE, STOCK, UPGRADE, REMANUFACTURE; `deployment_op` includes RENEW_CIC, FIPS_AUTO/MANUAL, GET_MAC_ADDRESS_TABLE. **Casing conflict** (KG-044): the legacy `cloudgenix_config` tool compares lowercase short states (`ready`, `bound`); compare case-insensitively.

## Dependency error catalog (WS-020 §17; 1,774 distinct codes in 400 examples; examples are not exhaustive)

Categories: DEPENDENCY_BLOCKED (48 codes: resolve referrer, retry), INVALID_STATE (10), NOT_FOUND (2: DELETE idempotent), TRANSIENT (2), ASYNC_PENDING (5), IMMUTABLE (13: system objects, restore instead of delete), OBJECT_IN_USE (1), OTHER (6). Representative codes and what they mean:
- Site delete: `DELETE_FORBIDDEN_ELEMENT_OR_ELEMENT_SHELL_EXISTS`, `DELETE_FORBIDDEN_SITE_WAN_EXISTS`, `DELETE_FORBIDDEN_SITE_WAN_LQM_CONFIG_EXISTS` (another site's circuit lists this site in `lqm_config.hub_site_ids`), `SITE_CONFIG_DELETE_NOTALLOWED_SERVICEENDPOINT_EXISTS`, `DELETE_FORBIDDEN_INVALID_STATE` (disable site first).
- Element: `SITE_WAN_INTERFACE_ID_EXISTS` (interface still carries a circuit label at unassign), `ELEMENT_SPOKE_CLUSTER_MEMBER`, `ELEMENT_BOUND_ERROR`, `ELEMENT_NOT_ASSIGNED_TO_SITE`, `CANNOT_DELETE_INTERFACE_USED_IN_INTRA_CLUSTER_TUNNEL`, `FIPS_MODE_PLEASE_RETRY_LATER`.
- Circuits/networks: `WAN_INTERFACE_CONFIGURED`, `WAN_INTERFACE_CONFIG_IN_ZONE`, `SITE_WAN_NETWORK_EXISTS`, `WANOVERLAY_IN_USE`, `LAN_NETWORK_IN_USE`, `LANNETWORK_IS_USED_IN_SECURITY_ZONES`, `ENABLED_CIRCUITS_NOT_REMOVED` (SASE connection).
- Interfaces: `INTERFACE_REFERRED_IN_SNMP_TRAP_CONFIG` (observed live, absent from the bundle), switch-port / cellular / default-VLAN deletes unsupported (IMMUTABLE), VLAN in use by switch ports, loopback binding constraints; SNMP trap, syslog and TACACS+ servers **require a source interface**.
- Routing: `ROUTE_MAP_IN_USE`, `PREFIX_LIST_IN_USE`, `ACCESS_LIST_IN_USE`, `COMMUNITY_LIST_IN_USE`, `CANNOT_DELETE_AUTOGENERATED_*`, `CANNOT_UPDATE_AUTOGENERATED_BGP_PEER`, `OSPF_CONFIG_NO_INTERFACE_ASSIGNED_TO_VRF`.
- Policies and profiles: `POLICYSET_IS_IN_USE`, `POLICYSETSTACK_IN_USE`, `POLICY_SET_CLONE_IN_PROGRESS`, `DEFAULT_*_CANNOT_BE_DELETED`, `PREFIX_IS_USED_IN_POLICY`, `PREFIX_IS_ASSOCIATED_WITH_SITE`, `NAT_POOL_USED_IN_POLICY_RULE`, `APPDEF_CONFIG_APP_IN_USE`, `PROBE_CONFIG_IN_USE_BY_*` (profile, label, circuit, threshold profile, network policy rule), `PERFMGMT_*_IN_USE`, `SERVICELABEL_DELETE_NOTALLOWED_*`, `SERVICELABEL/SERVICEENDPOINT_DELETE_NOTALLOWED_SASE` (auto-created SASE objects are immutable), `SERVICEBINDINGMAP_DELETE_NOTALLOWED_SITE_EXISTS`, `MULTICAST_PEER_GROUP_IN_USE`, `APN_PROFILE_IN_USE`, `SYSLOGSERVER_PROFILE_DELETE_IN_USE`, `TACACS_PLUS_PROFILE_DELETE_IN_USE`, `IPSECCONFIG_AUTO_CREATED`, `HUB_CLUSTER_HAS_ELEMENTS`, `SDWAN_APP_INVALID_APP_CONFIG_STATE` (CloudBlade), `EXPORT_ALREADY_IN_PROGRESS`.

## Logical export model (SRC-000004, live tenant1 2026-07)

A tenant snapshot has sections `resources`, `policies` (path, qos, nat, ngfwsecurity, performance), `profiles` (ipsec, apn, ipfix, dns, syslog, ntp, vrf, multicast, iot_discovery, site_templates, aaa), `system_administration`, `user_groups`, `secure_fabric` (anynetlinks, vpnlinks), `software_management`, `event_policies`, `cloud_blades`, `ions`, `sites` (with `waninterfaces`, `lan_networks`, `dhcpservers`, `spokeclusters`, `hub_clusters`, `prismaaccess_configs`, `deviceidconfigs`, `elements{routing, interfaces, ntp, snmp, ipfix, dns, multicast}`); 114 object types; `*_id` references resolve to names; volatile fields (`id`, `_etag`, `_schema`, timestamps) are ignored in comparisons. Useful as a checklist of what "complete configuration" means.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Scopes, resource families, version pairs, operations endpoints, enums | VERIFIED (bundle inspection, rank 2) | DOC | SRC-000046; WS-020 §02 |
| Asynchronous semantics and polling targets | CORROBORATED (bundle enums + `cloudgenix_config` retry logic; some rows CODE_INFERRED) | DOC | WS-020 §18; SRC-000058 |
| Dependency error meanings and recovery | CORROBORATED (bundle 400 examples; recovery steps authored) | DOC | WS-020 §17 |
| `INTERFACE_REFERRED_IN_SNMP_TRAP_CONFIG` exists but is undocumented | UNVERIFIED by this project (observed live by the WS-020 author) | LAB (other project) | WS-020 §17 |
| Logical export sections and 114 object types | UNVERIFIED (internal QA contract, live tenant1) | DOC | SRC-000004 |

## Open questions

- KG-044 (existing): element/machine state string casing between legacy and unified APIs.
- KG-110: official statement that the 400 example code lists are exhaustive, or an official error-code reference (none in the KB).
